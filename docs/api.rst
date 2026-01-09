APIs
====

.. currentmodule:: guirecognizer

The :ref:`Recognizer <api-recognizer-class>` class operates on a list of actions defined in a configuration. Each action can then be executed using :meth:`Recognizer.execute`.
Different actions exist, mainly to retrieve information from screen pixels or to interact with the screen.
Actions can be piped together :ref:`piped together <api-pipe-actions>` and the screen area can be :ref:`preprocessed <api-preprocessing>`.

Actions
-------

ActionType defines the different kinds of operations that can be performed on screen data or user input.

.. autoclass:: guirecognizer.ActionType
  :members: COORDINATES, SELECTION, FIND_IMAGE, CLICK, PIXEL_COLOR, COMPARE_PIXEL_COLOR, IS_SAME_PIXEL_COLOR,
    IMAGE_HASH, COMPARE_IMAGE_HASH, IS_SAME_IMAGE_HASH, TEXT, NUMBER

Even though the following examples define an action by giving a valid configuration using :class:`guirecognizer.recognizer.RecognizerData`,
it's best to create a configuration file with :doc:`guirecognizerapp <app>` because the companion app helps create and preview actions.

Coordinates
~~~~~~~~~~~

Actions of type :attr:`ActionType.COORDINATES` return absolute screen coordinates computed from the action ratios and the defined borders.

From a point:

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer({'borders': (0, 0, 50, 50), 'actions': [{'id': 'coord',
      'type': ActionType.COORDINATES, 'ratios': (0.5, 0.5)}]})
  coord = recognizer.executeCoordinates('coord')
  print(coord)

.. code-block:: console

  (25, 25)

From an area selection:

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer({'borders': (0, 0, 50, 50), 'actions': [{'id': 'coord',
      'type': ActionType.COORDINATES, 'ratios': (0.2, 0.4, 0.6, 0.8)}]})
  coord = recognizer.executeCoordinates('coord')
  print(coord)

.. code-block:: console

  (10, 20, 30, 40)

Selection
~~~~~~~~~

Actions of type :attr:`ActionType.SELECTION` return either the color of a selected pixel (for point selections)
or a `PIL.Image.Image <https://pillow.readthedocs.io/en/stable/reference/Image.html>`_ (for area selections).

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer({'borders': (0, 0, 50, 50), 'actions': [{'id': 'point',
      'type': ActionType.SELECTION, 'ratios': (0.5, 0.5)}]})
  color = recognizer.executeSelection('point')
  print(color)

.. code-block:: console

  (218, 213, 214)

From an area selection:

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer({'borders': (0, 0, 50, 50), 'actions': [{'id': 'area',
      'type': ActionType.SELECTION, 'ratios': (0.2, 0.4, 0.6, 0.8)}]})
  image = recognizer.executeSelection('area')
  print(image)

.. code-block:: console

  <PIL.Image.Image image mode=RGB size=20x20 at 0x1F0BCA68A50>

Find images
~~~~~~~~~~~

Actions of type :attr:`ActionType.FIND_IMAGE` search for an image (or visually similar ones) inside a larger image and return the coordinates of the matches.

Here is an example. Let's try to find the camera inside the following image from *Where's Wally?*.

.. figure:: /_static/api/wallyExcerpt.webp
   :alt: Let's use guirecognizer to find the camera inside this image. Let's call this file wallyExcerpt.webp.
   :width: 80%
   :align: center

   Let's use *guirecognizer* to find the camera inside this image. Let's call this file *wallyExcerpt.webp*.

Here is the camera we are looking for.

.. figure:: /_static/api/findImage1.webp
   :alt: The camera to find among other things.
   :width: 50%
   :align: center

   The camera to find among other things.

The most convenient way is to define the action with :ref:`guirecognizerapp <app-find-image>`.
Without *guirecognizerapp*, we can manually extract an area of pixels representing the camera.

.. figure:: /_static/api/wallyCamera.webp
   :alt: A subsection of the camera. Let's call this file wallyCamera.webp.
   :width: 10%
   :align: center

   A subsection of the camera. Let's call this file *wallyCamera.webp*.

