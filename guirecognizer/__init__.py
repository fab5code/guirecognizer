from .action_type import ActionType, SelectionType
from .common import RecognizerValueError
from .mouse_helper import MouseHelper
from .preprocessing import (ColorMapMethod, ColorMapPreprocessor,
                            GrayscalePreprocessor, Preprocessing, ResizeMethod,
                            ResizePreprocessor, ThresholdMethod,
                            ThresholdPreprocessor, ThresholdType)
from .preprocessing_type import PreprocessingType
from .recognizer import OcrType, Recognizer

"""A library to help recognize some patterns on screen and make GUI actions."""

__version__ = "0.1.0"
