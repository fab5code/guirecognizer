from typing import Any
from PIL import Image

class RecognizerValueError(ValueError):
  """
  Exception for invalid config data or action or preprocessing operation options.
  """
  pass

def isIdDataValid(idData: Any) -> bool:
  """
  :param idData:
  """
  return type(idData) == str and idData

def isPixelColorDataValid(pixelColorData: Any) -> bool:
  """
  :param pixelColorData:
  """
  return isinstance(pixelColorData, (list, tuple)) and len(pixelColorData) == 3 \
      and all(isinstance(i, int) and 0 <= i and i <= 255 for i in pixelColorData)

def isPixelColorDifferenceDataValid(differenceData: Any) -> bool:
  """
  :param differenceData:
  """
  return isinstance(differenceData, (int, float)) and 0 <= differenceData and differenceData <= 1

def isImageDataValid(imageData: Any) -> bool:
  """
  :param imageData:
  """
  return isinstance(imageData, Image.Image)
