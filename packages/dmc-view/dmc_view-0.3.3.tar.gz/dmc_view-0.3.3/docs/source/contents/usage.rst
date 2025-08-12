Usage
=====

------------
Installation
------------

| **dmcview** is available on PyPI hence you can use `pip` to install it.

It is recommended to perform the installation in an isolated `python virtual environment` (env).
You can create and activate an `env` using any tool of your preference (ie `virtualenv`, `venv`, `pyenv`).

Assuming you have 'activated' a `python virtual environment`:

.. code-block:: shell

  python -m pip install dmc-view


---------------
Simple Use Case
---------------

| Common Use Case for the dmcview in input mode

.. code-block:: shell

  dmcview -a 45.5 -d 5.6 -b 30.35 -e 15.23 -ac 14.21 13.0 14.5

| **a**: Azimuth angle in degree.
| **d**: Declination angle in degree which is the difference between Real North and Magnetic North.
| **b**: Bank or the angle of inclination of the object from horizontal axis in degree.
| **e**: Elevation or angular height of a point of interest above or below the horizon, in degrees.
| **ac**: Acceleration of the object, using 3 points vector.

|
| Common Use Case for the dmcview in simulation mode

.. code-block:: shell

  dmcview -s Y


--------------
Running PyTest 
--------------
| PyTest can be run from command line.

.. code-block:: shell
  
  python -m pip install -e . dmcview[test]
  pytest



