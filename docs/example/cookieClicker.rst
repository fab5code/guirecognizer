Cookie Clicker
==============

The code is available at
`https://github.com/fab5code/guirecognizer/tree/main/examples/cookieClicker <https://github.com/fab5code/guirecognizer/tree/main/examples/cookieClicker>`_
and includes instructions to run the bot. The bot plays the game automatically.

Let's explain how *guirecognizer* is used to handle different parts of the gameplay.

What is Cookie Clicker?
-----------------------

`Cookie Clicker <https://orteil.dashnet.org/cookieclicker/>`_ is an idle game where you click to bake cookies and use them to buy upgrades that automatically produce even more cookies over time.

Continuously click on the cookie
--------------------------------

Let's start with the most basic action: clicking the big cookie.

Create the bot configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install *guirecognizerapp* (it will also install *guirecognizer*)

.. code-block:: console

  (venv) $ pip install guirecognizerapp

Launch the app.

.. code-block:: console

  (venv) $ python -m guirecognizerapp

In parallel open `https://orteil.dashnet.org/cookieclicker/ <https://orteil.dashnet.org/cookieclicker/>`_.

In *guirecognizerapp* take a screenshot of the game: *Capture -> Take Screenshot* or shortcut *Ctrl+Alt+T*.

Then define the borders, which represent the absolute coordinates of the screen portion used as a reference to define all actions.
Define the borders so that it takes exactly the whole game interface without the top header with the settings like *Change Language*
or just select the whole screenshot.

.. figure:: /_static/examples/cookieClicker/setBorders.webp
   :alt: Set as borders the relevant part of the screen or just select the whole screenshot.
   :width: 80%
   :align: center

   Set as borders the relevant part of the screen or just select the whole screenshot.

To click on the cookie add a *Click* action: *Manage Actions -> Add Action Click*.
Name it *cookie* and make the action selection. Select the big cookie on the left.

.. figure:: /_static/examples/cookieClicker/clickCookie.webp
   :alt: Select where to click on screen for the new action *cookie*.
   :width: 80%
   :align: center

   Select where to click on screen for the new action *cookie*.

Save the file *cookieClickerConfig.json* in your project folder: *File -> Save* or *Ctrl+S*.

Python script
~~~~~~~~~~~~~

Create a Python file *bot.py*. Use the *guirecognizer* class :ref:`Recognizer <api-recognizer-class>` to load the configuration file.

Let's click on the cookie.

.. code-block:: python
  :linenos:

  from guirecognizer import Recognizer

  recognizer = Recognizer('cookieClickerConfig.json')
  recognizer.executeClick('cookie')

You may want to add a delay if you are using only one screen, to allow time to bring the game window to the foreground after launching the bot.

.. code-block:: python
  :linenos:
  :emphasize-lines: 1, 4

  import time
  from guirecognizer import Recognizer

  time.sleep(5)
  recognizer = Recognizer('cookieClickerConfig.json')
  recognizer.executeClick('cookie')

Run the bot. It makes one tiny click. It's possible to adjust with the options *nbClicks* and *clickPauseDuration*
the number of clicks and the duration between them. Some games don't register multiple clicks when done too fast.

.. code-block:: python
  :linenos:
  :emphasize-lines: 4

  from guirecognizer import Recognizer

  recognizer = Recognizer('cookieClickerConfig.json')
  recognizer.executeClick('cookie', clickPauseDuration=0.025, nbClicks=20)

Run the bot. You probably got the achievement *Uncanny clicker* from the game for clicking inhumanly fast.

Buying buildings
----------------

At this point, the bot behaves like an auto-clicker, but it can do much more. To gain more cookies it's important to buy upgrades and
especially the buildings listed on the right.

.. figure:: /_static/examples/cookieClicker/buildingList.webp
   :alt: List of the upgrades to produce more cookies, called *buildings* in this tutorial. More appear when some are unlocked.
   :width: 50%
   :align: center

   List of the upgrades to produce more cookies, called *buildings* in this tutorial. More appear when some are unlocked.

