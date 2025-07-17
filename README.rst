GuiRecognizer
=============

**GuiRecognizer** is a python library to recognize some patterns on screen and make GUI actions.

Development
-----------

Install the dependencies
In the root directory execute pip install -e ".[dev]"

Create wheel
In the root directory execute python -m build

Install tesseract
https://github.com/tesseract-ocr/tesseract

Some visual studio code settings of visualStudioCodeSettings.json should be used to ensure some homogeneity in the coding style.

In Visual Studio Code, install extensions
- isort to sort python automatically
- Pylance for type checking

Manually generate coverage html report (with branches)
coverage run --branch -m unittest discover
coverage html