Then we are going to find a similar area of pixels inside the image *wallyExcerpt.webp*.

You may need to install pillow to follow the example.

.. code-block:: console

  (venv) $ pip install pillow

.. code-block:: python
  :linenos:

  import base64
  from io import BytesIO
  from guirecognizer import ActionType, Recognizer
  from PIL import Image

  excerpt = Image.open('wallyExcerpt.webp')
  camera = Image.open('wallyCamera.webp')

  # Convert the camera image to a correct format.
  buffered = BytesIO()
  camera.save(buffered, format='PNG')
  imageToFind = base64.b64encode(buffered.getvalue()).decode('utf-8')

  recognizer = Recognizer({'borders': (0, 0, excerpt.width, excerpt.height), 'actions': [{'id': 'find',
      'type': ActionType.FIND_IMAGE, 'ratios': (0, 0, 1, 1), 'imageToFind': imageToFind, 'maxResults': 1, 'threshold': 15}]})
  coords = recognizer.executeFindImage('find', screenshot=excerpt)
  print(coords)

.. code-block:: console

  [(639, 398, 660, 411)]

.. figure:: /_static/api/findImage2.webp
   :alt: The camera is found following the coordinates. It's circled in blue.
   :width: 80%
   :align: center

   The camera is found following the coordinates. It's circled in blue.

Three parameters are available: :attr:`guirecognizer.recognizer.ActionData.maxResults`, :attr:`guirecognizer.recognizer.ActionData.threshold` and :attr:`guirecognizer.recognizer.ActionData.resizeInterval`.

Pixel color
~~~~~~~~~~~

Actions of type :attr:`ActionType.PIXEL_COLOR` return the color of the selected pixel or the average color of the selected area.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer({'borders': (0, 0, 50, 50), 'actions': [{'id': 'color',
      'type': ActionType.PIXEL_COLOR, 'ratios': (0.5, 0.5)}]})
  color = recognizer.executePixelColor('color')
  print(color)

.. code-block:: console

  (97, 96, 101)

Actions of type :attr:`ActionType.COMPARE_PIXEL_COLOR` return the difference between the color of the selected pixel (or the average color of the selected area)
and the color reference. The returned difference is a float between 0 and 1, where 0 means identical colors and higher values indicate greater differences.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer({'borders': (0, 0, 50, 50), 'actions': [{'id': 'compareColor',
      'type': ActionType.COMPARE_PIXEL_COLOR, 'ratios': (0.5, 0.5), 'pixelColor': (100, 100, 100)}]})
  diff = recognizer.executeComparePixelColor('compareColor')
  print(diff)

.. code-block:: console

  0.01045751633986928

Actions of type :attr:`ActionType.IS_SAME_PIXEL_COLOR` return whether the difference between the color of the selected pixel (or the average color of the selected area)
and the color reference is 0.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer({'borders': (0, 0, 50, 50), 'actions': [{'id': 'isSameColor',
      'type': ActionType.IS_SAME_PIXEL_COLOR, 'ratios': (0.5, 0.5), 'pixelColor': (100, 100, 100)}]})
  isSame = recognizer.executeIsSamePixelColor('isSameColor')
  print(isSame)

.. code-block:: console

  False

Image hash
~~~~~~~~~~

Actions of type :attr:`ActionType.IMAGE_HASH` return an image hash of the selected area.
Two visually similar images produce hashes with a small difference. Color information is taken into account when computing the hash.
It uses `https://pypi.org/project/ImageHash <https://pypi.org/project/ImageHash>`_.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer({'borders': (0, 0, 50, 50), 'actions': [{'id': 'imageHash',
      'type': ActionType.IMAGE_HASH, 'ratios': (0.2, 0.4, 0.3, 0.8)}]})
  imageHash = recognizer.executeImageHash('imageHash')
  print(imageHash)

.. code-block:: console

  f852add897319465,07000000000

Actions of type :attr:`ActionType.COMPARE_IMAGE_HASH` return the difference between the image hash of the selected area and the image hash reference.
The difference is a positive integer.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer({'borders': (0, 0, 50, 50), 'actions': [{'id': 'compareImageHash',
      'type': ActionType.COMPARE_IMAGE_HASH, 'ratios': (0.2, 0.4, 0.3, 0.8), 'imageHash': 'f852add897319465,07000000001'}]})
  diff = recognizer.executeCompareImageHash('compareImageHash')
  print(diff)

