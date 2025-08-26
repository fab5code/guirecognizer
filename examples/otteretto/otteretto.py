import datetime
import logging
import multiprocessing
import time
from random import randint

import keyboard
from guirecognizer import ActionType, MouseHelper, Recognizer
from guirecognizer.types import Coord


class Game:
  def __init__(self, grid=None):
    self.width = 4
    self.height = 10
    self.nbSquareTypes = 5
    if grid is None:
      self.reset()
    else:
      self.grid = grid

  def reset(self):
    self.grid = [0 for _ in range(self.width * self.height)]

  def getIndex(self, x, y):
    return y * self.width + x

  def getXY(self, index):
    return index % self.width, int(index / self.width)

  def getSquare(self, x, y):
    return self.grid[self.getIndex(x, y)]

  def setSquare(self, x, y, square):
    self.grid[self.getIndex(x, y)] = square

  def getGridId(self):
    return ','.join(str(index) for index in self.grid)

  def getEmptySquaresInfo(self):
    firstYWhereOnlyEmpty = 0
    for x in range(self.width):
      for y in range(self.height):
        if self.getSquare(x, y) != 0:
          if y > firstYWhereOnlyEmpty:
            firstYWhereOnlyEmpty = y
        else:
          break
    emptyGapHeight = (self.height - 1) - firstYWhereOnlyEmpty
    return emptyGapHeight, self.grid.count(0)

  def isEmpty(self):
    return self.grid.count(0) == self.width * self.height

  def fillRandom(self):
    for x in range(self.width):
      for y in range(self.height):
        square = randint(0, self.nbSquareTypes)
        self.setSquare(x, y, square)
    self.fallDown()

  def fallDown(self):
    for y in range(self.height):
      for x in range(self.width):
        if self.getSquare(x, y) == 0:
          for yAbove in range(y + 1, self.height):
            if self.getSquare(x, yAbove) == 0:
              continue
            self.setSquare(x, y, self.getSquare(x, yAbove))
            self.setSquare(x, yAbove, 0)
            break

  def applyMove(self, move):
    self.grid[move] = 0
    self.fallDown()

  def applyMoves(self, moves):
    for move in moves:
      self.applyMove(move)

  def findBestPalindromeWithMoves(self, depth, doesNotUseMultiprocessing=False):
    """
    If depth <= 3 the multiprocessing version is not used.
    The multiprocessing version has a large overhead because the ids of all processed grids are shared
    so as to avoid doing some work on already seen grids.
    This optimisation is greater than the gain from multiprocessing so it's better to pay the overhead to use it.
    """
    if depth > 3 and not doesNotUseMultiprocessing:
      return self.findBestPalindromeWithMovesMultiprocess(depth)
    else:
      return self.findBestPalindromeFromMoves(self, [], depth, {})

  def findBestPalindromeWithMovesMultiprocess(self, depth):
    bestScore, bestPalindrome = self.findBestPalindrome()
    bestMoves = []
    if depth == 0:
      return bestScore, bestPalindrome, bestMoves

    with multiprocessing.Manager() as manager:
      seenGridIds = manager.dict()

      processArgs = []
      for x in range(self.width):
        for y in range(self.height):
          if y == self.height - 1 or self.getSquare(x, y + 1) == 0:
            break
          game = Game(list(self.grid))
          moves = [self.getIndex(x, y)]
          game.applyMove(moves[-1])
          gridId = game.getGridId()
          if gridId in seenGridIds:
            continue
          seenGridIds[gridId] = None
          processArgs.append((game, moves, depth - 1, seenGridIds))

      with multiprocessing.Pool() as pool:
        for score, palindrome, moves in pool.starmap(Game.findBestPalindromeFromMoves, processArgs):
          if score > bestScore or (score == bestScore and len(moves) < len(bestMoves)):
            bestScore = score
            bestPalindrome = palindrome
            bestMoves = moves
    return bestScore, bestPalindrome, bestMoves

  @classmethod
  def findBestPalindromeFromMoves(cls, game, moves, depth, seenGridIds):
    bestScore, bestPalindrome = game.findBestPalindrome()
    bestMoves = moves
    if depth == 0:
      return bestScore, bestPalindrome, bestMoves
    for x in range(game.width):
      for y in range(game.height):
        if y == game.height - 1 or game.getSquare(x, y + 1) == 0 or game.getSquare(x, y) == 0:
          break
        localGame = Game(list(game.grid))
        localMoves = moves + [game.getIndex(x, y)]
        localGame.applyMove(localMoves[-1])
        gridId = localGame.getGridId()
        if gridId in seenGridIds:
          continue
        seenGridIds[gridId] = None
        finalScore, finalPalindrome, finalMoves = game.findBestPalindromeFromMoves(localGame,
            localMoves, depth - 1, seenGridIds)
        if finalScore > bestScore or (finalScore == bestScore and len(finalMoves) < len(bestMoves)):
          bestScore = finalScore
          bestPalindrome = finalPalindrome
          bestMoves = finalMoves
    return bestScore, bestPalindrome, bestMoves

  def findBestPalindrome(self):
    bestScore = 0
    bestPalindrome = []
    centerPairs = []
    for x in range(self.width):
      for y in range(self.height):
        if self.getSquare(x, y) == 0:
          break
        center = self.getIndex(x, y)
        centerPairs.append((center, center))
        newX = x + 1
        if newX < self.width and self.getSquare(x, y) == self.getSquare(newX, y):
          centerPairs.append((center, self.getIndex(newX, y)))
        newY = y + 1
        if newY < self.height and self.getSquare(x, y) == self.getSquare(x, newY):
          centerPairs.append((center, self.getIndex(x, newY)))
    for centerA, centerB in centerPairs:
      score, palindrome = self.findBestPalindromeFromCenters(centerA, centerB)
      if score > bestScore:
        bestScore = score
        bestPalindrome = palindrome
    return bestScore, bestPalindrome

  def findBestPalindromeFromCenters(self, centerA, centerB=None):
    if centerB is None or centerA == centerB:
      return self.findPalindrome(centerA, centerA, {centerA}, [centerA])
    else:
      return self.findPalindrome(centerA, centerB, {centerA, centerB}, [centerA, centerB])

  def findPalindrome(self, centerA, centerB, seenSpaces, palindrome):
    bestScore = self.computeScore(palindrome)
    bestPalindrome = palindrome
    for adjacentA in self.getAdjacents(centerA, seenSpaces):
      for adjacentB in self.getAdjacents(centerB, seenSpaces):
        if adjacentA == adjacentB or self.grid[adjacentA] != self.grid[adjacentB]:
          continue
        localSeenSpaces = set(seenSpaces)
        localSeenSpaces.add(adjacentA)
        localSeenSpaces.add(adjacentB)
        localPalindrom = [adjacentA] + palindrome
        localPalindrom.append(adjacentB)
        finalScore, finalPalindrome = self.findPalindrome(adjacentA, adjacentB, localSeenSpaces, localPalindrom)
        if finalScore > bestScore:
          bestScore = finalScore
          bestPalindrome = finalPalindrome
    return bestScore, bestPalindrome

  def computeScore(self, palindrome):
    nbSquareTypeChange = 0
    precedentSquare = None
    for index in palindrome:
      if precedentSquare is not None and self.grid[index] != precedentSquare:
        nbSquareTypeChange += 1
      precedentSquare = self.grid[index]
    return len(palindrome) * (nbSquareTypeChange + 1)

  def getAdjacents(self, center, seenSpaces):
    adjacents = []
    x, y = self.getXY(center)
    for xChange, yChange in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
      newX = x + xChange
      newY = y + yChange
      if newX < 0 or newX >= self.width or newY < 0 or newY >= self.height:
        continue
      adjacent = self.getIndex(newX, newY)
      if self.grid[adjacent] == 0 or adjacent in seenSpaces:
        continue
      adjacents.append(adjacent)
    return adjacents

  def printGrid(self):
    for y in reversed(range(self.height)):
      line = str(y) + ' |'
      for x in range(self.width):
        if self.getSquare(x, y) == 0:
          line += '   '
        else:
          line += ' ' + str(self.getSquare(x, y)) + ' '
      line += '|'
      print(line)

  def printMoves(self, moves):
    for move in moves:
      print('Move:', move)
      moveX, moveY = self.getXY(move)
      for y in reversed(range(self.height)):
        line = str(y) + ' |'
        for x in range(self.width):
          if x == moveX and y == moveY:
            line += ' X '
          else:
            line += '   '
        line += '|'
        print(line)

  def printPalindrome(self, palindrome):
    print('Palindrome:', len(palindrome), palindrome)
    for y in reversed(range(self.height)):
      line = str(y) + ' |'
      for x in range(self.width):
        if self.getSquare(x, y) == 0:
          line += '   '
          continue
        index = self.getIndex(x, y)
        if index not in palindrome:
          line += '   '
          continue
        position = palindrome.index(index)
        if position < 10:
          line += ' ' + str(position) + ' '
        else:
          line += str(position) + ' '
      line += '|'
      print(line)

