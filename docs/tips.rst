Tips and tricks
===============

Creating a bot based on screen pixels can sometimes feel a bit hacky.
Defining actions that are both reliable and efficient is not always straightforward:
small visual variations, noisy backgrounds, or performance constraints can easily lead to instability.
In addition, it is often impossible to test an action against every possible visual situation.

This section gathers practical tips and tricks drawn from real use cases.
They illustrate common problems encountered when interacting with graphical user interfaces
and show how *guirecognizer* can be used to mitigate them with simple but effective strategies.

.. contents:: In this section
   :local:
   :depth: 1

Noisy background color
----------------------

One action available in *guirecognizer* is to get the color of a pixel on screen.
It can be used to assess whether something is present or not on screen.
When the background is noisy, this strategy can still work by computing the average color over a screen area.

Let's take the following image as an example. It comes from the :doc:`bot example for cookie clicker <example/cookieClicker>`.

.. figure:: /_static/tips/noisyBackground1.webp
   :alt: Example of a noisy background. The colors for the highlighted game element are not uniform.
   :width: 50%
   :align: center

   Example of a noisy background. The colors for the highlighted game element are not uniform.

Here are two pixel colors for the highlighted game element. The lightness varies from *16%* to *40%*.

.. figure:: /_static/tips/noisyBackground2.webp
   :alt: Two pixel colors of the highlighted game element. The range of lightness is a bit wide.
   :width: 90%
   :align: center

   Two pixel colors of the highlighted game element. The range of lightness is a bit wide.

Here are two pixel colors for the non-highlighted game element. The lightness varies from *15%* to *35%*.
It overlaps with the range of lightness of the highlighted game element.

.. figure:: /_static/tips/noisyBackground3.webp
   :alt: Two pixel colors of the non-highlighted game element. The range of lightness overlaps with the previous one.
   :width: 90%
   :align: center

   Two pixel colors of the non-highlighted game element. The range of lightness overlaps with the previous one.

When using the average color of a screen area, we have a more stable color which can be used in comparison to know whether
the game element is highlighted or not.

.. figure:: /_static/tips/noisyBackground4.webp
   :alt: The average color over a screen area for both highlighted and non-highlighted elements.
   :width: 90%
   :align: center

   The average color over a screen area for both highlighted and non-highlighted elements.


Identify grid content
---------------------

It's quite common to have a grid of elements and we want to identify the content of the grid.
Even though creating a new action with :doc:`guirecognizerapp <app>` is easy, it would be cumbersome to create an action for each square of the grid.
Instead, the idea is to use two actions to mark the coordinates of the extremities of the grid.
From these two reference points, all grid cell positions can be computed programmatically.

Let's take the example of the game `2048 <https://play2048.co>`_.

.. figure:: /_static/tips/gridContent1.webp
   :alt: Example of a grid from the game 2048.
   :width: 50%
   :align: center

   Example of a grid from the game 2048.

Open the game in your browser at `https://play2048.co <https://play2048.co>`_ then take a screenshot in :doc:`guirecognizerapp <app>`.
Define the borders as the grid or the whole screenshot. Save the file *2048Config.json* in your project folder: *File -> Save* or *Ctrl+S*.

Create a *Get Coordinates* action: *Manage Actions -> Add Action Get Coordinates*.
Name it *topLeft*. Select a pixel in the top left part of the top left square.
The selected pixel should point to the background color and not the number inside the square, for any number possible.

.. figure:: /_static/tips/gridContent2.webp
   :alt: Selection of action topLeft.
   :width: 80%
   :align: center

   Selection of action *topLeft*.

Create another *Get Coordinates* action for the bottom right square. Name it *bottomRight*.
Select a pixel in the top left part of the bottom right square.

.. figure:: /_static/tips/gridContent3.webp
   :alt: Selection of action bottomRight.
   :width: 80%
   :align: center

   Selection of action *bottomRight*.

We can now loop through all the squares of the grid and retrieve the background color of each square.

