Overview
========

What is *guirecognizer*
-----------------------
The main goal of *guirecognizer* is to retrieve information on the screen like getting a pixel color,
an image hash of a screenshot area or finding an image on screen.

For an exhaustive list of available actions, see the :doc:`API <api>`.

Two optical character recognition libraries are supported by *guirecognizer*: `EasyOCR <https://github.com/JaidedAI/EasyOCR>`_
and `tesseract <https://github.com/tesseract-ocr/tesseract>`_. More information about the :ref:`OCRs <api-ocrs>`.

*guirecognizer* offers ways to preprocess an image before it's used by an action. This is especially useful to improve OCR efficiency.
For the exhaustive list of preprocessing operations: :ref:`Preprocessing API <api-preprocessing>`.

The compagnion app **guirecognizerapp** helps create and preview actions which are then executed via *guirecognizer*.

Getting started
---------------

It's advised to use *guirecognizerapp* to generate a configuration file listing the actions.

Install *guirecognizerapp* (this will also install *guirecognizer*)

.. code-block:: console

  (venv) $ pip install guirecognizerapp

Launch the application:

.. code-block:: console

  (venv) $ python -m guirecognizerapp

From the app, take a screenshot.

Before defining an action, the borders must be set. The **borders** represent the part of the screen where the actions are taken place.
They are defined in absolute coordinates while action selections are saved as relative coordinates, relative to the borders.
In case a configuration file is used on another screen setup, redefining the borders may be enough to support the new setup instead of redefining all the actions.
For instance select the whole screenshot as the borders.

For the sake of this tutorial let's try to get the color of a pixel. Create a new action *Get Pixel Color*. Name your action and select a pixel.

Now you can preview the action (from the eye icon in front the action).

Save the file *guirecognizerConfig.json*.

For a full presentation of *guirecognizerapp*: TODO

Now the configuration file can be used with *guirecognizer*.

In python

.. code-block:: python
  :linenos:

  from guirecognizer import Recognizer

  recognizer = Recognizer('guirecognizerConfig.json')
  color = recognizer.execute('getPixelColor')
  print(color)

.. code-block::

  TODO: complete


TODO: show example of preprocessing to improve ocr
