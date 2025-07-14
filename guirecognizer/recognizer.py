from enum import Enum, unique, auto
from io import BytesIO
import json
import logging
from math import ceil
import os
from statistics import mean
from typing import Any
from PIL import Image, ImageOps, ImageGrab, ImageStat
from imagehash import phash, colorhash, ImageHash, hex_to_hash, hex_to_flathash
import base64
from io import BytesIO
import numpy as np

from .action_type import ActionType, SelectionType
from .common import RecognizerValueError, isIdDataValid, isImageDataValid, isPixelColorDataValid, isPixelColorDifferenceDataValid
from .mouse_manager import MouseManager
from .preprocessing import Preprocessing
from .types import Coord, Ratios, PixelColor

logger = logging.getLogger(__name__)

AnyActionReturnType = Image.Image | list[Coord] | tuple[int, ...] | list[int] | str | int | float | bool | None

@unique
class OcrType(Enum):
  """
  OCR types.
  """
  TESSERACT = 'tesseract'
  EASY_OCR = 'easyOcr'

class Recognizer():
  """
  Recognize given patterns and make GUI actions.

  Can be used to load a config file or its content of actions (:class:`ActionType`).

  Can also be used as a static class to call a single action.
  """

  def __init__(self, data: str | dict | None=None) -> None:
    """
    :param data: (optional) config filepath or config data
    :raise RecognizerValueError: invalid `data`
    """
    self.borders = None
    self.actionById = {}
    self.ocrOrder = [OcrType.EASY_OCR, OcrType.TESSERACT]
    self.easyOcrReader = None
    self.tesseractOptions = None
    self.preprocessing = Preprocessing()
    if type(data) == str:
      self.loadFilepath(data)
    elif type(data) == dict:
      self.loadData(data)
    elif data is not None:
      raise RecognizerValueError('Expect a filepath or a dict as config data.')

  @classmethod
  def isBordersDataValid(cls, bordersData: Any) -> bool:
    """
    :param bordersData:
    """
    return isinstance(bordersData, (list, tuple)) and len(bordersData) == 4 \
        and all(isinstance(i, int) for i in bordersData) \
        and bordersData[0] <= bordersData[2] and bordersData[1] <= bordersData[3]

  @classmethod
  def isImageDataValid(cls, imageData: Any) -> bool:
    """
    :param imageData:
    """
    return isImageDataValid(imageData)

  @classmethod
  def isIdDataValid(cls, idData: Any) -> bool:
    """
    :param idData:
    """
    return isIdDataValid(idData)

  @classmethod
  def isRatiosDataValid(cls, ratiosData: Any) -> bool:
    """
    :param ratiosData:
    """
    return isinstance(ratiosData, (list, tuple)) and all(isinstance(n, (int, float)) for n in ratiosData) \
        and (len(ratiosData) == 2 or (len(ratiosData) == 4 and ratiosData[0] <= ratiosData[2] and ratiosData[1] <= ratiosData[3]))

  @classmethod
  def isTypeDataValid(cls, typeData: Any) -> bool:
    """
    :param typeData:
    """
    return type(typeData) == str and typeData in [actionType.value for actionType in ActionType]

  @classmethod
  def isCoordDataValid(cls, coordData: Any) -> bool:
    """
    :param coordData:
    """
    return isinstance(coordData, (list, tuple)) and all(isinstance(i, int) for i in coordData) \
        and (len(coordData) == 2 or (len(coordData) == 4 and coordData[0] <= coordData[2] and coordData[1] <= coordData[3]))

  @classmethod
  def isPointDataValid(cls, pointData: Any) -> bool:
    """
    :param pointData:
    """
    if isinstance(pointData, int):
      return 0 <= pointData and pointData <= 255
    return isinstance(pointData, (list, tuple)) and len(pointData) in [3, 4] \
        and all(isinstance(i, int) and 0 <= i and i <= 255 for i in pointData)

  @classmethod
  def isPixelColorDataValid(cls, pixelColorData: Any) -> bool:
    """
    :param pixelColorData:
    """
    return isPixelColorDataValid(pixelColorData)

  @classmethod
  def isPixelColorDifferenceDataValid(cls, differenceData: Any) -> bool:
    """
    :param differenceData:
    """
    return isPixelColorDifferenceDataValid(differenceData)

  @classmethod
  def isAreaDataValid(cls, areaData: Any) -> bool:
    """
    :param areaData:
    """
    return isinstance(areaData, Image.Image)

  @classmethod
  def isImageToFindDataValid(cls, imageToFindData: Any) -> bool:
    """
    :param imageToFindData:
    """
    if not isinstance(imageToFindData, str):
      return False
    try:
      cls.getImageToFindFromData(imageToFindData)
    except:
      return False
    return True

  @classmethod
  def isThresholdDataValid(cls, thresholdData: Any) -> bool:
    """
    :param thresholdData:
    """
    return isinstance(thresholdData, int) and thresholdData >= 0

  @classmethod
  def isMaxResultsDataValid(cls, maxResultsData: Any) -> bool:
    """
    :param maxResultsData:
    """
    return isinstance(maxResultsData, int) and maxResultsData > 0

  @classmethod
  def isResizeIntervalDataValid(cls, resizeIntervalData: Any) -> bool:
    """
    :param resizeIntervalData:
    """
    return isinstance(resizeIntervalData, (list, tuple)) and len(resizeIntervalData) == 2 \
        and all(isinstance(i, (int, float)) and i > 0 for i in resizeIntervalData) and resizeIntervalData[0] <= resizeIntervalData[1]

  @classmethod
  def isImageToFindCompatibleWithSelection(cls, imageToFind: str, borders: Coord, ratios: Ratios,
        resizeInterval: tuple[int, int] | None=None) -> bool:
    """
    :param imageToFind:
    :param borders:
    :param ratios:
    :param resizeInterval: (optional)
    """
    coord = cls.getCoord(borders, ratios)
    return cls.isImageToFindCompatibleWithAreaSize(imageToFind, (coord[2] - coord[0], coord[3] - coord[1]), resizeInterval)

  @classmethod
  def isImageToFindCompatibleWithAreaSize(cls, imageToFindValue: str, areaSize: tuple[int, int],
      resizeInterval: tuple[int, int] | None=None) -> bool:
    """
    :param imageToFindValue:
    :param areaSize:
    :param resizeInterval: (optional)
    """
    image = cls.getImageToFindFromData(imageToFindValue)
    imageSize = (image.width, image.height)
    if resizeInterval is not None:
      imageSize = (int(imageSize[0] * resizeInterval[1]), int(imageSize[1] * resizeInterval[1]))
    # TODO: should it be "<="" instead of "<"? The actual computation does floor the value with int. Also change the app checking image to find.
    return imageSize[0] < areaSize[0] and imageSize[1] < areaSize[1]

  @classmethod
  def isImageHashDataValid(cls, imageHashData: Any) -> bool:
    """
    :param imageHashData:
    """
    if not isinstance(imageHashData, str):
      return False
    try:
      hash = cls._getRawImageHashFromStr(imageHashData)
    except:
      return False
    return hash[0].hash.size == 64 and hash[1].hash.size == 42

  @classmethod
  def isImageHashDifferenceDataValid(cls, differenceData: Any) -> bool:
    """
    :param differenceData:
    """
    return isinstance(differenceData, int) and 0 <= differenceData

  @classmethod
  def isOcrOrderDataValid(cls, ocrOrderData: Any) -> bool:
    """
    :param ocrOrderData: In string form.
    """
    ocrTypes = set(ocrType.value for ocrType in OcrType)
    return isinstance(ocrOrderData, (tuple, list)) \
        and all(isinstance(ocrType, str) and ocrType in ocrTypes for ocrType in ocrOrderData) \
        and len(ocrOrderData) == len(set(ocrOrderData))

  @classmethod
  def getCoord(cls, borders: Coord, ratios: Ratios) -> tuple[int, int, int, int]:
    """
    :param borders:
    :param ratios:
    :return: absolute coordinates
    :raise RecognizerValueError: `borders` or `ratios` are invalid
    """
    width = borders[2] - borders[0]
    height = borders[3] - borders[1]
    x1Ratio = round(borders[0] + width * ratios[0])
    y1Ratio = round(borders[1] + height * ratios[1])
    if len(ratios) == 2:
      return (x1Ratio, y1Ratio)
    elif len(ratios) == 4:
      x2Ratio = round(borders[0] + width * ratios[2])
      y2Ratio = round(borders[1] + height * ratios[3])
      if x2Ratio == x1Ratio:
        x2Ratio += 1
      if y2Ratio == y1Ratio:
        y2Ratio += 1
      return (x1Ratio, y1Ratio, x2Ratio, y2Ratio)
    raise RecognizerValueError('Parameters borders or ratios are invalid.')

  @classmethod
  def getPoint(cls, coord: Coord) -> tuple[int, int, int] | int:
    """
    :param coord:
    :return: rgb colors - If outside screen (0, 0, 0).
    """
    imageCoord = (coord[0], coord[1], coord[0] + 1, coord[1] + 1)
    try:
      image = ImageGrab.grab(imageCoord)
      return image.getpixel((0, 0))
    except:
      return (0, 0, 0)

  @classmethod
  def getPointFromScreenshot(cls, screenshot: Image.Image, coord: Coord) -> tuple[int, int, int] | tuple[int, int, int, int] | int:
    """
    :param screenshot:
    :param coord:
    :return: rgb colors with or without alpha or gray value depending of `screenshot`
    """
    if coord[0] < 0 or coord[0] >= screenshot.size[0] or coord[1] < 0 or coord[1] >= screenshot.size[1]:
      return (0, 0, 0)
    else:
      return screenshot.getpixel((coord[0], coord[1]))

  @classmethod
  def getPointFromBordersImage(cls, bordersImage: Image.Image, coord: Coord, borders: Coord) -> tuple[int, int, int] | tuple[int, int, int, int] | int:
    """
    :param bordersImage:
    :param coord:
    :param borders:
    :return: rgb colors with or without alpha or gray value depending of `bordersImage`
    """
    relativeCoord = (coord[0] - borders[0], coord[1] - borders[1])
    return cls.getPointFromScreenshot(bordersImage, relativeCoord)

  @classmethod
  def getPixelColor(cls, point: tuple[int, int, int] | tuple[int, int, int, int] | int) -> tuple[int, int, int]:
    """
    :param point:
    :return: rgb colors without alpha
    """
    if isinstance(point, int):
      return (point, point, point)
    return point[0:3]

  @classmethod
  def getAveragePixelColor(cls, area: Image.Image) -> tuple[int, int, int]:
    """
    :param area:
    :return: rgb colors without alpha
    """
    stat = ImageStat.Stat(area)
    pixelColor = tuple([round(i) for i in stat.mean])
    if len(pixelColor) < 3:
      pixelColor = (pixelColor[0], pixelColor[0], pixelColor[0])
    return cls.getPixelColor(pixelColor)

  @classmethod
  def getPixelColorDifference(cls, pixelColorA: PixelColor, pixelColorB: PixelColor) -> float:
    """
    :param pixelColorA:
    :param pixelColorB:
    """
    return mean(tuple(map(lambda x, y: abs(x - y) / 255, pixelColorA, pixelColorB)))

  @classmethod
  def getArea(cls, coord: Coord) -> Image.Image:
    """
    :param coord:
    """
    return ImageGrab.grab(coord)

  @classmethod
  def getAreaFromScreenshot(cls, screenshot: Image.Image, coord: Coord) -> Image.Image:
    """
    :param screenshot:
    :param coord:
    """
    return screenshot.crop(coord)

  @classmethod
  def getAreaFromBordersImage(cls, bordersImage: Image.Image, coord: Coord, borders: Coord) -> Image.Image:
    """
    :param bordersImage:
    :param coord:
    :param borders:
    """
    relativeCoord = (coord[0] - borders[0], coord[1] - borders[1], coord[2] - borders[0], coord[3] - borders[1])
    return cls.getAreaFromScreenshot(bordersImage, relativeCoord)

  @classmethod
  def findImageCoordinates(cls, areaCoord: Coord, area: Image.Image, imageToFindValue: str,
      threshold: int, maxResults: int, resizeInterval: tuple[int, int] | None=None) -> list[Coord]:
    """
    :param areaCoord:
    :param area:
    :param imageToFindValue:
    :param threshold:
    :param maxResults:
    :param resizeInterval: (optional)
    """
    imageToFind = cls.getImageToFindFromData(imageToFindValue)
    return cls.findImageCoordinatesWithImageToFindAsImage(areaCoord, area, imageToFind, threshold, maxResults, resizeInterval)

  @classmethod
  def findImageCoordinatesWithImageToFindAsImage(cls, areaCoord: Coord, area: Image.Image, imageToFind: Image.Image,
      threshold: int, maxResults: int, resizeInterval: tuple[int, int] | None=None) -> list[Coord]:
    """
    :param areaCoord:
    :param area:
    :param imageToFind:
    :param threshold:
    :param maxResults:
    :param resizeInterval: (optional)
    """
    imageToFindHash = cls._getRawImageHash(imageToFind)
    areaCv = np.array(ImageOps.grayscale(area))

    if resizeInterval is None:
      results = cls._computeFindImageMatchResults(imageToFind, areaCv)
    else:
      nbMatches = 1 + ceil((resizeInterval[1] - resizeInterval[0]) / 0.05)
      precedentSize = None
      results = []
      # Multiprocessing seemed like a good idea but the overhead is too high.
      for ratio in np.linspace(resizeInterval[0], resizeInterval[1], num=nbMatches):
        newSize = (int(imageToFind.size[0] * ratio), int(imageToFind.size[1] * ratio))
        if newSize == precedentSize:
          continue
        precedentSize = newSize
        localImageToFind = imageToFind.resize(newSize, Image.LANCZOS)
        localResults = cls._computeFindImageMatchResults(localImageToFind, areaCv)
        results += localResults

    results.sort(key=lambda result: result[2], reverse=True)
    coords = []
    # Only a certain number of the best matches are tested using their image hash.
    maxResultsToInspect = 2 * maxResults + 5
    nbInspections = 0
    for result in results:
      if nbInspections == maxResultsToInspect or len(coords) == maxResults:
        break
      relativeCoord = (int(result[0]), int(result[1]), int(result[0] + result[3][0]), int(result[1] + result[3][1]))
      coord = (areaCoord[0] + relativeCoord[0], areaCoord[1] + relativeCoord[1],
          areaCoord[0] + relativeCoord[2], areaCoord[1] + relativeCoord[3])
      if cls._doesOverlay(coord, coords):
        continue
      nbInspections += 1
      resultHash = cls._getRawImageHash(area.crop(relativeCoord))
      if cls._getRawImageHashDifference(resultHash, imageToFindHash) > threshold:
        continue
      coords.append(coord)
    return coords

  @classmethod
  def _computeFindImageMatchResults(cls, imageToFind: Image.Image, areaCv: np.ndarray) -> list[tuple]:
    """
    :param imageToFind:
    :param areaCv:
    """
    import cv2 as cv

    imageToFindCv = np.array(ImageOps.grayscale(imageToFind))
    matches = cv.matchTemplate(areaCv, imageToFindCv, cv.TM_CCOEFF_NORMED)
    # Matches with a very low match value are not considered.
    indices = np.where(matches >= 0.2)
    return [(indice[1], indice[0], matches[indice], imageToFind.size) for indice in zip(*indices)]

  @classmethod
  def _doesOverlay(cls, coord: Coord, coords: list[Coord]) -> bool:
    """
    Return whether `coord` overlays one of `coords` more than 70% for each axe.

    :param coord:
    :param coords:
    """
    overlayThreshold = 1 - 0.7
    width = coord[2] - coord[0]
    height = coord[3] - coord[1]
    for otherCoord in coords:
      if abs(otherCoord[0] - coord[0]) < overlayThreshold * width and abs(otherCoord[1] - coord[1]) < overlayThreshold * height:
        return True
    return False

  @classmethod
  def getImageToFindFromData(cls, imageToFindValue: str) -> Image.Image:
    """
    :param imageToFindValue:
    """
    return Image.open(BytesIO(base64.b64decode(imageToFindValue)))

  @classmethod
  def getImageHash(cls, area: Image.Image) -> str:
    """
    :param area:
    """
    imageHash = cls._getRawImageHash(area)
    return str(imageHash[0]) + ',' + str(imageHash[1])

  @classmethod
  def _getRawImageHash(cls, area: Image.Image) -> tuple[ImageHash, ImageHash]:
    """
    :param area:
    """
    return (phash(area), colorhash(area))

  @classmethod
  def _getRawImageHashFromStr(cls, hashValue: str) -> tuple[ImageHash, ImageHash]:
    """
    :param hashValue:
    """
    phashValue, colorhashValue = hashValue.split(',')
    return (hex_to_hash(phashValue), hex_to_flathash(colorhashValue, 14))

  @classmethod
  def getImageHashDifference(cls, hashA: str, hashB: str) -> int:
    """
    :param hashA:
    :param hashB:
    """
    return cls._getRawImageHashDifference(cls._getRawImageHashFromStr(hashA), cls._getRawImageHashFromStr(hashB))

  @classmethod
  def _getRawImageHashDifference(cls, hashA: tuple[ImageHash, ImageHash], hashB: tuple[ImageHash, ImageHash]) -> int:
    """
    :param hashA:
    :param hashB:
    """
    return int((hashA[0] - hashB[0]) + (hashA[1] - hashB[1]))

  @classmethod
  def getTextTesseractOcr(cls, area: Image.Image, lang: str, config: str) -> str | None:
    """
    :param area:
    :param str:
    :param config:
    """
    import pytesseract

    result = pytesseract.image_to_string(area, lang=lang, config=config)
    if result == '':
      return None
    return result

  @classmethod
  def _getEasyOcrPredictions(cls, image: Image.Image, reader) -> list[str]:
    """
    :param image:
    :param reader:
    """
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return reader.readtext(buffer.getvalue(), detail=0)

  def loadFilepath(self, filepath: str) -> None:
    """
    Load actions.

    Can be called multiple times to load many files.

    :param filepath: config filepath
    :raise RecognizerValueError: invalid json data
    """
    with open(filepath, 'r') as file:
      try:
        data = json.load(file)
      except:
        raise RecognizerValueError('Invalid data: config file must be of format json.')
    self.loadData(data)

  def loadData(self, data: dict) -> None:
    """
    Load actions.

    Can be called multiple times to load more data.

    :param data: config data
    :raise RecognizerValueError: invalid or incomplete `data`
    """
    if type(data) != dict:
      raise RecognizerValueError('Invalid data: data to be loaded should be a dict.')

    if 'borders' in data and self.isBordersDataValid(data['borders']):
      self.borders = data['borders']
    else:
      raise RecognizerValueError('Incomplete data: the borders are missing which are necessary for any use.')

    if 'actions' in data and isinstance(data['actions'], (list, tuple)):
      for actionData in data['actions']:
        if type(actionData) != dict:
          raise RecognizerValueError('Invalid action data: every action data should be a dict.')
        self._createAction(actionData)
    else:
      raise RecognizerValueError('Incomplete data: the list of actions is missing.')
    self.preprocessing.loadData(data)

  def clearAllData(self) -> None:
    """
    Remove all data.
    """
    self.actionById.clear()
    self.preprocessing.clearAllData()

  def setOcrOrder(self, ocrOrder: tuple[OcrType, ...] | list[OcrType]) -> None:
    """
    :param ocrOrder:
    :raise RecognizerValueError: invalid `ocrOrder`
    """
    if not isinstance(ocrOrder, (tuple, list)) or any(not isinstance(ocrType, OcrType) for ocrType in ocrOrder) \
        or len(ocrOrder) == 0 or len(ocrOrder) != len(set(ocrOrder)):
      raise RecognizerValueError('Invalid OCR order: expects a list of OCR types containing a least one and without duplicates.')
    self.ocrOrder = ocrOrder

  def setTesseractOcr(self, tesseract_cmd: str | None=None, lang: str='eng',
      textConfig: str='--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ|0°@',
      numberConfig: str='--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789oOQiIl|') -> None:
    """
    :param tesseract_cmd: Filepath to tesseract.exe. If None, it tries to find the filepath which can take seconds or minutes.
    :param lang:
    :param textConfig:
    :param numberConfig:
    :raise RecognizerValueError: Automatically finding tesseract.exe filepath failed.
    """
    import pytesseract

    self.tesseractOptions = {
      'lang': lang,
      'textConfig': textConfig,
      'numberConfig': numberConfig
    }
    if tesseract_cmd is not None:
      pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
      return

    filename = 'tesseract.exe'
    for root, _, files in os.walk(os.path.abspath(os.sep)):
      for name in files:
        if name == filename:
          pytesseract.pytesseract.tesseract_cmd = os.path.abspath(os.path.join(root, name))
          return
    raise RecognizerValueError('Could not automatically find the filepath of tesseract.exe.'
        ' Maybe tesseract is not installed. More information is available in the documentation of pytesseract.'
        ' Installation link: https://github.com/tesseract-ocr/tesseract')

  def setEasyOcr(self, languages: list[str]=['en'], gpu: bool=False) -> None:
    """
    :param languages:
    :param gpu:
    """
    import easyocr
    self.easyOcrReader = easyocr.Reader(languages, gpu=gpu)

  def getTextEasyOcr(self, area: Image.Image) -> str | None:
    """
    :param area:
    :param reader:
    """
    if self.easyOcrReader is None:
      self.setEasyOcr()
    predictions = self._getEasyOcrPredictions(area, self.easyOcrReader)
    if len(predictions) == 0:
      return None
    return predictions[0]

  def getText(self, area: Image.Image) -> str:
    """
    :param area:
    """
    for ocrType in self.ocrOrder:
      result = self._getTextFromOcr(area, ocrType)
      if result is not None:
        return result
    return ''

  def _getTextFromOcr(self, area: Image.Image, ocrType: OcrType) -> str | None:
    """
    :param area:
    :param ocrType:
    """
    match ocrType:
      case OcrType.TESSERACT:
        if self.tesseractOptions is None:
          self.setTesseractOcr()
        return self.getTextTesseractOcr(area, self.tesseractOptions['lang'], self.tesseractOptions['textConfig'])
      case OcrType.EASY_OCR:
        return self.getTextEasyOcr(area)

  def getNumber(self, area: Image.Image) -> float | None:
    """
    :param area:
    """
    for ocrType in self.ocrOrder:
      result = self._getNumberFromOcr(area, ocrType)
      if result is not None:
        return result
    return None

  def _getNumberFromOcr(self, area: Image.Image, ocrType: OcrType) -> float | None:
    """
    :param area:
    :param ocrType:
    """
    match ocrType:
      case OcrType.TESSERACT:
        if self.tesseractOptions is None:
          self.setTesseractOcr()
        result = self.getTextTesseractOcr(area, self.tesseractOptions['lang'], self.tesseractOptions['numberConfig'])
      case OcrType.EASY_OCR:
        result = self.getTextEasyOcr(area)
    if result is None:
      return None
    result = result.replace('o', '0').replace('O', '0').replace('Q', '0')
    result = result.replace('i', '1').replace('I', '1').replace('l', '1').replace('|', '1')
    try:
      return float(result)
    except ValueError:
      return None

  def _createAction(self, data: dict) -> None:
    """
    Create an action and add it to the list of actions.

    The config data of the actions can have action not yet properly defined by the user.
    This is why invalid action should be ignored with a warning and not trigger an error.

    :param data:
    """
    if 'id' in data and self.isIdDataValid(data['id']):
      actionId = data['id']
      if actionId in self.actionById:
        logger.warning(f'Action id \'{actionId}\' is already used. This action is ignored.')
        return
      action = {'id': actionId}
    else:
      logger.warning('Invalid action id. This action is ignored.')
      return

    if 'ratios' in data and self.isRatiosDataValid(data['ratios']):
      action['ratios'] = data['ratios']
    else:
      logger.warning(f'Invalid action ratios. This action \'{actionId}\' is ignored.')
      return

    if 'type' in data and self.isTypeDataValid(data['type']):
      action['type'] = ActionType(data['type'])
    else:
      logger.warning(f'Invalid action type. This action \'{actionId}\' is ignored.')
      return

    if not action['type'].isCompatibleWithSelection(action['ratios']):
      logger.warning('Size of action ratios (2) is too small for action type \'{actionType}\'. This action \'{actionId}\' is ignored.'
          .format(actionType=action['type'].value, actionId=actionId))
      return
    elif not action['type'].isRightSelection(action['ratios']):
      logger.warning('Size of action ratios (4) is bigger than necessary for action type \'{actionType}\'.'
          ' This action \'{actionId}\' is still processed.'.format(actionType=action['type'].value, actionId=actionId))
      action['ratios'] = action['ratios'][0:2]

    match action['type']:
      case ActionType.FIND_IMAGE:
        if 'imageToFind' in data and self.isImageToFindDataValid(data['imageToFind']):
          action['imageToFind'] = data['imageToFind']
        else:
          logger.warning(f'Invalid imageToFind value. This action \'{actionId}\' is ignored.')
          return
        if 'threshold' in data and self.isThresholdDataValid(data['threshold']):
          action['threshold'] = data['threshold']
        else:
          logger.warning(f'Invalid threshold value. This action \'{actionId}\' is ignored.')
          return
        if 'maxResults' in data and self.isMaxResultsDataValid(data['maxResults']):
          action['maxResults'] = data['maxResults']
        else:
          logger.warning(f'Invalid maxResults value. This action \'{actionId}\' is ignored.')
          return
        action['resizeInterval'] = None
        if 'resizeInterval' in data:
          if self.isResizeIntervalDataValid(data['resizeInterval']):
            action['resizeInterval'] = tuple(data['resizeInterval'])
          else:
            logger.warning(f'Invalid min and max size ratios. This action \'{actionId}\' is ignored.')
            return
        else:
          action['resizeInterval'] = None
        if not self.isImageToFindCompatibleWithSelection(action['imageToFind'], self.borders, action['ratios'],
              action['resizeInterval']):
          # TODO: Is this relevant? Only the version with max size ration is going to be used (and max size ratio could be < 1)
          if self.isImageToFindCompatibleWithSelection(action['imageToFind'], self.borders, action['ratios']):
            logger.warning('The size of the image to find is too big for the selected area considering the max size ratio.'
                f' This action \'{actionId}\' is ignored.')
          else:
            logger.warning(f'The size of the image to find is too big for the selected area. This action \'{actionId}\' is ignored.')
          return
      case ActionType.COMPARE_PIXEL_COLOR | ActionType.IS_SAME_PIXEL_COLOR:
        if 'pixelColor' in data and self.isPixelColorDataValid(data['pixelColor']):
          action['pixelColor'] = tuple(data['pixelColor'])
        else:
          logger.warning(f'Invalid pixel color value. This action \'{actionId}\' is ignored.')
          return
      case ActionType.COMPARE_IMAGE_HASH | ActionType.IS_SAME_IMAGE_HASH:
        if 'imageHash' in data and self.isImageHashDataValid(data['imageHash']):
          action['imageHash'] = data['imageHash']
        else:
          logger.warning(f'Invalid image hash value. This action \'{actionId}\' is ignored.')
          return

    self.actionById[action['id']] = action

  def getBordersImage(self) -> Image.Image:
    """
    :raise RecognizerValueError: no borders data
    """
    if self.borders is None:
      raise RecognizerValueError('No borders data.')
    return self.getArea(self.borders)

  def execute(self, *args: str | ActionType, **kwargs: Image.Image | tuple[int, ...] | list[int] | str | int | float | ActionType) -> AnyActionReturnType:
    r"""
    Return the result of the given action(s).

    When many action ids or action types are specified, actions are executed as a pipeline.

    :param \*args: actions ids or types: At least one must be given.
    :type \*args: :obj:`str`
    :param \**kwargs: (optional) see below

    If none of the parameters **screenshot**, **screenshotFilepath**, **bordersImage** and **bordersImageFilepath** is given,
    the screen is used when necessary.

    With option **reinterpret**, the last action, if given by an id, is executed as if it was from the given type.
    An exception is raised if some parameters are missing.

    The selected area can be preprocessed using the id of a defined preprocessing operation with option **preprocessing**.

    :Keyword Arguments:
      * **screenshot** (:obj:`PIL.Image.Image`) -- (optional)
      * **screenshotFilepath** (:obj:`str`) -- (optional) filepath of the screenshot
      * **bordersImage** (:obj:`PIL.Image.Image`) -- (optional)
      * **bordersImageFilepath** (:obj:`str`) -- (optional) filepath of the bordersImage
      * **coord** (:obj:`Union`\ [:obj:`tuple`\ [:obj:`int`], :obj:`list`\ [:obj:`int`]]) -- (optional) absolute coordinates
      * **selectedPoint** (:obj:`Union`\ [:obj:`tuple`\ [:obj:`int`], :obj:`list`\ [:obj:`int`], :obj:`int`]) -- (optional)
        rgb colors with or without alpha or gray value
      * **selectedArea** (:obj:`PIL.Image.Image`) -- (optional)
      * **selectedAreaFilepath** (:obj:`str`) -- (optional) filepath of the selected area image
      * **clickPauseDuration** (:obj:`float`) -- (optional) pause duration of the click in second - default: 0.02s
      * **nbClicks** (:obj:`int`) -- (optional) number of clicks - default: 1
      * **pixelColor** (:obj:`Union`\ [:obj:`tuple`\ [:obj:`int`], :obj:`list`\ [:obj:`int`]]) -- (optional) rgb colors
      * **pixelColorReference** (:obj:`Union`\ [:obj:`tuple`\ [:obj:`int`], :obj:`list`\ [:obj:`int`]]) -- (optional) rgb colors
      * **pixelColorDifference** (:obj:`float`) -- (optional)
      * **imageHash** (:obj:`str`) -- (optional)
      * **imageHashReference** (:obj:`str`) -- (optional)
      * **imageHashDifference** (:obj:`int`) -- (optional)
      * **reinterpret** (:obj:`ActionType`) -- (optional)
      * **preprocessing** (:obj:`str`) -- (optional) id of a preprocessing operation
    :return: last action output

    :raise RecognizerValueError:
      * no action id or type is specified
      * an action id is unknown
      * could not open image from the borders filepath
      * could not open image from the selected area filepath
      * one of the parameters is invalid
      * a needed parameter is missing while using an action type
    """
    actionIdOrTypes = []
    for actionIdOrType in args:
      if not isinstance(actionIdOrType, (str, ActionType)):
        raise RecognizerValueError(f'Expected an action id or an action type instead of \'{actionIdOrType}\'')
      if isinstance(actionIdOrType, str) and  actionIdOrType not in self.actionById:
        raise RecognizerValueError(f'Id \'{actionIdOrType}\' is not in the list of available actions.'
            ' Maybe it\'s a typo or the action was ignored during the data loading because of an import issue.'
            ' You can check the logs for warnings about import issues.')
      actionIdOrTypes.append(actionIdOrType)
    if 'preprocessing' in kwargs:
      try:
        self.preprocessing.checkProcessInput(kwargs['preprocessing'])
      except RecognizerValueError as e:
        raise RecognizerValueError(f'Invalid parameter preprocessing. {str(e)}')
    if len(actionIdOrTypes) == 0:
      raise RecognizerValueError('At least one action id must be specified.')
    if 'reinterpret' in kwargs and not isinstance(kwargs['reinterpret'], ActionType):
      raise RecognizerValueError('Invalid parameter reinterpret: expects an action type.')

    if 'screenshotFilepath' in kwargs:
      if 'screenshot' in kwargs:
        raise RecognizerValueError('Cannot specify both parameters screenshot and screenshotFilepath.')
      try:
        kwargs['screenshot'] = Image.open(kwargs['screenshotFilepath'])
        kwargs.pop('screenshotFilepath')
      except:
        raise RecognizerValueError('Could not open screenshot filepath \'{filepath}\''
            .format(filepath=kwargs['screenshotFilepath']))
    if 'bordersImageFilepath' in kwargs:
      if 'bordersImage' in kwargs:
        raise RecognizerValueError('Cannot specify both parameters bordersImage and bordersImageFilepath.')
      try:
        kwargs['bordersImage'] = Image.open(kwargs['bordersImageFilepath'])
        kwargs.pop('bordersImageFilepath')
      except:
        raise RecognizerValueError('Could not open borders image filepath \'{filepath}\''
            .format(filepath=kwargs['bordersImageFilepath']))
    if 'screenshot' in kwargs and 'bordersImage' in kwargs:
      raise RecognizerValueError('Cannot specify both a screenshot and a borders image.')
    if 'selectedAreaFilepath' in kwargs:
      if 'selectedArea' in kwargs:
        raise RecognizerValueError('Cannot specify both parameters selectedArea and selectedAreaFilepath.')
      try:
        kwargs['selectedArea'] = Image.open(kwargs['selectedAreaFilepath'])
        kwargs.pop('selectedAreaFilepath')
      except:
        raise RecognizerValueError('Could not open selected area filepath \'{filepath}\''
            .format(filepath=kwargs['selectedAreaFilepath']))
    return self._pipeExecute(actionIdOrTypes, kwargs)

  def _pipeExecute(self, actionIdOrTypes: list[str | ActionType], pipeInfo: dict) -> Any:
    """
    :param actionIdOrTypes: assume len(actionIdOrTypes) > 0
    :param pipeInfo:
    """
    actionIdOrType = actionIdOrTypes.pop(0)
    if isinstance(actionIdOrType, str):
      action = self.actionById[actionIdOrType]
      actionType = action['type']
      if len(actionIdOrTypes) == 0 and 'reinterpret' in pipeInfo:
        actionType = pipeInfo['reinterpret']
    else:
      action = None
      actionType = actionIdOrType
    match actionType:
      case ActionType.COORDINATES:
        return self._pipeExecuteActionCoordinates(action, actionIdOrTypes, pipeInfo)
      case ActionType.SELECTION:
        return self._pipeExecuteActionSelection(action, actionIdOrTypes, pipeInfo)
      case ActionType.FIND_IMAGE:
        return self._pipeExecuteActionFindImage(action, actionIdOrTypes, pipeInfo)
      case ActionType.CLICK:
        return self._pipeExecuteActionClick(action, actionIdOrTypes, pipeInfo)
      case ActionType.PIXEL_COLOR:
        return self._pipeExecuteActionPixelColor(action, actionIdOrTypes, pipeInfo)
      case ActionType.COMPARE_PIXEL_COLOR:
        return self._pipeExecuteActionComparePixelColor(action, actionIdOrTypes, pipeInfo)
      case ActionType.IS_SAME_PIXEL_COLOR:
        return self._pipeExecuteActionIsSamePixelColor(action, actionIdOrTypes, pipeInfo)
      case ActionType.IMAGE_HASH:
        return self._pipeExecuteActionImageHash(action, actionIdOrTypes, pipeInfo)
      case ActionType.COMPARE_IMAGE_HASH:
        return self._pipeExecuteActionCompareImageHash(action, actionIdOrTypes, pipeInfo)
      case ActionType.IS_SAME_IMAGE_HASH:
        return self._pipeExecuteActionIsSameImageHash(action, actionIdOrTypes, pipeInfo)
      case ActionType.TEXT:
        return self._pipeExecuteActionText(action, actionIdOrTypes, pipeInfo)
      case ActionType.NUMBER:
        return self._pipeExecuteActionNumber(action, actionIdOrTypes, pipeInfo)

  def _pipeExecuteActionCoordinates(self, action: dict | None,
      actionIdOrTypes: list[str | ActionType], pipeInfo: dict) -> AnyActionReturnType:
    """
    :param action:
    :param actionIdOrTypes:
    :param pipeInfo:
    """
    if 'coord' in pipeInfo:
      if not self.isCoordDataValid(pipeInfo['coord']):
        raise RecognizerValueError('Invalid coord value: \'{coord}\'.'.format(coord=pipeInfo['coord']))
      else:
        if len(actionIdOrTypes) == 0:
          return pipeInfo['coord']
        else:
          return self._pipeExecute(actionIdOrTypes, pipeInfo)
    if action is None:
      raise RecognizerValueError('With given action types, option coord is required.')
    pipeInfo['coord'] = self.getCoord(self.borders, action['ratios'])
    return self._pipeExecuteActionCoordinates(action, actionIdOrTypes, pipeInfo)

  def _pipeExecuteActionSelection(self, action: dict | None,
      actionIdOrTypes: list[str | ActionType], pipeInfo: dict) -> AnyActionReturnType:
    """
    :param action:
    :param actionIdOrTypes:
    :param pipeInfo:
    """
    if action is None and ('selectedPoint' in pipeInfo or 'selectedArea' in pipeInfo):
      if 'selectedPoint' in pipeInfo:
        selectionType = SelectionType.POINT
      else:
        selectionType = SelectionType.AREA
    else:
      self._pipeExecuteActionCoordinates(action, [], pipeInfo)
      selectionType = SelectionType.fromSelection(pipeInfo['coord'])
    if selectionType == SelectionType.POINT:
      if 'selectedPoint' in pipeInfo:
        if not self.isPointDataValid(pipeInfo['selectedPoint']):
          raise RecognizerValueError('Invalid point value: \'{point}\'.'.format(point=pipeInfo['selectedPoint']))
        else:
          if len(actionIdOrTypes) == 0:
            return pipeInfo['selectedPoint']
          else:
            return self._pipeExecute(actionIdOrTypes, pipeInfo)
      if 'screenshot' in pipeInfo:
        if not self.isImageDataValid(pipeInfo['screenshot']):
          raise RecognizerValueError('Invalid screenshot value.')
        else:
          pipeInfo['selectedPoint'] = self.getPointFromScreenshot(pipeInfo['screenshot'], pipeInfo['coord'])
          return self._pipeExecuteActionSelection(action, actionIdOrTypes, pipeInfo)
      if 'bordersImage' in pipeInfo:
        if not self.isImageDataValid(pipeInfo['bordersImage']):
          raise RecognizerValueError('Invalid bordersImage value.')
        else:
          pipeInfo['selectedPoint'] = self.getPointFromBordersImage(pipeInfo['bordersImage'], pipeInfo['coord'], self.borders)
          return self._pipeExecuteActionSelection(action, actionIdOrTypes, pipeInfo)
      pipeInfo['selectedPoint'] = self.getPoint(pipeInfo['coord'])
      return self._pipeExecuteActionSelection(action, actionIdOrTypes, pipeInfo)
    else:
      if 'selectedArea' in pipeInfo:
        if not self.isAreaDataValid(pipeInfo['selectedArea']):
          raise RecognizerValueError('Invalid area value.')
        else:
          if 'preprocessing' in pipeInfo:
            pipeInfo['selectedArea'] = self.preprocessing.process(pipeInfo['selectedArea'], pipeInfo['preprocessing'])
          if len(actionIdOrTypes) == 0:
            return pipeInfo['selectedArea']
          else:
            return self._pipeExecute(actionIdOrTypes, pipeInfo)
      if 'screenshot' in pipeInfo:
        if not self.isImageDataValid(pipeInfo['screenshot']):
          raise RecognizerValueError('Invalid screenshot value.')
        else:
          pipeInfo['selectedArea'] = self.getAreaFromScreenshot(pipeInfo['screenshot'], pipeInfo['coord'])
          return self._pipeExecuteActionSelection(action, actionIdOrTypes, pipeInfo)
      if 'bordersImage' in pipeInfo:
        if not self.isImageDataValid(pipeInfo['bordersImage']):
          raise RecognizerValueError('Invalid bordersImage value.')
        else:
          pipeInfo['selectedArea'] = self.getAreaFromBordersImage(pipeInfo['bordersImage'], pipeInfo['coord'], self.borders)
          return self._pipeExecuteActionSelection(action, actionIdOrTypes, pipeInfo)
      pipeInfo['selectedArea'] = self.getArea(pipeInfo['coord'])
      return self._pipeExecuteActionSelection(action, actionIdOrTypes, pipeInfo)

  def _pipeExecuteActionFindImage(self, action: dict | None,
      actionIdOrTypes: list[str | ActionType], pipeInfo: dict) -> AnyActionReturnType:
    """
    :param action:
    :param actionIdOrTypes:
    :param pipeInfo:
    """
    self._pipeExecuteActionSelection(action, [], pipeInfo)
    if len(actionIdOrTypes) == 0:
      if action is None:
        raise RecognizerValueError('ActionType.FIND_IMAGE cannot be used by itself even with some options.'
            ' To load an action of this type, add it with its parameters in a config file or load it directly with loadData.')
      if any([paramName not in action for paramName in ['imageToFind', 'threshold', 'maxResults', 'resizeInterval']]):
        raise RecognizerValueError('Cannot reinterpret as ActionType.FIND_IMAGE.'
            ' To load an action of this type, add it with its parameters in a config file or load it directly with loadData.')
      self._checkSelectedAreaAndNotJustSelectedPoint(pipeInfo)
      if not self.isImageToFindCompatibleWithAreaSize(action['imageToFind'], pipeInfo['selectedArea'].size, action['resizeInterval']):
        if self.isImageToFindCompatibleWithAreaSize(action['imageToFind'], pipeInfo['selectedArea'].size):
          raise RecognizerValueError('Incompatible area value with image to find.'
              ' The image to find must be smaller than the area also considering the max size ratio.')
        else:
          raise RecognizerValueError('Incompatible area value with image to find. The image to find must be smaller than the area.')
      return self.findImageCoordinates(pipeInfo['coord'], pipeInfo['selectedArea'], action['imageToFind'], action['threshold'],
          action['maxResults'], action['resizeInterval'])
    else:
      return self._pipeExecute(actionIdOrTypes, pipeInfo)

  def _checkSelectedAreaAndNotJustSelectedPoint(self, pipeInfo):
    """
    :param pipeInfo:
    """
    if 'selectedArea' not in pipeInfo:
      raise RecognizerValueError('Expected an area selection instead of a point.')

  def _pipeExecuteActionClick(self, action: dict | None,
      actionIdOrTypes: list[str | ActionType], pipeInfo: dict) -> AnyActionReturnType:
    """
    :param action:
    :param actionIdOrTypes:
    :param pipeInfo:
    """
    self._pipeExecuteActionCoordinates(action, [], pipeInfo)
    options = {}
    if 'clickPauseDuration' in pipeInfo:
      if not isinstance(pipeInfo['clickPauseDuration'], float):
        raise RecognizerValueError('Invalid clickPauseDuration value: \'{duration}\'.'
            .format(duration=pipeInfo['clickPauseDuration']))
      options['pauseDuration'] = pipeInfo['clickPauseDuration']
    if 'nbClicks' in pipeInfo:
      if not isinstance(pipeInfo['nbClicks'], int):
        raise RecognizerValueError('Invalid nbClicks value: \'{nbClicks}\'.'
            .format(nbClicks=pipeInfo['nbClicks']))
      options['nbClicks'] = pipeInfo['nbClicks']
    if len(actionIdOrTypes) == 0:
      MouseManager.clickOnPosition(pipeInfo['coord'], **options)
      return None
    else:
      return self._pipeExecute(actionIdOrTypes, pipeInfo)

  def _pipeExecuteActionPixelColor(self, action: dict | None,
      actionIdOrTypes: list[str | ActionType], pipeInfo: dict) -> AnyActionReturnType:
    """
    :param action:
    :param actionIdOrTypes:
    :param pipeInfo:
    """
    if 'pixelColor' in pipeInfo:
      if not self.isPixelColorDataValid(pipeInfo['pixelColor']):
        raise RecognizerValueError('Invalid pixel color value: \'{pixelColor}\'.'.format(pixelColor=pipeInfo['pixelColor']))
      else:
        if len(actionIdOrTypes) == 0:
          return pipeInfo['pixelColor']
        else:
          return self._pipeExecute(actionIdOrTypes, pipeInfo)
    self._pipeExecuteActionSelection(action, [], pipeInfo)
    if 'selectedPoint' in pipeInfo and 'selectedArea' in pipeInfo and action is not None:
      selectionType = SelectionType.fromSelection(action['ratios'])
    elif 'selectedPoint' in pipeInfo:
      selectionType = SelectionType.POINT
    else:
      selectionType = SelectionType.AREA
    if selectionType == SelectionType.POINT:
      pipeInfo['pixelColor'] = self.getPixelColor(pipeInfo['selectedPoint'])
    else:
      pipeInfo['pixelColor'] = self.getAveragePixelColor(pipeInfo['selectedArea'])
    return self._pipeExecuteActionPixelColor(action, actionIdOrTypes, pipeInfo)

  def _pipeExecuteActionComparePixelColor(self, action: dict | None,
      actionIdOrTypes: list[str | ActionType], pipeInfo: dict) -> AnyActionReturnType:
    """
    :param action:
    :param actionIdOrTypes:
    :param pipeInfo:
    """
    if 'pixelColorDifference' in pipeInfo:
      if not self.isPixelColorDifferenceDataValid(pipeInfo['pixelColorDifference']):
        raise RecognizerValueError('Invalid pixel color difference value: \'{difference}\'.'
            .format(difference=pipeInfo['pixelColorDifference']))
      else:
        if len(actionIdOrTypes) == 0:
          return pipeInfo['pixelColorDifference']
        else:
          return self._pipeExecute(actionIdOrTypes, pipeInfo)
    self._pipeExecuteActionPixelColor(action, [], pipeInfo)

    if 'pixelColorReference' not in pipeInfo and action is not None and 'pixelColor' in action:
      pipeInfo['pixelColorReference'] = action['pixelColor']
    if 'pixelColorReference' not in pipeInfo:
      raise RecognizerValueError('With given action types, option pixelColorReference is required.')
    if not self.isPixelColorDataValid(pipeInfo['pixelColorReference']):
      raise RecognizerValueError('Invalid pixel color reference value: \'{pixelColor}\'.'.format(pixelColor=pipeInfo['pixelColorReference']))
    pipeInfo['pixelColorDifference'] = self.getPixelColorDifference(pipeInfo['pixelColor'], pipeInfo['pixelColorReference'])
    return self._pipeExecuteActionComparePixelColor(action, actionIdOrTypes, pipeInfo)

  def _pipeExecuteActionIsSamePixelColor(self, action: dict | None,
      actionIdOrTypes: list[str | ActionType], pipeInfo: dict) -> AnyActionReturnType:
    """
    :param action:
    :param actionIdOrTypes:
    :param pipeInfo:
    """
    self._pipeExecuteActionComparePixelColor(action, [], pipeInfo)
    if len(actionIdOrTypes) == 0:
      return pipeInfo['pixelColorDifference'] == 0
    else:
      return self._pipeExecute(actionIdOrTypes, pipeInfo)

  def _pipeExecuteActionImageHash(self, action: dict | None,
      actionIdOrTypes: list[str | ActionType], pipeInfo: dict) -> AnyActionReturnType:
    """
    :param action:
    :param actionIdOrTypes:
    :param pipeInfo:
    """
    if 'imageHash' in pipeInfo:
      if not self.isImageHashDataValid(pipeInfo['imageHash']):
        raise RecognizerValueError('Invalid image hash value: \'{imageHash}\'.'.format(imageHash=pipeInfo['imageHash']))
      else:
        if len(actionIdOrTypes) == 0:
          return pipeInfo['imageHash']
        else:
          return self._pipeExecute(actionIdOrTypes, pipeInfo)
    self._pipeExecuteActionSelection(action, [], pipeInfo)
    self._checkSelectedAreaAndNotJustSelectedPoint(pipeInfo)
    pipeInfo['imageHash'] = self.getImageHash(pipeInfo['selectedArea'])
    return self._pipeExecuteActionImageHash(action, actionIdOrTypes, pipeInfo)

  def _pipeExecuteActionCompareImageHash(self, action: dict | None,
      actionIdOrTypes: list[str | ActionType], pipeInfo: dict) -> AnyActionReturnType:
    """
    :param action:
    :param actionIdOrTypes:
    :param pipeInfo:
    """
    if 'imageHashDifference' in pipeInfo:
      if not self.isImageHashDifferenceDataValid(pipeInfo['imageHashDifference']):
        raise RecognizerValueError('Invalid image hash difference value: \'{difference}\'.'
            .format(difference=pipeInfo['imageHashDifference']))
      else:
        if len(actionIdOrTypes) == 0:
          return pipeInfo['imageHashDifference']
        else:
          return self._pipeExecute(actionIdOrTypes, pipeInfo)
    self._pipeExecuteActionImageHash(action, [], pipeInfo)

    if 'imageHashReference' not in pipeInfo and action is not None and 'imageHash' in action:
      pipeInfo['imageHashReference'] = action['imageHash']
    if 'imageHashReference' not in pipeInfo:
      raise RecognizerValueError('With given action types, option imageHashReference is required.')
    if not self.isImageHashDataValid(pipeInfo['imageHashReference']):
      raise RecognizerValueError('Invalid image hash reference value: \'{imageHash}\'.'.format(imageHash=pipeInfo['imageHashReference']))
    pipeInfo['imageHashDifference'] = self.getImageHashDifference(pipeInfo['imageHash'], pipeInfo['imageHashReference'])
    return self._pipeExecuteActionCompareImageHash(action, actionIdOrTypes, pipeInfo)

  def _pipeExecuteActionIsSameImageHash(self, action: dict | None,
      actionIdOrTypes: list[str | ActionType], pipeInfo: dict) -> AnyActionReturnType:
    """
    :param action:
    :param actionIdOrTypes:
    :param pipeInfo:
    """
    self._pipeExecuteActionCompareImageHash(action, [], pipeInfo)
    if len(actionIdOrTypes) == 0:
      return pipeInfo['imageHashDifference'] == 0
    else:
      return self._pipeExecute(actionIdOrTypes, pipeInfo)

  def _pipeExecuteActionText(self, action: dict | None,
      actionIdOrTypes: list[str | ActionType], pipeInfo: dict) -> AnyActionReturnType:
    """
    :param action:
    :param actionIdOrTypes:
    :param pipeInfo:
    """
    self._pipeExecuteActionSelection(action, [], pipeInfo)
    if len(actionIdOrTypes) == 0:
      self._checkSelectedAreaAndNotJustSelectedPoint(pipeInfo)
      return self.getText(pipeInfo['selectedArea'])
    else:
      return self._pipeExecute(actionIdOrTypes, pipeInfo)

  def _pipeExecuteActionNumber(self, action: dict | None,
      actionIdOrTypes: list[str | ActionType], pipeInfo: dict) -> AnyActionReturnType:
    """
    :param action:
    :param actionIdOrTypes:
    :param pipeInfo:
    """
    self._pipeExecuteActionSelection(action, [], pipeInfo)
    if len(actionIdOrTypes) == 0:
      self._checkSelectedAreaAndNotJustSelectedPoint(pipeInfo)
      return self.getNumber(pipeInfo['selectedArea'])
    else:
      return self._pipeExecute(actionIdOrTypes, pipeInfo)
