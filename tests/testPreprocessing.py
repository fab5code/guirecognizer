import logging
import sys
import unittest
from PIL import Image, ImageOps

from guirecognizer import Preprocessing, PreprocessingType, RecognizerValueError, \
    GrayscalePreprocessor, ColorMapMethod, ColorMapPreprocessor, \
    ThresholdMethod, ThresholdPreprocessor, ThresholdType, ResizeMethod, ResizePreprocessor

class LoggedTestCase(unittest.TestCase):
  def setUp(self):
    logger = logging.getLogger('guirecognizer')
    logger.level = logging.DEBUG
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(fmt='%(levelname)s: %(message)s'))
    logger.addHandler(stream_handler)

class TestPreprocessing(LoggedTestCase):
  def test_error_invalidOperations(self):
    with self.assertRaises(RecognizerValueError):
      Preprocessing('invalid')
    with self.assertRaises(RecognizerValueError):
      Preprocessing({'operations': 'invalid'})
    with self.assertRaises(RecognizerValueError):
      Preprocessing({'operations': ['invalid']})

  def test_error_invalidSuboperations(self):
    with self.assertRaises(RecognizerValueError):
      Preprocessing({'operations': [{'id': 'operationId', 'suboperations': 'invalid'}]})
    with self.assertRaises(RecognizerValueError):
      Preprocessing({'operations': [{'id': 'operationId', 'suboperations': ['invalid']}]})

  def test_error_invalidSuboperationData(self):
    preprocessing = Preprocessing({'operations': [{'id': '',
        'suboperations': [{'type': PreprocessingType.COLOR_MAP.value}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': 'invalid', 'colorMap': {}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value,
        'colorMap': 'invalid'}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)

  def test_error_sameIds(self):
    preprocessing = Preprocessing({'operations': [
      {'id': 'operationId', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value, 'colorMap': {}}]},
      {'id': 'operationId', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value, 'colorMap': {}}]}
    ]})
    self.assertEqual(len(preprocessing.operationById), 1)

  def test_error_invalidProcessInput(self):
    preprocessing = Preprocessing({'operations': [
        {'id': 'operationId', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value, 'colorMap': {}}]}]})
    image = Image.open('tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      preprocessing.process('invalid', 'operationId')
    with self.assertRaises(RecognizerValueError):
      preprocessing.process(image, 1)
    with self.assertRaises(RecognizerValueError):
      preprocessing.process(image, 'unknownId')

  def test_noOperation(self):
    preprocessing = Preprocessing({'operations': []})
    self.assertEqual(len(preprocessing.operationById), 0)

  def test_oneOperation(self):
    preprocessing = Preprocessing({'operations': [
        {'id': 'operationId', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value, 'colorMap': {}}]}]})
    self.assertEqual(len(preprocessing.operationById), 1)

class TestGrayscale(LoggedTestCase):
  def test_error_invalidImage(self):
    preprocessor = GrayscalePreprocessor()
    with self.assertRaises(RecognizerValueError):
      preprocessor.process('invalid')

  def test_grayscale(self):
    image = Image.open('tests/data/img/img4.png')
    preprocessor = GrayscalePreprocessor()
    newImage = preprocessor.process(image)
    self.assertEqual(newImage.getpixel((3, 0)), 94)

  def test_preprocessing_grayscale(self):
    image = Image.open('tests/data/img/img4.png')
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.GRAYSCALE.value}]}]})
    newImage = preprocessing.process(image, 'operation1')
    self.assertEqual(newImage.getpixel((3, 0)), 94)

