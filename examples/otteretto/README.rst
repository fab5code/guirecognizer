Bot for Otteretto
=================

This is a bot for the popular game Otteretto: `https://otteretto.app/classic/ <https://otteretto.app/classic/>`_.

Otteretto
---------

Otteretto is a game about palindromes. Blocks of different colors are arranged on a grid of 4 by 10.
The goal is to find palindromes of colored blocks inside the grid. Bigger palindromes awards more points.

Run the bot
-----------

To run the bot, adapt the borders of the recognizer. The bot needs to know where the grid is on screen.

Install *guirecognizerapp*.

.. code-block:: console

  (venv) $ pip install guirecognizerapp

Launch *guirecognizerapp*.

.. code-block:: console

  (venv) $ python -m guirecognizerapp

Open in the app *otteretto.json*.
Open the game: `https://otteretto.app/classic/ <https://otteretto.app/classic/>`_.
Take a screenshot from the app (Ctrl+Alt+T).
Modify the borders so that it takes exactly the grid frame and the bonus button on the bottom right of the grid.

Finally run the bot.

.. code-block:: console

  (venv) $ python otteretto.py
