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
"""unit tests for selectors mechanism"""

from contextlib import contextmanager
from operator import eq, lt, le, gt

from logilab.common.registry import NoSelectableObject
from logilab.common.decorators import clear_cache
from logilab.common.testlib import TestCase, unittest_main

from cubicweb import Binary
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.entity import EntityAdapter, Adapter
from cubicweb.predicates import (
    is_instance,
    adaptable,
    match_kwargs,
    match_user_groups,
    multi_lines_rset,
    score_entity,
    is_in_state,
    rql_condition,
    relation_possible,
)


class ImplementsTC(CubicWebTC):
    def test_etype_priority(self):
        with self.admin_access.cnx() as cnx:
            f = cnx.create_entity(
                "FakeFile",
                data_name="hop.txt",
                data=Binary(b"hop"),
                data_format="text/plain",
            )
            rset = f.as_rset()
            anyscore = is_instance("Any")(f.__class__, cnx, rset=rset)
            idownscore = adaptable("IDownloadable")(f.__class__, cnx, rset=rset)
            self.assertGreater(idownscore, anyscore, (idownscore, anyscore))
            filescore = is_instance("FakeFile")(f.__class__, cnx, rset=rset)
            self.assertGreater(filescore, idownscore, (filescore, idownscore))

    def test_etype_inheritance_no_yams_inheritance(self):
        cls = self.vreg["etypes"].etype_class("Personne")
        with self.admin_access.cnx() as cnx:
            self.assertFalse(is_instance("Societe").score_class(cls, cnx))

    def test_yams_inheritance(self):
        cls = self.vreg["etypes"].etype_class("Transition")
        with self.admin_access.cnx() as cnx:
            self.assertEqual(is_instance("BaseTransition").score_class(cls, cnx), 3)

    def test_outer_join(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute('Any U,B WHERE B? bookmarked_by U, U login "anon"')
            self.assertEqual(
                is_instance("Bookmark")(None, cnx, rset=rset, row=0, col=1), 0
            )


class WorkflowSelectorTC(CubicWebTC):
    def setUp(self):
        super().setUp()
        # enable debug mode to state/transition validation on the fly
        self.vreg.config.debugmode = True

    def tearDown(self):
        self.vreg.config.debugmode = False
        super().tearDown()

    def setup_database(self):
        with self.admin_access.shell() as shell:
            wf = shell.add_workflow("wf_test", "StateFull", default=True)
            created = wf.add_state("created", initial=True)
            validated = wf.add_state("validated")
            abandoned = wf.add_state("abandoned")
            wf.add_transition("validate", created, validated, ("managers",))
            wf.add_transition(
                "forsake",
                (
                    created,
                    validated,
                ),
                abandoned,
                ("managers",),
            )

    @contextmanager
    def statefull_stuff(self):
        with self.admin_access.cnx() as cnx:
            wf_entity = cnx.create_entity("StateFull", name="")
            rset = wf_entity.as_rset()
            adapter = wf_entity.cw_adapt_to("IWorkflowable")
            cnx.commit()
            self.assertEqual(adapter.state, "created")
            yield cnx, wf_entity, rset, adapter

    def test_is_in_state(self):
        with self.statefull_stuff() as (cnx, wf_entity, rset, adapter):
            for state in ("created", "validated", "abandoned"):
                selector = is_in_state(state)
                self.assertEqual(selector(None, cnx, rset=rset), state == "created")

            adapter.fire_transition("validate")
            cnx.commit()
            wf_entity.cw_clear_all_caches()
            self.assertEqual(adapter.state, "validated")

            clear_cache(rset, "get_entity")

            selector = is_in_state("created")
            self.assertEqual(selector(None, cnx, rset=rset), 0)
            selector = is_in_state("validated")
            self.assertEqual(selector(None, cnx, rset=rset), 1)
            selector = is_in_state("validated", "abandoned")
            self.assertEqual(selector(None, cnx, rset=rset), 1)
            selector = is_in_state("abandoned")
            self.assertEqual(selector(None, cnx, rset=rset), 0)

            adapter.fire_transition("forsake")
            cnx.commit()
            wf_entity.cw_clear_all_caches()
            self.assertEqual(adapter.state, "abandoned")

            clear_cache(rset, "get_entity")

            selector = is_in_state("created")
            self.assertEqual(selector(None, cnx, rset=rset), 0)
            selector = is_in_state("validated")
            self.assertEqual(selector(None, cnx, rset=rset), 0)
            selector = is_in_state("validated", "abandoned")
            self.assertEqual(selector(None, cnx, rset=rset), 1)
            self.assertEqual(adapter.state, "abandoned")
            self.assertEqual(selector(None, cnx, rset=rset), 1)

    def test_is_in_state_unvalid_names(self):
        with self.statefull_stuff() as (cnx, wf_entity, rset, adapter):
            selector = is_in_state("unknown")
            with self.assertRaises(ValueError) as cm:
                selector(None, cnx, rset=rset)
            self.assertEqual(str(cm.exception), "wf_test: unknown state(s): unknown")
            selector = is_in_state("weird", "unknown", "created", "weird")
            with self.assertRaises(ValueError) as cm:
                selector(None, cnx, rset=rset)
            self.assertEqual(
                str(cm.exception), "wf_test: unknown state(s): unknown,weird"
            )


class RelationPossibleTC(CubicWebTC):
    def test_rqlst_1(self):
        with self.admin_access.cnx() as cnx:
            selector = relation_possible("in_group")
            select = self.vreg.parse(cnx, "Any X WHERE X is CWUser").children[0]
            score = selector(
                None,
                cnx,
                rset=1,
                select=select,
                filtered_variable=select.defined_vars["X"],
            )
            self.assertEqual(score, 1)

    def test_rqlst_2(self):
        with self.admin_access.cnx() as cnx:
            selector = relation_possible("in_group")
            select = self.vreg.parse(
                cnx,
                "Any 1, COUNT(X) WHERE X is CWUser, X creation_date XD, "
                "Y creation_date YD, Y is CWGroup "
                "HAVING DAY(XD)=DAY(YD)",
            ).children[0]
            score = selector(
                None,
                cnx,
                rset=1,
                select=select,
                filtered_variable=select.defined_vars["X"],
            )
            self.assertEqual(score, 1)

    def test_ambiguous(self):
        # Ambiguous relations are :
        # (Service, fabrique_par, Personne) and (Produit, fabrique_par, Usine)
        # There used to be a crash here with a bad rdef choice in the strict
        # checking case.
        selector = relation_possible(
            "fabrique_par", role="object", target_etype="Personne", strict=True
        )
        with self.admin_access.cnx() as cnx:
            usine = cnx.create_entity("Usine", lieu="here")
            score = selector(None, cnx, rset=usine.as_rset())
            self.assertEqual(0, score)


class MatchUserGroupsTC(CubicWebTC):
    def test_owners_group(self):
        """tests usage of 'owners' group with match_user_group"""

        class SomeAdapter(Adapter):
            __regid__ = "yo"
            __select__ = match_user_groups("owners")

        self.vreg._loadedmods[__name__] = {}
        self.vreg.register(SomeAdapter)
        SomeAdapter.__registered__(self.vreg["adapters"])
        self.assertIn(SomeAdapter, self.vreg["adapters"]["yo"], self.vreg["adapters"])

        try:
            with self.admin_access.repo_cnx() as cnx:
                self.create_user(cnx, "john")

            # login as a simple user
            john_access = self.new_access("john")
            with john_access.repo_cnx() as cnx:
                # it should not be possible to use SomeAction not owned objects
                rset = cnx.execute('Any G WHERE G is CWGroup, G name "managers"')

                with self.assertRaises(NoSelectableObject):
                    cnx.vreg["adapters"].select("yo", cnx)

                # insert a new card, and check that we can use SomeAction on our object
                cnx.execute('INSERT Card C: C title "zoubidou"')
                cnx.commit()

                rset = cnx.execute('Card C WHERE C title "zoubidou"')

                # shouldn't raise since we have the rights now
                cnx.vreg["adapters"].select("yo", cnx, rset=rset)

            # make sure even managers can't use the action
            with self.admin_access.repo_cnx() as cnx:
                rset = cnx.execute('Card C WHERE C title "zoubidou"')

                with self.assertRaises(NoSelectableObject):
                    cnx.vreg["adapters"].select("yo", cnx, rset=rset)

        finally:
            del self.vreg[SomeAdapter.__registry__][SomeAdapter.__regid__]


class MultiLinesRsetTC(CubicWebTC):
    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            cnx.execute('INSERT CWGroup G: G name "group1"')
            cnx.execute('INSERT CWGroup G: G name "group2"')
            cnx.commit()

    def test_default_op_in_selector(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute("Any G WHERE G is CWGroup")
            expected = len(rset)
            selector = multi_lines_rset(expected)
            self.assertEqual(selector(None, cnx, rset=rset), 1)
            self.assertEqual(selector(None, cnx, None), 0)
            selector = multi_lines_rset(expected + 1)
            self.assertEqual(selector(None, cnx, rset=rset), 0)
            self.assertEqual(selector(None, cnx, None), 0)
            selector = multi_lines_rset(expected - 1)
            self.assertEqual(selector(None, cnx, rset=rset), 0)
            self.assertEqual(selector(None, cnx, None), 0)

    def test_without_rset(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute("Any G WHERE G is CWGroup")
            expected = len(rset)
            selector = multi_lines_rset(expected)
            self.assertEqual(selector(None, cnx, None), 0)
            selector = multi_lines_rset(expected + 1)
            self.assertEqual(selector(None, cnx, None), 0)
            selector = multi_lines_rset(expected - 1)
            self.assertEqual(selector(None, cnx, None), 0)

    def test_with_operators(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute("Any G WHERE G is CWGroup")
            expected = len(rset)

            # Format     'expected', 'operator', 'assert'
            testdata = (
                (expected, eq, 1),
                (expected + 1, eq, 0),
                (expected - 1, eq, 0),
                (expected, le, 1),
                (expected + 1, le, 1),
                (expected - 1, le, 0),
                (expected - 1, gt, 1),
                (expected, gt, 0),
                (expected + 1, gt, 0),
                (expected + 1, lt, 1),
                (expected, lt, 0),
                (expected - 1, lt, 0),
            )

            for expected, operator, assertion in testdata:
                selector = multi_lines_rset(expected, operator)
                with self.subTest(expected=expected, operator=operator):
                    self.assertEqual(selector(None, cnx, rset=rset), assertion)


class MatchKwargsTC(TestCase):
    def test_match_kwargs_default(self):
        selector = match_kwargs({"a", "b"})
        self.assertEqual(selector(None, None, a=1, b=2), 2)
        self.assertEqual(selector(None, None, a=1), 0)
        self.assertEqual(selector(None, None, c=1), 0)
        self.assertEqual(selector(None, None, a=1, c=1), 0)

    def test_match_kwargs_any(self):
        selector = match_kwargs({"a", "b"}, mode="any")
        self.assertEqual(selector(None, None, a=1, b=2), 2)
        self.assertEqual(selector(None, None, a=1), 1)
        self.assertEqual(selector(None, None, c=1), 0)
        self.assertEqual(selector(None, None, a=1, c=1), 1)


class ScoreEntityTC(CubicWebTC):
    def test_intscore_entity_selector(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute("Any E WHERE E eid 1")
            selector = score_entity(lambda x: None)
            self.assertEqual(selector(None, cnx, rset=rset), 0)
            selector = score_entity(lambda x: "something")
            self.assertEqual(selector(None, cnx, rset=rset), 1)
            selector = score_entity(lambda x: object)
            self.assertEqual(selector(None, cnx, rset=rset), 1)
            rset = cnx.execute("Any G LIMIT 2 WHERE G is CWGroup")
            selector = score_entity(lambda x: 10)
            self.assertEqual(selector(None, cnx, rset=rset), 20)
            selector = score_entity(lambda x: 10, mode="any")
            self.assertEqual(selector(None, cnx, rset=rset), 10)

    def test_rql_condition_entity(self):
        with self.admin_access.cnx() as cnx:
            selector = rql_condition("X identity U")
            rset = cnx.user.as_rset()
            self.assertEqual(selector(None, cnx, rset=rset), 1)
            self.assertEqual(selector(None, cnx, entity=cnx.user), 1)
            self.assertEqual(selector(None, cnx), 0)

    def test_rql_condition_user(self):
        with self.admin_access.cnx() as cnx:
            selector = rql_condition('U login "admin"', user_condition=True)
            self.assertEqual(selector(None, cnx), 1)
            selector = rql_condition('U login "toto"', user_condition=True)
            self.assertEqual(selector(None, cnx), 0)


class AdaptablePredicateTC(CubicWebTC):
    def test_multiple_entity_types_rset(self):
        class CWUserIWhatever(EntityAdapter):
            __regid__ = "IWhatever"
            __select__ = is_instance("CWUser")

        class CWGroupIWhatever(EntityAdapter):
            __regid__ = "IWhatever"
            __select__ = is_instance("CWGroup")

        with self.temporary_appobjects(CWUserIWhatever, CWGroupIWhatever):
            with self.admin_access.cnx() as cnx:
                selector = adaptable("IWhatever")
                rset = cnx.execute("Any X WHERE X is IN(CWGroup, CWUser)")
                self.assertTrue(selector(None, cnx, rset=rset))


if __name__ == "__main__":
    unittest_main()
