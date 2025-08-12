.. -*- coding: utf-8 -*-

.. _SetUpEnv:

Install a CubicWeb environment
==============================

.. _`CubicWeb.org forge`: https://forge.extranet.logilab.fr/cubicweb/cubicweb

Official releases are available from the `CubicWeb.org forge`_ and from
`PyPI <http://pypi.python.org/pypi?%3Aaction=search&term=cubicweb&submit=search>`_. Since CubicWeb is developed using `Agile software development
<http://en.wikipedia.org/wiki/Agile_software_development>`_ techniques, releases
happen frequently. In a version numbered X.Y.Z, X changes after a few years when
the API breaks, Y changes after a few weeks when features are added and Z
changes after a few days when bugs are fixed.

Additional configuration can be found in the section :ref:`ConfigEnv` for better control
and advanced features of |cubicweb|.


.. _InstallDependencies:

Install system dependencies
---------------------------

Assuming your are using a Debian system, here are the packages you need to install:

.. code-block:: console

   apt install gettext graphviz

``gettext`` is used for translations (see :ref:`internationalization`), and ``graphviz`` to display relation schemas within the website.

Install CubicWeb
----------------

.. _VirtualenvInstallation:

|cubicweb| can be safely installed, used and contained inside a virtual
environment. To create and activate a virtual environment, use the following
commands:

.. code-block:: console

   python3 -m venv venv
   source venv/bin/activate

Then, install |cubicweb| and its dependencies by running:

.. code-block:: console

  pip install cubicweb


Install `cubes`
---------------

Many components, called :ref:`cubes <AvailableCubes>`, are available. Those
cubes can help expanding the functionalities offered by |cubicweb|. A list is
available at `PyPI
<http://pypi.python.org/pypi?%3Aaction=search&term=cubicweb&submit=search>`_ or
at the `CubicWeb.org forge`_.

For example the `api cube <https://forge.extranet.logilab.fr/cubicweb/cubes/api>`_ can be installed using:

.. code-block:: console

  pip install cubicweb-api
