Sushi Go Round
==============

The code is available at
`https://github.com/fab5code/guirecognizer/tree/main/examples/sushiGoRound <https://github.com/fab5code/guirecognizer/tree/main/examples/sushiGoRound>`_
and includes instructions to run the bot. The bot plays the game automatically.

Let's explain how to retrieve game information from screen pixels and handle game interactions using *guirecognizer*.

What is Sushi Go Round?
-----------------------

`Sushi Go Round <https://www.crazygames.com/game/sushi-go-round>`_ is a fast-paced restaurant management game where you prepare and serve sushi to customers before they lose patience.
You must assemble dishes according to orders while managing a limited stock of ingredients,
restocking supplies in time to keep the sushi bar running smoothly.

.. figure:: /_static/examples/sushiGoRound/game.webp
   :alt: In Sushi Go Round, you have up to six customers to server. Identify their orders, make sushi and manage the stock of ingredients.
   :width: 50%
   :align: center

   In Sushi Go Round, you have up to six customers to server. Identify their orders, make sushi and manage the stock of ingredients.

Why a bot about Sushi Go Round?
-------------------------------

When searching for tutorials about creating bots that interact with graphical user interfaces, the following
`article <https://code.tutsplus.com/tutorials/how-to-build-a-python-bot-that-can-play-web-games--active-11117>`_
often comes up. It is an old but still valuable tutorial that explains how to build a Python bot for this exact browser game, Sushi Go Round,
using low-level techniques such as manual screen analysis and hardcoded logic.

This example is in part a homage to that original post.
At the same time, revisiting Sushi Go Round provides a good opportunity to demonstrate how using *guirecognizer* simplifies the process today.
Compared to the original approach, *guirecognizer* allows building the same kind of bot in a way that is faster to implement, cleaner to maintain,
and more user-friendly, thanks to its visual configuration tool, reusable actions, and higher-level abstractions over screen recognition and input handling.

Identify the customer orders
----------------------------

When a customer arrives, a bubble appears above their head showing a specific sushi. Let's use *guirecognizerapp* to retrieve the drawing of the sushi
and identify it.

Create the bot configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install *guirecognizerapp* (it will also install *guirecognizer*)

.. code-block:: console

  (venv) $ pip install guirecognizerapp

Launch the app.

.. code-block:: console

  (venv) $ python -m guirecognizerapp

In parallel open `https://www.crazygames.com/game/sushi-go-round <https://www.crazygames.com/game/sushi-go-round>`_.
Play or skip the tutorial until the first day starts and six customers are present.

In *guirecognizerapp* take a screenshot of the game: *Capture -> Take Screenshot* or shortcut *Ctrl+Alt+T*.

Then define the borders, which represent the absolute coordinates of the screen portion used as a reference to define all actions.
Define the borders so that they cover exactly the game interface, without any black borders if present.

.. figure:: /_static/examples/sushiGoRound/setBorders.webp
   :alt: Define as borders the game interface.
   :width: 50%
   :align: center

   Define as borders the game interface.

Select customer orders
~~~~~~~~~~~~~~~~~~~~~~

Create a *Get Image Hash* action: *Manage Actions -> Add Action Get Image Hash* and select a rectangle around the bubble of the first customer.
Name the action *client0*.

.. figure:: /_static/examples/sushiGoRound/identifyOrder1.webp
   :alt: To retrieve the first customer order, select a rectangle inside its bubble.
   :width: 50%
   :align: center

   To retrieve the first customer order, select a rectangle inside its bubble.

Save the file *sushiGoRoundConfig.json* in your project folder: *File -> Save* or *Ctrl+S*.

With an image hash, two visually similar images have a small difference in their hashes.
We can use those hashes to identify the order of each customer.

Create again a *Get Image Hash* action for each of the five other customers.
Select a rectangle of the same size and around the same pixels relatively to each customer bubble.
Use the controls at the bottom of the screenshot tab to monitor with accuracy the width and height of the selection.
Name thoses actions *client1*, *client2*, *client3*, *client4* and *client5*.

