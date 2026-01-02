import asyncio
import datetime
import logging
import time
from enum import Enum, auto, unique

import keyboard
from guirecognizer import Recognizer


@unique
class Ingredient(Enum):
  price: int
  nbByPayment: int

  RICE = (auto(), 100, 10)
  NORI = (auto(), 100, 10)
  FISH_EGG = (auto(), 200, 10)
  SHRIMP = (auto(), 350, 5)
  SALMON = (auto(), 300, 5)
  UNAGI = (auto(), 350, 5)
  SAKE = (auto(), 100, 2)

  def __new__(cls, value, price, nbByPayment):
    obj = object.__new__(cls)
    obj._value_ = value
    obj.price = price
    obj.nbByPayment = nbByPayment
    return obj

@unique
class Sushi(Enum):
  actionId: str
  ingredients: list[Ingredient]
  price: int

  ONIGIRI = (auto(), 'isOnigiri', [Ingredient.RICE, Ingredient.RICE, Ingredient.NORI], 60)
  SALMON_ROLL = (auto(), 'isSalmonRoll', [Ingredient.RICE, Ingredient.NORI, Ingredient.SALMON, Ingredient.SALMON], 280)
  CALIFORNIA_ROLL = (auto(), 'isCaliforniaRoll', [Ingredient.RICE, Ingredient.NORI, Ingredient.FISH_EGG], 80)
  SHRIMP_SUSHI = (auto(), 'isShrimpSushi', [Ingredient.RICE, Ingredient.NORI, Ingredient.SHRIMP, Ingredient.SHRIMP], 320)
  GUNKAN_MAKI = (auto(), 'isGunkanMaki', [Ingredient.RICE, Ingredient.NORI, Ingredient.FISH_EGG, Ingredient.FISH_EGG], 120)
  UNAGI_ROLL = (auto(), 'isUnagiRoll', [Ingredient.RICE, Ingredient.NORI, Ingredient.UNAGI, Ingredient.UNAGI], 320)
  DRAGON_ROLL = (auto(), 'isDragonRoll',
      [Ingredient.RICE, Ingredient.RICE, Ingredient.NORI, Ingredient.FISH_EGG, Ingredient.UNAGI, Ingredient.UNAGI], 380)
  COMBO_SUSHI = (auto(), 'isComboSushi',
      [Ingredient.RICE, Ingredient.RICE, Ingredient.NORI, Ingredient.FISH_EGG, Ingredient.SHRIMP, Ingredient.UNAGI, Ingredient.SALMON], 450)

  def __new__(cls, value, actionId, ingredients, price):
    obj = object.__new__(cls)
    obj._value_ = value
    obj.actionId = actionId
    obj.ingredients = ingredients
    obj.price = price
    return obj

