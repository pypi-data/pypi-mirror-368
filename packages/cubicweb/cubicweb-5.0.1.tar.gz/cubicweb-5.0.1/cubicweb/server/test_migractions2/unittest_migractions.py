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

from cubicweb import ExecutionError
from cubicweb.devtools import startpgcluster, stoppgcluster
from cubicweb.server.sqlutils import SQL_PREFIX
from cubicweb.server.test_migractions.unittest_migractions import MigrationTC

HERE = osp.dirname(osp.abspath(__file__))
migrschema = None


def setUpModule():
    startpgcluster(__file__)


def tearDownModule(*args):
    global migrschema
    del migrschema
    if hasattr(MigrationCommandsComputedTC, "origschema"):
        del MigrationCommandsComputedTC.origschema
    stoppgcluster(__file__)


class MigrationCommandsComputedTC(MigrationTC):
    """Unit tests for computed relations and attributes"""

    appid = "datacomputed"

    def setUp(self):
        MigrationTC.setUp(self)
        # ensure vregistry is reloaded, needed by generated hooks for computed
        # attributes
        self.repo.vreg.set_schema(self.repo.schema)

    def test_computed_relation_add_relation_definition(self):
        self.assertNotIn("works_for", self.schema)
        with self.mh() as (cnx, mh):
            with self.assertRaises(ExecutionError) as exc:
                mh.cmd_add_relation_definition("Employee", "works_for", "Company")
        self.assertEqual(
            str(exc.exception),
            "Cannot add a relation definition for a computed " "relation (works_for)",
        )

    def test_computed_relation_drop_relation_definition(self):
        self.assertIn("notes", self.schema)
        with self.mh() as (cnx, mh):
            with self.assertRaises(ExecutionError) as exc:
                mh.cmd_drop_relation_definition("Company", "notes", "Note")
        self.assertEqual(
            str(exc.exception),
            "Cannot drop a relation definition for a computed " "relation (notes)",
        )

    def test_computed_relation_add_relation_type(self):
        self.assertNotIn("works_for", self.schema)
        with self.mh() as (cnx, mh):
            mh.cmd_add_relation_type("works_for")
            self.assertIn("works_for", self.schema)
            self.assertEqual(
                self.schema["works_for"].rule,
                "O employees S, NOT EXISTS (O associates S)",
            )
            self.assertEqual(self.schema["works_for"].objects(), ("Company",))
            self.assertEqual(self.schema["works_for"].subjects(), ("Employee",))
            self.assertFalse(self.table_sql(mh, "works_for_relation"))
            e = cnx.create_entity("Employee")
            a = cnx.create_entity("Employee")
            cnx.create_entity("Company", employees=e, associates=a)
            cnx.commit()
            company = cnx.execute("Company X").get_entity(0, 0)
            self.assertEqual([e.eid], [x.eid for x in company.reverse_works_for])
            mh.rollback()

    def test_computed_relation_drop_relation_type(self):
        self.assertIn("notes", self.schema)
        with self.mh() as (cnx, mh):
            mh.cmd_drop_relation_type("notes")
        self.assertNotIn("notes", self.schema)

    def test_computed_relation_sync_schema_props_perms(self):
        self.assertIn("whatever", self.schema)
        with self.mh() as (cnx, mh):
            mh.cmd_sync_schema_props_perms("whatever")
            self.assertEqual(
                self.schema["whatever"].rule, "S employees E, O associates E"
            )
            self.assertEqual(self.schema["whatever"].objects(), ("Company",))
            self.assertEqual(self.schema["whatever"].subjects(), ("Company",))
            self.assertFalse(self.table_sql(mh, "whatever_relation"))

    def test_computed_relation_sync_schema_props_perms_security(self):
        with self.mh() as (cnx, mh):
            rdef = next(iter(self.schema["perm_changes"].relation_definitions.values()))
            self.assertEqual(
                rdef.permissions,
                {"add": (), "delete": (), "read": ("managers", "users")},
            )
            mh.cmd_sync_schema_props_perms("perm_changes")
            self.assertEqual(
                self.schema["perm_changes"].permissions, {"read": ("managers",)}
            )
            rdef = next(iter(self.schema["perm_changes"].relation_definitions.values()))
            self.assertEqual(
                rdef.permissions, {"add": (), "delete": (), "read": ("managers",)}
            )

    def test_computed_relation_sync_schema_props_perms_on_rdef(self):
        self.assertIn("whatever", self.schema)
        with self.mh() as (cnx, mh):
            with self.assertRaises(ExecutionError) as exc:
                mh.cmd_sync_schema_props_perms(("Company", "whatever", "Person"))
        self.assertEqual(
            str(exc.exception),
            "Cannot synchronize a relation definition for a computed "
            "relation (whatever)",
        )

    def test_computed_relation_rename_relation_type(self):
        with self.mh() as (cnx, mh):
            mh.cmd_rename_relation_type("to_be_renamed", "renamed")
        self.assertIn("renamed", self.schema)
        self.assertNotIn("to_be_renamed", self.schema)

    # computed attributes migration ############################################

    def setup_add_score(self):
        with self.admin_access.client_cnx() as cnx:
            assert not cnx.execute("Company X")
            c = cnx.create_entity("Company")
            e1 = cnx.create_entity("Employee", reverse_employees=c)
            cnx.create_entity("Note", note=2, concerns=e1)
            e2 = cnx.create_entity("Employee", reverse_employees=c)
            cnx.create_entity("Note", note=4, concerns=e2)
            cnx.commit()

    def assert_score_initialized(self, mh):
        self.assertEqual(
            self.schema["score"].relation_definitions["Company", "Float"].formula,
            "Any AVG(NN) WHERE X employees E, N concerns E, N note NN",
        )
        fields = self.table_schema(mh, f"{SQL_PREFIX}Company")
        self.assertEqual(fields[f"{SQL_PREFIX}score"], ("double precision", None))
        self.assertEqual(
            [[3.0]], mh.rqlexec("Any CS WHERE C score CS, C is Company").rows
        )

    def test_computed_attribute_add_relation_type(self):
        self.assertNotIn("score", self.schema)
        self.setup_add_score()
        with self.mh() as (cnx, mh):
            mh.cmd_add_relation_type("score")
            self.assertIn("score", self.schema)
            self.assertEqual(self.schema["score"].objects(), ("Float",))
            self.assertEqual(self.schema["score"].subjects(), ("Company",))
            self.assert_score_initialized(mh)

    def test_computed_attribute_add_attribute(self):
        self.assertNotIn("score", self.schema)
        self.setup_add_score()
        with self.mh() as (cnx, mh):
            mh.cmd_add_attribute("Company", "score")
            self.assertIn("score", self.schema)
            self.assert_score_initialized(mh)

    def assert_computed_attribute_dropped(self):
        self.assertNotIn("note20", self.schema)
        with self.mh() as (cnx, mh):
            fields = self.table_schema(mh, f"{SQL_PREFIX}Note")
        self.assertNotIn(f"{SQL_PREFIX}note20", fields)

    def test_computed_attribute_drop_type(self):
        self.assertIn("note20", self.schema)
        with self.mh() as (cnx, mh):
            mh.cmd_drop_relation_type("note20")
        self.assert_computed_attribute_dropped()

    def test_computed_attribute_drop_relation_definition(self):
        self.assertIn("note20", self.schema)
        with self.mh() as (cnx, mh):
            mh.cmd_drop_relation_definition("Note", "note20", "Int")
        self.assert_computed_attribute_dropped()

    def test_computed_attribute_drop_attribute(self):
        self.assertIn("note20", self.schema)
        with self.mh() as (cnx, mh):
            mh.cmd_drop_attribute("Note", "note20")
        self.assert_computed_attribute_dropped()

    def test_computed_attribute_sync_schema_props_perms_rtype(self):
        self.assertIn("note100", self.schema)
        with self.mh() as (cnx, mh):
            mh.cmd_sync_schema_props_perms("note100")
        rdef = self.schema["note100"].relation_definitions["Note", "Int"]
        self.assertEqual(
            rdef.formula_select.as_string(), "Any (N * 100) WHERE X note N, X is Note"
        )
        self.assertEqual(rdef.formula, "Any N*100 WHERE X note N")

    def test_computed_attribute_sync_schema_props_perms_rdef(self):
        self.setup_add_score()
        with self.mh() as (cnx, mh):
            mh.cmd_sync_schema_props_perms(("Note", "note100", "Int"))
            self.assertEqual(
                [[200], [400]], cnx.execute("Any N ORDERBY N WHERE X note100 N").rows
            )
            self.assertEqual(
                [[300]], cnx.execute("Any CS WHERE C score100 CS, C is Company").rows
            )


if __name__ == "__main__":
    import unittest

    unittest.main()