Let's loop through the customers to retrieve their image hash.

.. code-block:: python
  :linenos:

  from guirecognizer import Recognizer

  recognizer = Recognizer('sushiGoRoundConfig.json')
  for i in range(6):
    imageHash = recognizer.executeImageHash(f'client{i}')
    print(i, imageHash)

.. code-block:: console

  0 abcc61339de163c1,06e00000000
  1 ac33666ccc99cccc,07600030000
  2 afcc6323cdc163c1,06e00000000
  3 bc33764ccc8ccccc,07600030000
  4 b4cc999933333366,07c00008000
  5 bbc86133cde163c1,06e00000000


Identify the orders
~~~~~~~~~~~~~~~~~~~

Create a *Get Compare Image Hash* action: *Manage Actions -> Add Action Compare Image Hash*.
It will be used to identify whether a customer's order is an onigiri. Name it *onigiri*.
You could try to select manually the same rectangle as the one used by a *client* action but it's easier to use the controls
at the bottom and select the same selection as one of the *client* actions.

.. figure:: /_static/examples/sushiGoRound/identifyOrder2.webp
   :alt: Select the same selection as one of the client actions that has an onigiri. In this screenshot, any of the actions client0, client2 and client5 works.
   :width: 50%
   :align: center

   Select the same selection as one of the *client* actions that has an onigiri. In this screenshot, any of the actions *client0*, *client2* and *client5* works.

Create two similar actions for the other two sushi types. Name them *californiaRoll* and *gunkanMaki*.

Let's loop through the customers to retrieve their order. A customer's order is identified as the sushi with the smallest hash difference.

.. code-block:: python
  :linenos:

  from guirecognizer import Recognizer

  recognizer = Recognizer('sushiGoRoundConfig.json')
  for i in range(6):
    imageHash = recognizer.executeImageHash(f'client{i}')
    minDiff = 10000
    order = None
    for compareAction in ['onigiri', 'californiaRoll', 'gunkanMaki']:
      diff = recognizer.executeCompareImageHash(compareAction, imageHash=imageHash)
      if diff < minDiff:
        minDiff = diff
        order = compareAction
    print(i, order)

On the following screenshot we have this console output. Every order is correct.

.. figure:: /_static/examples/sushiGoRound/identifyOrder3.webp
   :alt: The bot correctly identifies the orders of all six customers.
   :width: 50%
   :align: center

   The bot correctly identifies the orders of all six customers.

.. code-block:: console

  0 californiaRoll
  1 onigiri
  2 gunkanMaki
  3 californiaRoll
  4 gunkanMaki
  5 gunkanMaki

Make sushi
----------

Now that we know our customer orders, let's make sushi.

Create a *Click* action: *Manage Actions -> Add Click Action*. Select the rice ingredient. Name the action *rice*.

.. figure:: /_static/examples/sushiGoRound/makeSushi1.webp
   :alt: Select the rice ingredient.
   :width: 50%
   :align: center

   Select the rice ingredient.

Create two other click actions for nori and fish eggs. Name them *nori* and *fishEggs*.
Finally add an action to click on the mat to make the sushi. Name it *makeSushi*.

.. figure:: /_static/examples/sushiGoRound/makeSushi2.webp
   :alt: Add an action to click on the mat to make the sushi.
   :width: 50%
   :align: center

   Add an action to click on the mat to make the sushi.

Let's make the sushi for the first customer.

