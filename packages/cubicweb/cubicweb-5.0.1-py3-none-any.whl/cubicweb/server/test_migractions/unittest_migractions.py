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

import os
import os.path as osp
import sys
from contextlib import contextmanager
from datetime import date
from tempfile import TemporaryDirectory

from logilab.common import tempattr
from yams.constraints import UniqueConstraint

from yams import ValidationError
from cubicweb import ConfigurationError, Binary
from cubicweb.devtools import startpgcluster, stoppgcluster
from cubicweb.devtools.apptest_config import PostgresApptestConfiguration
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.schema import constraint_name_for
from cubicweb.server.migractions import ServerMigrationHelper
from cubicweb.server.schema2sql import build_index_name
from cubicweb.server.sources import storages
from cubicweb.server.sqlutils import SQL_PREFIX

HERE = osp.dirname(osp.abspath(__file__))
migrschema = None


def setUpModule():
    startpgcluster(__file__)


def tearDownModule(*args):
    global migrschema
    del migrschema
    if hasattr(MigrationCommandsTC, "origschema"):
        del MigrationCommandsTC.origschema
    stoppgcluster(__file__)


class MigrationTC(CubicWebTC):
    appid = "data-migractions"

    configcls = PostgresApptestConfiguration

    def _init_repo(self):
        super()._init_repo()
        # we have to read schema from the database to get eid for schema entities
        self.repo.set_schema(self.repo.deserialize_schema(), resetvreg=False)
        # hack to read the schema from data/migrschema

        @contextmanager
        def temp_app(config, appid, apphome):
            old = config.apphome, config.appid
            sys.path.remove(old[0])
            sys.path.insert(0, apphome)
            config._apphome, config.appid = apphome, appid
            try:
                yield config
            finally:
                sys.path.remove(apphome)
                sys.path.insert(0, old[0])
                config._apphome, config.appid = old

        appid = osp.join(self.appid, "migratedapp")
        apphome = osp.join(HERE, appid)
        with temp_app(self.config, appid, apphome) as config:
            global migrschema
            migrschema = config.load_schema()

    def tearDown(self):
        super().tearDown()
        self.repo.vreg["etypes"].clear_caches()

    @contextmanager
    def mh(self):
        with self.admin_access.repo_cnx() as cnx:
            yield cnx, ServerMigrationHelper(
                self.repo.config, migrschema, repo=self.repo, cnx=cnx, interactive=False
            )

    def table_sql(self, mh, tablename):
        result = mh.sqlexec(
            "SELECT table_name FROM information_schema.tables WHERE LOWER(table_name)=%(table)s",
            {"table": tablename.lower()},
        )
        if result:
            return result[0][0]
        return None  # no such table

    def table_schema(self, mh, tablename):
        result = mh.sqlexec(
            "SELECT column_name, data_type, character_maximum_length "
            "FROM information_schema.columns "
            "WHERE LOWER(table_name) = %(table)s",
            {"table": tablename.lower()},
        )
        assert result, f"no table {tablename}"
        return {x[0]: (x[1], x[2]) for x in result}

    def table_constraints(self, mh, tablename):
        result = mh.sqlexec(
            "SELECT DISTINCT constraint_name FROM information_schema.constraint_column_usage "
            "WHERE LOWER(table_name) = '%(table)s' AND constraint_name LIKE 'cstr%%'"
            % {"table": tablename.lower()}
        )
        assert result, f"no table {tablename}"
        return {x[0] for x in result}


