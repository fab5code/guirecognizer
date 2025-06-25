import logging
import sys
import unittest
from PIL import Image, ImageOps

from guirecognizer import ActionType, OcrType, Recognizer, RecognizerValueError, SelectionType

class LoggedTestCase(unittest.TestCase):
  def setUp(self):
    logger = logging.getLogger('guirecognizer')
    logger.level = logging.DEBUG
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(fmt='%(levelname)s: %(message)s'))
    logger.addHandler(stream_handler)

class TestLoad(LoggedTestCase):
  def test_error_unexistentFile(self):
    with self.assertRaises(IOError):
      Recognizer('unexistent.json')

  def test_error_invalidJson(self):
    with self.assertRaises(RecognizerValueError):
      Recognizer('tests/data/json/invalid.json')

  def test_error_invalidData(self):
    with self.assertRaises(RecognizerValueError):
      Recognizer([])
    with self.assertRaises(RecognizerValueError):
      Recognizer(42)

  def test_error_loadData(self):
    recognizer = Recognizer()
    with self.assertRaises(RecognizerValueError):
      recognizer.loadData(42)

  def test_error_invalidBorder(self):
    with self.assertRaises(RecognizerValueError):
      Recognizer({'borders': (1, 20, 39, 10), 'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.CLICK.name}]})

  def test_error_noBorder(self):
    with self.assertRaises(RecognizerValueError):
      Recognizer({'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.CLICK.name}]})

  def test_error_noAction(self):
    with self.assertRaises(RecognizerValueError):
      Recognizer({'borders': (1, 1, 39, 39)})

  def test_error_invalidActionData(self):
    with self.assertRaises(RecognizerValueError):
      Recognizer({'borders': (1, 1, 39, 39), 'actions': [42]})

  def test_error_invalidId(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39), 'actions': [{'id': 42, 'ratios': (0, 0), 'type': ActionType.CLICK.name}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39), 'actions': [{'id': '', 'ratios': (0, 0), 'type': ActionType.CLICK.name}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.CLICK.name},
                    {'id': 'action1', 'ratios': (0, 0), 'type': ActionType.CLICK.name}]})
    self.assertEqual(len(recognizer.actionById), 1)

  def test_error_invalidRatios(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39), 'actions': [{'id': 'action1', 'ratios': 42, 'type': ActionType.CLICK.name}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, '0'), 'type': ActionType.CLICK.name}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.1), 'type': ActionType.CLICK.name}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.1, 0.1), 'type': ActionType.CLICK.name}]})
    self.assertEqual(len(recognizer.actionById), 1)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0.1, 0.3, 0.5, 0.2), 'type': ActionType.IMAGE_HASH.name}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0.1, 0.3), 'type': ActionType.IMAGE_HASH.name}]})
    self.assertEqual(len(recognizer.actionById), 0)

  def test_error_invalidActionType(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39), 'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': 'invalid'}]})
    self.assertEqual(len(recognizer.actionById), 0)

  def test_error_actionFindImage(self):
    # Missing parameter.
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name,
        'threshold': 10, 'maxResults': 5}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]]}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]]}]})
    self.assertEqual(len(recognizer.actionById), 0)

    # Wrong parameter imageToFind.
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': 'invalid'}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[]]}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [94, 94, 94, 255]}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[94, 94, 94, 255], [243, 243, 243]]}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]]}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.01, 0.01), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]]}]})
    self.assertEqual(len(recognizer.actionById), 0)

    # Wrong parameter threshold.
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 'invalid',
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]]}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold':-1,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]]}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10.0,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]]}]})
    self.assertEqual(len(recognizer.actionById), 0)

    # Wrong parameter maxResults.
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 'invalid', 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]]}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 0, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]]}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults':-1, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]]}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5.0, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]]}]})
    self.assertEqual(len(recognizer.actionById), 0)

    # Wrong parameter resizeInterval.
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]],
        'resizeInterval': None}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]],
        'resizeInterval': 'invalid'}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]],
        'resizeInterval': 1.1}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]],
        'resizeInterval': (1.1,)}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]],
        'resizeInterval': (1.1, 0.9)}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]],
        'resizeInterval': (0.9, 1.1, 1.3)}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.2, 0.2), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]],
        'resizeInterval': (1, 5)}]})
    self.assertEqual(len(recognizer.actionById), 0)

  def test_error_actionComparePixelColor(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.COMPARE_PIXEL_COLOR.name}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.COMPARE_PIXEL_COLOR.name, 'pixelColor': (1, 2)}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.COMPARE_PIXEL_COLOR.name, 'pixelColor': (1, 2, 256)}]})
    self.assertEqual(len(recognizer.actionById), 0)

  def test_error_actionCompareImageHash(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.COMPARE_IMAGE_HASH.name, 'imageHash': 42}]})
    self.assertEqual(len(recognizer.actionById), 0)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.1, 0.1), 'type': ActionType.COMPARE_IMAGE_HASH.name, 'imageHash': (0, 0)}]})
    self.assertEqual(len(recognizer.actionById), 0)

  def test_noData(self):
    recognizer = Recognizer()
    self.assertEqual(len(recognizer.actionById), 0)

  def test_zeroAction(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39), 'actions': []})
    self.assertEqual(len(recognizer.actionById), 0)

  def test_loadFile(self):
    recognizer = Recognizer('tests/data/json/config3.json')
    self.assertEqual(len(recognizer.actionById), 16)
    recognizer = Recognizer()
    recognizer.loadFilepath('tests/data/json/config3.json')
    self.assertEqual(len(recognizer.actionById), 16)

  def test_loadData(self):
    data1 = {'borders': (1, 1, 39, 39), 'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.SELECTION.name},
        {'id': 'action2', 'ratios': (0, 0), 'type': ActionType.SELECTION.name}]}
    data2 = {'borders': (1, 1, 39, 39), 'actions': [{'id': 'action3', 'ratios': (0, 0), 'type': ActionType.SELECTION.name},
        {'id': 'action4', 'ratios': (0, 0), 'type': ActionType.SELECTION.name},
        {'id': 'action5', 'ratios': (0, 0), 'type': ActionType.SELECTION.name}]}
    recognizer = Recognizer(data1)
    self.assertEqual(len(recognizer.actionById), 2)
    recognizer = Recognizer()
    recognizer.loadData(data1)
    self.assertEqual(len(recognizer.actionById), 2)
    recognizer.loadData(data2)
    self.assertEqual(len(recognizer.actionById), 5)

  def test_clearData(self):
    recognizer = Recognizer('tests/data/json/config3.json')
    self.assertEqual(len(recognizer.actionById), 16)
    recognizer.clearAllData()
    self.assertEqual(len(recognizer.actionById), 0)

  def test_loadFiles(self):
    recognizer = Recognizer()
    recognizer.loadFilepath('tests/data/json/config3.json')
    self.assertEqual(len(recognizer.actionById), 16)
    recognizer.loadFilepath('tests/data/json/config2.json')
    self.assertEqual(len(recognizer.actionById), 19)

  def test_actionCoordinates(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.COORDINATES.name}]})
    self.assertEqual(len(recognizer.actionById), 1)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.1, 0.1), 'type': ActionType.COORDINATES.name}]})
    self.assertEqual(len(recognizer.actionById), 1)

  def test_actionSelection(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.SELECTION.name}]})
    self.assertEqual(len(recognizer.actionById), 1)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.1, 0.1), 'type': ActionType.SELECTION.name}]})
    self.assertEqual(len(recognizer.actionById), 1)

  def test_actionFindImage(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]]}]})
    self.assertEqual(len(recognizer.actionById), 1)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94], [243, 243, 243]], [[69, 69, 69], [185, 185, 185]]]}]})
    self.assertEqual(len(recognizer.actionById), 1)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[94, 243], [69, 185]]}]})
    self.assertEqual(len(recognizer.actionById), 1)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]],
        'resizeInterval': (0.9, 1.1)}]})
    self.assertEqual(len(recognizer.actionById), 1)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]],
        'resizeInterval': (1, 3)}]})
    self.assertEqual(len(recognizer.actionById), 1)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.5, 0.5), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]],
        'resizeInterval': (2, 2)}]})
    self.assertEqual(len(recognizer.actionById), 1)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.06, 0.06), 'type': ActionType.FIND_IMAGE.name, 'threshold': 10,
        'maxResults': 5, 'imageToFind': [[[94, 94, 94, 255], [243, 243, 243, 255]], [[69, 69, 69, 255], [185, 185, 185, 255]]],
        'resizeInterval': (0.5, 0.5)}]})
    self.assertEqual(len(recognizer.actionById), 1)

  def test_actionClick(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.CLICK.name}]})
    self.assertEqual(len(recognizer.actionById), 1)
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.1, 0.1), 'type': ActionType.CLICK.name}]})
    self.assertEqual(len(recognizer.actionById), 1)

  def test_actionPixelColor(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.PIXEL_COLOR.name}]})
    self.assertEqual(len(recognizer.actionById), 1)

  def test_actionComparePixelColor(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.COMPARE_PIXEL_COLOR.name, 'pixelColor': (0, 255, 255)}]})
    self.assertEqual(len(recognizer.actionById), 1)

  def test_actionIsSamePixelColor(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0), 'type': ActionType.IS_SAME_PIXEL_COLOR.name, 'pixelColor': (0, 255, 255)}]})
    self.assertEqual(len(recognizer.actionById), 1)

  def test_actionImageHash(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.1, 0.1), 'type': ActionType.IMAGE_HASH.name}]})
    self.assertEqual(len(recognizer.actionById), 1)

  def test_actionCompareImageHash(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.1, 0.1), 'type': ActionType.COMPARE_IMAGE_HASH.name,
                     'imageHash': 'b88cf69dd66c8960,07000000000'}]})
    self.assertEqual(len(recognizer.actionById), 1)

  def test_actionIsSameImageHash(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.1, 0.1), 'type': ActionType.IS_SAME_IMAGE_HASH.name,
                     'imageHash': 'b88cf69dd66c8960,07000000000'}]})
    self.assertEqual(len(recognizer.actionById), 1)

  def test_actionText(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.1, 0.1), 'type': ActionType.TEXT.name}]})
    self.assertEqual(len(recognizer.actionById), 1)

  def test_actionNumber(self):
    recognizer = Recognizer({'borders': (1, 1, 39, 39),
        'actions': [{'id': 'action1', 'ratios': (0, 0, 0.1, 0.1), 'type': ActionType.NUMBER.name}]})
    self.assertEqual(len(recognizer.actionById), 1)

