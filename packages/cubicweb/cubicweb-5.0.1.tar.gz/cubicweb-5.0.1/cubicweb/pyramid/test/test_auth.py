# copyright 2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""Tests for cubicweb.pyramid.auth module."""

from http import cookiejar as http_cookiejar

from pyramid import security
from pyramid.settings import asbool
from pyramid.response import Response
from pyramid.httpexceptions import HTTPSeeOther

from cubicweb.pyramid.test import PyramidCWTest


def login_view(request):
    """
    Dummy testing view that only stimulate login to call out auth policy.
    It doesn't check the password or anything else.
    """
    repo = request.registry["cubicweb.repository"]

    with repo.internal_cnx() as cnx:
        user_eid = cnx.find("CWUser", login="admin")[0][0]

    headers = security.remember(
        request,
        user_eid,
        persistent=asbool(request.params.get("__setauthcookie", False)),
    )

    raise HTTPSeeOther("/", headers=headers)


def logout_view(request):
    headers = security.forget(request)
    raise HTTPSeeOther("/", headers=headers)


def current_user_view(request):
    return Response(request.cw_cnx.user.login)


class PyramidCWAuthTktAuthenticationPolicyTC(PyramidCWTest):
    anonymous_allowed = True

    def includeme(self, config):
        config.include("cubicweb.pyramid.auth")
        config.include("cubicweb.pyramid.session")

        config.add_route("login", "/login")
        config.add_route("logout", "/logout")
        config.add_route("current_user", "/current_user")

        config.add_view(login_view, route_name="login")
        config.add_view(logout_view, route_name="logout")
        config.add_view(current_user_view, route_name="current_user")

    def test_remember(self):
        assert self.webapp.get("/current_user").text == "anon"
        self.webapp.get("/login")
        assert self.webapp.get("/current_user").text == "admin"

    def test_remember_and_forget(self):
        assert self.webapp.get("/current_user").text == "anon"
        self.webapp.get("/login")
        assert self.webapp.get("/current_user").text == "admin"
        self.webapp.get("/logout")
        assert self.webapp.get("/current_user").text == "anon"

    def test_cant_reuse_loggedout_cookie(self):
        assert self.webapp.get("/current_user").text == "anon"
        self.webapp.get("/login")

        # simulate that the cookies have been stolen and that someone attempts to reuse them
        stolen_jar = http_cookiejar.CookieJar()
        for cookie in self.webapp.cookiejar:
            stolen_jar.set_cookie(cookie)

        assert self.webapp.get("/current_user").text == "admin"
        self.webapp.get("/logout")
        assert self.webapp.get("/current_user").text == "anon"

        self.webapp.cookiejar = stolen_jar

        # check that we can't reuse the cookie
        assert self.webapp.get("/current_user").text == "anon"


if __name__ == "__main__":
    import unittest

    unittest.main()
