# copyright 2003-2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""Fake objects to ease testing of cubicweb without a fully working environment"""

from contextlib import contextmanager

from logilab.database import get_db_helper

from cubicweb.cwvreg import CWRegistryStore
from cubicweb.devtools import BASE_URL
from cubicweb.devtools.apptest_config import ApptestConfiguration
from cubicweb.req import RequestSessionAndConnectionBase


class FakeConfig(dict, ApptestConfiguration):
    translations = {}
    uiprops = {}
    apphome = None
    debugmode = False

    def __init__(self, appid="data", apphome=None, cubes=()):
        self.appid = appid
        self.apphome = apphome
        self._cubes = cubes
        self["auth-mode"] = "cookie"
        self["uid"] = None
        self["base-url"] = BASE_URL
        self["rql-cache-size"] = 3000
        self.datadir_url = BASE_URL + "data/"

    def cubes(self, expand=False):
        return self._cubes

    def sources(self):
        return {"system": {"db-driver": "sqlite"}}


class FakeCWRegistryStore(CWRegistryStore):
    def property_value(self, key):
        if key == "ui.language":
            return "en"
        assert False


class FakeUser:
    login = "toto"
    eid = 0

    def in_groups(self, groups):
        return True


class FakeConnection(RequestSessionAndConnectionBase):
    def __init__(self, repo=None, user=None, vreg=None):
        self.repo = repo
        if vreg is None:
            vreg = getattr(self.repo, "vreg", None)
        if vreg is None:
            vreg = FakeCWRegistryStore(FakeConfig(), initlog=False)
        self.vreg = vreg
        self.cnxset = FakeConnectionsSet()
        self.user = user or FakeUser()
        self.is_internal_session = False
        self.transaction_data = {}

    def execute(self, *args, **kwargs):
        pass

    def commit(self, *args):
        self.transaction_data.clear()

    def system_sql(self, sql, args=None):
        pass

    def set_entity_cache(self, entity):
        pass

    def security_enabled(self, read=False, write=False):
        class FakeCM:
            def __enter__(self):
                pass

            def __exit__(self, exctype, exc, traceback):
                pass

        return FakeCM()

    # for use with enabled_security context manager
    read_security = write_security = True

    @contextmanager
    def running_hooks_ops(self):
        yield


class FakeRepo:
    querier = None

    def __init__(self, schema, vreg=None, config=None):
        self.eids = {}
        self._count = 0
        self.schema = schema
        self.config = config or FakeConfig()
        self.vreg = vreg or FakeCWRegistryStore(self.config, initlog=False)
        self.vreg.schema = schema


class FakeSource:
    dbhelper = get_db_helper("sqlite")

    def __init__(self, uri):
        self.uri = uri


class FakeConnectionsSet:
    def source(self, uri):
        return FakeSource(uri)
