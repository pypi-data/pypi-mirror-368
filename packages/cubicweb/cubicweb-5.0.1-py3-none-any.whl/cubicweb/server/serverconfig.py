# copyright 2003-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""server.serverconfig definition"""

import sys
from io import StringIO
from os.path import join

import logilab.common.configuration as lgconfig

from cubicweb.server import SOURCE_TYPES

USER_OPTIONS = (
    (
        "login",
        {
            "type": "string",
            "default": "admin",
            "help": "cubicweb manager account's login " "(this user will be created)",
            "level": 0,
        },
    ),
    (
        "password",
        {
            "type": "password",
            "default": lgconfig.REQUIRED,
            "help": "cubicweb manager account's password",
            "level": 0,
        },
    ),
)


class SourceConfiguration(lgconfig.Configuration):
    def __init__(self, appconfig, options):
        self.appconfig = appconfig  # has to be done before super call
        super().__init__(options=options)

    # make Method('default_instance_id') usable in db option defs (in native.py)
    def default_instance_id(self):
        return self.appconfig.appid

    def input_option(self, option, optdict, inputlevel):
        try:
            dbdriver = self["db-driver"]
        except lgconfig.OptionError:
            pass
        else:
            if dbdriver == "sqlite":
                if option in ("db-user", "db-password"):
                    return
                if option == "db-name":
                    optdict = optdict.copy()
                    optdict["help"] = "path to the sqlite database"
                    optdict["default"] = join(
                        self.appconfig.appdatahome, self.appconfig.appid + ".sqlite"
                    )
        super().input_option(option, optdict, inputlevel)


def ask_source_config(appconfig, type, inputlevel=0):
    options = SOURCE_TYPES[type].options
    sconfig = SourceConfiguration(appconfig, options=options)
    sconfig.input_config(inputlevel=inputlevel)
    return sconfig


def generate_source_config(sconfig, encoding=sys.stdin.encoding):
    """serialize a repository source configuration as text"""
    stream = StringIO()
    optsbysect = list(sconfig.options_by_section())
    assert (
        len(optsbysect) == 1
    ), "all options for a source should be in the same group, got %s" % [
        x[0] for x in optsbysect
    ]
    lgconfig.ini_format(stream, optsbysect[0][1], encoding)
    return stream.getvalue()