class TestRecognizer(LoggedTestCase):
  def test_error_getCoord(self):
    with self.assertRaises(RecognizerValueError):
      Recognizer.getCoord((0, 0, 39, 39), (1, 2, 3))

  def test_error_getBorders(self):
    recognizer = Recognizer()
    with self.assertRaises(RecognizerValueError):
      recognizer.getBordersImage()

  def test_error_ocrOrder(self):
    recognizer = Recognizer()
    with self.assertRaises(RecognizerValueError):
      recognizer.setOcrOrder('invalid')
    with self.assertRaises(RecognizerValueError):
      recognizer.setOcrOrder([])
    with self.assertRaises(RecognizerValueError):
      recognizer.setOcrOrder(['invalid'])
    with self.assertRaises(RecognizerValueError):
      recognizer.setOcrOrder([OcrType.EASY_OCR, OcrType.EASY_OCR])

  def test_getCoord(self):
    Recognizer.getCoord((0, 0, 39, 39), (0.2, 0.2, 0.2001, 0.2001))

  def test_ocrOrder(self):
    self.assertFalse(Recognizer.isOcrOrderDataValid('invalid'))
    self.assertFalse(Recognizer.isOcrOrderDataValid([None]))
    self.assertFalse(Recognizer.isOcrOrderDataValid(['invalid']))
    self.assertFalse(Recognizer.isOcrOrderDataValid([OcrType.EASY_OCR.value, OcrType.EASY_OCR.value]))
    self.assertTrue(Recognizer.isOcrOrderDataValid([]))
    self.assertTrue(Recognizer.isOcrOrderDataValid([OcrType.EASY_OCR.value]))

