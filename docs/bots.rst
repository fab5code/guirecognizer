Structuring Bots
================

Retrieving information from the screen is rarely the final goal.
The purpose of *guirecognizer* is to help with this task, so the rest of the bot logic can remain the main focus.

This section explains three ways to build your bot, depending on how its different parts should be executed.

.. contents::
   :local:
   :depth: 1

Sequential tasks
----------------

The simplest configuration is when the bot executes its tasks sequentially, one after the other.
This is the case of the :doc:`bot example with the game Otteretto <example/otteretto>`.

In your bot, you just need to instantiate a :ref:`Recognizer <api-recognizer-class>` when it is needed.

.. code-block:: python
  :linenos:

  from guirecognizer import Recognizer

  recognizer = Recognizer('config.json')
  recognizer.execute('action')


Asynchronous tasks
------------------

When your bot has to handle multiple independent tasks, an important distinction is whether those
tasks need true parallelism or can make progress independently while waiting on I/O or timers.
With asynchronous execution, tasks do not run simultaneously, but they can interleave their execution
by yielding control when they are idle.

As an analogy, true parallelism is like having a team of employees each working at the same time in a restaurant,
while asynchronous execution is like a single employee efficiently switching between tasks whenever one
is waiting, such as during cooking or customer delays.

In this section, we show a small bot handling independent tasks using asynchronous execution.
This execution model is used in the :doc:`bot example with the game SushiGoRound <example/sushiGoRound>`.
If your bot tasks truly need to run in parallel (for example, to bypass the GIL), read the next section.

Let's have two independent tasks: one to take orders and one to make orders.
We are going to use the Python library `asyncio <https://realpython.com/ref/stdlib/asyncio/>`_.
With *asyncio*, tasks run cooperatively in a single thread.

.. code-block:: python
  :linenos:

  import asyncio
  import random
  from guirecognizer import Recognizer

  recognizer = Recognizer('config.json')
  orders = []

  async def takeOrders():
    while True:
      await asyncio.sleep(0.5 + random.random() * 5) # Simulate waiting for order.
      order = random.randint(1, 1000)
      recognizer.execute('order')
      await asyncio.sleep(1) # Simulate taking one order.
      print('Took order', order)
      orders.append(order)

  async def makeOrders():
    while True:
      if len(orders) > 0:
        order = orders.pop()
        recognizer.execute('make')
        await asyncio.sleep(5) # Simulate making one order.
        print('Made order', order)
      await asyncio.sleep(0.5)

  async def main():
    await asyncio.gather(takeOrders(), makeOrders())

  asyncio.run(main())

In the console:

.. code-block:: console

  Took order 516
  Made order 516
  Took order 479
  Took order 24
  Made order 479
  Made order 24
  Took order 445
  Took order 485
  Made order 445
  Took order 795

No explicit synchronization is needed for shared Python objects in this example.
In a functional bot, lines 5, 12 and 21 should be replaced with your own usage of *guirecognizer*.
To test this example as-is, comment out those lines.


Parallel tasks
--------------

When your bot needs true parallelism, each task must run in a separate process.
The :doc:`bot example with the game Cookie Clicker <example/cookieClicker>` follows this approach..

As before, we define two tasks: one to take orders and one to make orders.
We are going to use the Python library `multiprocessing <https://realpython.com/ref/stdlib/multiprocessing/>`_.
This avoids the limitations imposed by Python's Global Interpreter Lock (GIL).

.. code-block:: python
  :linenos:

  import multiprocessing as mp
  import random
  import time
  from multiprocessing.synchronize import Lock
  from guirecognizer import Recognizer

  def takeOrders(orders: mp.Queue, mouseLock: Lock) -> None:
    recognizer = Recognizer('config.json')
    while True:
      time.sleep(0.5 + random.random() * 5) # Simulate waiting for order.
      order = random.randint(1, 1000)
      mouseLock.acquire()
      recognizer.execute('order')
      mouseLock.release()
      time.sleep(1) # Simulate taking one order.
      print('Took order', order)
      orders.put(order)

  def makeOrders(orders: mp.Queue, mouseLock: Lock) -> None:
    recognizer = Recognizer('config.json')
    while True:
      try:
        order = orders.get(timeout=1)
        mouseLock.acquire()
        recognizer.execute('make')
        mouseLock.release()
        time.sleep(5) # Simulate making one order.
        print('Made order', order)
      except mp.queues.Empty:
          pass
      time.sleep(0.5)

  def main() -> None:
    processes = []
    orders = mp.Queue()
    mouseLock = mp.Lock()
    processes.append(mp.Process(target=takeOrders, args=(orders, mouseLock)))
    processes.append(mp.Process(target=makeOrders, args=(orders, mouseLock)))
    for process in processes:
      process.start()
    for process in processes:
      process.join()

  if __name__ == '__main__':
    main()

In the console:

.. code-block:: console

  Took order 365
  Took order 227
  Made order 365
  Took order 704
  Took order 355
  Made order 227
  Took order 512
  Made order 704

A special structure is needed to share state between the processes.
Here `multiprocessing.Queue <https://docs.python.org/3/library/multiprocessing.html#pipes-and-queues>`_
shares the orders between the two tasks.

If your bot uses the mouse, it is important to avoid simultaneous mouse actions, for example by using a lock.
This is shown in the code above on lines 12, 14, 24, 26 and 36.

Instead of trying to share an instance of the :ref:`Recognizer <api-recognizer-class>`, instantiate one per process
as shown on lines 8 and 20.
In a functional bot, lines 8, 13, 20 and 25 should be replaced with your own usage of *guirecognizer*.
To test this example as-is, comment out those lines.

Choosing between these approaches depends on whether your bot can run cooperatively in a single thread or requires true parallel execution.