.. code-block:: console

  39

Usually a difference of 10 or below means the two images are very similar.

Actions of type :attr:`ActionType.IS_SAME_IMAGE_HASH` return whether the difference between the image hash of the selected area and the image hash reference is 0.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  recognizer = Recognizer({'borders': (0, 0, 50, 50), 'actions': [{'id': 'isSameImageHash',
      'type': ActionType.IS_SAME_IMAGE_HASH, 'ratios': (0.2, 0.4, 0.3, 0.8), 'imageHash': 'f852add897319465,07000000001'}]})
  isSame = recognizer.executeIsSameImageHash('isSameImageHash')
  print(isSame)

.. code-block:: console

  False

Text
~~~~

Actions of type :attr:`ActionType.TEXT` return the recognized text, or an empty string if no text was detected.
It uses an optical character recognition library. The supported OCR libraries are listed in the :ref:`section below <api-ocrs>`.

As an example let's retrieve the text from the following image. Install one of the available :ref:`OCRs <api-ocrs>`.

.. figure:: /_static/api/textExample.webp
   :alt: Use guirecognizer to retrieve the text inside this image. Let's call this file textExample.webp.
   :width: 50%
   :align: center

   Use *guirecognizer* to retrieve the text inside this image. Let's call this file *textExample.webp*.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  imagePath = 'textExample.webp'
  recognizer = Recognizer({'borders': (0, 0, 500, 221), 'actions': [{'id': 'text',
      'type': ActionType.TEXT, 'ratios': (0.1, 0.1, 0.9, 0.9)}]})
  text = recognizer.executeText('text', screenshotFilepath=imagePath)
  print(text)

.. code-block:: console

  Hello World

Number
~~~~~~

Actions of type :attr:`ActionType.NUMBER` return a *float*, or *None* if no number was detected.
It uses an optical character recognition library. The supported OCR libraries are listed in the :ref:`section below <api-ocrs>`.

As an example let's retrieve the number from the following image. Install one of the available :ref:`OCRs <api-ocrs>`.

.. figure:: /_static/api/numberExample.webp
   :alt: Use guirecognizer to retrieve the number inside this image. Let's call this file numberExample.webp.
   :width: 50%
   :align: center

   Use *guirecognizer* to retrieve the number inside this image. Let's call this file *numberExample.webp*.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType, Recognizer

  imagePath = 'numberExample.webp'
  recognizer = Recognizer({'borders': (0, 0, 500, 221), 'actions': [{'id': 'number',
      'type': ActionType.NUMBER, 'ratios': (0.7, 0.1, 0.9, 0.9)}]})
  number = recognizer.executeNumber('number', screenshotFilepath=imagePath)
  print(number)

.. code-block:: console

  42.0

.. _api-recognizer-class:

Recognizer class
----------------

.. autoclass:: guirecognizer.Recognizer
  :members: __init__, loadFilepath, loadData, clearAllData,
    executeCoordinates, executeSelection, executeFindImage, executeClick, executePixelColor, executeComparePixelColor, executeIsSamePixelColor,
    executeImageHash, executeCompareImageHash, executeIsSameImageHash, executeText, executeNumber, execute,
    setAllScreens, setOcrOrder, setEasyOcr, setTesseractOcr

.. autoclass:: guirecognizer.recognizer.ExecuteParams
   :members:
   :show-inheritance:

.. autoclass:: guirecognizer.recognizer.PipeInfoDict
   :members:

.. autoexception:: guirecognizer.RecognizerValueError

Load actions
~~~~~~~~~~~~

Create a configuration file using :doc:`guirecognizerapp <app>`. Then load the actions when creating a Recognizer instance: :meth:`Recognizer.__init__`.

.. code-block:: python
  :linenos:

  from guirecognizer import Recognizer

  recognizer = Recognizer('config.json')

Then execute actions with :meth:`Recognizer.execute` using their ids.

