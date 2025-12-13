Bot for Cookie Clicker
======================

This is a bot for the popular idle game Cookie Clicker: `https://orteil.dashnet.org/cookieclicker/ <https://orteil.dashnet.org/cookieclicker/>`_.

Cookie Clicker
--------------

Otteretto is a game about palindromes. Blocks of different colors are arranged on a grid of 4 by 10.
The goal is to find palindromes of colored blocks inside the grid. Bigger palindromes awards more points.

Run the bot
-----------

To run the bot, adapt the borders of the recognizer. The bot needs to know where the portion of the screen containing the game interface is.

Install *guirecognizerapp*.

.. code-block:: console

  (venv) $ pip install guirecognizerapp

Launch *guirecognizerapp*.

.. code-block:: console

  (venv) $ python -m guirecognizerapp

Open in the app *cookieclicker.json*.
Open the game: `https://orteil.dashnet.org/cookieclicker/ <https://orteil.dashnet.org/cookieclicker/>`_.
Take a screenshot from the app (Ctrl+Alt+T).
Modify the borders so that it takes exactly the whole game interface without the top header with the settings like *Change Language*.

Finally run the bot.

.. code-block:: console

  (venv) $ python cookieclicker.py