class TestColorMap(LoggedTestCase):
  def test_error_invalidImage(self):
    preprocessor = ColorMapPreprocessor()
    with self.assertRaises(RecognizerValueError):
      preprocessor.process('invalid')

  def test_error_invalidMethod(self):
    with self.assertRaises(RecognizerValueError):
      ColorMapPreprocessor(method='invalid')

  def test_error_invalidInputColor1(self):
    with self.assertRaises(RecognizerValueError):
      ColorMapPreprocessor(inputColor1='invalid')

  def test_error_invalidOutputColor1(self):
    with self.assertRaises(RecognizerValueError):
      ColorMapPreprocessor(outputColor1='invalid')

  def test_error_invalidDifference(self):
    with self.assertRaises(RecognizerValueError):
      ColorMapPreprocessor(outputColor1='invalid')

  def test_error_invalidInputColor2(self):
    with self.assertRaises(RecognizerValueError):
      ColorMapPreprocessor(method=ColorMapMethod.RANGE_TO_ONE, inputColor2='invalid')

  def test_error_invalidOutputColor2(self):
    with self.assertRaises(RecognizerValueError):
      ColorMapPreprocessor(method=ColorMapMethod.RANGE_TO_RANGE, outputColor2='invalid')

  def test_oneToOne(self):
    image = Image.open('tests/data/img/img1.png')
    color = image.getpixel((5, 5))[:3]
    outputColor = (255, 0, 0)
    preprocessor = ColorMapPreprocessor(method=ColorMapMethod.ONE_TO_ONE, inputColor1=color,
        difference=0, outputColor1=outputColor)
    newImage = preprocessor.process(image)
    newColor = newImage.getpixel((5, 5))
    self.assertEqual(newColor, outputColor)

  def test_oneToOne_grayImage(self):
    image = ImageOps.grayscale(Image.open('tests/data/img/img1.png'))
    color = image.getpixel((5, 5))
    inputColor = (color, color, color)
    outputColor = (255, 0, 0)
    preprocessor = ColorMapPreprocessor(method=ColorMapMethod.ONE_TO_ONE, inputColor1=inputColor,
        difference=0, outputColor1=outputColor)
    newImage = preprocessor.process(image)
    newColor = newImage.getpixel((5, 5))
    self.assertEqual(newColor, outputColor)

  def test_rangeToOne_sameInputColors(self):
    image = Image.open('tests/data/img/img1.png')
    color = image.getpixel((6, 6))[:3]
    outputColor = (255, 0, 0)
    preprocessor = ColorMapPreprocessor(method=ColorMapMethod.RANGE_TO_ONE, inputColor1=color, inputColor2=color,
        difference=0, outputColor1=outputColor)
    newImage = preprocessor.process(image)
    newColor = newImage.getpixel((6, 6))
    self.assertEqual(newColor, outputColor)

  def test_rangeToOne(self):
    image = Image.open('tests/data/img/img4.png')
    inputColor1 = image.getpixel((1, 0))[:3]
    inputColor2 = image.getpixel((3, 0))[:3]
    outputColor = (255, 0, 0)
    preprocessor = ColorMapPreprocessor(method=ColorMapMethod.RANGE_TO_ONE, inputColor1=inputColor1, inputColor2=inputColor2,
        difference=0.05, outputColor1=outputColor)
    newImage = preprocessor.process(image)
    self.assertEqual(newImage.getpixel((0, 0)), image.getpixel((0, 0)))
    for i in range(1, 4):
      self.assertEqual(newImage.getpixel((i, 0)), outputColor)
    self.assertEqual(newImage.getpixel((4, 0)), image.getpixel((4, 0)))

  def test_rangeToRange_sameInputColors(self):
    image = Image.open('tests/data/img/img1.png')
    color = image.getpixel((6, 6))[:3]
    outputColor1 = (200, 0, 0)
    outputColor2 = (100, 0, 0)
    preprocessor = ColorMapPreprocessor(method=ColorMapMethod.RANGE_TO_RANGE, inputColor1=color, inputColor2=color,
        difference=0, outputColor1=outputColor1, outputColor2=outputColor2)
    newImage = preprocessor.process(image)
    newColor = newImage.getpixel((6, 6))
    self.assertEqual(newColor, outputColor1)

  def test_rangeToRange_sameOutputColors(self):
    image = Image.open('tests/data/img/img4.png')
    inputColor1 = image.getpixel((1, 0))[:3]
    inputColor2 = image.getpixel((3, 0))[:3]
    outputColor = (255, 0, 0)
    preprocessor = ColorMapPreprocessor(method=ColorMapMethod.RANGE_TO_RANGE, inputColor1=inputColor1, inputColor2=inputColor2,
        difference=0.05, outputColor1=outputColor, outputColor2=outputColor)
    newImage = preprocessor.process(image)
    self.assertEqual(newImage.getpixel((0, 0)), image.getpixel((0, 0)))
    for i in range(1, 4):
      self.assertEqual(newImage.getpixel((i, 0)), outputColor)
    self.assertEqual(newImage.getpixel((4, 0)), image.getpixel((4, 0)))

  def test_rangeToRange(self):
    image = Image.open('tests/data/img/img4.png')
    inputColor1 = image.getpixel((1, 0))[:3]
    inputColor2 = image.getpixel((3, 0))[:3]
    outputColor1 = (200, 0, 0)
    outputColor2 = (100, 0, 0)
    preprocessor = ColorMapPreprocessor(method=ColorMapMethod.RANGE_TO_RANGE, inputColor1=inputColor1, inputColor2=inputColor2,
        difference=0.05, outputColor1=outputColor1, outputColor2=outputColor2)
    newImage = preprocessor.process(image)
    self.assertEqual(newImage.getpixel((0, 0)), image.getpixel((0, 0)))
    self.assertEqual(newImage.getpixel((1, 0)), outputColor1)
    self.assertEqual(newImage.getpixel((3, 0)), outputColor2)
    self.assertEqual(newImage.getpixel((4, 0)), image.getpixel((4, 0)))

  def test_preprocessing_error(self):
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value,
        'colorMap': {'method': 'invalid', 'inputColor1': [255, 255, 255], 'difference': 0.05, 'outputColor1': [0, 0, 0]}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value,
        'colorMap': {'method': ColorMapMethod.ONE_TO_ONE.value, 'inputColor1': 'invalid', 'difference': 0.05,
        'outputColor1': [0, 0, 0]}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value,
        'colorMap': {'method': ColorMapMethod.ONE_TO_ONE.value, 'inputColor1': [255, 255, 255], 'difference': 'invalid',
        'outputColor1': [0, 0, 0]}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value,
        'colorMap': {'method': ColorMapMethod.ONE_TO_ONE.value, 'inputColor1': [255, 255, 255], 'difference': 0.05,
        'outputColor1': 'invalid'}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value,
        'colorMap': {'method': ColorMapMethod.RANGE_TO_ONE.value, 'inputColor1': [255, 255, 255], 'inputColor2': 'invalid',
        'difference': 0.05, 'outputColor1': [0, 0, 0]}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value,
        'colorMap': {'method': ColorMapMethod.RANGE_TO_RANGE.value, 'inputColor1': [255, 255, 255], 'inputColor2': [255, 255, 255],
        'difference': 0.05, 'outputColor1': [0, 0, 0], 'outputColor1': 'invalid'}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)

  def test_preprocessing_oneToOne(self):
    image = Image.open('tests/data/img/img4.png')
    color = image.getpixel((3, 0))[:3]
    outputColor = (255, 0, 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value,
        'colorMap': {'method': ColorMapMethod.ONE_TO_ONE.value, 'inputColor1': color, 'difference': 0,
        'outputColor1': outputColor}}]}]})
    newImage = preprocessing.process(image, 'operation1')
    newColor = newImage.getpixel((3, 0))
    self.assertEqual(newColor, outputColor)

  def test_preprocessing_rangeToOne(self):
    image = Image.open('tests/data/img/img4.png')
    inputColor1 = image.getpixel((1, 0))[:3]
    inputColor2 = image.getpixel((3, 0))[:3]
    outputColor = (255, 0, 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value,
        'colorMap': {'method': ColorMapMethod.RANGE_TO_ONE.value, 'inputColor1': inputColor1, 'inputColor2': inputColor2,
        'difference': 0.05, 'outputColor1': outputColor}}]}]})
    newImage = preprocessing.process(image, 'operation1')
    self.assertEqual(newImage.getpixel((0, 0)), image.getpixel((0, 0)))
    for i in range(1, 4):
      self.assertEqual(newImage.getpixel((i, 0)), outputColor)
    self.assertEqual(newImage.getpixel((4, 0)), image.getpixel((4, 0)))

  def test_preprocessing_rangeToRange(self):
    image = Image.open('tests/data/img/img4.png')
    inputColor1 = image.getpixel((1, 0))[:3]
    inputColor2 = image.getpixel((3, 0))[:3]
    outputColor1 = (200, 0, 0)
    outputColor2 = (100, 0, 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.COLOR_MAP.value,
        'colorMap': {'method': ColorMapMethod.RANGE_TO_RANGE.value, 'inputColor1': inputColor1, 'inputColor2': inputColor2,
        'difference': 0.05, 'outputColor1': outputColor1, 'outputColor2': outputColor2}}]}]})
    newImage = preprocessing.process(image, 'operation1')
    self.assertEqual(newImage.getpixel((0, 0)), image.getpixel((0, 0)))
    self.assertEqual(newImage.getpixel((1, 0)), outputColor1)
    self.assertEqual(newImage.getpixel((3, 0)), outputColor2)
    self.assertEqual(newImage.getpixel((4, 0)), image.getpixel((4, 0)))

