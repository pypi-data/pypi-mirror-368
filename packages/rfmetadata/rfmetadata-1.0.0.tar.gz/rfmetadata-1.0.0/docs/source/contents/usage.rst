
Installation
------------

| **rfmetadata** is available on PyPI hence you can use `pip` to install it.

It is recommended to perform the installation in an isolated `python virtual environment` (env).
You can create and activate an `env` using any tool of your preference (ie `virtualenv`, `venv`, `pyenv`).

Assuming you have 'activated' a `python virtual environment`:

.. code-block:: shell

  python -m pip install rfmetadata


---------------
Simple Use Case 
---------------
You need to start the rfserver first to allow the client to query the database 

.. code-block:: shell

  rfmetadata  




--------------
Running PyTest 
--------------
| PyTest can be run from command line.

.. code-block:: shell
  
  python -m pip install -e . rfnode[test]
  pytest



