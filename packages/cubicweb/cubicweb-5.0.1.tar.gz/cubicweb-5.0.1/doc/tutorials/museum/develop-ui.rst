.. -*- coding: utf-8 -*-

Developping the user interface
------------------------------

Customize museum primary view
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The 'primary' view (i.e. any view with the identifier set to 'primary') is the one used to
display all the information about a single entity. The standard primary view is one
of the most sophisticated views of all. It has several customisation points, but
its power comes with `uicfg`, allowing you to control it without having to
subclass it. More information are available here : :ref:`primary_view`.

Now we have several museums, we want an easier way to identify its city when we are on the
museum page. To achieve this, we will subclass `PrimaryView` and override `render_entity_title`
method in :file:`tuto/cubicweb_tuto/views.py`:

.. sourcecode:: python

    from cubicweb.predicates import is_instance
    from cubicweb_web.views.primary import PrimaryView

    class MuseumPrimaryView(PrimaryView):
        __select__ = is_instance("Museum")

        def render_entity_title(self, entity):
            """Renders the entity title.
            """
            city_name = entity.is_in[0].name
            self.w(f"<h1>{entity.name} ({city_name})</h1>")

As stated before, CubicWeb comes with a system of views selection. This system is, among other
things, based on selectors declared with `__select__` (you'll find more information about this
in the :ref:`VRegistryIntro` chapter). As we want to customize museum primary view, we use
`__select__ = is_instance("Museum")` to tell CubicWeb this is only applicable when we display
a `Museum` entity.

Then, we just override the method used to compute title to add the city name. To reach the city
name, we use the relation `is_in` and choose the first and only one linked city, then ask
for its name.

.. image:: ../../images/tutos-museum_museum_with_city_name.png
   :alt: Museum entity customized with city name view.

Use entities.py to add more logic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|cubicweb| provides an ORM to easily programmaticaly manipulate
entities. By default, entity types are instances of the :class:`AnyEntity` class,
which holds a set of predefined methods as well as property automatically generated for
attributes/relations of the type it represents.

You can redefine each entity to provide additional methods or whatever you want
to help you write your application. Customizing an entity requires that your
entity:

- inherits from :class:`cubicweb.entities.AnyEntity` or any subclass

- defines a :attr:`__regid__` linked to the corresponding data type of your schema

You may then want to add your own methods, override default implementation of some
method, etc...

As we may want reuse our custom museum title (with city name, as defined in previous section),
we will define it as a property of our Museum class.

To do so, write this code in :file:`tuto/cubicweb_tuto/entities.py`:

.. sourcecode:: python

    from cubicweb.entities import AnyEntity, fetch_config

    class Museum(AnyEntity):
        __regid__ = "Museum"

        @property
        def title_with_city(self):
            return f"{self.name} ({self.is_in[0].name})"

Then, we just have to use it our previously defined view in :file:`tuto/cubicweb_tuto/views.py`:

.. sourcecode:: python

    from cubicweb.predicates import is_instance
    from cubicweb_web.views.primary import PrimaryView

    class MuseumPrimaryView(PrimaryView):
        __select__ = is_instance("Museum")

        def render_entity_title(self, entity):
            """Renders the entity title.
            """
            self.w(f"<h1>{entity.title_with_city}</h1>")

Conclusion
~~~~~~~~~~

In this first part, we laid the cornerstone of our futur site, and discovered some core
functionalities of |Cubicweb|. In next parts, we will improve views and see how to import all
our data.
