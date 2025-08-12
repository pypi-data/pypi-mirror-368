# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""Configuration for CubicWeb instances on top of a Pyramid application"""

import random
import string

from logilab.common.configuration import merge_options

from cubicweb.cwconfig import CubicWebConfiguration


def get_random_secret_key():
    """Return 50-character secret string"""
    chars = string.ascii_letters + string.digits
    secure_random = random.SystemRandom()

    return "".join([secure_random.choice(chars) for i in range(50)])


class AllInOneConfiguration(CubicWebConfiguration):
    """repository and web instance in the same Pyramid process"""

    name = "all-in-one"
    options = merge_options(
        (
            (
                "profile",
                {
                    "type": "string",
                    "default": None,
                    "help": (
                        "profile code and use the specified file to store stats if this option "
                        "is set"
                    ),
                    "group": "web",
                    "level": 3,
                },
            ),
            (
                "access-control-allow-origin",
                {
                    "type": "csv",
                    "default": (),
                    "help": 'comma-separated list of allowed origin domains or "*" for any domain',
                    "group": "web",
                    "level": 2,
                },
            ),
            (
                "access-control-allow-methods",
                {
                    "type": "csv",
                    "default": (),
                    "help": "comma-separated list of allowed HTTP methods",
                    "group": "web",
                    "level": 2,
                },
            ),
            (
                "access-control-max-age",
                {
                    "type": "int",
                    "default": None,
                    "help": "maximum age of cross-origin resource sharing (in seconds)",
                    "group": "web",
                    "level": 2,
                },
            ),
            (
                "access-control-expose-headers",
                {
                    "type": "csv",
                    "default": (),
                    "help": (
                        "comma-separated list of HTTP headers the application "
                        "declare in response to a preflight request"
                    ),
                    "group": "web",
                    "level": 2,
                },
            ),
            (
                "access-control-allow-headers",
                {
                    "type": "csv",
                    "default": (),
                    "help": (
                        "comma-separated list of HTTP headers the application may set in the "
                        "response"
                    ),
                    "group": "web",
                    "level": 2,
                },
            ),
            (
                "port",
                {
                    "type": "int",
                    "default": None,
                    "help": "http server port number (default to 8080)",
                    "group": "web",
                    "level": 0,
                },
            ),
            (
                "interface",
                {
                    "type": "string",
                    "default": "127.0.0.1",
                    "help": "http server address on which to listen (default to local requests)",
                    "group": "web",
                    "level": 1,
                },
            ),
        )
        + CubicWebConfiguration.options
    )
