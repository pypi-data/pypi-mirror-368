.. warning::
    Starting from *CubicWeb* version 4.0 all code related to **generating html
    views** has been moved to the Cube `cubicweb_web
    <https://forge.extranet.logilab.fr/cubicweb/cubes/web>`_.

    If you want to migrate a project from 3.38 to 4.* while still using all the
    html views you need to both install the `cubicweb_web` cube AND add it to
    your dependencies and run :py:obj:`add_cube('web')`.

    `cubicweb_web` can be installed from pypi this way::

        pip install cubicweb_web

    We don't plan to maintain the features in `cubicweb_web` in the long run;
    we are moving to a full javascript frontend using both
    `cubicweb_api <https://forge.extranet.logilab.fr/cubicweb/cubes/api>`_ (which
    exposes a HTTP API) and `@cubicweb/client
    <https://www.npmjs.com/package/@cubicweb/client>`_ as a frontend
    javascript toolkit.

    In the long run `cubicweb_api` will be merged inside of *CubicWeb*.
