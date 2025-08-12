.. -*- coding: utf-8 -*-

.. _TutosMuseums:

Create a data-oriented web application CubicWeb 4
=================================================

Introduction
------------

This tutorial aims to demonstrate how to create a data-oriented web application
using CubicWeb 4. This application will be a catalog of museums using data_
from the French Ministry of Culture.

.. _data: https://data.culture.gouv.fr/explore/dataset/liste-et-localisation-des-musees-de-france/export/

To get started, we will setup a development environment for CubicWeb, then
create an instance and check that it is accessible with a web browser.

As a second step, we will define the data model of the application, re-create
the database of the instance with this new schema, then check that a generic
admin interface provided by the `web` cube (server component) allows us to add
and display cities and museums.

.. _web: https://forge.extranet.logilab.fr/cubicweb/cubes/web

As a third step, we will quickly develop an independant user interface using
NextJS and ReactJS, that will query the database using the RQL language and
display the museums on a map.

As a fourth and final step, we will load the data downloaded form the repository
of the French Ministry of Culture, then expose that data using content
negotiation and the RDF standard.

You can find the code of the finished tutorial in our forge, by looking for the
cube tuto_.

.. _tuto: https://forge.extranet.logilab.fr/cubicweb/cubes/tuto/
.. toctree::
   :maxdepth: 2

   getting-started
   develop-app
   develop-ui
   enhance-views
   data-management

