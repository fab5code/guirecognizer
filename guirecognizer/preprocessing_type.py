from enum import Enum, unique, auto

@unique
class PreprocessingType(Enum):
  """
  Available preprocessing types.
  """
  GRAYSCALE = auto()
  COLOR_MAP = auto()
  THRESHOLD = auto()
  RESIZE = auto()
