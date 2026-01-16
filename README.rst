guirecognizer
=============

**guirecognizer** is a Python library to recognize patterns on screen and make GUI actions.

*guirecognizer* supports a list of actions like getting a pixel color, an image hash of a screenshot area or finding an image on screen.
The compagnion app **guirecognizerapp** helps create and preview actions which are then executed via *guirecognizer*.
See documentation with tutorials and examples: `https://guirecognizer.readthedocs.io <https://guirecognizer.readthedocs.io>`_.

Quick overview
--------------

It's advised to use *guirecognizerapp* to generate a configuration file listing the actions.

Install *guirecognizerapp*

.. code-block:: console

  (venv) $ pip install guirecognizerapp

Launch the application:

.. code-block:: console

  (venv) $ python -m guirecognizerapp

From the app, take a screenshot, define the borders of the relevant screen area and define actions.
Preview the actions on different screenshots to test they work as intended.
Save the file *guirecognizerConfig.json*.

Now the configuration file can be used with *guirecognizer*.

Install *guirecognizer* (already installed from installing *guirecognizerapp*)

.. code-block:: console

  (venv) $ pip install guirecognizer

In python

.. code-block:: python
  :linenos:

  from guirecognizer import Recognizer

  recognizer = Recognizer('guirecognizerConfig.json')
  color = recognizer.execute('getPixelColor')

Development
-----------

Install the dependencies
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

  (venv) $ pip install -e ".[dev]"


Create wheel
^^^^^^^^^^^^

.. code-block:: console

  (venv) $ python -m build

OCR
^^^

Two optical character recognition libraries are supported: `EasyOCR <https://github.com/JaidedAI/EasyOCR>`_ and `tesseract <https://github.com/tesseract-ocr/tesseract>`_.

Install EasyOCR (already in the dev dependencies).

.. code-block:: console

  (venv) $ python install easyocr

Install pytesseract (already in the dev dependencies).

.. code-block:: console

  (venv) $ python install easyocr

Install tesseract: follow installation instruction in `https://github.com/tesseract-ocr/tesseract <https://github.com/tesseract-ocr/tesseract>`_.

Generate full coverage report
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console
  :linenos:

  (venv) $ coverage run
  (venv) $ coverage html

Then open *htmlcov/index.html*

Documentation
^^^^^^^^^^^^^

Generate doc

.. code-block:: console

  (venv) $ make html

Then open *docsBuild/index.html*

Use the script *scripts/optimizeImages.sh* in a bash console to reduce the size of images before pushing them in git.
Image files are converted to webp files.

For instance:

.. code-block:: console

  $ ./scripts/optimizeImages.sh docs/_static/app

Coding style
^^^^^^^^^^^^

Some visual studio code settings of visualStudioCodeSettings.json should be used to ensure some homogeneity in the coding style.

In Visual Studio Code, install extensions

- isort to sort Python automatically
- Pylance for type checking

Improvements
------------

**Improve logger usage**: in code and tests.