class Kitchen:
  def __init__(self, recognizer: Recognizer):
    self.recognizer = recognizer
    self.reset()

  def reset(self) -> None:
    self.nbByIngredient = {
      Ingredient.RICE: 10,
      Ingredient.NORI: 10,
      Ingredient.FISH_EGG: 10,
      Ingredient.SHRIMP: 5,
      Ingredient.SALMON: 5,
      Ingredient.UNAGI: 5,
      Ingredient.SAKE: 2
    }
    self.money = 0
    self.isShipping = dict.fromkeys(Ingredient, False)

  async def buyIngredients(self, orders: list[Sushi]) -> None:
    # Sort ingredients depending on the priority of the orders.
    sortedIngredients = []
    for order in orders:
      for ingredient in order.ingredients:
        if ingredient not in sortedIngredients:
          sortedIngredients.append(ingredient)
    for ingredient in Ingredient:
      if ingredient not in sortedIngredients:
        sortedIngredients.append(ingredient)

    for ingredient in sortedIngredients:
      if self.isShipping[ingredient]:
        continue
      if self.nbByIngredient[ingredient] >= sum([order.ingredients.count(ingredient) for order in orders]):
        continue
      if ingredient.price > self.money:
        # If the most needed ingredient can't be bought, it's better to wait for more money instead of
        # wasting money on less important ingredients.
        return
      await self.buy(ingredient)
      # Let order manager have some work.
      await asyncio.sleep(0.01)

  async def buy(self, ingredient: Ingredient) -> None:
    logging.debug('  Buy ' + ingredient.name + '.')
    self.recognizer.executeClick('phone')
    match(ingredient):
      case Ingredient.RICE:
        self.recognizer.executeClick('buyRice')
      case Ingredient.NORI | Ingredient.FISH_EGG | Ingredient.SHRIMP | Ingredient.SALMON | Ingredient.UNAGI:
        self.recognizer.executeClick('buyTopping')
      case Ingredient.SAKE:
        self.recognizer.executeClick('buySake')
    match(ingredient):
      case Ingredient.RICE:
        self.recognizer.executeClick('buyRice')
        self.recognizer.executeClick('buyRice2')
      case Ingredient.NORI:
        self.recognizer.executeClick('buyTopping')
        self.recognizer.executeClick('buyNori')
      case Ingredient.FISH_EGG:
        self.recognizer.executeClick('buyTopping')
        self.recognizer.executeClick('buyFishEgg')
      case Ingredient.SHRIMP:
        self.recognizer.executeClick('buyTopping')
        self.recognizer.executeClick('buyShrimp')
      case Ingredient.SALMON:
        self.recognizer.executeClick('buyTopping')
        self.recognizer.executeClick('buySalmon')
      case Ingredient.UNAGI:
        self.recognizer.executeClick('buyTopping')
        self.recognizer.executeClick('buyUnagi')
        self.nbByIngredient[ingredient]
      case Ingredient.SAKE:
        self.recognizer.executeClick('buySake')
        self.recognizer.executeClick('buySake2')
    # May need some delay.
    await asyncio.sleep(0.1)
    self.recognizer.executeClick('confirmFreeBuy')
    self.money -= ingredient.price
    self.isShipping[ingredient] = True
    asyncio.create_task(self.updateAfterShipping(ingredient))

  async def updateAfterShipping(self, ingredient: Ingredient) -> None:
    await asyncio.sleep(0.5)
    while self.isShippingIngredient(ingredient):
      await asyncio.sleep(0.5)
    self.nbByIngredient[ingredient] += ingredient.nbByPayment
    self.isShipping[ingredient] = False

  def isShippingIngredient(self, ingredient: Ingredient) -> bool:
    match(ingredient):
      case Ingredient.RICE:
        return not self.recognizer.executeIsSamePixelColor('isNotShippingRice')
      case Ingredient.NORI:
        return not self.recognizer.executeIsSamePixelColor('isNotShippingNori')
      case Ingredient.FISH_EGG:
        return not self.recognizer.executeIsSamePixelColor('isNotShippingFishEgg')
      case Ingredient.SHRIMP:
        return not self.recognizer.executeIsSamePixelColor('isNotShippingShrimp')
      case Ingredient.SALMON:
        return not self.recognizer.executeIsSamePixelColor('isNotShippingSalmon')
      case Ingredient.UNAGI:
        return not self.recognizer.executeIsSamePixelColor('isNotShippingUnagi')
    return False

  def canMakeOrder(self, order: Sushi) -> bool:
    for ingredient in Ingredient:
      if self.nbByIngredient[ingredient] < order.ingredients.count(ingredient):
        return False
    return True

  def makeOrder(self, order: Sushi) -> None:
    for ingredient in order.ingredients:
      self.selectIngredient(ingredient)

  def selectIngredient(self, ingredient: Ingredient) -> None:
    match(ingredient):
      case Ingredient.RICE:
        self.recognizer.executeClick('selectRice')
      case Ingredient.NORI:
        self.recognizer.executeClick('selectNori')
      case Ingredient.FISH_EGG:
        self.recognizer.executeClick('selectFishEgg')
      case Ingredient.SHRIMP:
        self.recognizer.executeClick('selectShrimp')
      case Ingredient.SALMON:
        self.recognizer.executeClick('selectSalmon')
      case Ingredient.UNAGI:
        self.recognizer.executeClick('selectUnagi')
    self.nbByIngredient[ingredient] -= 1

class Statistics:
  def __init__(self):
    self.reset()

  def reset(self) -> None:
    self.nbClients = 0
    self.nbClientsServed = 0
    self.nbByOrder = dict.fromkeys(Sushi, 0)

  def printStats(self) -> None:
    print('Served clients:', str(self.nbClientsServed) + '/' + str(self.nbClients), ' Unsatisfied:', self.nbClients - self.nbClientsServed)
    print('Orders:', sum(self.nbByOrder.values()))
    for order in Sushi:
      print(' ', order.name + ':', self.nbByOrder[order])