Map the buildings on screen
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each building type is highlighted when it is possible to buy another one. Otherwise, it is greyed out.
Let's find where each building ui element is on the screen.

Create a *Get Coordinates* action: *Manage Actions -> Add Action Get Coordinates* that points at the top of the first building.
Name this action *buildingTop*.

.. figure:: /_static/examples/cookieClicker/mapBuilding1.webp
   :alt: Select a point at the top of the first building ui element.
   :width: 80%
   :align: center

   Select a point at the top of the first building ui element.

Create another *Get Coordinates* action that selects the height of a building ui element. Name this action *buildingHeight*.

.. figure:: /_static/examples/cookieClicker/mapBuilding2.webp
   :alt: Select the height of a building ui element.
   :width: 80%
   :align: center

   Select the height of a building ui element.

Of course you could hardcode those values but this is one reason to use *guirecognizerapp* and a config file.
Moreover, if the bot needs to be adapted to another screen, only the borders will need to change, along with some minor tweaks.

We can now compute the screen coordinates of all buildings.

.. code-block:: python
  :linenos:

  from guirecognizer import Recognizer

  recognizer = Recognizer('cookieClickerConfig.json')
  nbBuildingsInScreen = 9
  buildingCoords = []
  topCoord = recognizer.executeCoordinates('buildingTop')
  coord = recognizer.executeCoordinates('buildingHeight')
  height = coord[3] - coord[1]
  for i in range(nbBuildingsInScreen):
    coord = (topCoord[0], int(topCoord[1] + i * height))
    buildingCoords.append(coord)
  print(buildingCoords)

.. code-block:: console

   [(1826, 362), (1826, 442), (1826, 522), (1826, 602), (1826, 682), (1826, 762), (1826, 842), (1826, 922), (1826, 1002)]

Assess whether a building can be bought
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We could look at the pixel color of the screen coordinate of each building and compare it to a value to know whether the building is highlighted
meaning it can be bought or not. In practice, the building texture contains color variations. So a more stable solution is to get the average color of
a screen portion of the building ui element.

Create a *Compare Pixel Color* action: *Manage Actions -> Add Action Compare Pixel Color* and select a rectangle starting at the same point of
the previous action *buildingTop* with 50 pixel width and 10 pixel height. Name it *buildingAvailableDiff*.

.. figure:: /_static/examples/cookieClicker/canBuyBuilding1.webp
   :alt: Select the area for the *Compare Pixel Color* action.
   :width: 80%
   :align: center

   Select the area for the *Compare Pixel Color* action.

Create another action called *buildingUnavailableDiff*. For instance buy the first building until it's unavailable, take a screenshot,
then select the same area of *buildingAvailableDiff*. It's possible to select the same area as another action in the controls of the
screenshot tab.

.. figure:: /_static/examples/cookieClicker/canBuyBuilding2.webp
   :alt: Select the area for the *Compare Pixel Color* action to test when a building cannot be bought.
   :width: 80%
   :align: center

   Select the area for the *Compare Pixel Color* action to test when a building cannot be bought.

Let's find out in the bot for each building if it can be bought.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer('cookieClickerConfig.json')
  nbBuildingsInScreen = 9
  buildingCoords = []
  topCoord = recognizer.executeCoordinates('buildingTop')
  coord = recognizer.executeCoordinates('buildingHeight')
  height = coord[3] - coord[1]
  for i in range(nbBuildingsInScreen):
    coord = (topCoord[0], int(topCoord[1] + i * height))
    buildingCoords.append(coord)

  canBuy = []
  for coord in buildingCoords:
    pixels = (coord[0], coord[1], coord[0] + 50, coord[1] + 10)
    color = recognizer.executePixelColor(ActionType.PIXEL_COLOR, coord=pixels)
    availableDiff = recognizer.executeComparePixelColor('buildingAvailableDiff', pixelColor=color)
    unavailableDiff = recognizer.executeComparePixelColor('buildingUnavailableDiff', pixelColor=color)
    canBuy.append(availableDiff < unavailableDiff)
  print(canBuy)