class TestThreshold(LoggedTestCase):
  def test_error_invalidImage(self):
    preprocessor = ThresholdPreprocessor()
    with self.assertRaises(RecognizerValueError):
      preprocessor.process('invalid')

  def test_error_invalidMethod(self):
    with self.assertRaises(RecognizerValueError):
      ThresholdPreprocessor(method='invalid')

  def test_error_invalidThresholdType(self):
    with self.assertRaises(RecognizerValueError):
      ThresholdPreprocessor(thresholdType='invalid')

  def test_error_incompatibleThresholdTypeAndMethod(self):
    with self.assertRaises(RecognizerValueError):
      ThresholdPreprocessor(method=ThresholdMethod.ADAPTIVE_GAUSSIAN, thresholdType=ThresholdType.TRUNCATE)
    with self.assertRaises(RecognizerValueError):
      ThresholdPreprocessor(method=ThresholdMethod.ADAPTIVE_GAUSSIAN, thresholdType=ThresholdType.TO_ZERO)
    with self.assertRaises(RecognizerValueError):
      ThresholdPreprocessor(method=ThresholdMethod.ADAPTIVE_GAUSSIAN, thresholdType=ThresholdType.TO_ZERO_INVERSE)
    with self.assertRaises(RecognizerValueError):
      ThresholdPreprocessor(method=ThresholdMethod.ADAPTIVE_MEAN, thresholdType=ThresholdType.TRUNCATE)
    with self.assertRaises(RecognizerValueError):
      ThresholdPreprocessor(method=ThresholdMethod.ADAPTIVE_MEAN, thresholdType=ThresholdType.TO_ZERO)
    with self.assertRaises(RecognizerValueError):
      ThresholdPreprocessor(method=ThresholdMethod.ADAPTIVE_MEAN, thresholdType=ThresholdType.TO_ZERO_INVERSE)

  def test_error_invalidMaxValue(self):
    with self.assertRaises(RecognizerValueError):
      ThresholdPreprocessor(maxValue='invalid')

  def test_error_invalidThreshold(self):
    with self.assertRaises(RecognizerValueError):
      ThresholdPreprocessor(threshold='invalid')

  def test_error_invalidBlockSize(self):
    with self.assertRaises(RecognizerValueError):
      ThresholdPreprocessor(method=ThresholdMethod.ADAPTIVE_MEAN, thresholdType=ThresholdType.BINARY, blockSize='invalid')

  def test_error_invalidCConstant(self):
    with self.assertRaises(RecognizerValueError):
      ThresholdPreprocessor(method=ThresholdMethod.ADAPTIVE_MEAN, thresholdType=ThresholdType.BINARY, cConstant='invalid')

  def test_simple(self):
    image = Image.open('tests/data/img/img1.png')
    maxValue = 200
    preprocessor = ThresholdPreprocessor(method=ThresholdMethod.SIMPLE, thresholdType=ThresholdType.BINARY,
        maxValue=maxValue, threshold=100)
    newImage = preprocessor.process(image)
    self.assertEqual(newImage.getpixel((5, 5)), maxValue)
    self.assertEqual(newImage.getpixel((6, 9)), 0)
    self.assertEqual(newImage.getpixel((6, 11)), 0)

    maxValue = 150
    preprocessor = ThresholdPreprocessor(method=ThresholdMethod.SIMPLE, thresholdType=ThresholdType.BINARY,
        maxValue=maxValue, threshold=30)
    newImage = preprocessor.process(image)
    self.assertEqual(newImage.getpixel((5, 5)), maxValue)
    self.assertEqual(newImage.getpixel((6, 9)), maxValue)
    self.assertEqual(newImage.getpixel((6, 11)), 0)

  def test_preprocessing_error(self):
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.THRESHOLD.value,
        'threshold': {'method': 'invalid', 'thresholdType': ThresholdType.BINARY.value}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.THRESHOLD.value,
        'threshold': {'method': ThresholdMethod.SIMPLE.value, 'thresholdType': 'invalid'}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.THRESHOLD.value,
        'threshold': {'method': ThresholdMethod.ADAPTIVE_MEAN.value, 'thresholdType': ThresholdType.TRUNCATE.value}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.THRESHOLD.value,
        'threshold': {'method': ThresholdMethod.SIMPLE.value, 'thresholdType': ThresholdType.BINARY.value,
        'maxValue': 'invalid'}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.THRESHOLD.value,
        'threshold': {'method': ThresholdMethod.SIMPLE.value, 'thresholdType': ThresholdType.BINARY.value,
        'threshold': 'invalid'}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.THRESHOLD.value,
        'threshold': {'method': ThresholdMethod.ADAPTIVE_MEAN.value, 'thresholdType': ThresholdType.BINARY.value,
        'blockSize': 'invalid'}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.THRESHOLD.value,
        'threshold': {'method': ThresholdMethod.ADAPTIVE_MEAN.value, 'thresholdType': ThresholdType.BINARY.value,
        'cConstant': 'invalid'}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)

