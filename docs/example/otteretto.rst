Otteretto
=========

The code is available at
`https://github.com/fab5code/guirecognizer/tree/main/examples/otteretto <https://github.com/fab5code/guirecognizer/tree/main/examples/otteretto>`_
and includes instructions to run the bot. The bot plays the game automatically.

Let's explain how to retrieve game information using screen pixels.

What is Otteretto?
------------------

`Otteretto <https://otteretto.app/classic/>`_ is a game about palindromes. Blocks of different colors are arranged on a grid of 4 by 10.
The goal is to find palindromes of colored blocks inside the grid. Larger palindromes award more points.

.. figure:: /_static/examples/otteretto/gridExample.webp
   :alt: Example of the grid.
   :width: 50%
   :align: center

   Example of the grid.

Retrieve the grid values from the screen
----------------------------------------

Let's create a Python script to retrieve grid information from the screen using guirecognizer.

Create the bot configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install *guirecognizerapp* (it will also install *guirecognizer*)

.. code-block:: console

  (venv) $ pip install guirecognizerapp

Launch the app.

.. code-block:: console

  (venv) $ python -m guirecognizerapp

In parallel open `https://otteretto.app/classic/ <https://otteretto.app/classic/>`_. Play or skip the tutorial until the game with the grid starts.

In *guirecognizerapp* take a screenshot of the game: *Capture -> Take Screenshot* or shortcut *Ctrl+Alt+T*.

Then define the borders, which represent the absolute coordinates of the screen portion used as a reference to define all actions.

.. figure:: /_static/examples/otteretto/setBorders1.webp
   :alt: Setting the borders instructions: click on borders button.
   :width: 80%
   :align: center

   Click on the button to set the borders.

.. figure:: /_static/examples/otteretto/setBorders2.webp
   :alt: Setting the borders instructions: select the screen portion.
   :width: 80%
   :align: center

   Select the screen portion. It's also possible to select the whole screenshot.

To retrieve the grid information we need to know where the grid is.
Let's add three actions to retrieve the coordinates of the grid at the top-left, top-right, and bottom-left corners.

Add a *Get Coordinates* action: *Manage Actions -> Add Action Get Coordinates*.
Name it *topLeft* and make the action selection. Select the point at the top left of the grid with some offset from the grid frame.
Try to select a point near the top-left corner of where a colored block appears.

.. figure:: /_static/examples/otteretto/getCoordinates1.webp
   :alt: Click on the button to make the action selection.
   :width: 80%
   :align: center

   Click on the button to make the action selection.

.. figure:: /_static/examples/otteretto/getCoordinates2.webp
   :alt: Select the point at the top left of the grid.
   :width: 80%
   :align: center

   Select the point at the top left of the grid.

Do the same for the top-right and bottom-left corners, again selecting a point near where a colored block appears.

Save the file *otterettoConfig.json* in your project folder: *File -> Save* or *Ctrl+S*.

Loop through the grid blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a python file *bot.py*. Use the *guirecognizer* class :ref:`Recognizer <api-recognizer-class>` to load the configuration file.

Check that the action called *topLeft*, defined earlier, is working correctly.

.. code-block:: python
  :linenos:

  from guirecognizer import Recognizer

  recognizer = Recognizer('otterettoConfig.json')
  topLeft = recognizer.executeCoordinates('topLeft')
  print('Top left coord:', topLeft)

.. code-block:: console

   Top left coord: (752, 310)

We are going to loop through each block of the grid and retrieve the pixel color. First, test retrieving the color of a specific pixel on the screen.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer('otterettoConfig.json')
  pixelColor = recognizer.executePixelColor(ActionType.PIXEL_COLOR, coord=(752, 310))
  print(pixelColor)

.. code-block:: console

   (42, 63, 148)

Here is the code that loops through the grid blocks and retrieves the color of each one.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer('otterettoConfig.json')
  width = 4
  height = 10
  topLeft = recognizer.executeCoordinates('topLeft')
  topRight = recognizer.executeCoordinates('topRight')
  bottomLeft = recognizer.executeCoordinates('bottomLeft')
  xGap = abs(topRight[0] - topLeft[0]) / (width - 1)
  yGap = abs(bottomLeft[1] - topLeft[1]) / (height - 1)
  for x in range(width):
    for y in range(height):
      coord = (int(bottomLeft[0] + x * xGap), int(bottomLeft[1] - y * yGap))
      pixelColor = recognizer.executePixelColor(ActionType.PIXEL_COLOR, coord=coord)

However, to identify a block, we need to know its color. Let's extend the configuration file.

Identify the block colors
~~~~~~~~~~~~~~~~~~~~~~~~~