.. code-block:: python

  recognizer.execute('click')

Many options are available, as described in :class:`guirecognizer.recognizer.ExecuteParams`, to specify the screenshot, the borders and other specific action options.

For type hinting support, use one of the methods *execute...* associated with the action type.

.. code-block:: python

  recognizer.executeClick('click')

It's possible to load multiple config files with :meth:`Recognizer.loadFilepath`.

.. _api-pipe-actions:

Pipe actions
~~~~~~~~~~~~

Multiple actions can be executed in a chain.

For instance let's have an action called *getImageHash* of type :attr:`ActionType.IMAGE_HASH` that computes the image hash
of a specific screen area. Let's have a second action called *isSameHash* of type :attr:`ActionType.IS_SAME_IMAGE_HASH` that
returns whether it's the same image hash as the one in reference. The action *isSameHash* points to a different screen area
than *getImageHash*. We want to test whether the screen area pointed by *getImageHash* has the correct image hash.
It's possible to execute the two actions in chain.

.. code-block:: python

  isSame = recognizer.executeIsSameImageHash('getImageHash', 'isSameHash')

This is equivalent to the following two calls.

.. code-block:: python
  :linenos:

  hash = recognizer.executeImageHash('getImageHash')
  isSame = recognizer.executeIsSameImageHash('isSameHash', imageHash=hash)

An action can be specified just with its type instead of using the id of a defined action when all its necessary parameters are already present.

For instance let's have an action called *coord* of type :attr:`ActionType.COORDINATES` that returns the coordinates of a point on screen.
We can click on the point with an action of type :attr:`ActionType.CLICK` without defining a new *click* action.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType

  recognizer.executeClick('coord', ActionType.CLICK)

Reinterpret
~~~~~~~~~~~

Sometimes you may have an action of a certain type but only want some elements of the action to be executed.
The parameter :attr:`guirecognizer.recognizer.PipeInfoDict.reinterpret` stops the execution of an action earlier.
The execution returns the result expected by the action type specified in *reinterpret*.

Here is an example. Let's say we have an action of type :attr:`ActionType.CLICK` called *click*.
We want to retrieve the coordinates of the action *click* without actually clicking.

.. code-block:: python
  :linenos:

  from guirecognizer import ActionType

  coord = recognizer.executeClick('coord', reinterpret=ActionType.COORDINATES)


Manual configuration
~~~~~~~~~~~~~~~~~~~~

This section documents the Python data structures used internally to represent configuration data.
It's still best to create a configuration file with :doc:`guirecognizerapp <app>` instead because the companion app helps create and preview actions.

.. autoclass:: guirecognizer.recognizer.RecognizerData
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: guirecognizer.recognizer.ActionData
   :members:
   :undoc-members:

.. autoclass:: guirecognizer.preprocessing.PreprocessingData
   :members:
   :undoc-members:

.. autoclass:: guirecognizer.preprocessing.OperationData
   :members:
   :undoc-members:

.. autoclass:: guirecognizer.preprocessing.GrayscaleSuboperationData
   :members:
   :undoc-members:

.. autoclass:: guirecognizer.preprocessing.ColorMapSuboperationData
   :members:
   :undoc-members:

.. autoclass:: guirecognizer.preprocessing.ColorMapData
   :members:
   :undoc-members:

.. autoclass:: guirecognizer.preprocessing.ThresholdSuboperationData
   :members:
   :undoc-members:

.. autoclass:: guirecognizer.preprocessing.ThresholdData
   :members:
   :undoc-members:

.. autoclass:: guirecognizer.preprocessing.ResizeSuboperationData
   :members:
   :undoc-members:

.. autoclass:: guirecognizer.preprocessing.ResizeData
   :members:
   :undoc-members:

.. autoclass:: guirecognizer.PreprocessingType
   :members:
   :undoc-members:

.. autoclass:: guirecognizer.ColorMapMethod
   :members:
   :undoc-members:

.. autoclass:: guirecognizer.ThresholdMethod
   :members:
   :undoc-members:

.. autoclass:: guirecognizer.ResizeMethod
   :members:
   :undoc-members:


.. _api-preprocessing:

Preprocessing
-------------

