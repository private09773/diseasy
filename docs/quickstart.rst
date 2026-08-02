Quickstart
==========

Installation
-------------

.. code-block:: bash

   pip install diseasy

A minimal bot
-------------

.. code-block:: python

   import diseasy

   client = diseasy.Client(intents=["guilds", "messages"])

   @client.event(name="on_ready")
   async def on_ready():
       print("Diseasy is ready.")

   client.run("TOKEN")