Here is the result when this is the state of the game.

.. figure:: /_static/examples/cookieClicker/canBuyBuilding3.webp
   :alt: Select the area for the *Compare Pixel Color* action.
   :width: 50%
   :align: center

   Select the area for the *Compare Pixel Color* action.

.. code-block:: console

  [True, True, False, False, False, False, False, False, False]

Then the bot can decide whether to buy any of the available ones but the logic is up to you.

Here is how to buy a building.

.. code-block:: python

  recognizer.executeClick(ActionType.CLICK, coord=buildingCoords[1])

The golden cookie
-----------------

Golden cookies appear randomly on the screen and provide significant bonuses to cookie production.
Detecting them makes the bot a lot more efficient.

.. figure:: /_static/examples/cookieClicker/goldenCookie1.webp
   :alt: A golden cookie.
   :width: 80%
   :align: center

   A golden cookie.

Simple approach
~~~~~~~~~~~~~~~

Golden cookies appear randomly and don't appear often at the start of the game.
Automating rare events like this one is difficult to test. Wait until a golden cookie appear and take a screenshot of it.

Create a *Find Coordinates of Images Inside Area* action: *Manage Actions -> Add Action Find Coordinates of Images Inside Area*. Name it *findGolden*.
It will try to find a specific image inside the selected area. Select the same area as the borders to search for golden cookies inside the whole game
interface. Then select as the image to find a rectangle contained inside the golden cookie.

.. figure:: /_static/examples/cookieClicker/goldenCookie2.webp
   :alt: Select the image to find as to search for golden cookies.
   :width: 80%
   :align: center

   Select the image to find so as to search for golden cookies.

You can also increase the image hash threshold in the parameters of the action to the value 10 to better identify similar but different golden cookies.
You can also increase the number of subimages to allow finding multiple golden cookies at once.

With *guirecognizerapp* you can preview any action on the current screenshot. Preview the new action *findGolden*.

.. figure:: /_static/examples/cookieClicker/goldenCookie3.webp
   :alt: Preview action findGolden.
   :width: 80%
   :align: center

   Preview action *findGolden*.

If you are using the same screenshot where you defined the image to find, it should find it.
The performance of the search algorithm depends on the size of the search area and the size of the image to find.
It's faster when the search area is small and when the image to find is big.

In the Python bot, search for the coordinates of golden cookies then click on them if any.

.. code-block:: python
  :linenos:

  coords = recognizer.executeFindImage('findGolden')
  for coord in coords:
    center = (int((coord[0] + coord[2]) / 2), int((coord[1] + coord[3]) / 2))
    recognizer.executeClick(ActionType.CLICK, coord=center)

Improve performance
~~~~~~~~~~~~~~~~~~~

After the first call (which warms up the server) it takes in the example of this tutorial around *400ms* to search for golden cookies.
Since golden cookies have different size, you may need to create other actions and/or use the parameters min and max size ratios meaning
efficiently searching for golden cookies takes a lot of time. But golden cookies don't stay on the screen for a long time so it may be
interesting to improve the performance of the search.

A way to improve the performance is to reduce the search area by applying a preprocessing operation to the screenshot.

Create a new operation: *Preprocess -> Add Operation*. Name it *golden*. Click on the edit button of the operation.
Then add a suboperation *Resize*: *Preprocess -> Add Suboperation -> Resize*. Let's resize by fixing the width to 200 pixels.

.. figure:: /_static/examples/cookieClicker/goldenCookie4.webp
   :alt: Create a preprocessing operation to resize the screenshot.
   :width: 80%
   :align: center

   Create a preprocessing operation to resize the screenshot.

