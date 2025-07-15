from enum import Enum, unique


@unique
class PreprocessingType(Enum):
  """
  Available preprocessing types.
  """
  GRAYSCALE = 'grayscale'
  COLOR_MAP = 'colorMap'
  THRESHOLD = 'threshold'
  RESIZE = 'resize'