Preprocessing operations are applied after capturing a screen area and before the action-specific logic runs.
This is especially useful for :attr:`ActionType.TEXT` and :attr:`ActionType.NUMBER` because the preprocessing can help the OCR performance.

The parameter :attr:`guirecognizer.recognizer.PipeInfoDict.preprocessing` takes the string id of a defined preprocessing operation.
A preprocessing operation consists of a string id and one or more suboperations of type :class:`PreprocessingType`.
The available suboperation types are described in the following subsections.

Here is an example. Let's try to retrieve the text in this image.

.. figure:: /_static/api/preprocessingExample.webp
   :alt: Image with a difficult text to identify by an OCR. Let's call this file preprocessingExample.webp.
   :width: 50%
   :align: center

   Image with a difficult text to identify by an OCR. Let's call this file *preprocessingExample.webp*.

It's more convenient to define a preprocessing operation with :ref:`guirecognizerapp <app-preview-preprocessing>`
but it's also possible to pass a valid configuration with :class:`guirecognizer.recognizer.RecognizerData`.

We define a preprocessing operation called *myThreshold* with one suboperation of type :attr:`PreprocessingType.THRESHOLD`.
We also define an action called *text*.

.. code-block:: python
  :linenos:

  from guirecognizer import (ActionType, OcrType, PreprocessingType, Recognizer,
                            ThresholdMethod, ThresholdType)

  recognizer = Recognizer({'borders': (0, 0, 500, 200), 'actions': [{'id': 'text',
      'type': ActionType.TEXT, 'ratios': (0.1, 0.1, 0.9, 0.9)},],
      'operations': [{'id': 'myThreshold', 'suboperations': [{'type': PreprocessingType.THRESHOLD,
      'threshold': {'method': ThresholdMethod.SIMPLE, 'threshold': 29, 'thresholdType': ThresholdType.TO_ZERO}}]}]})
  recognizer.setOcrOrder([OcrType.EASY_OCR])

Let's see if the OCR can recognize the text.

.. code-block:: python
  :linenos:

  from PIL import Image

  image = Image.open('preprocessingExample.webp')
  text = recognizer.executeText('text', screenshot=image)
  print('Text:', text)

.. code-block:: console

  Text:

As expected the OCR did not manage to recognize the text.

Let's see the image after applying the preprocessing operation we defined.

.. code-block:: python
  :linenos:

  preprocessedImage = recognizer.preprocessing.process(image, 'myThreshold')
  preprocessedImage.show()

.. figure:: /_static/api/preprocessingExample2.webp
   :alt: The image after applying the preprocessing operation myThreshold.
   :width: 50%
   :align: center

   The image after applying the preprocessing operation *myThreshold*.

The text is more readable. The OCR has a better chance to work.

Pass the parameter :attr:`guirecognizer.recognizer.PipeInfoDict.preprocessing` to use the preprocessing operation *myThreshold*
directly without computing separately the preprocessed image.

.. code-block:: python
  :linenos:

  text = recognizer.executeText('text', screenshot=image, preprocessing='myThreshold')
  print('Text after preprocessing:', text)

.. code-block:: console

  Text after preprocessing: Preprocessing

The text is correctly recognized.

Grayscale
~~~~~~~~~

The grayscale suboperation converts the image into a gray monochrome.

Here is an example.

.. figure:: /_static/api/example.webp
   :alt: An image before applying grayscale.
   :width: 50%
   :align: center

   An image before applying grayscale.

.. code-block:: python
  :linenos:

  from guirecognizer import PreprocessingType, Recognizer
  from PIL import Image

  recognizer = Recognizer({'borders': (0, 0, 240, 224), 'actions': [],
      'operations': [{'id': 'myGrayscale', 'suboperations': [{'type': PreprocessingType.GRAYSCALE}]}]})

  image = Image.open('example.webp')
  image.show()

  preprocessedImage = recognizer.preprocessing.process(image, 'myGrayscale')
  preprocessedImage.show()

.. figure:: /_static/api/grayscaleExample.webp
   :alt: The image after applying grayscale.
   :width: 50%
   :align: center

   The image after applying grayscale.