.. code-block:: python
  :linenos:

   from guirecognizer import ActionType, Recognizer

   recognizer = Recognizer('2048Config.json')
   topLeft = recognizer.executeCoordinates('topLeft')
   bottomRight = recognizer.executeCoordinates('bottomRight')
   gridWidth = 4
   gridHeight = 4
   width = (bottomRight[0] - topLeft[0]) / (gridWidth - 1)
   height = (bottomRight[1] - topLeft[1]) / (gridHeight - 1)

   for y in range(gridHeight):
   line = ''
   for x in range(gridWidth):
    coord = (round(topLeft[0] + x  * width), round(topLeft[1] + y  * height))
    color = recognizer.executePixelColor(ActionType.PIXEL_COLOR, coord=coord)
    line += f'{color} '
   print(line)

.. code-block::

   (238, 228, 218) (247, 100, 67) (247, 127, 99) (235, 216, 182)
   (246, 148, 97) (242, 177, 120) (240, 210, 108) (243, 178, 120)
   (235, 216, 182) (238, 228, 218) (238, 228, 218) (190, 173, 152)
   (238, 228, 218) (189, 172, 152) (189, 173, 152) (190, 173, 152)

Now add a *Compare Pixel Color* action for each square type including the empty square: *Manage Actions -> Add Action Get Coordinates*.
For each action select the background color of the corresponding square. Name them *isEmpty*, *is2*, *is4* and so on.

.. figure:: /_static/tips/gridContent4.webp
   :alt: For action is4, select the background color of the square with the number 4.
   :width: 80%
   :align: center

   For action *is4*, select the background color of the square with the number *4*.

To identify the square, we compare the color retrieved with the one in reference of all actions *isEmpty*, *is2*, *is4*...
The one with the smallest difference is the right square type.

.. code-block:: python
  :linenos:
  :emphasize-lines: 18, 22

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer('2048Config.json')
  topLeft = recognizer.executeCoordinates('topLeft')
  bottomRight = recognizer.executeCoordinates('bottomRight')
  gridWidth = 4
  gridHeight = 4
  width = (bottomRight[0] - topLeft[0]) / (gridWidth - 1)
  height = (bottomRight[1] - topLeft[1]) / (gridHeight - 1)

  compareActions = ['isEmpty', 'is2', 'is4', 'is8', 'is16', 'is32', 'is64', 'is128']
  squareTypes = ['   _', '   2', '   4', '   8', '  16', '  32', '  64', ' 128']

  for y in range(gridHeight):
  line = ''
  for x in range(gridWidth):
    coord = (round(topLeft[0] + x  * width), round(topLeft[1] + y  * height))
    color = recognizer.executePixelColor(ActionType.PIXEL_COLOR, coord=coord)
    squareType = None
    minDiff = 10000
    for i in range(len(compareActions)):
      diff = recognizer.executeComparePixelColor(compareActions[i], pixelColor=color)
      if diff < minDiff:
      minDiff = diff
      squareType = squareTypes[i]
    line += f'{squareType} '
  print(line)

.. code-block:: console

     2   64   32    4
    16    8  128    8
     4    2    2    _
     2    _    _    _

The identified square types are correct.
Line 22 shows how to compare the retrieved color with the reference color of the associated action.

Every time we retrieve the color on line 18, the pixel color on screen is retrieved by calling the operating system's screen API.
It's inefficient.
Instead, retrieve the borders portion of the screen once using :meth:`guirecognizer.Recognizer.getBordersImage`,
so the screen API is called only a single time.
Then pass the image as a parameter of *recognizer.executeComparePixelColor*.

.. code-block:: python

  borders = recognizer.getBordersImage()
  for y in range(gridHeight):
    line = ''
    for x in range(gridWidth):
      ...
      color = recognizer.executePixelColor(ActionType.PIXEL_COLOR, coord=coord, bordersImage=borders)
      ...

With this approach, execution time drops to about 30ms instead of 500ms.


Estimating the number of health points from a health bar
--------------------------------------------------------

Let's take as an example the game Pokémon Ruby. Each Pokémon has health points. In our bot we want to know how much health has our Pokémon.

