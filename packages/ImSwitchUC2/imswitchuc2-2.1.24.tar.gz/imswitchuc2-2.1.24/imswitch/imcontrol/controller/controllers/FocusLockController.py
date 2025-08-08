import io
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple, List

import cv2
import numpy as np
import scipy.ndimage as ndi
from PIL import Image, ImageFile
from fastapi import Response
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter
from skimage.feature import peak_local_max
import threading
from imswitch.imcommon.framework import Thread, Signal  # noqa: F401 (Timer kept for context)
from imswitch.imcommon.model import initLogger, APIExport
from ..basecontrollers import ImConWidgetController
from imswitch import IS_HEADLESS

ImageFile.LOAD_TRUNCATED_IMAGES = True


@dataclass
class FocusLockParams:
    """Parameters for focus lock measurement and processing."""
    focus_metric: str = "JPG"
    crop_center: Optional[List[int]] = None
    crop_size: Optional[int] = None
    gaussian_sigma: float = 11.0
    background_threshold: float = 40.0
    update_freq: float = 10.0
    two_foci_enabled: bool = False
    z_stack_enabled: bool = False
    z_step_limit_nm: float = 40.0  # Minimum z-stack step in nanometers
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization."""
        return {
            "focus_metric": self.focus_metric,
            "crop_center": self.crop_center,
            "crop_size": self.crop_size,
            "gaussian_sigma": self.gaussian_sigma,
            "background_threshold": self.background_threshold,
            "update_freq": self.update_freq,
            "two_foci_enabled": self.two_foci_enabled,
            "z_stack_enabled": self.z_stack_enabled,
            "z_step_limit_nm": self.z_step_limit_nm,
        }


@dataclass
class PIControllerParams:
    """Parameters for PI controller feedback loop."""
    kp: float = 0.0
    ki: float = 0.0
    set_point: float = 0.0
    safety_distance_limit: float = 50.0
    safety_move_limit: float = 3.0
    min_step_threshold: float = 0.002
    safety_motion_active: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization."""
        return {
            "kp": self.kp,
            "ki": self.ki,
            "set_point": self.set_point,
            "safety_distance_limit": self.safety_distance_limit,
            "safety_move_limit": self.safety_move_limit,
            "min_step_threshold": self.min_step_threshold,
            "safety_motion_active": self.safety_motion_active,
        }


@dataclass 
class CalibrationParams:
    """Parameters for focus calibration."""
    from_position: float = 49.0
    to_position: float = 51.0
    num_steps: int = 20
    settle_time: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization."""
        return {
            "from_position": self.from_position,
            "to_position": self.to_position,
            "num_steps": self.num_steps,
            "settle_time": self.settle_time,
        }


@dataclass
class FocusLockState:
    """Current state of the focus lock system."""
    is_measuring: bool = False
    is_locked: bool = False
    about_to_lock: bool = False
    current_focus_value: float = 0.0
    lock_position: float = 0.0
    current_position: float = 0.0
    measurement_active: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization."""
        return {
            "is_measuring": self.is_measuring,
            "is_locked": self.is_locked,
            "about_to_lock": self.about_to_lock,
            "current_focus_value": self.current_focus_value,
            "lock_position": self.lock_position,
            "current_position": self.current_position,
            "measurement_active": self.measurement_active,
        }


