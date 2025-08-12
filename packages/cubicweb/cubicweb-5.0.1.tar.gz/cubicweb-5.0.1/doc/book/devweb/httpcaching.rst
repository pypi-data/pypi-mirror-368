.. -*- coding: utf-8 -*-

.. include:: warning.rst

.. _HttpCaching:

HTTP cache management
=====================

.. automodule:: cubicweb_web.httpcache

Cache policies
--------------
.. autoclass:: cubicweb_web.httpcache.NoHTTPCacheManager
.. autoclass:: cubicweb_web.httpcache.MaxAgeHTTPCacheManager
.. autoclass:: cubicweb_web.httpcache.EtagHTTPCacheManager
.. autoclass:: cubicweb_web.httpcache.EntityHTTPCacheManager

Exception
---------
.. autoexception:: cubicweb_web.httpcache.NoEtag

Helper functions
----------------
.. autofunction:: cubicweb_web.httpcache.set_http_cache_headers

.. NOT YET AVAILABLE IN STABLE autofunction:: cubicweb_web.httpcache.lastmodified