Color map
~~~~~~~~~

The color map suboperation replaces a color or range of colors by another color or another range of colors: :class:`guirecognizer.preprocessing.ColorMapData`.

In this example let's replace the top red rectangle by the color black.

.. code-block:: python
  :linenos:

  from guirecognizer import PreprocessingType, Recognizer
  from PIL import Image

  recognizer = Recognizer({'borders': (0, 0, 240, 224), 'actions': [],
      'operations': [{'id': 'myColorMap', 'suboperations': [{
      'type': PreprocessingType.COLOR_MAP, 'colorMap': {'inputColor1': (128, 0, 0), 'outputColor1': (0, 0, 0)}}]}]})

  image = Image.open('example.webp')
  image.show()

  preprocessedImage = recognizer.preprocessing.process(image, 'myColorMap')
  preprocessedImage.show()

.. figure:: /_static/api/colorMapExample1.webp
   :alt: The image after applying the color map suboperation.
   :width: 50%
   :align: center

   The image after applying the color map suboperation.

Some red pixels were not converted into black. Those pixels are not exactly equal to the input color.
We can increase the value of :attr:`guirecognizer.preprocessing.ColorMapData.difference`.

.. code-block:: python
  :linenos:

  from guirecognizer import PreprocessingType, Recognizer
  from PIL import Image

  recognizer = Recognizer({'borders': (0, 0, 240, 224), 'actions': [],
      'operations': [{'id': 'myColorMap', 'suboperations': [{
      'type': PreprocessingType.COLOR_MAP, 'colorMap': {'inputColor1': (128, 0, 0), 'outputColor1': (0, 0, 0), 'difference': 0.07}}]}]})

  image = Image.open('example.webp')
  image.show()

  preprocessedImage = recognizer.preprocessing.process(image, 'myColorMap')
  preprocessedImage.show()

.. figure:: /_static/api/colorMapExample2.webp
   :alt: The image after applying the color map suboperation with a less strict difference.
   :width: 50%
   :align: center

   The image after applying the color map suboperation with a less strict difference.

More red pixels are converted into black.

In this example let's replace the bottom blue rectangle by a range of green.

.. code-block:: python
  :linenos:

  from guirecognizer import ColorMapMethod, PreprocessingType, Recognizer
  from PIL import Image

  recognizer = Recognizer({'borders': (0, 0, 240, 224), 'actions': [],
      'operations': [{'id': 'myColorMap', 'suboperations': [{
      'type': PreprocessingType.COLOR_MAP, 'colorMap': {'inputColor1': (16, 0, 83), 'inputColor2': (0, 84, 213),
      'method': ColorMapMethod.RANGE_TO_RANGE, 'outputColor1': (0, 210, 0), 'outputColor2': (0, 120, 0), 'difference': 0.07}}]}]})

  image = Image.open('example.webp')
  image.show()

  preprocessedImage = recognizer.preprocessing.process(image, 'myColorMap')
  preprocessedImage.show()

.. figure:: /_static/api/colorMapExample3.webp
   :alt: The image after applying a color map suboperation on a range of colors.
   :width: 50%
   :align: center

   The image after applying a color map suboperation on a range of colors.

Threshold
~~~~~~~~~

The threshold suboperation applies a color thresholding returning a black and white image depending of the method used: :class:`guirecognizer.preprocessing.ThresholdData`.
More information is available in the OpenCV image thresholding documentation:
`https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html <https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html>`_.

Here is an example trying to isolate the word *Example*.

.. code-block:: python
  :linenos:

  from guirecognizer import PreprocessingType, Recognizer, ThresholdMethod
  from PIL import Image

  recognizer = Recognizer({'borders': (0, 0, 240, 224), 'actions': [],
      'operations': [{'id': 'myThreshold', 'suboperations': [{
      'type': PreprocessingType.THRESHOLD, 'threshold': {'method': ThresholdMethod.ADAPTIVE_MEAN}}]}]})

  image = Image.open('example.webp')
  image.show()

  preprocessedImage = recognizer.preprocessing.process(image, 'myThreshold')
  preprocessedImage.show()