class TestSelectionType(LoggedTestCase):
  def test_error_selectionType(self):
    with self.assertRaises(ValueError):
      SelectionType.fromSelection((1, 2, 3))

  def test_selectionType(self):
    selectionType = SelectionType.POINT
    self.assertTrue(selectionType.isCompatibleWithSelectionType(SelectionType.AREA))
    self.assertTrue(selectionType.isCompatibleWithSelection((1, 1, 3, 3)))
    self.assertFalse(selectionType.isRightSelectionType(SelectionType.AREA))
    self.assertFalse(selectionType.isRightSelection((1, 1, 3, 3)))

class TestExecuteAction(LoggedTestCase):
  def setUp(self):
    super().setUp()
    self.recognizer = Recognizer('tests/data/json/config1.json')
    self.recognizer.setOcrOrder([OcrType.EASY_OCR])

  def test_error_actionIdOrType(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute(screenshotFilepath='tests/data/img/img1.png')

    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute(None, screenshotFilepath='tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute(42, screenshotFilepath='tests/data/img/img1.png')

    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('unkownId', screenshotFilepath='tests/data/img/img1.png')

  def test_error_optionScreenshot(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', screenshot='invalid')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', screenshot=42)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection2', screenshot='invalid')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection2', screenshot=42)

  def test_error_optionScreenshotFilepath(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', screenshotFilepath='tests/data/json/config1.json')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', screenshotFilepath='unexistent.png')

    self.recognizer.execute('coordinates1', screenshotFilepath='tests/data/img/img1.png')
    screenshot = Image.open('tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('coordinates1', screenshot=screenshot, screenshotFilepath='tests/data/img/img1.png')

  def test_error_optionBordersImage(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', bordersImage='invalid')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', bordersImage=42)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection2', bordersImage='invalid')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection2', bordersImage=42)

    bordersImage = Image.open('tests/data/img/img1.png')
    self.recognizer.execute('coordinates1', bordersImage=bordersImage)
    screenshot = Image.open('tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('coordinates1', screenshot=screenshot, bordersImage=bordersImage)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('coordinates1', screenshotFilepath='tests/data/img/img1.png', bordersImage=bordersImage)

  def test_error_optionBordersImageFilepath(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', bordersImageFilepath='tests/data/json/config1.json')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', bordersImageFilepath='unexistent.png')

    self.recognizer.execute('coordinates1', bordersImageFilepath='tests/data/img/img1.png')
    bordersImage = Image.open('tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('coordinates1', bordersImage=bordersImage, bordersImageFilepath='tests/data/img/img1.png')
    screenshot = Image.open('tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('coordinates1', screenshot=screenshot, bordersImageFilepath='tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('coordinates1', screenshotFilepath='tests/data/img/img1.png',
          bordersImageFilepath='tests/data/img/img1.png')

  def test_error_optionCoord(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('coordinates1', coord='invalid')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('coordinates1', coord=42)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('coordinates1', coord=(1))
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('coordinates1', coord=(1, 2, 3))
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('coordinates1', coord=(1, 2, 3, 4, 5))
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('coordinates1', coord=(1.0, 2))
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('coordinates1', coord=(1, 2, 3.0, 4))
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('findImage1', coord=(5, 5), screenshotFilepath='tests/data/img/img1.png')

  def test_error_optionSelectedPoint(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', selectedPoint='invalid')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', selectedPoint=(42, 42))
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', selectedPoint=(42, 42, 42, 42, 42))
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', selectedPoint=(42, 420, 42))
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', selectedPoint=(42.0, 42, 42))

  def test_error_optionPixelColor(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('pixelColor1', pixelColor='invalid')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('pixelColor1', pixelColor=42)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('pixelColor1', pixelColor=(42, 42, 42, 42))
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('pixelColor1', pixelColor=(42, 42.0, 42))

  def test_error_optionPixelColorReference(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('comparePixelColor1', pixelColorReference='invalid')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('comparePixelColor1', pixelColorReference=42)

  def test_error_optionPixelColorDifference(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('comparePixelColor1', pixelColorDifference='invalid')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('comparePixelColor1', pixelColorDifference=(42, 42, 42))
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('comparePixelColor1', pixelColorDifference=2)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('comparePixelColor1', pixelColorDifference=-1)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('comparePixelColor1', pixelColorDifference=1.1)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('comparePixelColor1', pixelColorDifference=-0.1)

  def test_error_optionSelectedArea(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection2', selectedArea='invalid')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection2', selectedArea=42)

  def test_error_optionSelectedAreaFilepath(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection2', selectedAreaFilepath='tests/data/json/config1.json')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection2', selectedAreaFilepath='unexistent.png')

    self.recognizer.execute('imageHash1', selectedAreaFilepath='tests/data/img/img1.png')
    area = Image.open('tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('imageHash2', selectedArea=area, selectedAreaFilepath='tests/data/img/img1.png')

  def test_error_optionImageHash(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('imageHash1', imageHash='invalid')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('imageHash1', imageHash=42)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('imageHash1', imageHash='b88cf69dd66c8960,')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('imageHash1', imageHash='b88cf69dd66c8960')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('imageHash1', imageHash='07000000000')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('imageHash1', imageHash='b88cf69dd66c8960,07000000000,07000000000')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('imageHash1', imageHash=',')

  def test_error_optionImageHashReference(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('compareImageHash1', imageHashReference='invalid')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('compareImageHash1', imageHashReference=42)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('compareImageHash1', imageHashReference='a1e24e1f1372761e,1b00b0')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('compareImageHash1', imageHashReference='a1e24e1f13727,1b00b000040')

  def test_error_optionImageHashDifference(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('compareImageHash1', imageHashDifference='invalid')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('compareImageHash1', imageHashDifference=2.72)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('compareImageHash1', imageHashDifference=3.0)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('compareImageHash1', imageHashDifference=-1)

  def test_error_actionCoordinates(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute(ActionType.COORDINATES)

  def test_error_actionFindImage(self):
    area = self.recognizer.execute('selection4', screenshotFilepath='tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('findImage1', selectedArea=area)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('findImage2', selectedArea=area)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute(ActionType.FIND_IMAGE, screenshotFilepath='tests/data/img/img1.png', coord=(7, 7, 10, 10))

  def test_error_actionComparePixelColor(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute(ActionType.COMPARE_PIXEL_COLOR, screenshotFilepath='tests/data/img/img1.png', coord=(7, 7))

  def test_error_actionCompareImageHash(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute(ActionType.COMPARE_IMAGE_HASH, screenshotFilepath='tests/data/img/img1.png', coord=(7, 7, 10, 10))

  def test_error_reinterpret(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', reinterpret='invalid', screenshotFilepath='tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', reinterpret=42, screenshotFilepath='tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', reinterpret=ActionType.FIND_IMAGE, screenshotFilepath='tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('isSamePixelColor1', reinterpret=ActionType.COMPARE_IMAGE_HASH, screenshotFilepath='tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('isSamePixelColor1', reinterpret=ActionType.TEXT, screenshotFilepath='tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('isSamePixelColor1', reinterpret=ActionType.NUMBER, screenshotFilepath='tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('isSameImageHash1', reinterpret=ActionType.COMPARE_PIXEL_COLOR, screenshotFilepath='tests/data/img/img1.png')

  def test_actionCoordinates(self):
    result = self.recognizer.execute('coordinates1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (20, 33))

    result = self.recognizer.execute('coordinates2', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (21, 8, 34, 22))

    result = self.recognizer.execute(ActionType.COORDINATES, coord=(7, 7))
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (7, 7))

  def test_actionSelection(self):
    result = self.recognizer.execute('selection1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (178, 178, 178, 255))

    result = self.recognizer.execute('selection2', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), Image.Image)
    width, height = result.size
    self.assertEqual(width * height, 35)

    result = self.recognizer.execute('selection1', bordersImageFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (178, 178, 178, 255))

    result = self.recognizer.execute('selection2', bordersImageFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), Image.Image)
    width, height = result.size
    self.assertEqual(width * height, 35)

  def test_actionFindImage(self):
    result = self.recognizer.execute('findImage1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), list)
    self.assertEqual(len(result), 1)
    self.assertEqual(result, [(12, 12, 19, 18)])

    result = self.recognizer.execute('findImage1', screenshotFilepath='tests/data/img/img3.png')
    self.assertEqual(type(result), list)
    self.assertEqual(len(result), 0)

    result = self.recognizer.execute('findImage2', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), list)
    self.assertEqual(len(result), 2)
    self.assertEqual(result, [(7, 28, 13, 29), (6, 27, 15, 28)])

  def test_actionPixelColor(self):
    result = self.recognizer.execute('pixelColor1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (114, 114, 114))

    result = self.recognizer.execute('pixelColor1', screenshotFilepath='tests/data/img/img2.png')
    self.assertEqual(type(result), tuple)
    self.assertNotEqual(result, (114, 114, 114))

    result = self.recognizer.execute('pixelColor2', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (0, 0, 0))

    result = self.recognizer.execute('pixelColor2', screenshotFilepath='tests/data/img/img2.png')
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (0, 0, 0))

    result = self.recognizer.execute('pixelColor3', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (95, 95, 95))

    result = self.recognizer.execute('pixelColor3', screenshotFilepath='tests/data/img/img2.png')
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (160, 160, 160))

    screenshot = Image.open('tests/data/img/img2.png')
    screenshot = ImageOps.grayscale(screenshot)
    result = self.recognizer.execute('pixelColor3', screenshot=screenshot)
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (160, 160, 160))

    screenshot = Image.open('tests/data/img/img1.png')
    result = self.recognizer.execute('pixelColor3', screenshot=screenshot, selectedPoint=42)
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (95, 95, 95))

    result = self.recognizer.execute(ActionType.PIXEL_COLOR, selectedPoint=42)
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (42, 42, 42))

    area = Image.open('tests/data/img/img1.png')
    result = self.recognizer.execute(ActionType.PIXEL_COLOR, selectedArea=area)
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (198, 198, 198))

    area = Image.open('tests/data/img/img1.png')
    result = self.recognizer.execute(ActionType.PIXEL_COLOR, selectedPoint=42, selectedArea=area)
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (42, 42, 42))

  def test_actionComparePixelColor(self):
    result = self.recognizer.execute('comparePixelColor1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), float)
    self.assertEqual(result, 0)

    result = self.recognizer.execute('comparePixelColor1', screenshotFilepath='tests/data/img/img2.png')
    self.assertEqual(type(result), float)
    self.assertNotEqual(result, 0)

  def test_actionIsSamePixelColor(self):
    result = self.recognizer.execute('isSamePixelColor1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), bool)
    self.assertTrue(result)

    result = self.recognizer.execute('isSamePixelColor1', screenshotFilepath='tests/data/img/img2.png')
    self.assertEqual(type(result), bool)
    self.assertFalse(result)

  def test_actionImageHash(self):
    result = self.recognizer.execute('imageHash1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), str)
    self.assertEqual(result, 'b88cf69dd66c8960,07000000000')

    result = self.recognizer.execute('imageHash1', screenshotFilepath='tests/data/img/img2.png')
    self.assertEqual(type(result), str)
    self.assertEqual(result, 'c77109622993769f,0e000000000')

    result = self.recognizer.execute('imageHash2', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), str)
    self.assertEqual(result, '8000000000000000,07000000000')

  def test_actionCompareImageHash(self):
    result = self.recognizer.execute('compareImageHash1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), int)
    self.assertEqual(result, 0)

    result = self.recognizer.execute('compareImageHash1', screenshotFilepath='tests/data/img/img2.png')
    self.assertEqual(type(result), int)
    self.assertEqual(result, 65)

  def test_actionIsSameImageHash(self):
    result = self.recognizer.execute('isSameImageHash1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), bool)
    self.assertTrue(result)

    result = self.recognizer.execute('isSameImageHash1', screenshotFilepath='tests/data/img/img2.png')
    self.assertEqual(type(result), bool)
    self.assertFalse(result)

  def test_actionText(self):
    result = self.recognizer.execute('text1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), str)
    self.assertNotIn('Love', result)

    result = self.recognizer.execute('text1', screenshotFilepath='tests/data/img/img3.png')
    self.assertEqual(type(result), str)
    self.assertIn('Love', result)

  def test_actionNumber(self):
    result = self.recognizer.execute('number1', screenshotFilepath='tests/data/img/img1.png')
    self.assertIsNone(result)

    result = self.recognizer.execute('number1', screenshotFilepath='tests/data/img/img3.png')
    self.assertEqual(type(result), float)
    self.assertEqual(result, 42)

    result = self.recognizer.execute('number2', screenshotFilepath='tests/data/img/img3.png')
    self.assertIsNone(result)

  def test_optionScreenshot(self):
    screenshot = Image.open('tests/data/img/img1.png')
    result = self.recognizer.execute('selection1', screenshot=screenshot)
    self.assertEqual(result, (178, 178, 178, 255))

  def test_optionScreenshotFilepath(self):
    result = self.recognizer.execute('selection1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(result, (178, 178, 178, 255))

  def test_optionBordersImage(self):
    bordersImage = Image.open('tests/data/img/img1.png')
    result = self.recognizer.execute('selection1', bordersImage=bordersImage)
    self.assertEqual(result, (178, 178, 178, 255))

  def test_optionBordersImageFilepath(self):
    result = self.recognizer.execute('selection1', bordersImageFilepath='tests/data/img/img1.png')
    self.assertEqual(result, (178, 178, 178, 255))

  def test_optionSelectedPoint(self):
    result = self.recognizer.execute('selection1', selectedPoint=42)
    self.assertEqual(result, 42)
    result = self.recognizer.execute('selection1', selectedPoint=(42, 42, 42))
    self.assertEqual(result, (42, 42, 42))
    result = self.recognizer.execute('selection1', selectedPoint=(42, 42, 42, 42))
    self.assertEqual(result, (42, 42, 42, 42))
    result = self.recognizer.execute('pixelColor1', selectedPoint=42)
    self.assertEqual(result, (42, 42, 42))

  def test_optionPixelColor(self):
    result = self.recognizer.execute('pixelColor1', pixelColor=(1, 42, 1))
    self.assertEqual(result, (1, 42, 1))
    result = self.recognizer.execute('comparePixelColor1', pixelColor=(167, 167, 167))
    self.assertEqual(result, 0)

  def test_optionPixelColorReference(self):
    result = self.recognizer.execute(ActionType.COMPARE_PIXEL_COLOR, pixelColor=(42, 9, 42), pixelColorReference=(42, 9, 42))
    self.assertEqual(result, 0)
    result = self.recognizer.execute('comparePixelColor1', pixelColorReference=(88, 88, 88), screenshotFilepath='tests/data/img/img2.png')
    self.assertEqual(result, 0)

  def test_optionPixelColorDifference(self):
    result = self.recognizer.execute('comparePixelColor1', pixelColorDifference=0.3)
    self.assertEqual(result, 0.3)
    result = self.recognizer.execute('isSamePixelColor1', pixelColorDifference=0.0)
    self.assertTrue(result)
    result = self.recognizer.execute('isSamePixelColor1', pixelColorDifference=0.3)
    self.assertFalse(result)

  def test_optionImageHash(self):
    result = self.recognizer.execute('imageHash1', imageHash='c77109622993769f,0e000000000')
    self.assertEqual(result, 'c77109622993769f,0e000000000')
    result = self.recognizer.execute('compareImageHash1', imageHash='c77109622993769f,0e000000000')
    self.assertEqual(result, 28)

  def test_optionImageHashReference(self):
    result = self.recognizer.execute(ActionType.COMPARE_IMAGE_HASH, imageHash='c77109622993769f,0e000000000',
        imageHashReference='c77109622993769f,0e000000000')
    self.assertEqual(result, 0)
    result = self.recognizer.execute('compareImageHash1', imageHashReference='c77109622993769f,0e000000000',
        screenshotFilepath='tests/data/img/img2.png')
    self.assertEqual(result, 41)

  def test_optionImageHashDifference(self):
    result = self.recognizer.execute('compareImageHash1', imageHashDifference=3)
    self.assertEqual(result, 3)
    result = self.recognizer.execute('isSameImageHash1', imageHashDifference=0)
    self.assertTrue(result)
    result = self.recognizer.execute('isSameImageHash1', imageHashDifference=3)
    self.assertFalse(result)

  def test_optionSelectedArea(self):
    area = Image.open('tests/data/img/img1.png')
    result = self.recognizer.execute('imageHash1', selectedArea=area)
    self.assertEqual(result, '9aa5e4ca304967b7,07000000000')

  def test_optionSelectedAreaFilepath(self):
    result = self.recognizer.execute('imageHash2', selectedAreaFilepath='tests/data/img/img1.png')
    self.assertEqual(result, '9aa5e4ca304967b7,07000000000')

  def test_reinterpret(self):
    result = self.recognizer.execute('selection1', reinterpret=ActionType.COORDINATES, screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), tuple)
    self.assertEqual(result, (9, 7))

    result = self.recognizer.execute('number1', reinterpret=ActionType.SELECTION, screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), Image.Image)
    width, height = result.size
    self.assertEqual(width * height, 432)

    result = self.recognizer.execute('isSamePixelColor1', reinterpret=ActionType.COMPARE_PIXEL_COLOR,
        screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), float)
    self.assertEqual(result, 0)

    result = self.recognizer.execute('comparePixelColor1', reinterpret=ActionType.IS_SAME_PIXEL_COLOR,
        screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), bool)
    self.assertTrue(result)

    result = self.recognizer.execute('isSameImageHash1', reinterpret=ActionType.COMPARE_IMAGE_HASH,
        screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), int)
    self.assertEqual(result, 0)

    result = self.recognizer.execute('compareImageHash1', reinterpret=ActionType.IS_SAME_IMAGE_HASH,
        screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(type(result), bool)
    self.assertTrue(result)

class TestExecuteActions(LoggedTestCase):
  def setUp(self):
    super().setUp()
    self.recognizer = Recognizer('tests/data/json/config1.json')
    self.recognizer.setOcrOrder([OcrType.EASY_OCR])

  def test_error_actionIdOrType(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', None, 'selection1', screenshotFilepath='tests/data/img/img1.png')
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', 42, 'selection1', screenshotFilepath='tests/data/img/img1.png')

    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('selection1', 'unkownId', 'selection1', screenshotFilepath='tests/data/img/img1.png')

  def test_actions_Coordinates_PixelColorLike(self):
    result = self.recognizer.execute('coordinates1', 'pixelColor1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(result, (186, 186, 186))

  def test_actions_Selection_PixelColorLike(self):
    result = self.recognizer.execute('selection1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(result, (178, 178, 178, 255))

    result = self.recognizer.execute('selection1', 'pixelColor1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(result, (178, 178, 178))

    result = self.recognizer.execute('selection1', 'comparePixelColor1', screenshotFilepath='tests/data/img/img1.png')
    self.assertNotEqual(result, 0)

    result = self.recognizer.execute('selection1', 'pixelColor1', 'comparePixelColor1',
        screenshotFilepath='tests/data/img/img1.png', pixelColor=(167, 167, 167))
    self.assertEqual(result, 0)

    result = self.recognizer.execute('selection1', 'pixelColor1', 'comparePixelColor1', 'isSamePixelColor1',
        screenshotFilepath='tests/data/img/img1.png', pixelColor=(167, 167, 167))
    self.assertTrue(result)

    result = self.recognizer.execute('selection1', 'isSamePixelColor1', screenshotFilepath='tests/data/img/img1.png')
    self.assertFalse(result)

    result = self.recognizer.execute('selection1', 'isSamePixelColor1', 'pixelColor1',
        screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(result, (178, 178, 178))

  def test_actions_Coordinates_ImageHashLike(self):
    result = self.recognizer.execute('coordinates2', 'imageHash1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(result, 'd48ad13dc2c939a7,07000000000')

  def test_actions_Selection_ImageHashLike(self):
    result = self.recognizer.execute('selection2', 'imageHash1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(result, 'c71626324d4bed8d,07000000000')

    result = self.recognizer.execute('selection2', 'imageHash1', 'compareImageHash1',
        screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(result, 34)

    result = self.recognizer.execute('selection2', 'compareImageHash1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(result, 34)

    result = self.recognizer.execute('selection2', 'imageHash1', 'compareImageHash1', 'isSameImageHash1',
        screenshotFilepath='tests/data/img/img1.png', imageHash='8e1b79e1a1a5a783,07000000000')
    self.assertTrue(result)

    result = self.recognizer.execute('selection2', 'isSameImageHash1', screenshotFilepath='tests/data/img/img1.png')
    self.assertFalse(result)

    result = self.recognizer.execute('selection2', 'isSameImageHash1', 'imageHash1',
        screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(result, 'c71626324d4bed8d,07000000000')

  def test_actions_Selection_Text(self):
    result = self.recognizer.execute('selection3', 'text1', screenshotFilepath='tests/data/img/img3.png')
    self.assertIn('2', result)

    result = self.recognizer.execute('text1', 'text1', screenshotFilepath='tests/data/img/img3.png')
    self.assertIn('Love', result)

  def test_actions_Selection_Number(self):
    result = self.recognizer.execute('selection3', 'number1', screenshotFilepath='tests/data/img/img3.png')
    self.assertEqual(result, 2)

    result = self.recognizer.execute('number1', 'number1', screenshotFilepath='tests/data/img/img3.png')
    self.assertEqual(result, 42)

  def test_actions_FindImage_ImageHashLike(self):
    result = self.recognizer.execute('findImage1', 'imageHash1', screenshotFilepath='tests/data/img/img1.png')
    self.assertEqual(result, '9aa5e4ca304967b7,07000000000')

class TestPreprocessing(LoggedTestCase):
  def setUp(self):
    super().setUp()
    self.recognizer = Recognizer('tests/data/json/config4.json')
    self.recognizer.setOcrOrder([OcrType.EASY_OCR])

  def test_error_invalidPreprocessingId(self):
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('pixelColor1', screenshotFilepath='tests/data/img/img1.png', preprocessing=42)
    with self.assertRaises(RecognizerValueError):
      self.recognizer.execute('pixelColor1', screenshotFilepath='tests/data/img/img1.png', preprocessing='unknown')

  def test_preprocessing_PixelColor(self):
    result = self.recognizer.execute('pixelColor1', screenshotFilepath='tests/data/img/img1.png', preprocessing='grayscale1')
    self.assertEqual(result, (198, 198, 198))
    result = self.recognizer.execute('pixelColor1', screenshotFilepath='tests/data/img/img1.png', preprocessing='colorMap1')
    self.assertEqual(result, (202, 101, 214))
    result = self.recognizer.execute('pixelColor1', screenshotFilepath='tests/data/img/img1.png', preprocessing='threshold1')
    self.assertEqual(result, (186, 186, 186))
    result = self.recognizer.execute('pixelColor1', screenshotFilepath='tests/data/img/img1.png', preprocessing='resize1')
    self.assertEqual(result, (197, 197, 197))

if __name__ == '__main__':
  unittest.main()
