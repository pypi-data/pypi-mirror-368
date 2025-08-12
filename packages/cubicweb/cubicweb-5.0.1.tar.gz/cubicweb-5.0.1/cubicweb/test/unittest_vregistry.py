# copyright 2003-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from os.path import join

from logilab.common.testlib import unittest_main, TestCase

from cubicweb import CW_SOFTWARE_ROOT as BASE
from cubicweb.cwvreg import CWRegistryStore, UnknownProperty
from cubicweb.devtools.apptest_config import ApptestConfiguration
from cubicweb.entity import EntityAdapter


class YesSchema:
    def __contains__(self, something):
        return True


class VRegistryTC(TestCase):
    def setUp(self):
        config = ApptestConfiguration("data", __file__)
        self.vreg = CWRegistryStore(config)
        config.bootstrap_cubes()
        self.vreg.schema = config.load_schema()

    def test_load_interface_based_vobjects(self):
        assert len(self.vreg) == 0

        self.vreg.init_registration([])
        assert "etypes" not in self.vreg

        self.vreg.load_file(
            join(BASE, "entities", "__init__.py"), "cubicweb.entities.__init__"
        )
        assert "etypes" in self.vreg

        self.vreg.initialization_completed()
        assert "etypes" in self.vreg

    def test_load_subinterface_based_appobjects(self):
        assert len(self.vreg) == 0

        # we've to emulate register_objects to add custom MyCard objects
        path = [
            join(BASE, "entities", "__init__.py"),
            join(BASE, "entities", "adapters.py"),
        ]
        filemods = self.vreg.init_registration(path, None)
        assert "etypes" not in self.vreg
        assert "adapters" not in self.vreg

        for filepath, modname in filemods:
            self.vreg.load_file(filepath, modname)

        assert "etypes" in self.vreg
        assert "adapters" in self.vreg

        class CardIDownloadableAdapter(EntityAdapter):
            __regid__ = "IDownloadable"

        self.vreg._loadedmods[__name__] = {}
        self.vreg.register(CardIDownloadableAdapter)
        self.vreg.initialization_completed()

        assert "IDownloadable" in self.vreg["adapters"]
        assert CardIDownloadableAdapter in self.vreg["adapters"]["IDownloadable"]

    def test_properties(self):
        self.vreg.reset()
        self.assertNotIn("system.version.cubicweb", self.vreg["propertydefs"])
        self.assertTrue(self.vreg.property_info("system.version.cubicweb"))
        self.assertRaises(
            UnknownProperty, self.vreg.property_info, "a.non.existent.key"
        )


if __name__ == "__main__":
    unittest_main()