.. code-block:: python
  :linenos:

  from guirecognizer import Recognizer

  recognizer = Recognizer('sushiGoRoundConfig.json')
  imageHash = recognizer.executeImageHash('client0')
  minDiff = 10000
  order = None
  for compareAction in ['onigiri', 'californiaRoll', 'gunkanMaki']:
    diff = recognizer.executeCompareImageHash(compareAction, imageHash=imageHash)
    if diff < minDiff:
      minDiff = diff
      order = compareAction

  if order == 'onigiri':
    recognizer.executeClick('rice')
    recognizer.executeClick('rice')
    recognizer.executeClick('nori')
  elif order == 'californiaRoll':
    recognizer.executeClick('rice')
    recognizer.executeClick('nori')
    recognizer.executeClick('fishEggs')
  else:
    recognizer.executeClick('rice')
    recognizer.executeClick('nori')
    recognizer.executeClick('fishEggs')
    recognizer.executeClick('fishEggs')
  recognizer.executeClick('makeSushi')

From line 4 to 11 the order of the first customer is found. Then, starting at line 13, the bot makes the sushi inhumanly fast.

In this part of the bot, *guirecognizer* is particularly useful to manage many different elements to click on.

Managing the stock of ingredients
---------------------------------

Let's see how to refill rice when we run out.

Create a click action on the telephone to open the buy menu. Name it *buy*.

Take a screenshot and add another action to click on the rice item. Name it *buyRice1*.

.. figure:: /_static/examples/sushiGoRound/manageIngredients1.webp
   :alt: Add an action to click on the rice item.
   :width: 50%
   :align: center

   Add an action to click on the rice item.

Take another screenshot and add a third click action to confirm buying rice. Name it *buyRice2*.

.. figure:: /_static/examples/sushiGoRound/manageIngredients2.webp
   :alt: Add a click action to confirm buying rice.
   :width: 50%
   :align: center

   Add a click action to confirm buying rice.

Finally take another screenshot and add a fourth and last click action to confirm the delivery. Name it *delivery*.

Here is the code to buy some rice.

.. code-block:: python
  :linenos:

  from guirecognizer import Recognizer

  recognizer = Recognizer('sushiGoRoundConfig.json')
  recognizer.executeClick('buy')
  recognizer.executeClick('buyRice1')
  recognizer.executeClick('buyRice2')
  recognizer.executeClick('delivery')

You can extend the bot to handle buying the other ingredients and manage the stock.

Assembling the pieces together
------------------------------

The bot handles three independent tasks: identifying orders, making sushi and managing ingredients.
Those tasks can be done sequentially.
As an analogy, instead of having multiple employees each handling a single task, we have one employee multitasking.
This is why we are going to use the python library `asyncio <https://realpython.com/ref/stdlib/asyncio/>`_.

For the sake of this tutorial, here is only a skeleton illustrating the use of asyncio.

.. code-block:: python
  :linenos:

  import asyncio
  import time

  async def takeOrders():
    while True:
      print('Taking orders')
      time.sleep(1) # Simulate taking orders.
      await asyncio.sleep(0.5)

  async def makeSushi():
    while True:
      print('Making sushi')
      time.sleep(1.5) # Simulate making sushi.
      await asyncio.sleep(0.5)

  async def manageIngredients():
    while True:
      print('Managing ingredients')
      time.sleep(2.5) # Simulate managing ingredients.
      await asyncio.sleep(0.5)

  async def main():
    await asyncio.gather(takeOrders(), makeSushi(), manageIngredients())

  asyncio.run(main())

Here is a part of the console output.

.. code-block:: console

  Taking orders
  Making sushi
  Managing ingredients
  Taking orders
  Making sushi
  Managing ingredients
  Taking orders

The different functions can share a common state containing for instance the list of orders and the number of ingredients left.
Now you can replace the content of the functions *takeOrders*, *makeSushi* and *manageIngredients* and create your own bot.

What's next?
------------

To build a fully functional bot that can successfully play through a full day, you will probably need to:

- identify when a customer is present
- manage empty plates
- handle the case where one customer takes another customer's order
- make sure the sushi made has left the mat to make another one

You can try running a functional bot at
`https://github.com/fab5code/guirecognizer/tree/main/examples/sushiGoRound <https://github.com/fab5code/guirecognizer/tree/main/examples/sushiGoRound>`_.
