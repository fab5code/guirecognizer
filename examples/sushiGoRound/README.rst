Bot for Sushi Go Round
======================

This is a bot for the browser game Sushi Go Round: `https://www.crazygames.com/game/sushi-go-round <https://www.crazygames.com/game/sushi-go-round>`_.

Sushi Go Round
--------------

Sushi Go Round is a fast-paced restaurant management game where you prepare and serve sushi to customers before they lose patience.
You must assemble dishes according to orders while managing a limited stock of ingredients,
restocking supplies in time to keep the sushi bar running smoothly.

Run the bot
-----------

To run the bot, adapt the borders of the recognizer.

Install *guirecognizerapp*.

.. code-block:: console

  (venv) $ pip install guirecognizerapp

Launch *guirecognizerapp*.

.. code-block:: console

  (venv) $ python -m guirecognizerapp

Open in the app *sushiGoRound.json*.
Open the game: `https://www.crazygames.com/game/sushi-go-round <https://www.crazygames.com/game/sushi-go-round>`_.
Take a screenshot from the app (Ctrl+Alt+T).
Modify the borders so that they cover exactly the game interface, without any black borders if present.

Finally run the bot from the start of the game. It is assumed the tutorial has already been seen.

.. code-block:: console

  (venv) $ python sushiGoRound.py

Potential improvements
----------------------

- monitor client moods to manage priority and use sake
- improve order guessing when customer has stolen an order
- monitor passage of time to buy preemptively ingredients and even make preemptively orders (may not worth it for orders)
especially while no client is waiting to be served
