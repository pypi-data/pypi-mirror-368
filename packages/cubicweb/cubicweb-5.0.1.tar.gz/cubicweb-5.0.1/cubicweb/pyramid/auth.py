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
"""
CubicWeb AuthTkt authentication policy
--------------------------------------

When using the `cubicweb.pyramid.auth` module, which is the default in most
cases, you may have to configure the behaviour of these authentication
policies using standard's Pyramid configuration. You may want to configure in
your pyramid configuration file:

:Session Authentication:

    This is a `AuthTktAuthenticationPolicy`_ so you may overwrite default
    configuration values by adding configuration entries using the prefix
    ``cubicweb.auth.authtkt.session``. Default values are:

    ::

        cubicweb.auth.authtkt.session.hashalg = sha512
        cubicweb.auth.authtkt.session.cookie_name = auth_tkt
        cubicweb.auth.authtkt.session.timeout = 1200
        cubicweb.auth.authtkt.session.reissue_time = 120
        cubicweb.auth.authtkt.session.http_only = True
        cubicweb.auth.authtkt.session.secure = True


:Persistent Authentication:

    This is also a `AuthTktAuthenticationPolicy`_. It is used when persistent
    sessions are activated (typically when using the cubicweb-rememberme_
    cube). You may overwrite default configuration values by adding
    configuration entries using the prefix
    ``cubicweb.auth.authtkt.persistent``. Default values are:

    ::

        cubicweb.auth.authtkt.persistent.hashalg = sha512
        cubicweb.auth.authtkt.persistent.cookie_name = pauth_tkt
        cubicweb.auth.authtkt.persistent.max_age = 3600*24*30
        cubicweb.auth.authtkt.persistent.reissue_time = 3600*24
        cubicweb.auth.authtkt.persistent.http_only = True
        cubicweb.auth.authtkt.persistent.secure = True


.. Warning:: Legacy timeout values from the instance's
             ``all-in-one.conf`` are **not** used at all (``
             http-session-time`` and ``cleanup-session-time``)

.. _CubicWeb: https://www.cubicweb.org/
.. _`cubicweb-rememberme`: \
    https://forge.extranet.logilab.fr/cubicweb/cubes/rememberme
.. _AuthTktAuthenticationPolicy: \
    http://docs.pylonsproject.org/projects/pyramid/en/latest/api/authentication.html#pyramid.authentication.AuthTktAuthenticationPolicy


Secrets
~~~~~~~
There are a number of secrets to configure in ``pyramid.ini``. They
should be different one from each other, as explained in `Pyramid's
documentation`_.

For the record, regarding authentication:

:cubicweb.auth.authtkt.session.secret: This secret is used to encrypt
   the authentication cookie.

:cubicweb.auth.authtkt.persistent.secret: This secret is used to
   encrypt the persistent authentication cookie.
"""

import logging

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.settings import asbool
from pyramid_multiauth import MultiAuthenticationPolicy
from zope.interface import implementer

from cubicweb.pyramid.core import get_principals
from cubicweb.pyramid.config import get_random_secret_key

log = logging.getLogger(__name__)


@implementer(IAuthenticationPolicy)
class UpdateLoginTimeAuthenticationPolicy:
    """An authentication policy that update the user last_login_time.

    The update is done in the 'remember' method, which is called by the login
    views login,

    Usually used via :func:`includeme`.
    """

    def authenticated_userid(self, request):
        pass

    def effective_principals(self, request):
        return ()

    def remember(self, request, principal, **kw):
        repo = request.registry["cubicweb.repository"]
        with repo.internal_cnx() as cnx:
            try:
                cnx.execute(
                    "SET U last_login_time NOW WHERE U eid %(user)s",
                    {"user": principal},
                )
                cnx.commit()
            except Exception:
                log.exception("Failed to update last_login_time")
        return ()

    def forget(self, request):
        return ()