.. figure:: /_static/api/thresholdExample.webp
   :alt: The image after applying a threshold suboperation.
   :width: 50%
   :align: center

   The image after applying a threshold suboperation.

Resize
~~~~~~

The resize suboperation resizes the image with or without keeping the same aspect ratio: :class:`guirecognizer.preprocessing.ResizeData`.

Here is an example where the image is resized by reducing the width while keeping the same aspect ratio.

.. code-block:: python
  :linenos:

  from guirecognizer import PreprocessingType, Recognizer, ResizeMethod
  from PIL import Image

  recognizer = Recognizer({'borders': (0, 0, 240, 224), 'actions': [],
      'operations': [{'id': 'myResize', 'suboperations': [{
      'type': PreprocessingType.RESIZE, 'resize': {'method': ResizeMethod.FIXED_RATIO_WIDTH, 'width': 30}}]}]})

  image = Image.open('example.webp')
  image.show()

  preprocessedImage = recognizer.preprocessing.process(image, 'myResize')
  preprocessedImage.show()

.. figure:: /_static/api/resizeExample.webp
   :alt: The image after applying a resize suboperation.
   :width: 50%
   :align: center

   The image after applying a resize suboperation.


.. _api-ocrs:

OCRs
----

Two optical character recognition libraries are supported by *guirecognizer*: `EasyOCR <https://github.com/JaidedAI/EasyOCR>`_
and `tesseract <https://github.com/tesseract-ocr/tesseract>`_.

If multiple OCRs are installed, it's possible to use multiple OCRs as fallbacks.
For instance when trying to identify a text on an image
with :attr:`ActionType.TEXT`, if the first OCR in the list fails to retrieve some text, the second OCR will be used.
If the first OCR retrieves any text, the second OCR is not used.
Define the list of OCRs and their order with :meth:`Recognizer.setOcrOrder`.
By default *guirecognizer* tries to use EasyOCR then tesseract.

Here is an example which sets tesseract as the only OCR.

.. code-block:: python
  :linenos:

  from guirecognizer import OcrType

  recognizer.setOcrOrder([OcrType.TESSERACT])

.. autoclass:: guirecognizer.OcrType
   :members:
   :undoc-members:

When actions are previewed with :ref:`guirecognizerapp <app-preview-actions>`, if the OCR settings have been changed,
it's important to adapt the OCR configuration again with *guirecognizer*.
The configuration file produced by *guirecognizerapp* does not save the OCR settings (or other settings).

EasyOCR
~~~~~~~

Follow the instructions at `https://github.com/JaidedAI/EasyOCR <https://github.com/JaidedAI/EasyOCR>`_ to install EasyOCR.

Configure the OCR with :meth:`Recognizer.setEasyOcr`. More information about the options is available
at `https://github.com/JaidedAI/EasyOCR <https://github.com/JaidedAI/EasyOCR>`_.

Here is an example to change the expected language to French.

.. code-block:: python

  recognizer.setEasyOcr(languages=['fr'])

Tesseract
~~~~~~~~~

Follow the instructions at `https://github.com/tesseract-ocr/tesseract <https://github.com/tesseract-ocr/tesseract>`_ to install tesseract
and at `https://github.com/madmaze/pytesseract <https://github.com/madmaze/pytesseract>`_ to install pytesseract.

Configure the OCR with :meth:`Recognizer.setTesseractOcr`.

The library pytesseract needs to know the path to *tesseract.exe*. You can pass it with the parameter *tesseract_cmd* of :meth:`Recognizer.setTesseractOcr`.
Or you can let *guirecognizer* try to find it on your computer, which may take seconds or minutes.

More information about tesseract options is available
at `https://muthu.co/all-tesseract-ocr-options <https://muthu.co/all-tesseract-ocr-options>`_.

Here is an example to treat the image as a single word and change the expected language to Spanish.

.. code-block:: python

  recognizer.setTesseractOcr(textConfig='--psm 8 --oem 3', lang='spa')


.. _api-mouse-helper:

Mouse helper
------------

.. autoclass:: guirecognizer.MouseHelper
   :members:

For more advanced mouse interactions, use another library like `pyautogui <https://pyautogui.readthedocs.io/en/latest>`_.