class Bot:
  clientsToServe: list[int]
  orderByClient: dict[int, Sushi]
  sendOrderTime: list[float | None]

  def __init__(self):
    self.stats = Statistics()
    self.recognizer = Recognizer('sushiGoRound.json')
    self.kitchen = Kitchen(self.recognizer)

    self.nbClients = 6
    self.nbDays = 7
    self.reset()
    shortcut = 'ctrl+shift+p'
    print(f'To stop bot: {shortcut}')
    keyboard.add_hotkey(shortcut, self.stop, suppress=True)

  def reset(self) -> None:
    self.wasPresent = [False for _ in range(self.nbClients)]
    self.wasEating = [False for _ in range(self.nbClients)]
    self.hasPrepare = [False for _ in range(self.nbClients)]
    self.clientsToServe = []
    self.orderByClient = {}
    self.sendOrderTime = [None for _ in range(self.nbClients)]
    self.doesStop = False

  def stop(self) -> None:
    logging.debug('STOP')
    self.doesStop = True

  def run(self) -> None:
    logging.debug('Run bot.')
    asyncio.run(self.runFromMenu())

  def runOneDay(self) -> None:
    logging.debug('Run bot for the day.')
    asyncio.run(self.runDay())
    self.stats.printStats()

  async def runFromMenu(self) -> None:
    day = 1
    startTime = datetime.datetime.now()
    await self.passMenu()
    while True:
      if self.doesStop:
        return
      await self.runDay()
      self.stats.printStats()
      self.doesStop = False
      if self.recognizer.executeIsSamePixelColor('isWorking'):
        return
      durationSinceStart = datetime.datetime.now() - startTime
      print('Time elapsed:', str(durationSinceStart))
      if day == self.nbDays:
        return
      day += 1
      print('Day', day, 'will start in 30s.')
      await asyncio.sleep(30)
      if self.doesStop:
        return
      self.resetDay()
      self.recognizer.executeClick('continueNextDay1')
      await asyncio.sleep(0.1)
      self.recognizer.executeClick('continueNextDay2')
      await asyncio.sleep(0.1)

  async def runDay(self) -> None:
    await asyncio.gather(self.takeOrders(), self.sendOrders(), self.buyIngredients())

  def resetDay(self) -> None:
    self.reset()
    self.kitchen.reset()
    self.stats.reset()

  async def passMenu(self) -> None:
    while not self.recognizer.executeIsSameImageHash('isStartMenu'):
      if self.doesStop:
        return
      logging.debug('Waiting for game menu.')
      await asyncio.sleep(1)
    if self.doesStop:
      return
    self.recognizer.executeClick('startGame')
    await asyncio.sleep(0.1)
    self.recognizer.executeClick('welcome1')
    await asyncio.sleep(0.1)
    self.recognizer.executeClick('welcome2')
    await asyncio.sleep(0.1)

  async def takeOrders(self) -> None:
    while True:
      if self.doesStop:
        return
      self.manageOrders()
      await asyncio.sleep(0.5)

  def manageOrders(self) -> None:
    if not self.recognizer.executeIsSamePixelColor('isWorking'):
      self.doesStop = True
      return

    isPresent = [False for _ in range(self.nbClients)]
    isEating = [False for _ in range(self.nbClients)]
    for client in range(self.nbClients):
      isPresent[client] = not self.recognizer.executeIsSamePixelColor('hasNotClient' + str(client))
      isEating[client] = isPresent[client] and not self.recognizer.executeIsSamePixelColor('hasClientChoice' + str(client))

    for client in range(self.nbClients):
      if not isPresent[client] and self.wasPresent[client]:
        self.wasPresent[client] = False
        if self.wasEating[client]:
          self.kitchen.money += self.orderByClient[client].price
        elif self.hasPrepare[client]:
          # An order is on the loose: try reassign it.
          reassignClient = None
          for otherClient in self.clientsToServe:
            if self.orderByClient[otherClient] == self.orderByClient[client]:
              reassignClient = otherClient
          if reassignClient is not None:
            self.clientsToServe.remove(reassignClient)
            self.hasPrepare[reassignClient] = True
            self.sendOrderTime[reassignClient] = self.sendOrderTime[client]
            logging.debug('Sushi ' + self.orderByClient[client].name + ' reassigned for client ' + str(reassignClient) + '.')
          else:
            logging.debug('Free sushi ' + self.orderByClient[client].name + '!')
        self.wasEating[client] = False
        self.hasPrepare[client] = False
        del self.orderByClient[client]
        if client in self.clientsToServe:
            self.clientsToServe.remove(client)
        self.sendOrderTime[client] = None
        logging.debug('Client ' + str(client) + ' left.')
        self.removePlate(client)

    for client in range(self.nbClients):
      if isPresent[client]:
        if not self.wasPresent[client]:
          self.stats.nbClients += 1
        self.wasPresent[client] = True
        if isEating[client]:
          if not self.wasEating[client]:
            self.stats.nbClientsServed += 1
          self.wasEating[client] = True
          if self.hasPrepare[client]:
            # Client is eating their order.
            continue
          # Client is a thief and is eating someone else order!
          if client in self.orderByClient:
            thiefOrder = self.orderByClient[client]
          else:
            thiefOrder = self.inferThiefOrder(client, isEating)
            if thiefOrder is not None:
              logging.debug('  Infered thief order: ' + thiefOrder.name + '.')
              self.orderByClient[client] = thiefOrder

          hasFoundVictim = False
          if thiefOrder is not None:
            for victim in reversed(range(client + 1, self.nbClients)):
              if self.hasPrepare[victim] and not isEating[victim] and self.orderByClient[victim] == thiefOrder:
                self.hasPrepare[victim] = False
                hasFoundVictim = True
                break
          if hasFoundVictim:
            logging.debug('  Client ' + str(client) + ' is a thief! They stole client ' + str(victim) + '\'s order.')
          elif thiefOrder is not None:
            logging.debug('  Client ate ' + thiefOrder.name + ' and it was probably left over.')
          else:
            logging.debug('  Client ' + str(client) + ' ate something.')

          if client in self.clientsToServe:
            self.clientsToServe.remove(client)
          self.hasPrepare[client] = True
        else:
          if self.hasPrepare[client] or client in self.clientsToServe:
            # Order is already taken or sent.
            continue
          logging.debug('Take order of client ' + str(client))
          # Take order.
          self.clientsToServe.append(client)
          # The furthest client has priority. Their order takes more time to reach them and may be stolen by others.
          self.clientsToServe.sort(reverse=True)
          if client not in self.orderByClient:
            self.orderByClient[client] = self.getOrder(client)
      elif self.wasPresent[client]:
        self.wasPresent[client] = False
        if self.wasEating[client]:
          self.kitchen.money += self.orderByClient[client].price
        self.wasEating[client] = False
        self.hasPrepare[client] = False
        del self.orderByClient[client]
        if client in self.clientsToServe:
            self.clientsToServe.remove(client)
        logging.debug('Client ' + str(client) + ' left.')
        self.removePlate(client)

  def getOrder(self, client: int) -> Sushi:
    imageHash = self.recognizer.executeImageHash('client' + str(client))
    order = Sushi.ONIGIRI
    minScore = 1000000
    for sushi in Sushi:
      score = self.recognizer.executeCompareImageHash(sushi.actionId, imageHash=imageHash)
      if score < minScore:
        minScore = score
        order = sushi
    logging.debug('  Client ' + str(client) + ' wants ' + order.name)
    return order

  def inferThiefOrder(self, thief: int, isEating: list[bool]) -> Sushi | None:
    victimByOrder = {}
    for victim in reversed(range(thief + 1, self.nbClients)):
      if isEating[victim] or not self.hasPrepare[victim] or victim not in self.orderByClient \
          or self.orderByClient[victim] in victimByOrder:
        continue
      victimByOrder[self.orderByClient[victim]] = victim
    if len(victimByOrder) == 0:
      return None
    if len(victimByOrder) == 1:
      return list(victimByOrder.keys())[0]
    thiefDuration = 5 + thief * 3
    minDiff = 1000000
    mostLikelyOrder = None
    for order, victim in victimByOrder.items():
      duration = time.time() - self.sendOrderTime[victim]
      diff = abs(thiefDuration - duration)
      if diff < minDiff:
        minDiff = diff
        mostLikelyOrder = order
    return mostLikelyOrder

  def removePlate(self, client: int) -> None:
    self.recognizer.executeClick('removePlate' + str(client))

  async def sendOrders(self) -> None:
    while True:
      if self.doesStop:
        return
      while len(self.clientsToServe) > 0:
        client = self.clientsToServe[0]
        order = self.orderByClient[client]

        # If another client is before the target client and has the same order, they need to be served first so
        # as to serve the target client as fast as possible.
        for otherClient in self.clientsToServe:
          if otherClient >= client:
            continue
          if self.orderByClient[otherClient] == order:
            client = otherClient
        await self.sendOrder(order, client)
        # Let order manager have some work.
        await asyncio.sleep(0.01)
      await asyncio.sleep(0.5)

  async def sendOrder(self, order, client: int) -> None:
    if not self.kitchen.canMakeOrder(order):
      await asyncio.sleep(0.5)
      return
    if not self.recognizer.executeIsSamePixelColor('canMakeSushi'):
      await asyncio.sleep(0.5)
      return
    self.kitchen.makeOrder(order)
    self.recognizer.executeClick('sendSushi')
    self.sendOrderTime[client] = time.time()
    self.hasPrepare[client] = True
    self.clientsToServe.remove(client)
    self.stats.nbByOrder[order] += 1
    logging.debug('Made sushi ' + order.name + ' for client ' + str(client) + '.')

  async def buyIngredients(self) -> None:
    while True:
      if self.doesStop:
        return
      orders = self.getAllPendingOrders()
      await self.kitchen.buyIngredients(orders)
      await asyncio.sleep(0.5)

  def getAllPendingOrders(self) -> list[Sushi]:
    orders: list[Sushi] = []
    for client in self.clientsToServe:
      orders.append(self.orderByClient[client])
    return orders

def main():
  logging.basicConfig(format='%(levelname)s-%(asctime)s: %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)
  bot = Bot()
  bot.run()
  # bot.runOneDay()

if __name__ == '__main__':
  main()
