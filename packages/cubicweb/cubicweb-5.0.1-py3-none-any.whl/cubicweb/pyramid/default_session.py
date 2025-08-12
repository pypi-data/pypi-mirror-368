# copyright 2023 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
A very simple default session for CubicWeb when no other sessions are set
"""
import logging

from pyramid.session import SignedCookieSessionFactory


logger = logging.getLogger("cubicweb.pyramid.security.session")


def includeme(config):
    secret = config.registry.settings["cubicweb.session.secret"]
    session_factory = SignedCookieSessionFactory(secret)
    config.set_session_factory(session_factory)
    logger.warning(
        "You are currently using the pyramid "
        "default session factory, which is unsecure.\n"
        "Do not use it in production! Prefer using pyramid_session_redis. "
        "See the documentation for more information."
    )
