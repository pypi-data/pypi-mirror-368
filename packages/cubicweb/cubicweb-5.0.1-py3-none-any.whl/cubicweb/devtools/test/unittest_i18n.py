# copyright 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""unit tests for i18n messages generator"""

import os.path as osp
import sys
from contextlib import contextmanager
from io import StringIO
from unittest import main
from unittest.mock import patch

from cubicweb.devtools import devctl
from cubicweb.devtools.testlib import BaseTestCase

DATADIR = osp.join(osp.abspath(osp.dirname(__file__)), "data")


TESTCUBE_DIR = osp.join(DATADIR, "libpython", "cubicweb_i18ntestcube")


class CustomMessageExtractor(devctl.I18nCubeMessageExtractor):
    blacklist = devctl.I18nCubeMessageExtractor.blacklist | {"excludeme"}


@contextmanager
def capture_stdout():
    stream = StringIO()
    sys.stdout = stream
    yield stream
    stream.seek(0)
    sys.stdout = sys.__stdout__


class I18nCollectorTest(BaseTestCase):
    def test_i18ncube_py_collection(self):
        extractor = CustomMessageExtractor(DATADIR, TESTCUBE_DIR)
        collected = extractor.collect_py()
        expected = [
            osp.join(TESTCUBE_DIR, path)
            for path in ("__init__.py", "__pkginfo__.py", "schema.py")
        ]
        self.assertCountEqual(expected, collected)

    def test_i18ncube_js_collection(self):
        extractor = CustomMessageExtractor(DATADIR, TESTCUBE_DIR)
        collected = extractor.collect_js()
        self.assertCountEqual([], collected, [])
        extractor.blacklist = ()  # don't ignore anything
        collected = extractor.collect_js()
        expected = [osp.join(TESTCUBE_DIR, "node_modules/cubes.somefile.js")]
        self.assertCountEqual(expected, collected)

    class FakeMessageExtractor(devctl.I18nCubeMessageExtractor):
        """Fake message extractor that generates no pot file."""

        def generate_pot_file(self):
            return None

    @patch("pkg_resources.load_entry_point", return_value=FakeMessageExtractor)
    def test_cube_custom_extractor(self, mock_load_entry_point):
        distname = "cubicweb_i18ntestcube"  # same for new and legacy layout
        cubedir = osp.join(DATADIR, "libpython", "cubicweb_i18ntestcube")
        with capture_stdout() as stream:
            devctl.update_cube_catalogs(cubedir)
        self.assertIn("no message catalog for cube i18ntestcube", stream.read())
        mock_load_entry_point.assert_called_once_with(
            distname, "cubicweb.i18ncube", "i18ntestcube"
        )
        mock_load_entry_point.reset_mock()


if __name__ == "__main__":
    main()
