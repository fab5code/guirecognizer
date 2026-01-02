APIs
====

.. _api-actions:

Actions
-------

TODO

.. autoclass:: guirecognizer.ActionType
  :members: COORDINATES, SELECTION, FIND_IMAGE, CLICK, PIXEL_COLOR, COMPARE_PIXEL_COLOR, IS_SAME_PIXEL_COLOR,
    IMAGE_HASH, COMPARE_IMAGE_HASH, IS_SAME_IMAGE_HASH, TEXT, NUMBER

.. _recognizer-class:

Recognizer class
----------------

.. autoclass:: guirecognizer.Recognizer
  :members: loadFilepath, loadData, clearAllData,
    executeCoordinates, executeSelection, executeFindImage, executeClick, executePixelColor, executeComparePixelColor, executeIsSamePixelColor,
    executeImageHash, executeCompareImageHash, executeIsSameImageHash, executeText, executeNumber, execute,
    setAllScreens, setOcrOrder, setEasyOcr, setTesseractOcr

.. autoclass:: guirecognizer.recognizer.ExecuteParams
   :members:
   :show-inheritance:

.. autoclass:: guirecognizer.recognizer.PipeInfoDict
   :members:

.. autoexception:: guirecognizer.RecognizerValueError

.. _api-preprocessing:

Preprocessing
-------------

TODO

.. _api-ocrs:

OCRs
----

TODO

.. _mouse-helper:

Mouse helper
------------

TODO

.. autoclass:: guirecognizer.MouseHelper
   :members:
