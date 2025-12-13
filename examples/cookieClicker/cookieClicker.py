import logging
import multiprocessing as mp
import os
import random

import keyboard
from guirecognizer import ActionType, Recognizer


class Manager:
  def __init__(self, recognizerConfig, stopEvent, mouseLock):
    self.recognizer = Recognizer(recognizerConfig)
    self.stopEvent = stopEvent
    self.mouseLock = mouseLock

class CookieManager(Manager):
  @classmethod
  def runNewManager(cls, recognizerConfig, stopEvent, mouseLock):
    manager = CookieManager(recognizerConfig, stopEvent, mouseLock)
    manager.run()

  def run(self):
    while not self.stopEvent.wait(0.001):
      self.mouseLock.acquire()
      self.recognizer.executeClick('cookie', clickPauseDuration=0.02, nbClicks=20)
      self.mouseLock.release()

class UpdateManager(Manager):
  def __init__(self, recognizerConfig, stopEvent, mouseLock):
    super().__init__(recognizerConfig, stopEvent, mouseLock)
    self.nbBuildingsInScreen = 9
    self.maxNbBuildings = 15
    self.maxNbCursors = 50

    self.nbBuildings = [27, 5, 3, 0, 0, 0, 0, 0, 0]
    self.initBuildingCoords()

  @classmethod
  def runNewManager(cls, recognizerConfig, stopEvent, mouseLock):
    manager = UpdateManager(recognizerConfig, stopEvent, mouseLock)
    manager.run()

  def initBuildingCoords(self):
    self.buildingCoords = []
    topCoord = self.recognizer.executeCoordinates('buildingTop')
    bottomCoord = self.recognizer.executeCoordinates('buildingBottom')
    yStep = (bottomCoord[1] - topCoord[1]) / (self.nbBuildingsInScreen - 1)
    for i in range(self.nbBuildingsInScreen):
      coord = (topCoord[0], int(topCoord[1] + i * yStep))
      self.buildingCoords.append(coord)

  def run(self):
    nextWait = 1
    while not self.stopEvent.wait(nextWait):
      buildingToBuy = self.getBuildingToBuy()
      canBuyUpgrade = self.canBuyUpgrade()
      if buildingToBuy is None and not canBuyUpgrade:
        nextWait = 5
        continue
      if self.mouseLock.acquire(timeout=1):
        if buildingToBuy is not None and canBuyUpgrade:
          # Choose randomly between buying a building or an upgrade.
          canBuyUpgrade = random.choice([True, False])
        if canBuyUpgrade:
          self.recognizer.executeClick('buyUpgrade')
        else:
          assert buildingToBuy is not None
          self.recognizer.executeClick(ActionType.CLICK, coord=self.buildingCoords[buildingToBuy])
          self.nbBuildings[buildingToBuy] += 1
        self.mouseLock.release()
        nextWait = 0.5
      else:
        nextWait = 5

  def getBuildingToBuy(self):
    for building in reversed(range(self.nbBuildingsInScreen)):
      if (building == 0 and self.nbBuildings[building] >= self.maxNbCursors) or (building != 0 and self.nbBuildings[building] >= self.maxNbBuildings):
        continue
      pixels = (self.buildingCoords[building][0], self.buildingCoords[building][1], self.buildingCoords[building][0] + 8, self.buildingCoords[building][1] + 7)
      color = self.recognizer.executePixelColor(ActionType.PIXEL_COLOR, coord=pixels)
      availableDiff = self.recognizer.executeComparePixelColor('buildingAvailableDiff', pixelColor=color)
      unavailableDiff = self.recognizer.executeComparePixelColor('buildingUnavailableDiff', pixelColor=color)
      if building == 1:
        print('Building 1', availableDiff, '<', unavailableDiff, availableDiff < unavailableDiff)
      if availableDiff < unavailableDiff:
        return building
    return None

  def canBuyUpgrade(self):
    color = self.recognizer.executePixelColor('upgrade')
    availableDiff = self.recognizer.executeComparePixelColor('upgradeAvailableDiff', pixelColor=color)
    unavailableDiff = self.recognizer.executeComparePixelColor('upgradeUnavailableDiff', pixelColor=color)
    return availableDiff < unavailableDiff

class GoldenManager(Manager):
  @classmethod
  def runNewManager(cls, recognizerConfig, stopEvent, mouseLock):
    manager = GoldenManager(recognizerConfig, stopEvent, mouseLock)
    manager.run()

  def run(self):
    while not self.stopEvent.wait(0.1):
      for action in ['findGolden1', 'findGolden2', 'findGolden3', 'findGolden4']:
        coords = self.recognizer.executeFindImage(action)
        if len(coords) == 0:
          continue
        self.mouseLock.acquire()
        for coord in coords:
          center = (int((coord[0] + coord[2]) / 2), int((coord[1] + coord[3]) / 2))
          self.recognizer.execute(ActionType.CLICK, coord=center)
        self.mouseLock.release()

class Bot:
  def __init__(self):
    self.recognizerConfig = 'cookieClicker.json'
    self.stopEvent = mp.Event()
    shortcut = 'ctrl+shift+m'
    print(f'To stop bot: {shortcut}')
    keyboard.add_hotkey(shortcut, self.stop, suppress=True)

  def stop(self):
    logging.debug('STOP')
    self.stopEvent.set()

  def run(self):
    mouseLock = mp.Lock()
    processes = []
    args = (self.recognizerConfig, self.stopEvent, mouseLock)
    processes.append(mp.Process(target=CookieManager.runNewManager, args=args))
    processes.append(mp.Process(target=UpdateManager.runNewManager, args=args))
    # processes.append(mp.Process(target=GoldenManager.runNewManager, args=args))
    for process in processes:
      process.start()
    for process in processes:
      process.join()

def main():
  logging.basicConfig(format='%(levelname)s-%(asctime)s: %(message)s', datefmt='%H:%M:%S', level=logging.INFO)
  bot = Bot()
  bot.run()

if __name__ == '__main__':
  main()
