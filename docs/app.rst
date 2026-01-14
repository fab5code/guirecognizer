guirecognizerapp
================

The library *guirecognizerapp* is the companion app for *guirecognizer*.
It helps create and preview actions and preprocessing operations thanks to its visual interface.

Installation
------------

Install *guirecognizerapp* (it will also install *guirecognizer*)

.. code-block:: console

  (venv) $ pip install guirecognizerapp

Launch the app

.. code-block:: console

  (venv) $ python -m guirecognizerapp

The launch script has some options.

.. code-block:: console

  (venv) $ python -m guirecognizerapp -help
  usage: __main__.py [-h] [-n] [-p PORT]

  Start the server of the compagnion app guirecognizerapp of guirecognizer.

  options:
    -h, --help        show this help message and exit
    -n, --no-browser  Start the server without opening a browser window.
    -p, --port PORT   Port to run the server on (default: 8000).

Define borders and actions
--------------------------

The first step when creating a configuration file for *guirecognizer* is to define the borders.
The borders represent the absolute coordinates of the screen portion that are used as a reference to define all actions.
Action screen selections are defined relative to the borders. This helps with the reusability of the configuration file.

Take screenshot
~~~~~~~~~~~~~~~

The borders can only be defined once a screenshot has been taken or opened.

To take a screenshot: *Capture -> Take Screenshot* or use the keyboard shortcut *Ctrl+Alt+T*.
If you are working with only one screen, using the keyboard shortcut helps to take the screenshot while hiding the interface.
You can always take a screenshot by other means or choose any image and then open it: *Capture -> Open Screenshot*.

If you are working with multiple screens, an option exists to take a screenshot with all the screens in the tab *Settings*
under *Screenshot Settings*.

Define borders
~~~~~~~~~~~~~~

Click on the *Make Selection* button in the tab *Actions*.

.. figure:: /_static/app/defineBorders1.webp
   :alt: Click on the Make Selection to define the borders.
   :width: 80%
   :align: center

   Click on the *Make Selection* to define the borders.

Then select the area by mouse or with the controls at the bottom in the tab *Screenshot*.

.. figure:: /_static/app/defineBorders2.webp
   :alt: Select the area.
   :width: 80%
   :align: center

   Select the area.

Define an action
~~~~~~~~~~~~~~~~

To add a new action, use the menu *Manage Actions*.
For the exhaustive list of actions: :doc:`API <api>`.

Every action has an id. The id is necessary to call the action with *guirecognizer*.
The id is also used in *guirecognizerapp* for other features like copying another selection.

Let's say we have an action named *getScore* with its selection already made.
When making the selection of another action, you can copy the selection of *getScore* from the controls.

.. figure:: /_static/app/defineBorders3.webp
   :alt: Copy the selection of another action.
   :width: 80%
   :align: center

   Copy the selection of another action.

.. _app-preview-actions:

Preview actions
---------------

The main strength of *guirecognizerapp* is to preview actions.

.. _app-find-image:

Find images
~~~~~~~~~~~

.. _app-preview-preprocessing:

Define and preview preprocessing
--------------------------------

Add context
-----------