class TestResize(LoggedTestCase):
  def test_error_invalidImage(self):
    preprocessor = ResizePreprocessor()
    with self.assertRaises(RecognizerValueError):
      preprocessor.process('invalid')

  def test_error_invalidWidth(self):
    with self.assertRaises(RecognizerValueError):
      ResizePreprocessor(width='invalid', method=ResizeMethod.UNFIXED_RATIO)
    with self.assertRaises(RecognizerValueError):
      ResizePreprocessor(width=0, method=ResizeMethod.UNFIXED_RATIO)
    with self.assertRaises(RecognizerValueError):
      ResizePreprocessor(width=30.1, method=ResizeMethod.UNFIXED_RATIO)
    with self.assertRaises(RecognizerValueError):
      ResizePreprocessor(width=40.0, method=ResizeMethod.UNFIXED_RATIO)

  def test_error_invalidHeight(self):
    with self.assertRaises(RecognizerValueError):
      ResizePreprocessor(height='invalid', method=ResizeMethod.UNFIXED_RATIO)
    with self.assertRaises(RecognizerValueError):
      ResizePreprocessor(height=0, method=ResizeMethod.UNFIXED_RATIO)
    with self.assertRaises(RecognizerValueError):
      ResizePreprocessor(height=30.1, method=ResizeMethod.UNFIXED_RATIO)
    with self.assertRaises(RecognizerValueError):
      ResizePreprocessor(height=40.0, method=ResizeMethod.UNFIXED_RATIO)

  def test_error_invalidMethod(self):
    with self.assertRaises(RecognizerValueError):
      ResizePreprocessor(method='invalid')

  def test_resize_unfixedRatio(self):
    image = Image.open('tests/data/img/img1.png')
    originalWidth, originalHeight = image.size
    width = round(originalWidth * 1.6)
    height = round(originalHeight * 1.3)
    preprocessor = ResizePreprocessor(width=width, height=height, method=ResizeMethod.UNFIXED_RATIO)
    newImage = preprocessor.process(image)
    newWidth, newHeight = newImage.size
    self.assertEqual(newWidth, width)
    self.assertEqual(newHeight, height)

  def test_resize_fixedRatioWidth(self):
    image = Image.open('tests/data/img/img1.png')
    originalWidth, originalHeight = image.size
    width = round(originalWidth * 1.8)
    height = round(originalHeight * 1.8)
    preprocessor = ResizePreprocessor(width=width, method=ResizeMethod.FIXED_RATIO_WIDTH)
    newImage = preprocessor.process(image)
    newWidth, newHeight = newImage.size
    self.assertEqual(newWidth, width)
    self.assertEqual(newHeight, height)

  def test_resize_fixedRatioHeight(self):
    image = Image.open('tests/data/img/img1.png')
    originalWidth, originalHeight = image.size
    width = round(originalWidth * 1.7)
    height = round(originalHeight * 1.7)
    preprocessor = ResizePreprocessor(height=height, method=ResizeMethod.FIXED_RATIO_HEIGHT)
    newImage = preprocessor.process(image)
    newWidth, newHeight = newImage.size
    self.assertEqual(newWidth, width)
    self.assertEqual(newHeight, height)

  def test_preprocessing_error(self):
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.RESIZE.value,
        'resize': {'width': 'invalid', 'height': 200, 'method': ResizeMethod.UNFIXED_RATIO.value}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.RESIZE.value,
        'resize': {'width': 200, 'height': 'invalid', 'method': ResizeMethod.UNFIXED_RATIO.value}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.RESIZE.value,
        'resize': {'width': 200, 'height': 200, 'method': 'invalid'}}]}]})
    self.assertEqual(len(preprocessing.operationById), 0)

  def test_preprocessing_resize_unfixedRatio(self):
    image = Image.open('tests/data/img/img1.png')
    originalWidth, originalHeight = image.size
    width = round(originalWidth * 1.6)
    height = round(originalHeight * 1.3)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.RESIZE.value,
        'resize': {'width': width, 'height': height, 'method': ResizeMethod.UNFIXED_RATIO.value}}]}]})
    newImage = preprocessing.process(image, 'operation1')
    newWidth, newHeight = newImage.size
    self.assertEqual(newWidth, width)
    self.assertEqual(newHeight, height)

  def test_preprocessing_resize_fixedRatioWidth(self):
    image = Image.open('tests/data/img/img1.png')
    originalWidth, originalHeight = image.size
    width = round(originalWidth * 1.8)
    height = round(originalHeight * 1.8)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.RESIZE.value,
        'resize': {'width': width, 'method': ResizeMethod.FIXED_RATIO_WIDTH.value}}]}]})
    newImage = preprocessing.process(image, 'operation1')
    newWidth, newHeight = newImage.size
    self.assertEqual(newWidth, width)
    self.assertEqual(newHeight, height)

  def test_preprocessing_resize_fixedRatioHeight(self):
    image = Image.open('tests/data/img/img1.png')
    originalWidth, originalHeight = image.size
    width = round(originalWidth * 1.7)
    height = round(originalHeight * 1.7)
    preprocessing = Preprocessing({'operations': [{'id': 'operation1', 'suboperations': [{'type': PreprocessingType.RESIZE.value,
        'resize': {'height': height, 'method': ResizeMethod.FIXED_RATIO_HEIGHT.value}}]}]})
    newImage = preprocessing.process(image, 'operation1')
    newWidth, newHeight = newImage.size
    self.assertEqual(newWidth, width)
    self.assertEqual(newHeight, height)

if __name__ == '__main__':
  unittest.main()