Using *guirecognizerapp* add a *Is Same Pixel Color* action for each of the five block types: *Manage Actions -> Add Action Is Same Pixel Color*.
For each action, name it then select on the screenshot a pixel corresponding to the color of the block.

.. figure:: /_static/examples/otteretto/identifyColor.webp
   :alt: Add actions Is Same Pixel Color to identify block colors.
   :width: 80%
   :align: center

   Add actions Is Same Pixel Color to identify block colors.

Now we can identify each block. The following code prints the full grid to the console.
Make sure the window with the game is displayed. You may want to add a sleep command at the start of script if you need the time to display the game window.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer('otterettoConfig.json')
  width = 4
  height = 10
  topLeft = recognizer.executeCoordinates('topLeft')
  topRight = recognizer.executeCoordinates('topRight')
  bottomLeft = recognizer.executeCoordinates('bottomLeft')
  xGap = abs(topRight[0] - topLeft[0]) / (width - 1)
  yGap = abs(bottomLeft[1] - topLeft[1]) / (height - 1)
  for y in reversed(range(height)):
    line = ''
    for x in range(width):
      coord = (int(bottomLeft[0] + x * xGap), int(bottomLeft[1] - y * yGap))
      color = recognizer.executePixelColor(ActionType.PIXEL_COLOR, coord=coord)
      if recognizer.executeIsSamePixelColor('typeSquare', pixelColor=color):
        line += ' 🟦'
      elif recognizer.executeIsSamePixelColor('typeStar', pixelColor=color):
        line += ' 🟪'
      elif recognizer.executeIsSamePixelColor('typeCircle', pixelColor=color):
        line += ' 🟥'
      elif recognizer.executeIsSamePixelColor('typeTriangle', pixelColor=color):
        line += ' 🟩'
      elif recognizer.executeIsSamePixelColor('typeDiamond', pixelColor=color):
        line += ' 🟨'
      else:
        line += '  '
    print(line)

.. code-block:: console

   <empty>
   <empty>
   <empty>
   <empty>
   🟥 🟪 🟥 🟦
   🟪 🟨 🟥 🟪
   🟩 🟥 🟥 🟦
   🟩 🟪 🟥 🟪
   🟪 🟦 🟪 🟨
   🟨 🟦 🟨 🟦

Improve performance
~~~~~~~~~~~~~~~~~~~

At this point, each call to *recognizer.executePixelColor* retrieves screen information by calling the operating system's screen API.
The whole loop takes around a second. Instead, retrieve the entire borders portion of the screen once and extract pixel colors directly from this image.

To retrieve the borders portion of the screen, call :meth:`guirecognizer.Recognizer.getBordersImage`.
Then pass the image as a parameter of *recognizer.executePixelColor*.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer('otterettoConfig.json')
  width = 4
  height = 10
  topLeft = recognizer.executeCoordinates('topLeft')
  topRight = recognizer.executeCoordinates('topRight')
  bottomLeft = recognizer.executeCoordinates('bottomLeft')
  xGap = abs(topRight[0] - topLeft[0]) / (width - 1)
  yGap = abs(bottomLeft[1] - topLeft[1]) / (height - 1)
  bordersImage = recognizer.getBordersImage()
  for y in reversed(range(height)):
    line = ''
    for x in range(width):
      coord = (int(bottomLeft[0] + x * xGap), int(bottomLeft[1] - y * yGap))
      color = recognizer.executePixelColor(ActionType.PIXEL_COLOR, coord=coord, bordersImage=bordersImage)
      if recognizer.executeIsSamePixelColor('typeSquare', pixelColor=color):
        line += ' 🟦'
      elif recognizer.executeIsSamePixelColor('typeStar', pixelColor=color):
        line += ' 🟪'
      elif recognizer.executeIsSamePixelColor('typeCircle', pixelColor=color):
        line += ' 🟥'
      elif recognizer.executeIsSamePixelColor('typeTriangle', pixelColor=color):
        line += ' 🟩'
      elif recognizer.executeIsSamePixelColor('typeDiamond', pixelColor=color):
        line += ' 🟨'
      else:
        line += '  '
    print(line)

With this approach, execution time drops to about 0.3s instead of 1s.

What's next?
------------

Now that you have access to the grid information, you can try to write a solver to find the best palindrome.
*guirecognizer* does not help with this part.

You can try running a functional bot at
`https://github.com/fab5code/guirecognizer/tree/main/examples/otteretto <https://github.com/fab5code/guirecognizer/tree/main/examples/otteretto>`_.
It uses :meth:`MouseHelper.dragCoords` from the utility class :ref:`MouseHelper <api-mouse-helper>` to drag the mouse across blocks and select palindromes.