class CWAuthTktAuthenticationPolicy(AuthTktAuthenticationPolicy):
    """
    An authentication policy that inhibate the call the 'remember' if a
    'persistent' argument is passed to it, and is equal to the value that
    was passed to the constructor.

    This allow to combine two policies with different settings and select them
    by just setting this argument.

    This also implement a ticket mechanism to invalidate a user cookie once it
    has logged out (to prevent a cookie reuse after a logout, pyramid doesn't
    provide this mechanism because it doesn't have any storage by default).

    This is done by storing a randomly generated token (that is an auth ticket)
    both in the user encrypted cookie and in its session. On logout, the ticket
    is marked as invalid in the session thus preventing any further use of this
    cookie.
    """

    def __init__(self, secret, persistent, defaults=None, prefix="", **settings):
        self.persistent = persistent
        unset = object()
        kw = {}
        if defaults is None:
            defaults = {}

        # load string settings
        for name in ("cookie_name", "path", "domain", "hashalg", "samesite"):
            value = settings.get(prefix + name, defaults.get(name, unset))
            if value is not unset:
                kw[name] = value

        # load boolean settings
        for name in (
            "secure",
            "include_ip",
            "http_only",
            "wild_domain",
            "parent_domain",
            "debug",
        ):
            value = settings.get(prefix + name, defaults.get(name, unset))
            if value is not unset:
                kw[name] = asbool(value)

        # load int settings
        for name in ("timeout", "reissue_time", "max_age"):
            value = settings.get(prefix + name, defaults.get(name, unset))
            if value is not unset and value is not None:
                kw[name] = int(value)

        super().__init__(secret, **kw)

    def _get_authentication_ticket_token(self, request):
        cookie_data = self.cookie.identify(request)
        if not cookie_data:
            return None

        authentication_ticket_token = [
            token for token in cookie_data["tokens"] if token.startswith("authticket_")
        ]

        if authentication_ticket_token:
            return authentication_ticket_token[0]
        else:
            return None

    def remember(self, request, userid, max_age=None, tokens=(), **kwargs):
        """
        Generate an auth ticket on login and stores it in the user session
        """

        # we are not handling a request for our kind of auth
        # for example it's a request for pauth_tkt but we are auth_tkt
        if "persistent" in kwargs and kwargs.pop("persistent") != self.persistent:
            return ()

        log.debug(f"generating an authentication ticket for user {userid}")

        # generate a new authentication ticket
        authentication_ticket_token = "authticket_" + get_random_secret_key()
        tokens += (authentication_ticket_token,)
        request.session["authentication_ticket"] = authentication_ticket_token

        return super().remember(
            request, userid, max_age=max_age, tokens=tokens, **kwargs
        )

    def unauthenticated_userid(self, request):
        """
        Validate that the current auth ticket, if it exists, is still valid
        """
        authentication_ticket_token = self._get_authentication_ticket_token(request)

        # auth hasn't finished yet
        if authentication_ticket_token is None:
            return None

        # no user stored in the cookie
        user_id = super().unauthenticated_userid(request)
        if not user_id:
            return None

        # likely when a new auth hasn't finished yet
        if authentication_ticket_token == request.session.get("authentication_ticket"):
            log.debug(
                "user %s authentication ticket is valid, validating user", user_id
            )
            return user_id
        else:
            log.debug(
                "could not find authentication ticket for user %s, preventing "
                "authentication (this could be a concurrent request during login or logout, not "
                "especially an attack",
                user_id,
            )
            return None

    def forget(self, request):
        """
        Invalidate the auth ticket if it's present
        """
        if "authentication_ticket" in request.session:
            log.debug("logout, deleting authentication ticket on request %s", request)
            # invalidate the ticket
            del request.session["authentication_ticket"]

        return super().forget(request)


def includeme(config):
    """Activate the CubicWeb AuthTkt authentication policy.

    It is automatically included by the configuration system, unless the
    following entry is added to the :ref:`pyramid_settings`:

    .. code-block:: ini

        cubicweb.pyramid.auth = no

    """
    settings = config.registry.settings

    policies = []

    if asbool(settings.get("cubicweb.auth.update_login_time", True)):
        policies.append(UpdateLoginTimeAuthenticationPolicy())

    if asbool(settings.get("cubicweb.auth.authtkt", True)):
        session_prefix = "cubicweb.auth.authtkt.session."
        persistent_prefix = "cubicweb.auth.authtkt.persistent."

        session_secret = settings.get(session_prefix + "secret", "notsosecret")
        persistent_secret = settings.get(persistent_prefix + "secret", "notsosecret")

        policies.append(
            CWAuthTktAuthenticationPolicy(
                session_secret,
                False,
                defaults={
                    "hashalg": "sha512",
                    "cookie_name": "auth_tkt",
                    "timeout": 1200,
                    "reissue_time": 120,
                    "http_only": True,
                    "secure": True,
                },
                prefix=session_prefix,
                **settings,
            )
        )

        policies.append(
            CWAuthTktAuthenticationPolicy(
                persistent_secret,
                True,
                defaults={
                    "hashalg": "sha512",
                    "cookie_name": "pauth_tkt",
                    "max_age": 3600 * 24 * 30,
                    "reissue_time": 3600 * 24,
                    "http_only": True,
                    "secure": True,
                },
                prefix=persistent_prefix,
                **settings,
            )
        )

    kw = {}
    if asbool(settings.get("cubicweb.auth.groups_principals", True)):
        kw["callback"] = get_principals

    authpolicy = MultiAuthenticationPolicy(policies, **kw)
    config.registry["cubicweb.authpolicy"] = authpolicy

    config.set_authentication_policy(authpolicy)
    config.set_authorization_policy(ACLAuthorizationPolicy())
