# copyright 2003 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""unit tests for module cubicweb.server.migractions"""

import os.path as osp

from cubicweb import Binary
from cubicweb.devtools import startpgcluster, stoppgcluster
from cubicweb.server.test.unittest_storage import StorageTCBase

from cubicweb.server.test_migractions.unittest_migractions import MigrationTC

HERE = osp.dirname(osp.abspath(__file__))
migrschema = None


def setUpModule():
    startpgcluster(__file__)


def tearDownModule(*args):
    global migrschema
    del migrschema
    stoppgcluster(__file__)


class MigrationStorageCommandsTC(StorageTCBase, MigrationTC):
    def test_change_bfss_path(self):
        with self.mh() as (cnx, mh):
            file1 = mh.cmd_create_entity(
                "File",
                data_name="foo.pdf",
                data=Binary(b"xxx"),
                data_format="text/plain",
            )
            mh.commit()
            current_dir = osp.dirname(self.fspath(cnx, file1))

            mh.update_bfss_path(current_dir, "loutre", commit=True)

            self.assertEqual("loutre", osp.dirname(self.fspath(cnx, file1)))


if __name__ == "__main__":
    import unittest

    unittest.main()