class MigrationCommandsTC(MigrationTC):
    def _init_repo(self):
        super()._init_repo()
        assert "Folder" in migrschema

    def test_add_attribute_bool(self):
        with self.mh() as (cnx, mh):
            self.assertNotIn("yesno", self.schema)
            cnx.create_entity("Note")
            cnx.commit()
            mh.cmd_add_attribute("Note", "yesno")
            self.assertIn("yesno", self.schema)
            self.assertEqual(self.schema["yesno"].subjects(), ("Note",))
            self.assertEqual(self.schema["yesno"].objects(), ("Boolean",))
            self.assertEqual(self.schema["Note"].default("yesno"), False)
            # test default value set on existing entities
            note = cnx.execute("Note X").get_entity(0, 0)
            self.assertEqual(note.yesno, False)
            # test default value set for next entities
            self.assertEqual(cnx.create_entity("Note").yesno, False)

    def test_add_attribute_int(self):
        with self.mh() as (cnx, mh):
            self.assertNotIn("whatever", self.schema)
            cnx.create_entity("Note")
            cnx.commit()
            orderdict = dict(
                mh.rqlexec(
                    'Any RTN, O WHERE X name "Note", RDEF from_entity X, '
                    "RDEF relation_type RT, RDEF ordernum O, RT name RTN"
                )
            )
            mh.cmd_add_attribute("Note", "whatever")
            self.assertIn("whatever", self.schema)
            self.assertEqual(self.schema["whatever"].subjects(), ("Note",))
            self.assertEqual(self.schema["whatever"].objects(), ("Int",))
            self.assertEqual(self.schema["Note"].default("whatever"), 0)
            # test default value set on existing entities
            note = cnx.execute("Note X").get_entity(0, 0)
            self.assertIsInstance(note.whatever, int)
            self.assertEqual(note.whatever, 0)
            # test default value set for next entities
            self.assertEqual(cnx.create_entity("Note").whatever, 0)
            # test attribute order
            orderdict2 = dict(
                mh.rqlexec(
                    'Any RTN, O WHERE X name "Note", RDEF from_entity X, '
                    "RDEF relation_type RT, RDEF ordernum O, RT name RTN"
                )
            )
            whateverorder = (
                migrschema["whatever"].relation_definition("Note", "Int").order
            )
            for k, v in orderdict.items():
                if v >= whateverorder:
                    orderdict[k] = v + 1
            orderdict["whatever"] = whateverorder
            self.assertDictEqual(orderdict, orderdict2)

    def test_add_attribute_varchar(self):
        with self.mh() as (cnx, mh):
            self.assertNotIn("whatever", self.schema)
            cnx.create_entity("Note")
            cnx.commit()
            self.assertNotIn("shortpara", self.schema)
            mh.cmd_add_attribute("Note", "shortpara")
            self.assertIn("shortpara", self.schema)
            self.assertEqual(self.schema["shortpara"].subjects(), ("Note",))
            self.assertEqual(self.schema["shortpara"].objects(), ("String",))
            # test created column is actually a varchar(64)
            fields = self.table_schema(mh, f"{SQL_PREFIX}Note")
            self.assertEqual(
                fields[f"{SQL_PREFIX}shortpara"], ("character varying", 11)
            )
            # test default value set on existing entities
            self.assertEqual(cnx.execute("Note X").get_entity(0, 0).shortpara, "hop")
            # test default value set for next entities
            self.assertEqual(
                cnx.create_entity("Note", shortpara="hop hop").shortpara, "hop hop"
            )
            # serialized constraint added
            constraints = self.table_constraints(mh, "cw_Personne")
            self.assertEqual(len(constraints), 1, constraints)

    def test_add_attribute_unique(self):
        with self.mh() as (cnx, mh):
            self.assertNotIn("unique_id", self.schema)
            mh.cmd_add_attribute("Note", "unique_id")
            # test unique index creation
            dbh = self.repo.system_source.dbhelper
            self.assertTrue(
                dbh.index_exists(cnx.cnxset.cu, "cw_Note", "cw_unique_id", unique=True)
            )

    def test_add_datetime_with_default_value_attribute(self):
        with self.mh() as (cnx, mh):
            self.assertNotIn("mydate", self.schema)
            self.assertNotIn("newstyledefaultdate", self.schema)
            mh.cmd_add_attribute("Note", "mydate")
            mh.cmd_add_attribute("Note", "newstyledefaultdate")
            self.assertIn("mydate", self.schema)
            self.assertIn("newstyledefaultdate", self.schema)
            self.assertEqual(self.schema["mydate"].subjects(), ("Note",))
            self.assertEqual(self.schema["mydate"].objects(), ("Date",))
            testdate = date(2005, 12, 13)
            eid1 = mh.rqlexec("INSERT Note N")[0][0]
            eid2 = mh.rqlexec(
                "INSERT Note N: N mydate %(mydate)s", {"mydate": testdate}
            )[0][0]
            d1 = mh.rqlexec("Any D WHERE X eid %(x)s, X mydate D", {"x": eid1})[0][0]
            d2 = mh.rqlexec("Any D WHERE X eid %(x)s, X mydate D", {"x": eid2})[0][0]
            d4 = mh.rqlexec(
                "Any D WHERE X eid %(x)s, X newstyledefaultdate D", {"x": eid1}
            )[0][0]
            self.assertEqual(d1, date.today())
            self.assertEqual(d2, testdate)
            myfavoritedate = date(2013, 1, 1)
            self.assertEqual(d4, myfavoritedate)

    def test_drop_chosen_constraints_ctxmanager(self):
        with self.mh() as (cnx, mh):
            with mh.cmd_dropped_constraints("Note", "unique_id", UniqueConstraint):
                mh.cmd_add_attribute("Note", "unique_id")
                # make sure the maxsize constraint is not dropped
                self.assertRaises(
                    ValidationError, mh.rqlexec, 'INSERT Note N: N unique_id "xyz"'
                )
                mh.rollback()
                # make sure the unique constraint is dropped
                mh.rqlexec('INSERT Note N: N unique_id "x"')
                mh.rqlexec('INSERT Note N: N unique_id "x"')
                mh.rqlexec("DELETE Note N")

    def test_drop_required_ctxmanager(self):
        with self.mh() as (cnx, mh):
            with mh.cmd_dropped_constraints(
                "Note", "unique_id", cstrtype=None, droprequired=True
            ):
                mh.cmd_add_attribute("Note", "unique_id")
                mh.rqlexec("INSERT Note N")
                mh.rqlexec('SET N unique_id "x"')
            # make sure the required=True was restored
            self.assertRaises(ValidationError, mh.rqlexec, "INSERT Note N")
            mh.rollback()

    def test_rename_attribute(self):
        with self.mh() as (cnx, mh):
            self.assertNotIn("civility", self.schema)
            eid1 = mh.rqlexec('INSERT Personne X: X nom "lui", X sexe "M"')[0][0]
            eid2 = mh.rqlexec('INSERT Personne X: X nom "l\'autre", X sexe NULL')[0][0]
            mh.cmd_rename_attribute("Personne", "sexe", "civility")
            self.assertNotIn("sexe", self.schema)
            self.assertIn("civility", self.schema)
            # test data has been backported
            c1 = mh.rqlexec(f"Any C WHERE X eid {eid1}, X civility C")[0][0]
            self.assertEqual(c1, "M")
            c2 = mh.rqlexec(f"Any C WHERE X eid {eid2}, X civility C")[0][0]
            self.assertEqual(c2, None)

    def test_workflow_actions(self):
        with self.mh() as (cnx, mh):
            mh.cmd_add_workflow("foo", ("Personne", "Email"), ensure_workflowable=False)
            for etype in ("Personne", "Email"):
                s1 = mh.rqlexec(
                    f'Any N WHERE WF workflow_of ET, ET name "{etype}", WF name N'
                )[0][0]
                self.assertEqual(s1, "foo")
                s1 = mh.rqlexec(
                    f'Any N WHERE ET default_workflow WF, ET name "{etype}", WF name N'
                )[0][0]
                self.assertEqual(s1, "foo")

    def test_add_entity_type(self):
        with self.mh() as (cnx, mh):
            self.assertNotIn("Folder2", self.schema)
            self.assertNotIn("filed_under2", self.schema)
            mh.cmd_add_entity_type("Folder2")
            self.assertIn("Folder2", self.schema)
            self.assertIn("Old", self.schema)
            self.assertTrue(cnx.execute('CWEType X WHERE X name "Folder2"'))
            self.assertIn("filed_under2", self.schema)
            self.assertTrue(cnx.execute('CWRType X WHERE X name "filed_under2"'))
            self.assertEqual(
                sorted(self.schema["Folder2"].subject_relations),
                [
                    "created_by",
                    "creation_date",
                    "cw_source",
                    "cwuri",
                    "description",
                    "description_format",
                    "eid",
                    "filed_under2",
                    "has_text",
                    "identity",
                    "in_basket",
                    "inlined_rel",
                    "is",
                    "is_instance_of",
                    "modification_date",
                    "name",
                    "owned_by",
                ],
            )
            self.assertCountEqual(
                [str(rs) for rs in self.schema["Folder2"].object_relations.values()],
                ["filed_under2", "identity", "inlined_rel"],
            )
            # Old will be missing as it has been renamed into 'New' in the migrated
            # schema while New hasn't been added here.
            self.assertEqual(
                sorted(str(e) for e in self.schema["filed_under2"].subjects()),
                sorted(
                    str(e) for e in self.schema.entities() if not e.final and e != "Old"
                ),
            )
            self.assertEqual(self.schema["filed_under2"].objects(), ("Folder2",))
            eschema = self.schema.entity_schema_for("Folder2")
            for cstr in eschema.relation_definition("name").constraints:
                self.assertTrue(hasattr(cstr, "eid"))

    def test_add_entity_type_with_constraint(self):
        with self.mh() as (cnx, mh):
            mh.cmd_add_entity_type("Activity")
            constraints = self.table_constraints(mh, "cw_Activity")
            self.assertEqual(len(constraints), 2, constraints)

    def test_add_cube_with_custom_final_type(self):
        with self.mh() as (cnx, mh):
            try:
                mh.cmd_add_cube("fakecustomtype")
                self.assertIn("Numeric", self.schema)
                self.assertTrue(self.schema["Numeric"].final)
                rdef = self.schema["num"].relation_definitions[("Location", "Numeric")]
                self.assertEqual(rdef.scale, 10)
                self.assertEqual(rdef.precision, 18)
                fields = self.table_schema(mh, f"{SQL_PREFIX}Location")
                self.assertEqual(fields[f"{SQL_PREFIX}num"], ("numeric", None))  # XXX
            finally:
                mh.cmd_drop_cube("fakecustomtype")
                mh.drop_entity_type("Numeric")

    def test_add_drop_entity_type(self):
        with self.mh() as (cnx, mh):
            mh.cmd_add_entity_type("Folder2")
            wf = mh.cmd_add_workflow("folder2 wf", "Folder2", ensure_workflowable=False)
            todo = wf.add_state("todo", initial=True)
            done = wf.add_state("done")
            wf.add_transition("redoit", done, todo)
            wf.add_transition("markasdone", todo, done)
            cnx.commit()
            mh.cmd_drop_entity_type("Folder2")
            self.assertNotIn("Folder2", self.schema)
            self.assertFalse(cnx.execute('CWEType X WHERE X name "Folder2"'))
            # test automatic workflow deletion
            self.assertFalse(cnx.execute("Workflow X WHERE NOT X workflow_of ET"))
            self.assertFalse(cnx.execute("State X WHERE NOT X state_of WF"))
            self.assertFalse(cnx.execute("Transition X WHERE NOT X transition_of WF"))

    def test_rename_entity_type(self):
        with self.mh() as (cnx, mh):
            entity = mh.create_entity("Old", name="old")
            self.repo.type_from_eid(entity.eid, entity._cw)
            mh.cmd_rename_entity_type("Old", "New")
            dbh = self.repo.system_source.dbhelper
            indices = set(dbh.list_indices(cnx.cnxset.cu, "cw_New"))
            self.assertNotIn(build_index_name("cw_Old", ["cw_name"]), indices)
            self.assertIn(build_index_name("cw_New", ["cw_name"]), indices)
            mh.cmd_rename_attribute("New", "name", "new_name")
            indices = set(dbh.list_indices(cnx.cnxset.cu, "cw_New"))
            # check 'indexed' index
            self.assertNotIn(build_index_name("cw_New", ["cw_name"], "idx_"), indices)
            self.assertIn(build_index_name("cw_New", ["cw_new_name"], "idx_"), indices)
            # check 'unique' index
            self.assertNotIn(build_index_name("cw_New", ["cw_name"], "key_"), indices)
            self.assertIn(build_index_name("cw_New", ["cw_new_name"], "key_"), indices)

    def test_add_drop_relation_type(self):
        with self.mh() as (cnx, mh):
            mh.cmd_add_entity_type("Folder2", auto=False)
            mh.cmd_add_relation_type("filed_under2")
            self.assertIn("filed_under2", self.schema)
            # Old will be missing as it has been renamed into 'New' in the migrated
            # schema while New hasn't been added here.
            self.assertEqual(
                sorted(str(e) for e in self.schema["filed_under2"].subjects()),
                sorted(
                    str(e) for e in self.schema.entities() if not e.final and e != "Old"
                ),
            )
            self.assertEqual(self.schema["filed_under2"].objects(), ("Folder2",))
            mh.cmd_drop_relation_type("filed_under2")
            self.assertNotIn("filed_under2", self.schema)
            # this should not crash
            mh.cmd_drop_relation_type("filed_under2")

    def test_add_relation_definition_nortype(self):
        with self.mh() as (cnx, mh):
            mh.cmd_add_relation_definition("Personne", "concerne2", "Affaire")
            self.assertEqual(self.schema["concerne2"].subjects(), ("Personne",))
            self.assertEqual(self.schema["concerne2"].objects(), ("Affaire",))
            self.assertEqual(
                self.schema["concerne2"]
                .relation_definition("Personne", "Affaire")
                .cardinality,
                "1*",
            )
            mh.cmd_add_relation_definition("Personne", "concerne2", "Note")
            self.assertEqual(
                sorted(self.schema["concerne2"].objects()), ["Affaire", "Note"]
            )
            mh.create_entity("Personne", nom="tot")
            mh.create_entity("Affaire")
            mh.rqlexec("SET X concerne2 Y WHERE X is Personne, Y is Affaire")
            cnx.commit()
            mh.cmd_drop_relation_definition("Personne", "concerne2", "Affaire")
            self.assertIn("concerne2", self.schema)
            mh.cmd_drop_relation_definition("Personne", "concerne2", "Note")
            self.assertNotIn("concerne2", self.schema)

    def test_drop_relation_definition_existant_rtype(self):
        with self.mh() as (cnx, mh):
            self.assertEqual(
                sorted(str(e) for e in self.schema["concerne"].subjects()),
                ["Affaire", "Personne"],
            )
            self.assertEqual(
                sorted(str(e) for e in self.schema["concerne"].objects()),
                ["Affaire", "Division", "Note", "Societe", "SubDivision"],
            )
            mh.cmd_drop_relation_definition("Personne", "concerne", "Affaire")
            self.assertEqual(
                sorted(str(e) for e in self.schema["concerne"].subjects()), ["Affaire"]
            )
            self.assertEqual(
                sorted(str(e) for e in self.schema["concerne"].objects()),
                ["Division", "Note", "Societe", "SubDivision"],
            )
            mh.cmd_add_relation_definition("Personne", "concerne", "Affaire")
            self.assertEqual(
                sorted(str(e) for e in self.schema["concerne"].subjects()),
                ["Affaire", "Personne"],
            )
            self.assertEqual(
                sorted(str(e) for e in self.schema["concerne"].objects()),
                ["Affaire", "Division", "Note", "Societe", "SubDivision"],
            )
            # trick: overwrite self.maxeid to avoid deletion of just reintroduced types
            self.maxeid = cnx.execute("Any MAX(X)")[0][0]

    def test_drop_relation_definition_with_specialization(self):
        with self.mh() as (cnx, mh):
            self.assertEqual(
                sorted(str(e) for e in self.schema["concerne"].subjects()),
                ["Affaire", "Personne"],
            )
            self.assertEqual(
                sorted(str(e) for e in self.schema["concerne"].objects()),
                ["Affaire", "Division", "Note", "Societe", "SubDivision"],
            )
            mh.cmd_drop_relation_definition("Affaire", "concerne", "Societe")
            self.assertEqual(
                sorted(str(e) for e in self.schema["concerne"].subjects()),
                ["Affaire", "Personne"],
            )
            self.assertEqual(
                sorted(str(e) for e in self.schema["concerne"].objects()),
                ["Affaire", "Note"],
            )
            mh.cmd_add_relation_definition("Affaire", "concerne", "Societe")
            self.assertEqual(
                sorted(str(e) for e in self.schema["concerne"].subjects()),
                ["Affaire", "Personne"],
            )
            self.assertEqual(
                sorted(str(e) for e in self.schema["concerne"].objects()),
                ["Affaire", "Division", "Note", "Societe", "SubDivision"],
            )
            # trick: overwrite self.maxeid to avoid deletion of just reintroduced types
            self.maxeid = cnx.execute("Any MAX(X)")[0][0]

    def test_rename_relation(self):
        self.skipTest("implement me")

    def test_change_relation_props_non_final(self):
        with self.mh() as (cnx, mh):
            rschema = self.schema["concerne"]
            card = rschema.relation_definition("Affaire", "Societe").cardinality
            self.assertEqual(card, "**")
            try:
                mh.cmd_change_relation_props(
                    "Affaire", "concerne", "Societe", cardinality="?*"
                )
                card = rschema.relation_definition("Affaire", "Societe").cardinality
                self.assertEqual(card, "?*")
            finally:
                mh.cmd_change_relation_props(
                    "Affaire", "concerne", "Societe", cardinality="**"
                )

    def test_change_relation_props_final(self):
        with self.mh() as (cnx, mh):
            rschema = self.schema["adel"]
            card = rschema.relation_definition("Personne", "String").fulltextindexed
            self.assertEqual(card, False)
            try:
                mh.cmd_change_relation_props(
                    "Personne", "adel", "String", fulltextindexed=True
                )
                card = rschema.relation_definition("Personne", "String").fulltextindexed
                self.assertEqual(card, True)
            finally:
                mh.cmd_change_relation_props(
                    "Personne", "adel", "String", fulltextindexed=False
                )

    def test_sync_schema_props_perms_rqlconstraints(self):
        with self.mh() as (cnx, mh):
            # Drop one of the RQLConstraint.
            rdef = self.schema["evaluee"].relation_definitions[("Personne", "Note")]
            oldconstraints = rdef.constraints
            self.assertIn(
                "S created_by U", [cstr.expression for cstr in oldconstraints]
            )
            mh.cmd_sync_schema_props_perms("evaluee", commit=True)
            newconstraints = rdef.constraints
            self.assertNotIn(
                "S created_by U", [cstr.expression for cstr in newconstraints]
            )

            # Drop all RQLConstraint.
            rdef = self.schema["travaille"].relation_definitions[
                ("Personne", "Societe")
            ]
            oldconstraints = rdef.constraints
            self.assertEqual(len(oldconstraints), 2)
            mh.cmd_sync_schema_props_perms("travaille", commit=True)
            rdef = self.schema["travaille"].relation_definitions[
                ("Personne", "Societe")
            ]
            newconstraints = rdef.constraints
            self.assertEqual(len(newconstraints), 0)

    def test_sync_schema_props_perms(self):
        with self.mh() as (cnx, mh):
            nbrqlexpr_start = cnx.execute("Any COUNT(X) WHERE X is RQLExpression")[0][0]
            migrschema["titre"].relation_definitions[("Personne", "String")].order = 7
            migrschema["adel"].relation_definitions[("Personne", "String")].order = 6
            migrschema["ass"].relation_definitions[("Personne", "String")].order = 5
            migrschema["Personne"].description = "blabla bla"
            migrschema["titre"].description = "usually a title"
            migrschema["titre"].relation_definitions[
                ("Personne", "String")
            ].description = "title for this person"
            delete_concerne_rqlexpr = self._rrqlexpr_rset(cnx, "delete", "concerne")
            add_concerne_rqlexpr = self._rrqlexpr_rset(cnx, "add", "concerne")

            # make sure properties (e.g. etype descriptions) are synced by the
            # second call to sync_schema
            mh.cmd_sync_schema_props_perms(syncprops=False, commit=False)
            mh.cmd_sync_schema_props_perms(commit=False)

            self.assertEqual(
                cnx.execute('Any D WHERE X name "Personne", X description D')[0][0],
                "blabla bla",
            )
            self.assertEqual(
                cnx.execute('Any D WHERE X name "titre", X description D')[0][0],
                "usually a title",
            )
            self.assertEqual(
                cnx.execute(
                    'Any D WHERE X relation_type RT, RT name "titre",'
                    'X from_entity FE, FE name "Personne",'
                    "X description D"
                )[0][0],
                "title for this person",
            )
            rinorder = [
                n
                for n, in cnx.execute(
                    "Any N ORDERBY O,N WHERE X is CWAttribute, X relation_type RT, RT name N,"
                    'X from_entity FE, FE name "Personne",'
                    "X ordernum O"
                )
            ]
            expected = [
                "nom",
                "prenom",
                "sexe",
                "promo",
                "ass",
                "adel",
                "titre",
                "web",
                "tel",
                "fax",
                "datenaiss",
                "test",
                "tzdatenaiss",
                "description",
                "firstname",
                "photo",
                "creation_date",
                "cwuri",
                "modification_date",
            ]
            self.assertEqual(expected, rinorder)

            # test permissions synchronization ####################################
            # new rql expr to add note entity
            eexpr = self._erqlexpr_entity(cnx, "add", "Note")
            self.assertEqual(
                eexpr.expression,
                "X ecrit_part PE, U in_group G, "
                'PE require_permission P, P name "add_note", P require_group G',
            )
            self.assertEqual([et.name for et in eexpr.reverse_add_permission], ["Note"])
            self.assertEqual(eexpr.reverse_read_permission, ())
            self.assertEqual(eexpr.reverse_delete_permission, ())
            self.assertEqual(eexpr.reverse_update_permission, ())
            self.assertTrue(self._rrqlexpr_rset(cnx, "add", "para"))
            # no rqlexpr to delete para attribute
            self.assertFalse(self._rrqlexpr_rset(cnx, "delete", "para"))
            # new rql expr to add ecrit_par relation
            rexpr = self._rrqlexpr_entity(cnx, "add", "ecrit_par")
            self.assertEqual(
                rexpr.expression,
                'O require_permission P, P name "add_note", '
                "U in_group G, P require_group G",
            )
            self.assertEqual(
                [rdef.relation_type[0].name for rdef in rexpr.reverse_add_permission],
                ["ecrit_par"],
            )
            self.assertEqual(rexpr.reverse_read_permission, ())
            self.assertEqual(rexpr.reverse_delete_permission, ())
            # no more rqlexpr to delete and add travaille relation
            self.assertFalse(self._rrqlexpr_rset(cnx, "add", "travaille"))
            self.assertFalse(self._rrqlexpr_rset(cnx, "delete", "travaille"))
            # no more rqlexpr to delete and update Societe entity
            self.assertFalse(self._erqlexpr_rset(cnx, "update", "Societe"))
            self.assertFalse(self._erqlexpr_rset(cnx, "delete", "Societe"))
            # no more rqlexpr to read Affaire entity
            self.assertFalse(self._erqlexpr_rset(cnx, "read", "Affaire"))
            # rqlexpr to update Affaire entity has been updated
            eexpr = self._erqlexpr_entity(cnx, "update", "Affaire")
            self.assertEqual(eexpr.expression, "X concerne S, S owned_by U")
            # no change for rqlexpr to add and delete Affaire entity
            self.assertEqual(len(self._erqlexpr_rset(cnx, "delete", "Affaire")), 1)
            self.assertEqual(len(self._erqlexpr_rset(cnx, "add", "Affaire")), 1)
            # no change for rqlexpr to add and delete concerne relation
            self.assertEqual(
                len(self._rrqlexpr_rset(cnx, "delete", "concerne")),
                len(delete_concerne_rqlexpr),
            )
            self.assertEqual(
                len(self._rrqlexpr_rset(cnx, "add", "concerne")),
                len(add_concerne_rqlexpr),
            )
            # * migrschema involve:
            #   * 7 erqlexprs deletions (2 in (Affaire + Societe + Note.para) + 1 Note.something
            #   * 2 rrqlexprs deletions (travaille)
            #   * 1 update (Affaire update)
            #   * 2 new (Note add, ecrit_par add)
            #   * 2 implicit new for attributes (Note.para, Person.test)
            # remaining orphan rql expr which should be deleted at commit (composite relation)
            # unattached expressions -> pending deletion on commit
            self.assertEqual(
                cnx.execute(
                    'Any COUNT(X) WHERE X is RQLExpression, X exprtype "ERQLExpression",'
                    "NOT ET1 read_permission X, NOT ET2 add_permission X, "
                    "NOT ET3 delete_permission X, NOT ET4 update_permission X"
                )[0][0],
                7,
            )
            self.assertEqual(
                cnx.execute(
                    'Any COUNT(X) WHERE X is RQLExpression, X exprtype "RRQLExpression",'
                    "NOT ET1 read_permission X, NOT ET2 add_permission X, "
                    "NOT ET3 delete_permission X, NOT ET4 update_permission X"
                )[0][0],
                2,
            )
            # finally
            self.assertEqual(
                cnx.execute("Any COUNT(X) WHERE X is RQLExpression")[0][0],
                nbrqlexpr_start + 1 + 2 + 2 + 2,
            )
            cnx.commit()
            # unique_together test
            self.assertEqual(
                len(self.schema.entity_schema_for("Personne")._unique_together), 1
            )
            self.assertCountEqual(
                self.schema.entity_schema_for("Personne")._unique_together[0],
                ("nom", "prenom", "datenaiss"),
            )
            rset = cnx.execute(
                "Any C WHERE C is CWUniqueTogetherConstraint, "
                'C constraint_of ET, ET name "Personne"'
            )
            self.assertEqual(len(rset), 1)
            relations = [r.name for r in rset.get_entity(0, 0).relations]
            self.assertCountEqual(relations, ("nom", "prenom", "datenaiss"))

            # serialized constraint changed
            constraints = self.table_constraints(mh, "cw_Personne")
            self.assertEqual(len(constraints), 1, constraints)
            rdef = migrschema["promo"].relation_definitions["Personne", "String"]
            cstr = rdef.constraint_by_type("StaticVocabularyConstraint")
            self.assertIn(constraint_name_for(cstr, rdef), constraints)

    def _erqlexpr_rset(self, cnx, action, ertype):
        rql = (
            "RQLExpression X WHERE ET is CWEType, ET %s_permission X, ET name %%(name)s"
            % action
        )
        return cnx.execute(rql, {"name": ertype})

    def _erqlexpr_entity(self, cnx, action, ertype):
        rset = self._erqlexpr_rset(cnx, action, ertype)
        self.assertEqual(len(rset), 1)
        return rset.get_entity(0, 0)

    def _rrqlexpr_rset(self, cnx, action, ertype):
        return cnx.execute(
            "RQLExpression X WHERE RT is CWRType, RDEF %s_permission X, "
            "RT name %%(name)s, RDEF relation_type RT" % action,
            {"name": ertype},
        )

    def _rrqlexpr_entity(self, cnx, action, ertype):
        rset = self._rrqlexpr_rset(cnx, action, ertype)
        self.assertEqual(len(rset), 1)
        return rset.get_entity(0, 0)

    def test_set_size_constraint(self):
        with self.mh() as (cnx, mh):
            # existing previous value
            try:
                mh.cmd_set_size_constraint("CWEType", "name", 128)
            finally:
                mh.cmd_set_size_constraint("CWEType", "name", 64)
            # non existing previous value
            try:
                mh.cmd_set_size_constraint("CWEType", "description", 256)
            finally:
                mh.cmd_set_size_constraint("CWEType", "description", None)

    def test_add_drop_cube_and_deps(self):
        with self.mh() as (cnx, mh):
            schema = self.repo.schema
            self.assertEqual(
                sorted(
                    (str(s), str(o)) for s, o in schema["see_also"].relation_definitions
                ),
                sorted(
                    [
                        ("EmailThread", "EmailThread"),
                        ("Folder", "Folder"),
                        ("Bookmark", "Bookmark"),
                        ("Bookmark", "Note"),
                        ("Note", "Note"),
                        ("Note", "Bookmark"),
                    ]
                ),
            )
            try:
                mh.cmd_drop_cube("fakeemail", removedeps=True)
                # file was there because it's an email dependancy, should have been removed
                self.assertNotIn("fakeemail", self.config.cubes())
                self.assertNotIn(
                    self.config.cube_dir("fakeemail"), self.config.cubes_path()
                )
                self.assertNotIn("file", self.config.cubes())
                self.assertNotIn(self.config.cube_dir("file"), self.config.cubes_path())
                for ertype in (
                    "Email",
                    "EmailThread",
                    "EmailPart",
                    "File",
                    "sender",
                    "in_thread",
                    "reply_to",
                    "data_format",
                ):
                    self.assertNotIn(ertype, schema)
                self.assertEqual(
                    sorted(schema["see_also"].relation_definitions),
                    sorted(
                        [
                            ("Folder", "Folder"),
                            ("Bookmark", "Bookmark"),
                            ("Bookmark", "Note"),
                            ("Note", "Note"),
                            ("Note", "Bookmark"),
                        ]
                    ),
                )
                self.assertEqual(
                    sorted(schema["see_also"].subjects()),
                    ["Bookmark", "Folder", "Note"],
                )
                self.assertEqual(
                    sorted(schema["see_also"].objects()), ["Bookmark", "Folder", "Note"]
                )
                self.assertEqual(
                    cnx.execute(
                        'Any X WHERE X pkey "system.version.fakeemail"'
                    ).rowcount,
                    0,
                )
                self.assertEqual(
                    cnx.execute('Any X WHERE X pkey "system.version.file"').rowcount, 0
                )
            finally:
                mh.cmd_add_cube("fakeemail")
                self.assertIn("fakeemail", self.config.cubes())
                self.assertIn(
                    self.config.cube_dir("fakeemail"), self.config.cubes_path()
                )
                self.assertIn("file", self.config.cubes())
                self.assertIn(self.config.cube_dir("file"), self.config.cubes_path())
                for ertype in (
                    "Email",
                    "EmailThread",
                    "EmailPart",
                    "File",
                    "sender",
                    "in_thread",
                    "reply_to",
                    "data_format",
                ):
                    self.assertIn(ertype, schema)
                self.assertEqual(
                    sorted(schema["see_also"].relation_definitions),
                    sorted(
                        [
                            ("EmailThread", "EmailThread"),
                            ("Folder", "Folder"),
                            ("Bookmark", "Bookmark"),
                            ("Bookmark", "Note"),
                            ("Note", "Note"),
                            ("Note", "Bookmark"),
                        ]
                    ),
                )
                self.assertEqual(
                    sorted(schema["see_also"].subjects()),
                    ["Bookmark", "EmailThread", "Folder", "Note"],
                )
                self.assertEqual(
                    sorted(schema["see_also"].objects()),
                    ["Bookmark", "EmailThread", "Folder", "Note"],
                )
                from cubicweb_fakeemail.__pkginfo__ import version as email_version
                from cubicweb_file.__pkginfo__ import version as file_version

                self.assertEqual(
                    cnx.execute(
                        'Any V WHERE X value V, X pkey "system.version.fakeemail"'
                    )[0][0],
                    email_version,
                )
                self.assertEqual(
                    cnx.execute('Any V WHERE X value V, X pkey "system.version.file"')[
                        0
                    ][0],
                    file_version,
                )
                # why this commit is necessary is unclear to me (though without it
                # next test may fail complaining of missing tables
                cnx.commit()

    def test_add_drop_cube_no_deps(self):
        with self.mh() as (cnx, mh):
            cubes = set(self.config.cubes())
            schema = self.repo.schema
            try:
                mh.cmd_drop_cube("fakeemail")
                cubes.remove("fakeemail")
                self.assertNotIn("fakeemail", self.config.cubes())
                self.assertIn("file", self.config.cubes())
                for ertype in (
                    "Email",
                    "EmailThread",
                    "EmailPart",
                    "sender",
                    "in_thread",
                    "reply_to",
                ):
                    self.assertNotIn(ertype, schema)
            finally:
                mh.cmd_add_cube("fakeemail")
                self.assertIn("fakeemail", self.config.cubes())
                # why this commit is necessary is unclear to me (though without it
                # next test may fail complaining of missing tables
                cnx.commit()

    def test_drop_dep_cube(self):
        with self.mh() as (cnx, mh):
            with self.assertRaises(ConfigurationError) as cm:
                mh.cmd_drop_cube("file")
            self.assertEqual(
                str(cm.exception),
                "can't remove cube file, used as a dependency."
                "Consider using 'force_drop=True' if you want to drop it anyway",
            )

    def test_introduce_base_class(self):
        with self.mh() as (cnx, mh):
            mh.cmd_add_entity_type("Para")
            self.assertEqual(
                sorted(et.type for et in self.schema["Para"].specialized_by()), ["Note"]
            )
            self.assertEqual(self.schema["Note"].specializes().type, "Para")
            mh.cmd_add_entity_type("Text")
            self.assertEqual(
                sorted(et.type for et in self.schema["Para"].specialized_by()),
                ["Note", "Text"],
            )
            self.assertEqual(self.schema["Text"].specializes().type, "Para")
            # test columns have been actually added
            text = cnx.create_entity("Text", para="hip", summary="hop", newattr="momo")
            note = cnx.create_entity(
                "Note", para="hip", shortpara="hop", newattr="momo", unique_id="x"
            )
            aff = cnx.create_entity("Affaire")
            self.assertTrue(
                cnx.execute(
                    "SET X newnotinlined Y WHERE X eid %(x)s, Y eid %(y)s",
                    {"x": text.eid, "y": aff.eid},
                )
            )
            self.assertTrue(
                cnx.execute(
                    "SET X newnotinlined Y WHERE X eid %(x)s, Y eid %(y)s",
                    {"x": note.eid, "y": aff.eid},
                )
            )
            self.assertTrue(
                cnx.execute(
                    "SET X newinlined Y WHERE X eid %(x)s, Y eid %(y)s",
                    {"x": text.eid, "y": aff.eid},
                )
            )
            self.assertTrue(
                cnx.execute(
                    "SET X newinlined Y WHERE X eid %(x)s, Y eid %(y)s",
                    {"x": note.eid, "y": aff.eid},
                )
            )
            # XXX remove specializes by ourselves, else tearDown fails when removing
            # Para because of Note inheritance. This could be fixed by putting the
            # MemSchemaCWETypeDel(session, name) operation in the
            # after_delete_entity(CWEType) hook, since in that case the MemSchemaSpecializesDel
            # operation would be removed before, but I'm not sure this is a desired behaviour.
            #
            # also we need more tests about introducing/removing base classes or
            # specialization relationship...
            cnx.execute('DELETE X specializes Y WHERE Y name "Para"')
            cnx.commit()
            self.assertEqual(
                sorted(et.type for et in self.schema["Para"].specialized_by()), []
            )
            self.assertEqual(self.schema["Note"].specializes(), None)
            self.assertEqual(self.schema["Text"].specializes(), None)

    def test_add_symmetric_relation_type(self):
        with self.mh() as (cnx, mh):
            self.assertFalse(self.table_sql(mh, "same_as_relation"))
            mh.cmd_add_relation_type("same_as")
            self.assertTrue(self.table_sql(mh, "same_as_relation"))

    def test_change_attribute_type(self):
        with self.mh() as (cnx, mh):
            mh.cmd_create_entity("Societe", tel=1)
            mh.commit()
            mh.change_attribute_type("Societe", "tel", "Float")
            self.assertNotIn(
                ("Societe", "Int"), self.schema["tel"].relation_definitions
            )
            self.assertIn(("Societe", "Float"), self.schema["tel"].relation_definitions)
            self.assertEqual(
                self.schema["tel"].relation_definitions[("Societe", "Float")].object,
                "Float",
            )
            tel = mh.rqlexec("Any T WHERE X tel T")[0][0]
            self.assertEqual(tel, 1.0)
            self.assertIsInstance(tel, float)

    def test_drop_required_inlined_relation(self):
        with self.mh() as (cnx, mh):
            bob = mh.cmd_create_entity("Personne", nom="bob")
            mh.cmd_create_entity("Note", ecrit_par=bob)
            mh.commit()
            rdef = mh.fs_schema.relation_schema_for("ecrit_par").relation_definitions[
                ("Note", "Personne")
            ]
            with tempattr(rdef, "cardinality", "1*"):
                mh.sync_schema_props_perms("ecrit_par", syncperms=False)
            mh.cmd_drop_relation_type("ecrit_par")
            self.assertNotIn(
                f"{SQL_PREFIX}ecrit_par",
                self.table_schema(mh, f"{SQL_PREFIX}Personne"),
            )

    def test_drop_inlined_rdef_delete_data(self):
        with self.mh() as (cnx, mh):
            mh.cmd_create_entity("Note", ecrit_par=cnx.user.eid)
            mh.commit()
            mh.drop_relation_definition("Note", "ecrit_par", "CWUser")
            self.assertFalse(
                mh.sqlexec("SELECT * FROM cw_Note WHERE cw_ecrit_par IS NOT NULL")
            )

    def test_storage_changed(self):
        with self.mh() as (cnx, mh):
            john = mh.cmd_create_entity(
                "Personne", nom="john", photo=Binary(b"something")
            )
            bill = mh.cmd_create_entity("Personne", nom="bill")
            mh.commit()
            with TemporaryDirectory() as tempdir:
                bfs_storage = storages.BytesFileSystemStorage(tempdir)
                storages.set_attribute_storage(
                    self.repo, "Personne", "photo", bfs_storage
                )
                mh.cmd_storage_changed("Personne", "photo")
                bob = mh.cmd_create_entity("Personne", nom="bob")
                bffss_dir_content = os.listdir(tempdir)
                self.assertEqual(len(bffss_dir_content), 1)
                john.cw_clear_all_caches()
                self.assertEqual(
                    john.photo.getvalue(),
                    osp.join(tempdir, bffss_dir_content[0]).encode("utf8"),
                )
                bob.cw_clear_all_caches()
                self.assertIsNone(bob.photo)
                bill.cw_clear_all_caches()
                self.assertIsNone(bill.photo)
                storages.unset_attribute_storage(self.repo, "Personne", "photo")


if __name__ == "__main__":
    import unittest

    unittest.main()