Let's use the following screenshot of the game. Our Pokémon health status is on the right. We can read it has *8* health points left.
There is also a health bar visually representing how much health it has left.

.. figure:: /_static/tips/healthBar1.webp
   :alt: Screenshot of a battle in the game Pokémon. We want to recognize how much health our Pokémon (at the bottom) has left.
   :width: 80%
   :align: center

   Screenshot of a battle in the game Pokémon. We want to recognize how much health our Pokémon (at the bottom) has left.

We could first try to use an action to recognize the number *8* (:ref:`API section Number <api-action-number>`). Here are some drawbacks:

- In game interfaces the health points are often written in a very small font and in front of stylized background.
  As a result, it is sometimes hard for OCRs to retrieve the number.
  Some :ref:`preprocessing <api-preprocessing>` may drastically improve the performance.
- The action may lack reliability because the OCR may recognize a specific number but not another. It may not be possible to test all numbers.
- The time it takes for the OCR to execute may be unacceptable.
  It can take half a second just to retrieve the health points. This can slow down the bot significantly if the action needs to be executed frequently.

Instead of recognizing the number of health points, let's use the health bar. It assumes the bot does not need the exact number of health points
but only an estimation. We can use the average color of the health bar to compute by how much the health bar is filled.
Then if we already know the maximum number of health points of our Pokémon, we can estimate the number of health points.
If we don't have the maximum number of health points, maybe the bot only needs the percentage of health points left.

Open the screeenshot in :doc:`guirecognizerapp <app>`.
Create a *Get Pixel Color* action: *Manage Actions -> Add Action Get Pixel Color*.
Name it *healthBar*. Select a rectangle covering the whole inside of the health bar.

.. figure:: /_static/tips/healthBar2.webp
   :alt: Select the inside of the health bar to get its average color.
   :width: 80%
   :align: center

   Select the inside of the health bar to get its average color.

To compute the fill percentage of the health bar, we need to process the image first.
Create a new operation: *Preprocess -> Add Operation*. Name it *threshold*. Click on the edit button of the operation.
Then add a suboperation *Threshold*: *Preprocess -> Add Suboperation -> Threshold*.

Preview the preprocessing operation in the tab *Suboperations* by selecting your action *healthBar* in the dropdown *Preview preprocessing operation*.

.. figure:: /_static/tips/healthBar3.webp
   :alt: Preview of the operation threshold on the selection of the action healthBar.
   :width: 80%
   :align: center

   Preview of the operation *threshold* on the selection of the action *healthBar*.

The preprocessed image is in black and white. Its average color is a shade of grey that represents by how much the health bar is filled.

Let's preview the action *healthBar* (the eye icon in front of the action in the tab *Actions*). Then select the operation *threshold* in the dropdown *Preprocess*.

.. figure:: /_static/tips/healthBar4.webp
   :alt: Preview of the action healthBar with the preprocessing operation threshold.
   :width: 80%
   :align: center

   Preview of the action *healthBar* with the preprocessing operation *threshold*.

The average color is a shade of grey. Its value is *91*. Black value is *0*. White value is *255*. If the health bar was full, its color would be fully white.
If the health bar was empty, its color would be fully black. So we can compute the fill percentage of the health bar by dividing by *255*.
Here the bar is filled at :code:`91 / 255 ≃ 36%`. The maximum number of health points is *22* so our estimation of the number of health points
is :code:`22 * 0.36 ≃ 8`. Our estimation is exactly right.

To use the action in the bot, save the configuration file *healthBarConfig.json* in your project folder: *File -> Save* or *Ctrl+S*.
Here is the bot code.

.. code-block:: python
  :linenos:

  from guirecognizer import Recognizer

  recognizer = Recognizer('healthBarConfig.json')
  color = recognizer.executePixelColor('healthBar', preprocessing='threshold')
  ratio = color[0] / 255
  maxHp = 22
  hp = round(ratio * maxHp)
  print(f'Ratio: {round(ratio * 100)}%  HP: {hp}')

.. code-block:: console

  Ratio: 36%  HP: 8