Then adapt the action *findGolden*. Reselect the image to find on the screeenshot but first apply the preprocessing *golden* from the controls
at the bottom of the screenshot tab.

.. figure:: /_static/examples/cookieClicker/goldenCookie5.webp
   :alt: Reselect the image to find.
   :width: 80%
   :align: center

   Reselect the image to find.

Finally preview again the action *findGolden* and select the preprocessing *golden*. The performance in this example has improved from *400ms* to *33ms*.

.. figure:: /_static/examples/cookieClicker/goldenCookie6.webp
   :alt: Preview findGolden with preprocessing golden. The search performance has improved.
   :width: 80%
   :align: center

   Preview *findGolden* with preprocessing *golden*. The search performance has improved.

In the Python bot:

.. code-block:: python

  coords = recognizer.executeFindImage('findGolden', preprocessing='golden')

Assembling the pieces together
------------------------------

The bot handles three independent tasks: clicking on the cookie, managing updates and finding golden cookies.
Since at least clicking on the cookie and searching golden cookies are full time jobs, multiple processes are necessary.
As an analogy, instead of one employee multitasking, we assign one employee to each task.
This is why we are going to use the Python library `multiprocessing <https://realpython.com/ref/stdlib/multiprocessing/>`_.

We are going to spawn one process for each task then wait for them to finish. They are multiple processes but only one mouse.
So we are going to use a *multiprocessing.Lock* to handle the mouse between the tasks.

Here is the full code example.

.. code-block:: python
  :linenos:

  import multiprocessing as mp
  import time
  from multiprocessing.synchronize import Lock

  def clickCookie(mouseLock: Lock) -> None:
    while True:
      mouseLock.acquire()
      print('click for 1s')
      time.sleep(1) # Simulate clicking continuously on the big cookie.
      mouseLock.release()

  def manageUpdates(mouseLock: Lock) -> None:
    while True:
      time.sleep(5) # Simulate assessing if any update should be bought and waiting.
      mouseLock.acquire()
      print('manage updates') # Simulate clicking on the building to buy.
      mouseLock.release()

  def findGolden(mouseLock: Lock) -> None:
    while True:
      time.sleep(12) # Simulate searching for golden cookies with action findGolden until one is find.
      mouseLock.acquire()
      print('find golden') # Simulate clicking on the found golden cookie.
      mouseLock.release()

  def main() -> None:
    mouseLock = mp.Lock()
    processes = []
    args = (mouseLock,)
    processes.append(mp.Process(target=clickCookie, args=args))
    processes.append(mp.Process(target=manageUpdates, args=args))
    processes.append(mp.Process(target=findGolden, args=args))
    for process in processes:
      process.start()
    for process in processes:
      process.join()

  if __name__ == '__main__':
    main()

For the sake of this tutorial each task is simulated with *time.sleep*.

On lines 30, 31, and 32, a new process is created for each task. Line 36 is essential to wait for each process to finish.

You can stop the bot with Ctrl+C or implement a cleaner way to stop it with *multiprocessing.Event* for instance.

Here is a part of the console output.

.. code-block:: console

  click for 1s
  click for 1s
  click for 1s
  click for 1s
  click for 1s
  manage updates
  click for 1s
  click for 1s
  click for 1s
  click for 1s
  click for 1s
  manage updates
  click for 1s
  click for 1s
  find golden
  click for 1s

Now you can replace the content of the functions *clickCookie*, *manageUpdates* and *findGolden* and create a functional bot.

What's next?
------------

You can extend the bot by buying upgrades, supporting more than the first buildings, fine tune the golden cookie detection and more.

You can try running a functional bot at
`https://github.com/fab5code/guirecognizer/tree/main/examples/cookieClicker <https://github.com/fab5code/guirecognizer/tree/main/examples/cookieClicker>`_.
