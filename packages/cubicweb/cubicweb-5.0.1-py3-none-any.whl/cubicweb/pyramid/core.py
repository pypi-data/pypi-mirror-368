# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2014-2016 UNLISH S.A.S. (Montpellier, FRANCE), all rights reserved.
#
# contact https://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <https://www.gnu.org/licenses/>.

"""Binding of CubicWeb connection to Pyramid request."""

import logging

from pyramid import httpexceptions

from cubicweb.pyramid import tools
from cubicweb.server import session as cwsession

log = logging.getLogger(__name__)


class Connection(cwsession.Connection):
    """A specialised Connection that access the session data through a
    property.

    This behavior makes sure the actual session data is not loaded until
    actually accessed.
    """

    def __init__(self, session, *args, **kw):
        super().__init__(session._repo, session._user, *args, **kw)
        self.session = session
        self.lang = session._cached_lang

    def _get_session_data(self):
        return self.session.data

    def _set_session_data(self, data):
        pass

    _session_data = property(_get_session_data, _set_session_data)


class Session:
    """A Session that access the session data through a property.

    Along with :class:`Connection`, it avoid any load of the pyramid session
    data until it is actually accessed.
    """

    def __init__(self, pyramid_request, user, repo):
        self._pyramid_request = pyramid_request
        self._user = user
        self._repo = repo

    @property
    def anonymous_session(self):
        # XXX for now, anonymous_user only exists in webconfig (and testconfig).
        # It will only be present inside all-in-one instance.
        # there is plan to move it down to global config.
        if not hasattr(self._repo.config, "anonymous_user"):
            # not a web or test config, no anonymous user
            return False
        return self._user.login == self._repo.config.anonymous_user()[0]

    def get_data(self):
        if not getattr(self, "_protect_data_access", False):
            self._data_accessed = True
            return self._pyramid_request.session

    def set_data(self, data):
        if getattr(self, "_data_accessed", False):
            self._pyramid_request.session.clear()
            self._pyramid_request.session.update(data)

    data = property(get_data, set_data)

    def new_cnx(self):
        self._protect_data_access = True
        try:
            return Connection(self)
        finally:
            self._protect_data_access = False


def _cw_cnx(request):
    """Obtains a cw session from a pyramid request

    The connection will be commited or rolled-back in a request finish
    callback (this is temporary, we should make use of the transaction manager
    in a later version).

    Not meant for direct use, use ``request.cw_cnx`` instead.

    :param request: A pyramid request
    :returns type: :class:`cubicweb.server.session.Connection`
    """
    session = request.cw_session
    if session is None:
        return None

    cnx = session.new_cnx()

    def commit_state(cnx):
        return cnx.commit_state

    def cleanup(request):
        try:
            if request.exception is not None and not isinstance(
                request.exception,
                (httpexceptions.HTTPSuccessful, httpexceptions.HTTPRedirection),
            ):
                cnx.rollback()
            elif commit_state(cnx) == "uncommitable":
                cnx.rollback()
            else:
                cnx.commit()
        finally:
            cnx.__exit__(None, None, None)

    request.add_finished_callback(cleanup)
    cnx.__enter__()
    return cnx


def repo_connect(request, repo, eid):
    """A lightweight version of
    :meth:`cubicweb.server.repository.Repository.connect` that does not keep
    track of opened sessions, removing the need of closing them"""
    user, lang = tools.cached_build_user(repo, eid)
    session = Session(request, user, repo)
    session._cached_lang = lang
    tools.cnx_attach_entity(session, user)
    return session


def _cw_session(request):
    """Obtains a cw session from a pyramid request

    :param request: A pyramid request
    :returns type: :class:`cubicweb.server.session.Session`

    Not meant for direct use, use ``request.cw_session`` instead.
    """
    repo = request.registry["cubicweb.repository"]

    if not request.authenticated_userid:
        eid = request.registry.get("cubicweb.anonymous_eid")
        if eid is None:
            return None
        session = repo_connect(request, repo, eid=eid)
    else:
        session = request._cw_cached_session

    return session


def get_principals(login, request):
    """Returns the group names of the authenticated user.

    This function is meant to be used as an authentication policy callback.

    It also pre-open the cubicweb session and put it in
    request._cw_cached_session for later usage by :func:`_cw_session`.

    .. note::

        If the default authentication policy is not used, make sure this
        function gets called by the active authentication policy.

    :param login: A cubicweb user eid
    :param request: A pyramid request
    :returns: A list of group names
    """
    repo = request.registry["cubicweb.repository"]

    try:
        session = repo_connect(request, repo, eid=login)
        request._cw_cached_session = session
    except Exception:
        log.exception("Failed")
        raise

    with session.new_cnx() as cnx:
        with cnx.security_enabled(read=False):
            return {
                group
                for group, in cnx.execute(
                    "Any GN WHERE U in_group G, G name GN, U eid %(userid)s",
                    {"userid": login},
                )
            }


def includeme(config):
    """Enables the core features of Pyramid CubicWeb.

    Automatically called by the 'pyramid' command, or via
    ``config.include('cubicweb.pyramid.code')``. In the later case,
    the following registry entries must be defined first:

    'cubicweb.config'
        A cubicweb 'config' instance.

    'cubicweb.repository'
        The correponding cubicweb repository.

    'cubicweb.registry'
        The vreg.
    """
    repo = config.registry["cubicweb.repository"]

    with repo.internal_cnx() as cnx:
        login = config.registry["cubicweb.config"].anonymous_user()[0]
        if login is not None:
            config.registry["cubicweb.anonymous_eid"] = (
                cnx.find("CWUser", login=login).one().eid
            )

    config.add_request_method(_cw_session, name="cw_session", property=True, reify=True)
    config.add_request_method(_cw_cnx, name="cw_cnx", property=True, reify=True)

    cwcfg = config.registry["cubicweb.config"]
    for cube in cwcfg.cubes():
        pkgname = f"cubicweb_{cube}"
        mod = __import__(pkgname)
        if hasattr(mod, "includeme"):
            config.include(pkgname)
