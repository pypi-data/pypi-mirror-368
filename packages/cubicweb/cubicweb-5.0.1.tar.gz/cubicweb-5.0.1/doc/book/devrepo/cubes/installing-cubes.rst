.. _InstallingCubes:

Installing cubes
----------------

Installing the code
~~~~~~~~~~~~~~~~~~~

Using Pip
_________

Cubes are written in python so most of then are
distributing with ``pip``.

The naming convention for cubes pip packages is
``cubicweb_<CUBE_NAME>``.

So if you want to install the ``api`` cube,
you need to run the command
``pip install cubicweb_api``

Using Sources
_____________

If the cube is not distributed with pip,
you can download the sources on your machine
and install it manually.

If you are using venv, make sure your shell is using
the one for your CubicWeb application.

Open a shell in the cube's source files and run
``pip install``.

This will install the cube in the venv of you application.

If you want to make changes on the cube and see
those changes on your main CubicWeb application,
run ``pip install -e .`` instead.

Adding the dependency
~~~~~~~~~~~~~~~~~~~~~

Once you have installed the cube's code in your application,
you need to declare the dependency.

Open the file ``__pkginfo__.py`` in you main CubicWeb application
and add your cube with the required version in the ``__depends__``.

The naming convention here for the cube name is
``cubicweb-<CUBE_NAME>``. Notice the use of **-** instead of **_** in ``pip``.

For example, if you want to install the api cube version 0.9.0, you would write

.. code-block:: python
    __depends__ = {
        'cubicweb-api': '~= 0.9.0',
    }


Installing on existing instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your CubicWeb application has already an instance running,
you need to manually add the cube and run a migration.

To do so, run the following commands
(replacing <YOUR_INSTANCE> with your instance name):

Open a shell using ``cubicweb-ctl shell <YOUR_INSTANCE>``.
In that shell type ``add_cube(api)``, then ``exit()`` to leave the shell.
And finally upgrade your instance:
``cubicweb-ctl upgrade <YOUR_INSTANCE>``

More information on migration :ref:`here <book/devrepo/migration/>`

