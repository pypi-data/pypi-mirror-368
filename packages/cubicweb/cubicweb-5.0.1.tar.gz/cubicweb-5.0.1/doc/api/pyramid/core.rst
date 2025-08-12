.. _core_module:

:mod:`cubicweb.pyramid.core`
----------------------------

.. automodule:: cubicweb.pyramid.core

    .. autofunction:: includeme


    .. autofunction:: repo_connect
    .. autofunction:: get_principals

    .. autofunction:: _cw_session
    .. autofunction:: _cw_cnx


Some code that used to be in cubicweb.pyramid.core has been moved to cubicweb_web.bwcompat:

.. automodule:: cubicweb_web.bwcompat
    .. autofunction:: cw_to_pyramid
    .. autofunction:: render_view

    .. autoclass:: CubicWebPyramidRequest
        :show-inheritance:
        :members:

    .. autofunction:: _cw_request