class FocusLockController(ImConWidgetController):
    """Linked to FocusLockWidget."""

    sigUpdateFocusValue = Signal(object)  # (focus_data_dict)
    sigFocusLockStateChanged = Signal(object)  # (state_dict)
    sigCalibrationProgress = Signal(object)  # (progress_dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = initLogger(self)

        if self._setupInfo.focusLock is None:
            return

        self.camera = self._setupInfo.focusLock.camera
        self.positioner = self._setupInfo.focusLock.positioner
        try:
            self.stage = self._master.positionersManager[self.positioner]
        except KeyError:
            self._logger.error(f"Positioner '{self.positioner}' not found using first in list. ")
            self.positioner = self._master.positionersManager.getAllDeviceNames()[0]
            self.stage = self._master.positionersManager[self.positioner]

        # Initialize parameters from setup info
        self._focus_params = FocusLockParams(
            focus_metric=getattr(self._setupInfo.focusLock, "focusLockMetric", "JPG"),
            crop_center=getattr(self._setupInfo.focusLock, "cropCenter", None),
            crop_size=getattr(self._setupInfo.focusLock, "cropSize", None),
            update_freq=self._setupInfo.focusLock.updateFreq or 10,
        )
        
        self._pi_params = PIControllerParams(
            kp=self._setupInfo.focusLock.piKp,
            ki=self._setupInfo.focusLock.piKi,
        )
        
        self._calib_params = CalibrationParams()
        self._state = FocusLockState()

        # Legacy compatibility parameters - keep for backward compatibility
        self.setPointSignal = 0.0
        self.locked = False
        self.aboutToLock = False
        self.zStackVar = self._focus_params.z_stack_enabled
        self.twoFociVar = self._focus_params.two_foci_enabled
        self.noStepVar = True
        self.__isPollingFramesActive = True
        self.pollingFrameUpdateRate = 1.0 / self._focus_params.update_freq  # Update frequency in seconds
        
        self.zStepLimLo = 0.0
        self.aboutToLockDiffMax = 0.4
        self.lockPosition = 0.0
        self.currentPosition = 0.0
        self.lastPosition = 0.0
        self.buffer = 40
        self.currPoint = 0
        self.setPointData = np.zeros(self.buffer, dtype=float)
        self.timeData = np.zeros(self.buffer, dtype=float)
        self.reduceImageScaleFactor  = 1
        # Legacy parameters for astigmatism (from dataclass)
        self.gaussianSigma = self._focus_params.gaussian_sigma
        self.backgroundThreshold = self._focus_params.background_threshold
        self.cropCenter = self._focus_params.crop_center
        self.cropSize = self._focus_params.crop_size
        self.kp = self._pi_params.kp
        self.ki = self._pi_params.ki
        

        # Threads and Workers for focus lock
        try:
            self._master.detectorsManager[self.camera].startAcquisition()
        except Exception as e:
            self._logger.error(f"Failed to start acquisition on camera '{self.camera}': {e}")

        self.__processDataThread = ProcessDataThread(self)
        self.__focusCalibThread = FocusCalibThread(self)
        self.__processDataThread.setFocusLockMetric(self._focus_params.focus_metric)

        # start update thread
        self.updateThread()

        # In case we run on QT, assign the widgets
        if IS_HEADLESS:
            return
        self._widget.setKp(self._pi_params.kp)
        self._widget.setKi(self._pi_params.ki)

        # Connect FocusLockWidget buttons
        self._widget.kpEdit.textChanged.connect(self.unlockFocus)
        self._widget.kiEdit.textChanged.connect(self.unlockFocus)

        self._widget.lockButton.clicked.connect(self.toggleFocus)
        self._widget.camDialogButton.clicked.connect(self.cameraDialog)
        self._widget.focusCalibButton.clicked.connect(self.focusCalibrationStart)
        self._widget.calibCurveButton.clicked.connect(self.showCalibrationCurve)

        self._widget.zStackBox.stateChanged.connect(self.zStackVarChange)
        self._widget.twoFociBox.stateChanged.connect(self.twoFociVarChange)

        self._widget.sigSliderExpTValueChanged.connect(self.setExposureTime)
        self._widget.sigSliderGainValueChanged.connect(self.setGain)

    def __del__(self):
        try:
            self.__isPollingFramesActive = False
            self.__processDataThread.quit()
            self.__processDataThread.wait()
        except Exception:
            pass
        try:
            self.__focusCalibThread.quit()
            self.__focusCalibThread.wait()
        except Exception:
            pass
        try:
            if hasattr(self, "_master") and hasattr(self, "camera"):
                self._master.detectorsManager[self.camera].stopAcquisition()
        except Exception:
            pass
        try:
            if hasattr(self, "ESP32Camera"):
                self.ESP32Camera.stopStreaming()
        except Exception:
            pass
        if hasattr(super(), "__del__"):
            try:
                super().__del__()
            except Exception:
                pass

    def updateThread(self):
        """start pulling the update() function in a thread continously until the end of the lifetime of ImSwitch
        to pull the frames continously - we assume we don't have a camera in forAcquisition mode """
        self._pollFramesThread = threading.Thread(target=self._pollFrames, name="FocusLockPollFramesThread")
        self._pollFramesThread.daemon = True
        self._pollFramesThread.start()
        
        
    # === API Methods for Parameter Management ===
    
    
    @APIExport(runOnUIThread=True)
    def getFocusLockParams(self) -> Dict[str, Any]:
        """Get current focus lock parameters."""
        return self._focus_params.to_dict()

    @APIExport(runOnUIThread=True)
    def setFocusLockParams(self, **kwargs) -> Dict[str, Any]:
        """Set focus lock parameters. Returns updated parameters."""
        for key, value in kwargs.items():
            if hasattr(self._focus_params, key):
                setattr(self._focus_params, key, value)
                # Update legacy attributes for backward compatibility
                if key == "focus_metric":
                    self.__processDataThread.setFocusLockMetric(value)
                elif key == "two_foci_enabled":
                    self.twoFociVar = value
                elif key == "z_stack_enabled":
                    self.zStackVar = value
        return self._focus_params.to_dict()

    @APIExport(runOnUIThread=True)
    def getPIControllerParams(self) -> Dict[str, Any]:
        """Get current PI controller parameters."""
        return self._pi_params.to_dict()

    @APIExport(runOnUIThread=True)
    def setPIControllerParams(self, **kwargs) -> Dict[str, Any]:
        """Set PI controller parameters. Returns updated parameters."""
        for key, value in kwargs.items():
            if hasattr(self._pi_params, key):
                setattr(self._pi_params, key, value)
                # Update PI controller if it exists
                if hasattr(self, "pi") and key in ["kp", "ki"]:
                    self.pi.setParameters(self._pi_params.kp, self._pi_params.ki)
        
        # Update GUI if not headless
        if not IS_HEADLESS:
            self._widget.setKp(self._pi_params.kp)
            self._widget.setKi(self._pi_params.ki)
        
        return self._pi_params.to_dict()

    @APIExport(runOnUIThread=True)
    def getCalibrationParams(self) -> Dict[str, Any]:
        """Get current calibration parameters."""
        return self._calib_params.to_dict()

    @APIExport(runOnUIThread=True)
    def setCalibrationParams(self, **kwargs) -> Dict[str, Any]:
        """Set calibration parameters. Returns updated parameters."""
        for key, value in kwargs.items():
            if hasattr(self._calib_params, key):
                setattr(self._calib_params, key, value)
        return self._calib_params.to_dict()

    @APIExport(runOnUIThread=True)
    def getFocusLockState(self) -> Dict[str, Any]:
        """Get current focus lock state."""
        # Update state from current values
        self._state.is_locked = self.locked
        self._state.about_to_lock = self.aboutToLock
        self._state.current_focus_value = self.setPointSignal
        self._state.lock_position = self.lockPosition
        self._state.current_position = self.currentPosition
        self._state.measurement_active = hasattr(self, '__processDataThread') and self.__processDataThread.isRunning()
        return self._state.to_dict()

    # === Focus Measurement Control ===

    @APIExport(runOnUIThread=True)
    def startFocusMeasurement(self) -> bool:
        """Start focus value measurements from camera frames."""
        try:
            if not self._state.is_measuring:
                self._state.is_measuring = True
                self._emitStateChangedSignal()
                self._logger.info("Focus measurement started")
                return True
            return False
        except Exception as e:
            self._logger.error(f"Failed to start focus measurement: {e}")
            return False

    @APIExport(runOnUIThread=True)
    def stopFocusMeasurement(self) -> bool:
        """Stop focus value measurements."""
        try:
            if self._state.is_measuring:
                self._state.is_measuring = False
                self.unlockFocus()  # Also unlock if locked
                self._emitStateChangedSignal()
                self._logger.info("Focus measurement stopped")
                return True
            return False
        except Exception as e:
            self._logger.error(f"Failed to stop focus measurement: {e}")
            return False

    # === Focus Locking Control ===

    @APIExport(runOnUIThread=True)
    def enableFocusLock(self, enable: bool = True) -> bool:
        """Enable or disable focus locking (PI controller feedback)."""
        try:
            if enable and not self.locked:
                if not self._state.is_measuring:
                    self.startFocusMeasurement()
                zpos = self.stage.getPosition()["Z"]
                self.lockFocus(zpos)
                return True
            elif not enable and self.locked:
                self.unlockFocus()
                return True
            return False
        except Exception as e:
            self._logger.error(f"Failed to enable/disable focus lock: {e}")
            return False

    @APIExport(runOnUIThread=True)
    def isFocusLocked(self) -> bool:
        """Check if focus is currently locked."""
        return self.locked

    def _emitStateChangedSignal(self):
        """Emit state changed signal for WebSocket updates."""
        state_data = self.getFocusLockState()
        self.sigFocusLockStateChanged.emit(state_data)

    # === Legacy Methods (maintained for backward compatibility) ===

    @APIExport(runOnUIThread=True)
    def unlockFocus(self):
        if self.locked:
            self.locked = False
            if not IS_HEADLESS:
                self._widget.lockButton.setChecked(False)
                try:
                    self._widget.focusPlot.removeItem(self._widget.focusLockGraph.lineLock)
                except Exception:
                    pass

    @APIExport(runOnUIThread=True)  
    def toggleFocus(self, toLock:bool=None):
        self.aboutToLock = False
        if (not IS_HEADLESS and self._widget.lockButton.isChecked()) or (toLock is not None and toLock and self.locked is False):
            zpos = self.stage.getPosition()["Z"]
            self.lockFocus(zpos)
            if not IS_HEADLESS: self._widget.lockButton.setText("Unlock")
        else:
            self.unlockFocus()
            if not IS_HEADLESS:  self._widget.lockButton.setText("Lock")

    def cameraDialog(self):
        try:
            self._master.detectorsManager[self.camera].openPropertiesDialog()
        except Exception as e:
            self._logger.error(f"Failed to open camera dialog: {e}")

    @APIExport(runOnUIThread=True)
    def focusCalibrationStart(self):
        """Start focus calibration with current parameters."""
        self.__focusCalibThread.start()

    @APIExport(runOnUIThread=True)
    def runFocusCalibration(self, from_position: Optional[float] = None, 
                           to_position: Optional[float] = None,
                           num_steps: Optional[int] = None,
                           settle_time: Optional[float] = None) -> Dict[str, Any]:
        """Run focus calibration with specified parameters and return results."""
        # Update calibration parameters if provided
        if from_position is not None:
            self._calib_params.from_position = from_position
        if to_position is not None:
            self._calib_params.to_position = to_position
        if num_steps is not None:
            self._calib_params.num_steps = num_steps
        if settle_time is not None:
            self._calib_params.settle_time = settle_time
            
        # Start calibration in background thread
        self.__focusCalibThread.start()
        
        # Wait for completion and return results
        self.__focusCalibThread.wait()
        return self.__focusCalibThread.getData()

    @APIExport(runOnUIThread=True)
    def getCalibrationResults(self) -> Dict[str, Any]:
        """Get the results from the last calibration run."""
        return self.__focusCalibThread.getData()

    @APIExport(runOnUIThread=True)
    def isCalibrationRunning(self) -> bool:
        """Check if calibration is currently running."""
        return self.__focusCalibThread.isRunning()

    def showCalibrationCurve(self):
        if not IS_HEADLESS:
            self._widget.showCalibrationCurve(self.__focusCalibThread.getData())

    def twoFociVarChange(self):
        self.twoFociVar = not self.twoFociVar
        self._focus_params.two_foci_enabled = self.twoFociVar

    def zStackVarChange(self):
        self.zStackVar = not self.zStackVar
        self._focus_params.z_stack_enabled = self.zStackVar

    @APIExport(runOnUIThread=True)
    def setExposureTime(self, exposure_time: float):
        """Set camera exposure time."""
        try:
            self._master.detectorsManager[self.camera].setParameter('exposure', exposure_time)
            self._logger.debug(f"Set exposure time to {exposure_time}")
        except Exception as e:
            self._logger.error(f"Failed to set exposure time: {e}")

    @APIExport(runOnUIThread=True)  
    def setGain(self, gain: float):
        """Set camera gain."""
        try:
            self._master.detectorsManager[self.camera].setParameter('gain', gain)
            self._logger.debug(f"Set gain to {gain}")
        except Exception as e:
            self._logger.error(f"Failed to set gain: {e}")

    def _pollFrames(self):
        
        while self.__isPollingFramesActive:
            # Only process if measurement is enabled or legacy behavior is active
            time.sleep(self.pollingFrameUpdateRate)  # Sleep for the configured update frequency

            im = self._master.detectorsManager[self.camera].getLatestFrame()
            # Crop the image before processing
            import NanoImagingPack as nip
            if 1:
                self.cropped_im = nip.extract(img=im, ROIsize=(self._focus_params.crop_size, self._focus_params.crop_size), centerpos=self._focus_params.crop_center, PadValue=0.0, checkComplex=True)
            else:
                self.cropped_im = self.extract(
                im,
                crop_center=self._focus_params.crop_center,
                crop_size=self._focus_params.crop_size,
                )
            if not self._state.is_measuring and not self.locked and not self.aboutToLock:
                # For backward compatibility, still process if locked or about to lock
                continue
            self.setPointSignal = self.__processDataThread.update(self.cropped_im, self.twoFociVar)
            
            # Emit enhanced focus value signal with more context
            focus_data = {
                "focus_value": self.setPointSignal,
                "timestamp": time.time(),
                "is_locked": self.locked,
                "lock_position": self.lockPosition if self.locked else None,
                "current_position": self.stage.getPosition()["Z"],
                "focus_metric": self._focus_params.focus_metric,
            }
            self.sigUpdateFocusValue.emit(focus_data)
            
            # move
            if self.locked:
                value_move = self.updatePI()
                if self.noStepVar and abs(value_move) > self._pi_params.min_step_threshold:
                    self.stage.move(value_move, 0)
            elif self.aboutToLock:
                if not hasattr(self, "aboutToLockDataPoints"):
                    self.aboutToLockDataPoints = np.zeros(5, dtype=float)
                self.aboutToLockUpdate()

            # update graphics
            self.updateSetPointData()
            if IS_HEADLESS:
                continue
            try:
                self._widget.camImg.setImage(im)
                if self.currPoint < self.buffer:
                    self._widget.focusPlotCurve.setData(
                        self.timeData[1:self.currPoint],
                        self.setPointData[1:self.currPoint],
                    )
                else:
                    self._widget.focusPlotCurve.setData(self.timeData, self.setPointData)
            except Exception:
                pass
            

        @APIExport(runOnUIThread=True)
        def setParamsAstigmatism(
            self,
            gaussianSigma: float,
            backgroundThreshold: float,
            cropSize: int,
            cropCenter: Optional[List[int]] = None,
        ):
            """Set parameters for astigmatism focus metric."""
            # Update the new dataclass-based parameters
            self._focus_params.gaussian_sigma = float(gaussianSigma)
            self._focus_params.background_threshold = float(backgroundThreshold) 
            self._focus_params.crop_size = int(cropSize)
            if cropCenter is None:
                cropCenter = [cropSize // 2, cropSize // 2]
            self._focus_params.crop_center = cropCenter
            
            # Keep legacy attributes for backward compatibility
            self.gaussianSigma = float(gaussianSigma)
            self.backgroundThreshold = float(backgroundThreshold)
            self.cropSize = int(cropSize)
            if cropCenter is None:
                cropCenter = [self.cropSize // 2, self.cropSize // 2]
            self.cropCenter = np.asarray(cropCenter, dtype=int)

    @APIExport(runOnUIThread=True)
    def getParamsAstigmatism(self):
        """Get parameters for astigmatism focus metric."""
        # Return from dataclass for consistency
        return {
            "gaussianSigma": self._focus_params.gaussian_sigma,
            "backgroundThreshold": self._focus_params.background_threshold,
            "cropSize": self._focus_params.crop_size,
            "cropCenter": self._focus_params.crop_center,
        }

    def aboutToLockUpdate(self):
        self.aboutToLockDataPoints = np.roll(self.aboutToLockDataPoints, 1)
        self.aboutToLockDataPoints[0] = float(self.setPointSignal)
        averageDiff = float(np.std(self.aboutToLockDataPoints))
        if averageDiff < self.aboutToLockDiffMax:
            zpos = self.stage.getPosition()["Z"]
            self.lockFocus(zpos)
            self.aboutToLock = False

    def updateSetPointData(self):
        if self.currPoint < self.buffer:
            self.setPointData[self.currPoint] = self.setPointSignal
            self.timeData[self.currPoint] = 0.0  # placeholder for potential timing
        else:
            self.setPointData = np.roll(self.setPointData, -1)
            self.setPointData[-1] = self.setPointSignal
            self.timeData = np.roll(self.timeData, -1)
            self.timeData[-1] = 0.0
        self.currPoint += 1

    @APIExport(runOnUIThread=True)
    def setPIParameters(self, kp: float, ki: float):
        """Set parameters for the PI controller."""
        # Update dataclass parameters
        self._pi_params.kp = float(kp)
        self._pi_params.ki = float(ki)
        
        if not hasattr(self, "pi"):
            self.pi = PI(self.setPointSignal, kp, ki)
        else:
            self.pi.setParameters(kp, ki)
            
        # Keep legacy attributes for backward compatibility
        self.ki = ki
        self.kp = kp
        
        if not IS_HEADLESS:
            self._widget.setKp(kp)
            self._widget.setKi(ki)
         
    @APIExport(runOnUIThread=True)
    def getPIParameters(self) -> Tuple[float, float]:
        """Get parameters for the PI controller."""
        return self._pi_params.kp, self._pi_params.ki
       
    def updatePI(self):
        if not self.noStepVar:
            self.noStepVar = True
        self.currentPosition = float(self.stage.getPosition()["Z"])
        self.stepDistance = abs(self.currentPosition - self.lastPosition)
        distance = self.currentPosition - self.lockPosition
        move = self.pi.update(self.setPointSignal)
        self.lastPosition = self.currentPosition

        # Use parameters from dataclass
        if abs(distance) > self._pi_params.safety_distance_limit or abs(move) > self._pi_params.safety_move_limit and self._pi_params.safety_motion_active:
            self._logger.warning(
                f"Safety unlocking! Distance to lock: {distance:.3f}, current move step: {move:.3f}."
            )
            # Emit signal for WebSocket notification 
            safety_data = {
                "event": "safety_unlock",
                "distance_to_lock": distance,
                "move_step": move,
                "timestamp": time.time(),
            }
            self.sigFocusLockStateChanged.emit(safety_data)
            self.unlockFocus()
        elif self.zStackVar:
            if self.stepDistance > self.zStepLimLo:
                self.unlockFocus()
                self.aboutToLockDataPoints = np.zeros(5, dtype=float)
                self.aboutToLock = True
                self.noStepVar = False
        return move

    def lockFocus(self, zpos):
        if not self.locked:
            if IS_HEADLESS:
                kp, ki = self._pi_params.kp, self._pi_params.ki # TODO: who is master of states here? PI or FocusLockController?
            else:
                kp = float(self._widget.kpEdit.text())
                ki = float(self._widget.kiEdit.text())
                # Update dataclass with GUI values
                self._pi_params.kp = kp
                self._pi_params.ki = ki
            
            self._pi_params.set_point = self.setPointSignal
            self.pi = PI(self.setPointSignal, kp, ki)
            self.lockPosition = float(zpos)
            self.locked = True
            
            if not IS_HEADLESS:
                try:
                    self._widget.focusLockGraph.lineLock = self._widget.focusPlot.addLine(
                        y=self.setPointSignal, pen="r"
                    )
                    self._widget.lockButton.setChecked(True)
                except Exception:
                    pass
            
            self.updateZStepLimits()
            self._emitStateChangedSignal()
            self._logger.info(f"Focus locked at position {zpos} with set point {self.setPointSignal}")

    def updateZStepLimits(self):
        """Update z-step limits from parameters or GUI."""
        try:
            if not IS_HEADLESS and hasattr(self, '_widget'):
                self.zStepLimLo = 0.001 * float(self._widget.zStepFromEdit.text())
                # Also update the parameter for consistency
                self._focus_params.z_step_limit_nm = float(self._widget.zStepFromEdit.text())
            else:
                # Use parameter from dataclass (converted to micrometers)
                self.zStepLimLo = 0.001 * self._focus_params.z_step_limit_nm
        except Exception:
            # Fallback to parameter value
            self.zStepLimLo = 0.001 * self._focus_params.z_step_limit_nm

    @staticmethod
    def extract(marray: np.ndarray, crop_size: Optional[int] = None, crop_center: Optional[List[int]] = None) -> np.ndarray:
        """Extract/crop a region from an image array."""
        h, w = marray.shape[:2]
        if crop_center is None:
            center_x, center_y = w // 2, h // 2
        else:
            center_x, center_y = int(crop_center[0]), int(crop_center[1])

        if crop_size is None:
            crop_size = min(h, w) // 2
        crop_size = int(crop_size)

        half = crop_size // 2
        x_start = max(0, center_x - half)
        y_start = max(0, center_y - half)
        x_end = min(w, x_start + crop_size)
        y_end = min(h, y_start + crop_size)

        # Adjust starts if we hit a boundary on the end
        x_start = max(0, x_end - crop_size)
        y_start = max(0, y_end - crop_size)

        return marray[y_start:y_end, x_start:x_end]

    @APIExport(runOnUIThread=True)
    def setZStepLimit(self, limit_nm: float):
        """Set the minimum z-step limit in nanometers."""
        self._focus_params.z_step_limit_nm = float(limit_nm)
        self.updateZStepLimits()
        return self._focus_params.z_step_limit_nm

    @APIExport(runOnUIThread=True)
    def getZStepLimit(self) -> float:
        """Get the current z-step limit in nanometers."""
        return self._focus_params.z_step_limit_nm

    @APIExport(runOnUIThread=True)
    def returnLastCroppedImage(self) -> Response:
        """Returns the last cropped image from the camera."""
        try:
            arr = self.cropped_im
            im = Image.fromarray(arr.astype(np.uint8))
            with io.BytesIO() as buf:
                im = im.convert("L")  # ensure grayscale
                im.save(buf, format="PNG")
                im_bytes = buf.getvalue()
            headers = {"Content-Disposition": 'inline; filename="crop.png"'}
            return Response(im_bytes, headers=headers, media_type="image/png")
        except Exception as e:
            raise RuntimeError("No cropped image available. Please run update() first.") from e

    @APIExport(runOnUIThread=True)
    def returnLastImage(self) -> Response:
        lastFrame = self._master.detectorsManager[self.camera].getLatestFrame()
        # reduce side
        lastFrame = lastFrame[::self.reduceImageScaleFactor, ::self.reduceImageScaleFactor]
        if lastFrame is None:
            raise RuntimeError("No image available. Please run update() first.")
        try:
            im = Image.fromarray(lastFrame.astype(np.uint8))
            with io.BytesIO() as buf:
                im.save(buf, format="PNG")
                im_bytes = buf.getvalue()
            headers = {"Content-Disposition": 'inline; filename="last_image.png"'}
            return Response(im_bytes, headers=headers, media_type="image/png")
        except Exception as e:
            raise RuntimeError("Failed to convert last image to PNG.") from e

    @APIExport(runOnUIThread=True, requestType="POST")
    def setCropFrameParameters(self, cropSize: int, cropCenter: List[int] = None, frameSize: List[int] = None):
        """Set the crop frame parameters for the camera in pixelvalues
            cropSize - same for x/y
            cropCenter - center of the crop in pixelvalues, if None, center of the frame is used
            frameSize - size of the frame in pixelvalues, if None, the current camera frame
        """
        # first scale the values to real pixel values
        detectorSize = self._master.detectorsManager[self.camera].shape
        # scale the crop size to pixel values
        if frameSize is None:
            mRatio = 1/self.reduceImageScaleFactor
        else:
            mRatio =  detectorSize[0] / frameSize[0]  
        self._focus_params.crop_size = int(cropSize * mRatio)
        if cropCenter is None:
            cropCenter = [detectorSize[1] // 2, detectorSize[0] // 2]
        else:
            cropCenter = [int(cropCenter[1] * mRatio), int(cropCenter[0] * mRatio)]
        if cropSize < 100:
            cropSize = 100
        detectorSize = self._master.detectorsManager[self.camera].shape
        if cropSize > detectorSize[0] or cropSize > detectorSize[1]:
            raise ValueError(f"Crop size {cropSize} exceeds detector size {detectorSize}.")
        if cropCenter is None:
            cropCenter = [cropSize // 2, cropSize // 2]
        self._focus_params.crop_center = cropCenter
        self._logger.info(f"Set crop parameters: size={self._focus_params.crop_size}, center={self._focus_params.crop_center}")

        
class ProcessDataThread(Thread):
    def __init__(self, controller, *args, **kwargs):
        self._controller = controller
        super().__init__(*args, **kwargs)
        self.focusLockMetric: Optional[str] = None

    def setFocusLockMetric(self, focuslockMetric: str):
        self.focusLockMetric = focuslockMetric

    def getCroppedImage(self) -> np.ndarray:
        """Returns the last processed (cropped) image array."""
        if hasattr(self, "imagearraygf"):
            return self.imagearraygf
        raise RuntimeError("No image processed yet. Please run update() first.")

    def _jpeg_size_metric(self, img: np.ndarray) -> int:
        # Ensure uint8 grayscale for JPEG encode
        if img.dtype != np.uint8:
            img_u8 = np.clip(img, 0, 255).astype(np.uint8)
        else:
            img_u8 = img
        success, buffer = cv2.imencode(".jpg", img_u8, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not success:
            self._controller._logger.warning("Failed to encode image to JPEG.")
            return 0
        return int(len(buffer))

    def update(self, cropped_img: np.ndarray, twoFociVar: bool) -> float:
        """Update focus metric with pre-cropped image."""
        self.imagearraygf = cropped_img
        if self.focusLockMetric == "JPG":
            focusMetricGlobal = float(self._jpeg_size_metric(self.imagearraygf))
        elif self.focusLockMetric == "astigmatism":
            config = FocusConfig(
                gaussian_sigma=float(self._controller._focus_params.gaussian_sigma),
                background_threshold=int(self._controller._focus_params.background_threshold),
                crop_radius=int(self._controller._focus_params.crop_size or 300),
                enable_gaussian_blur=True,
            )
            focus_metric = FocusMetric(config)
            result = focus_metric.compute(self.imagearraygf)
            focusMetricGlobal = float(result["focus"])
            self._controller._logger.debug(
                f"Focus computation result: {result}, Focus value: {result['focus']:.4f}, Timestamp: {result['t']}"
            )
        else:
            # Gaussian filter to remove noise for better center estimate
            self.imagearraygf = gaussian_filter(self.imagearraygf.astype(float), 7)

            # Update the focus signal
            if twoFociVar:
                allmaxcoords = peak_local_max(self.imagearraygf, min_distance=60)
                size = allmaxcoords.shape[0]
                if size >= 2:
                    maxvals = np.full(2, -np.inf)
                    maxvalpos = np.zeros(2, dtype=int)
                    for n in range(size):
                        val = self.imagearraygf[allmaxcoords[n][0], allmaxcoords[n][1]]
                        if val > maxvals[0]:
                            if val > maxvals[1]:
                                maxvals[0] = maxvals[1]
                                maxvals[1] = val
                                maxvalpos[0] = maxvalpos[1]
                                maxvalpos[1] = n
                            else:
                                maxvals[0] = val
                                maxvalpos[0] = n
                    xcenter = allmaxcoords[maxvalpos[0]][0]
                    ycenter = allmaxcoords[maxvalpos[0]][1]
                    if allmaxcoords[maxvalpos[1]][1] < ycenter:
                        xcenter = allmaxcoords[maxvalpos[1]][0]
                        ycenter = allmaxcoords[maxvalpos[1]][1]
                    centercoords2 = np.array([xcenter, ycenter])
                else:
                    # Fallback to global max if not enough peaks
                    centercoords = np.where(self.imagearraygf == np.max(self.imagearraygf))
                    centercoords2 = np.array([centercoords[0][0], centercoords[1][0]])
            else:
                centercoords = np.where(self.imagearraygf == np.max(self.imagearraygf))
                centercoords2 = np.array([centercoords[0][0], centercoords[1][0]])

            subsizey = 50
            subsizex = 50
            h, w = self.imagearraygf.shape[:2]
            xlow = max(0, int(centercoords2[0] - subsizex))
            xhigh = min(h, int(centercoords2[0] + subsizex))
            ylow = max(0, int(centercoords2[1] - subsizey))
            yhigh = min(w, int(centercoords2[1] + subsizey))

            self.imagearraygfsub = self.imagearraygf[xlow:xhigh, ylow:yhigh]
            massCenter = np.array(ndi.center_of_mass(self.imagearraygfsub))
            # Add the information about where the center of the subarray is
            focusMetricGlobal = float(massCenter[1] + centercoords2[1])

        return focusMetricGlobal


class FocusCalibThread(Thread):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._controller = controller
        self.signalData: List[float] = []
        self.positionData: List[float] = []
        self.poly = None
        self.calibrationResult = None

    def run(self):
        """Run calibration using parameters from controller's dataclass."""
        self.signalData = []
        self.positionData = []
        
        calib_params = self._controller._calib_params
        
        # Use calibration parameters from dataclass or fallback to GUI
        if not IS_HEADLESS and hasattr(self._controller, '_widget'):
            try:
                from_val = float(self._controller._widget.calibFromEdit.text())
                to_val = float(self._controller._widget.calibToEdit.text()) 
            except (ValueError, AttributeError):
                from_val = calib_params.from_position
                to_val = calib_params.to_position
        else:
            from_val = calib_params.from_position
            to_val = calib_params.to_position
            
        scan_list = np.round(np.linspace(from_val, to_val, calib_params.num_steps), 2)
        
        # Emit progress signal for WebSocket updates
        progress_data = {
            "event": "calibration_started", 
            "total_steps": len(scan_list),
            "from_position": from_val,
            "to_position": to_val,
        }
        self._controller.sigCalibrationProgress.emit(progress_data)
        
        for i, z in enumerate(scan_list):
            self._controller._master.positionersManager[self._controller.positioner].setPosition(z, 0)
            time.sleep(calib_params.settle_time)
            focus_signal = float(self._controller.setPointSignal)
            actual_position = float(
                self._controller._master.positionersManager[self._controller.positioner].get_abs()
            )
            
            self.signalData.append(focus_signal)
            self.positionData.append(actual_position)
            
            # Emit progress updates
            progress_data = {
                "event": "calibration_progress",
                "step": i + 1,
                "total_steps": len(scan_list),
                "position": actual_position,
                "focus_value": focus_signal,
                "progress_percent": ((i + 1) / len(scan_list)) * 100,
            }
            self._controller.sigCalibrationProgress.emit(progress_data)
            
        self.poly = np.polyfit(self.positionData, self.signalData, 1)
        self.calibrationResult = np.around(self.poly, 4)
        
        # Emit completion signal
        completion_data = {
            "event": "calibration_completed",
            "coefficients": self.poly.tolist(),
            "r_squared": self._calculate_r_squared(),
            "sensitivity_nm_per_px": self._get_sensitivity_nm_per_px(),
        }
        self._controller.sigCalibrationProgress.emit(completion_data)
        
        self.show()

    def _calculate_r_squared(self) -> float:
        """Calculate R-squared value for the calibration fit."""
        if self.poly is None or len(self.signalData) == 0:
            return 0.0
        
        y_pred = np.polyval(self.poly, self.positionData)
        ss_res = np.sum((self.signalData - y_pred) ** 2)
        ss_tot = np.sum((self.signalData - np.mean(self.signalData)) ** 2)
        
        if ss_tot == 0:
            return 0.0
        return 1 - (ss_res / ss_tot)

    def _get_sensitivity_nm_per_px(self) -> float:
        """Get calibration sensitivity in nm per pixel."""
        if self.poly is None or self.poly[0] == 0:
            return 0.0
        return float(1000 / self.poly[0])  # Convert to nm/px

    def show(self):
        """Update GUI display if available."""
        if IS_HEADLESS or not hasattr(self._controller, '_widget'):
            return
            
        if self.poly is None or self.poly[0] == 0:
            cal_text = "Calibration invalid"
        else:
            cal_nm = self._get_sensitivity_nm_per_px()
            cal_text = f"1 px --> {cal_nm:.1f} nm"
        
        try:
            self._controller._widget.calibrationDisplay.setText(cal_text)
        except AttributeError:
            pass

    def getData(self) -> Dict[str, Any]:
        """Get calibration data for API or GUI use."""
        return {
            "signalData": self.signalData,
            "positionData": self.positionData,
            "poly": self.poly.tolist() if self.poly is not None else None,
            "calibrationResult": self.calibrationResult.tolist() if self.calibrationResult is not None else None,
            "r_squared": self._calculate_r_squared(),
            "sensitivity_nm_per_px": self._get_sensitivity_nm_per_px(),
        }


class PI:
    """Simple implementation of a discrete PI controller.
    Taken from http://code.activestate.com/recipes/577231-discrete-pid-controller/
    Author: Federico Barabas
    """

    def __init__(self, setPoint: float, kp: float = 0.0, ki: float = 0.0):
        self._kp = kp
        self._ki = ki
        self._setPoint = float(setPoint)
        self.error = 0.0
        self._started = False
        self.out = 0.0
        self.lastError = 0.0

    def setParameters(self, kp: float, ki: float):
        self.kp = kp
        self.ki = ki

    def update(self, currentValue: float) -> float:
        """Calculate PI output value for given reference input and feedback.
        Using the iterative formula to avoid integrative part building."""
        self.error = self.setPoint - float(currentValue)
        if self.started:
            self.dError = self.error - self.lastError
            self.out = self.out + self.kp * self.dError + self.ki * self.error
        else:
            self.out = self.kp * self.error
            self.started = True
        self.lastError = self.error
        return self.out

    def restart(self):
        self.started = False
        self.out = 0.0
        self.lastError = 0.0

    @property
    def started(self) -> bool:
        return self._started

    @started.setter
    def started(self, value: bool):
        self._started = bool(value)

    @property
    def setPoint(self) -> float:
        return self._setPoint

    @setPoint.setter
    def setPoint(self, value: float):
        self._setPoint = float(value)

    @property
    def kp(self) -> float:
        return self._kp

    @kp.setter
    def kp(self, value: float):
        self._kp = float(value)

    @property
    def ki(self) -> float:
        return self._ki

    @ki.setter
    def ki(self, value: float):
        self._ki = float(value)


"""
Focus Metric Algorithm Implementation

Based on the specification in section 5:
1. Convert frame to grayscale (numpy uint8)
2. Optional Gaussian blur σ ≈ 11 px to suppress noise
3. Threshold: im[im < background] = 0, background configurable
4. Compute mean projections projX, projY
5. Fit projX with double-Gaussian, projY with single-Gaussian (SciPy curve_fit)
6. Focus value F = σx / σy (float32)
7. Return timestamped JSON {"t": timestamp, "focus": F}
"""


@dataclass
class FocusConfig:
    """Configuration for focus metric computation"""
    gaussian_sigma: float = 11.0  # Gaussian blur sigma
    background_threshold: int = 40  # Background threshold value
    crop_radius: int = 300  # Radius for cropping around max intensity
    enable_gaussian_blur: bool = True  # Enable/disable Gaussian preprocessing


class FocusMetric:
    """Focus metric computation using double/single Gaussian fitting"""

    def __init__(self, config: Optional[FocusConfig] = None):
        self.config = config or FocusConfig()

    @staticmethod
    def gaussian_1d(xdata: np.ndarray, i0: float, x0: float, sigma: float, amp: float) -> np.ndarray:
        """Single Gaussian model function"""
        x = xdata
        x0 = float(x0)
        return i0 + amp * np.exp(-((x - x0) ** 2) / (2 * sigma ** 2))

    @staticmethod
    def double_gaussian_1d(
        xdata: np.ndarray, i0: float, x0: float, sigma: float, amp: float, dist: float
    ) -> np.ndarray:
        """Double Gaussian model function"""
        x = xdata
        x0 = float(x0)
        return (
            i0
            + amp * np.exp(-((x - (x0 - dist / 2)) ** 2) / (2 * sigma ** 2))
            + amp * np.exp(-((x - (x0 + dist / 2)) ** 2) / (2 * sigma ** 2))
        )

    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess frame according to specification steps 1-3

        Args:
            frame: Input frame (can be RGB or grayscale)

        Returns:
            Preprocessed grayscale frame
        """
        # Step 1: Convert to grayscale if needed
        if frame.ndim == 3:
            im = np.mean(frame, axis=-1).astype(np.uint8)
        else:
            im = frame.astype(np.uint8)

        # Convert to float for processing
        im = im.astype(float)

        # Find maximum intensity location for cropping
        if self.config.crop_radius > 0:
            # Apply heavy Gaussian blur to find general maximum location
            im_gauss = gaussian_filter(im, sigma=111)
            max_coord = np.unravel_index(np.argmax(im_gauss), im_gauss.shape)

            # Crop around maximum with specified radius
            h, w = im.shape
            y_min = max(0, max_coord[0] - self.config.crop_radius)
            y_max = min(h, max_coord[0] + self.config.crop_radius)
            x_min = max(0, max_coord[1] - self.config.crop_radius)
            x_max = min(w, max_coord[1] + self.config.crop_radius)

            im = im[y_min:y_max, x_min:x_max]

        # Step 2: Optional Gaussian blur to suppress noise
        if self.config.enable_gaussian_blur:
            im = gaussian_filter(im, sigma=self.config.gaussian_sigma)

        # Mean subtraction
        im = im - np.mean(im) / 2.0

        # Step 3: Threshold background
        im[im < self.config.background_threshold] = 0

        return im

    def preprocess_frame_rainer(self, frame: np.ndarray) -> np.ndarray:
        """
        Alternate preprocessor (kept for context). Implemented as a thin wrapper
        around `preprocess_frame` to avoid undefined references in the original.
        """
        return self.preprocess_frame(frame)

    def compute_projections(self, im: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Step 4: Compute mean projections projX, projY

        Args:
            im: Preprocessed image

        Returns:
            (projX, projY) - mean projections along y and x axes
        """
        projX = np.mean(im, axis=0)  # Project along y-axis
        projY = np.mean(im, axis=1)  # Project along x-axis
        return projX, projY

    def fit_projections(
        self, projX: np.ndarray, projY: np.ndarray, isDoubleGaussX: bool = False
    ) -> Tuple[float, float]:
        """
        Steps 5-6: Fit projections and compute focus value

        Args:
            projX: X projection (fit with double-Gaussian if requested)
            projY: Y projection (fit with single-Gaussian)

        Returns:
            (sigma_x, sigma_y) - fitted standard deviations
        """
        h1, w1 = len(projY), len(projX)
        x = np.arange(w1)
        y = np.arange(h1)

        # Initial guess parameters
        i0_x = float(np.mean(projX))
        amp_x = float(np.max(projX) - i0_x)
        sigma_x_init = float(np.std(projX))
        i0_y = float(np.mean(projY))
        amp_y = float(np.max(projY) - i0_y)
        sigma_y_init = float(np.std(projY))

        if isDoubleGaussX:
            init_guess_x = [i0_x, w1 / 2, sigma_x_init, amp_x, 100.0]
        else:
            init_guess_x = [i0_x, w1 / 2, sigma_x_init, amp_x]
        init_guess_y = [i0_y, h1 / 2, sigma_y_init, amp_y]

        try:
            if isDoubleGaussX:
                popt_x, _ = curve_fit(self.double_gaussian_1d, x, projX, p0=init_guess_x, maxfev=50000)
                sigma_x = abs(float(popt_x[2]))
            else:
                popt_x, _ = curve_fit(self.gaussian_1d, x, projX, p0=init_guess_x, maxfev=50000)
                sigma_x = abs(float(popt_x[2]))

            popt_y, _ = curve_fit(self.gaussian_1d, y, projY, p0=init_guess_y, maxfev=50000)
            sigma_y = abs(float(popt_y[2]))
        except Exception:
            # Fallback to standard deviation if fitting fails
            sigma_x = float(np.std(projX))
            sigma_y = float(np.std(projY))

        return sigma_x, sigma_y

    def compute(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Main computation method - implements complete focus metric algorithm

        Args:
            frame: Input camera frame (RGB or grayscale)

        Returns:
            Timestamped JSON with focus value: {"t": timestamp, "focus": focus_value}
        """
        timestamp = time.time()

        try:
            im = self.preprocess_frame(frame)
            projX, projY = self.compute_projections(im)
            sigma_x, sigma_y = self.fit_projections(projX, projY)
            focus_value = 12334567 if sigma_y == 0 else float(sigma_x / sigma_y)
        except Exception:
            focus_value = 12334567

        return {"t": timestamp, "focus": focus_value}

    def update_config(self, **kwargs) -> None:
        """Update configuration parameters"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                raise ValueError(f"Unknown configuration parameter: {key}")


# Copyright (C) 2020-2024 ImSwitch developers
# This file is part of ImSwitch.
#
# ImSwitch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ImSwitch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
