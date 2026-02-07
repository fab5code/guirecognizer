import unittest
from unittest.mock import MagicMock, patch

from guirecognizer import MouseHelper
from tests.test_utility import LoggedTestCase


class TestMouseManager(LoggedTestCase):
  def test_click(self):
    pyautoguiMock = MagicMock()
    with patch.dict("sys.modules", {"pyautogui": pyautoguiMock}):
      MouseHelper.clickOnPosition((0, 0))
    pyautoguiMock.moveTo.assert_called_once()
    pyautoguiMock.click.assert_called_once()

  def test_click_pauseDuration(self):
    pyautoguiMock = MagicMock()
    with patch.dict("sys.modules", {"pyautogui": pyautoguiMock}):
      MouseHelper.clickOnPosition((0, 0), pauseDuration=0.5)
    pyautoguiMock.moveTo.assert_called_once()
    pyautoguiMock.click.assert_called_once()

  def test_click_manyClicks(self):
    pyautoguiMock = MagicMock()
    with patch.dict("sys.modules", {"pyautogui": pyautoguiMock}):
      MouseHelper.clickOnPosition((0, 0), nbClicks=10)
    pyautoguiMock.moveTo.assert_called_once()
    self.assertEqual(pyautoguiMock.click.call_count, 10)

  def test_dragCoords_noCoord(self):
    pyautoguiMock = MagicMock()
    with patch.dict("sys.modules", {"pyautogui": pyautoguiMock}):
      MouseHelper.dragCoords([])
    pyautoguiMock.moveTo.assert_not_called()
    pyautoguiMock.mouseDown.assert_not_called()
    pyautoguiMock.mouseUp.assert_not_called()

  def test_dragCoords_oneCoord(self):
    pyautoguiMock = MagicMock()
    with patch.dict("sys.modules", {"pyautogui": pyautoguiMock}):
      MouseHelper.dragCoords([(0, 0)])
    pyautoguiMock.moveTo.assert_called_once()
    pyautoguiMock.mouseDown.assert_called_once()
    pyautoguiMock.mouseUp.assert_called_once()

  def test_dragCoords_manyCoords(self):
    pyautoguiMock = MagicMock()
    with patch.dict("sys.modules", {"pyautogui": pyautoguiMock}):
      MouseHelper.dragCoords([(0, 0), (5, 5), (10, 20)])
    self.assertEqual(pyautoguiMock.moveTo.call_count, 3)
    pyautoguiMock.mouseDown.assert_called_once()
    pyautoguiMock.mouseUp.assert_called_once()

  def test_dragCoords_pauseDuration(self):
    pyautoguiMock = MagicMock()
    with patch.dict("sys.modules", {"pyautogui": pyautoguiMock}):
      MouseHelper.dragCoords([(0, 0), (5, 5), (10, 20)], pauseDuration=0.5)
    self.assertEqual(pyautoguiMock.moveTo.call_count, 3)
    pyautoguiMock.mouseDown.assert_called_once()
    pyautoguiMock.mouseUp.assert_called_once()

  def test_dragCoords_moveDuration(self):
    pyautoguiMock = MagicMock()
    with patch.dict("sys.modules", {"pyautogui": pyautoguiMock}):
      MouseHelper.dragCoords([(0, 0), (5, 5), (10, 20)], moveDuration=0.5)
    self.assertEqual(pyautoguiMock.moveTo.call_count, 3)
    pyautoguiMock.mouseDown.assert_called_once()
    pyautoguiMock.mouseUp.assert_called_once()

if __name__ == '__main__':
  unittest.main()