class Statistics:
  def __init__(self):
    self.nbPalindromes = 0
    self.maxScore = 0
    self.sumScore = 0
    self.maxPalindromeLength = 0
    self.sumPalindromeLength = 0
    self.sumPreMoves = 0
    self.maxPreMoves = 0

  def printStats(self):
    if self.nbPalindromes == 0:
      print('No stats.')
      return
    print('Max score:', self.maxScore, 'Max palindrome length:', self.maxPalindromeLength,
        'Max nb of transitional moves:', self.maxPreMoves)
    print('Nb palindromes:', self.nbPalindromes, 'Average score:', '{:.1f}'.format(self.sumScore / self.nbPalindromes),
        'Average palindrome length:', '{:.1f}'.format(self.sumPalindromeLength / self.nbPalindromes),
        'Average nb of transitional moves:', '{:.1f}'.format(self.sumPreMoves / self.nbPalindromes))

class Bot:
  def __init__(self):
    self.recognizer = Recognizer('otteretto.json')
    self.game = Game()
    self.stats = Statistics()
    self.doesStop = False

    self.coords: list[Coord] = [(0, 0) for _ in range(self.game.width * self.game.height)]
    topLeft = self.recognizer.executeCoordinates('topLeft')
    topRight = self.recognizer.executeCoordinates('topRight')
    bottomLeft = self.recognizer.executeCoordinates('bottomLeft')
    xGap = abs(topRight[0] - topLeft[0]) / (self.game.width - 1)
    yGap = abs(bottomLeft[1] - topLeft[1]) / (self.game.height - 1)
    for x in range(self.game.width):
      for y in range(self.game.height):
        coord = (int(bottomLeft[0] + x * xGap), int(bottomLeft[1] - y * yGap))
        self.coords[self.game.getIndex(x, y)] = coord
    keyboard.add_hotkey('ctrl+shift+p', self.stop, suppress=True)

  def stop(self):
    logging.debug('STOP')
    self.doesStop = True

  def updateGame(self):
    self.game.reset()
    bordersImage = self.recognizer.getBordersImage()
    for x in range(self.game.width):
      for y in range(self.game.height):
        color = self.recognizer.executePixelColor(ActionType.PIXEL_COLOR, bordersImage=bordersImage, coord=self.coords[self.game.getIndex(x, y)])
        if self.recognizer.executeIsSamePixelColor('typeSquare', pixelColor=color):
          self.game.setSquare(x, y, 1)
        elif self.recognizer.executeIsSamePixelColor('typeStar', pixelColor=color):
          self.game.setSquare(x, y, 2)
        elif self.recognizer.executeIsSamePixelColor('typeCircle', pixelColor=color):
          self.game.setSquare(x, y, 3)
        elif self.recognizer.executeIsSamePixelColor('typeTriangle', pixelColor=color):
          self.game.setSquare(x, y, 4)
        elif self.recognizer.executeIsSamePixelColor('typeDiamond', pixelColor=color):
          self.game.setSquare(x, y, 5)

  def findBestPalindromeWithAppliedMoves(self, depth, doesNotUseMultiprocessing=False):
    score, palindrome, localMoves = self.game.findBestPalindromeWithMoves(depth, doesNotUseMultiprocessing)
    self.game.applyMoves(localMoves)
    if depth == 0:
      return score, palindrome, localMoves
    moves = localMoves
    while True:
      score, palindrome, localMoves = self.game.findBestPalindromeWithMoves(depth - 1, doesNotUseMultiprocessing)
      self.game.applyMoves(localMoves)
      if len(localMoves) == 0:
        break
      moves += localMoves
    return score, palindrome, moves

  def runOneGame(self, depth):
    self.updateGame()
    if self.game.isEmpty() and self.recognizer.executeIsSamePixelColor('hasBonus'):
      self.recognizer.executeClick('bonus')
      time.sleep(5)
      self.updateGame()
    if self.game.isEmpty():
      return False
    if self.doesStop:
      return False

    startTime = datetime.datetime.now()
    score, palindrome, moves = self.findBestPalindromeWithAppliedMoves(depth)
    duration = datetime.datetime.now() - startTime
    logging.info('Palindrome of score {score} and length {length} using {nbMoves} transitional moves found in {duration}.'
        .format(score=score, length=len(palindrome), nbMoves=len(moves), duration=duration))
    if self.doesStop:
      return False

    self.stats.nbPalindromes += 1
    if score > self.stats.maxScore:
      self.stats.maxScore = score
    self.stats.sumScore += score
    if len(palindrome) > self.stats.maxPalindromeLength:
      self.stats.maxPalindromeLength = len(palindrome)
    self.stats.sumPalindromeLength += len(palindrome)
    if len(moves) > self.stats.maxPreMoves:
      self.stats.maxPreMoves = len(moves)
    self.stats.sumPreMoves += len(moves)

    for move in moves:
      self.recognizer.executeClick(ActionType.CLICK, coord=self.coords[move])
      time.sleep(1)
    MouseHelper.dragCoords([self.coords[index] for index in palindrome])
    return True

  def fakeRun(self, depth):
    self.doesStop = False
    self.updateGame()
    if self.game.isEmpty():
      return False
    self.game.printGrid()
    startTime = datetime.datetime.now()
    score, palindrome, moves = self.findBestPalindromeWithAppliedMoves(depth)
    duration = datetime.datetime.now() - startTime
    print('Score:', score, 'duration', str(duration))
    self.game.printMoves(moves)
    self.game.printPalindrome(palindrome)
    return True

  def runForHighScore(self):
    self.run(4)

  def runForModerateSpeed(self):
    self.run(3)

  def run(self, depth):
    self.doesStop = False
    while not self.doesStop:
      canPlay = self.runOneGame(depth)
      if not canPlay or self.doesStop:
        break
      time.sleep(5)
    self.stats.printStats()

def main():
  logging.basicConfig(format='%(levelname)s-%(asctime)s: %(message)s', datefmt='%H:%M:%S', level=logging.INFO)
  bot = Bot()
  # bot.fakeRun(4)
  # bot.runOneGame(5)
  # bot.runForModerateSpeed()
  bot.runForHighScore()

if __name__ == '__main__':
  main()
