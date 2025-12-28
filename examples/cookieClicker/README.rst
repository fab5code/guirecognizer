Bot for Cookie Clicker
======================

This is a bot for the popular idle game Cookie Clicker: `https://orteil.dashnet.org/cookieclicker/ <https://orteil.dashnet.org/cookieclicker/>`_.

Cookie Clicker
--------------

Cookie Clicker is an idle game where you click to bake cookies and use them to buy upgrades that automatically produce even more cookies over time.

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
