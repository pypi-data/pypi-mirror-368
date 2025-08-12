# copyright 2003-2018 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""unit tests for module cubicweb.rset"""

import pickle
from urllib.parse import urlsplit

from logilab.common.testlib import TestCase, unittest_main, mock_object
from rql import parse

from cubicweb import NoResultError, MultipleResultsError
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.rset import NotAnEntity, ResultSet, attr_desc_iterator


def pprelcachedict(d):
    res = {}
    for k, (rset, related) in d.items():
        res[k] = sorted(v.eid for v in related)
    return sorted(res.items())


class AttrDescIteratorTC(TestCase):
    """TestCase for cubicweb.rset.attr_desc_iterator"""

    def test_relations_description(self):
        """tests relations_description() function"""
        queries = {
            "Any U,L,M where U is CWUser, U login L, U mail M": [
                (1, "login", "subject"),
                (2, "mail", "subject"),
            ],
            "Any U,L,M where U is CWUser, L is Foo, U mail M": [(2, "mail", "subject")],
            "Any C,P where C is Company, C employs P": [(1, "employs", "subject")],
            "Any C,P where C is Company, P employed_by P": [],
            "Any C where C is Company, C employs P": [],
        }
        for rql, relations in queries.items():
            result = list(attr_desc_iterator(parse(rql).children[0], 0, 0))
            self.assertEqual((rql, result), (rql, relations))

    def test_relations_description_indexed(self):
        """tests relations_description() function"""
        queries = {
            "Any C,U,P,L,M where C is Company, C employs P, U is CWUser, U login L, U mail M": {
                0: [(2, "employs", "subject")],
                1: [(3, "login", "subject"), (4, "mail", "subject")],
            },
        }
        for rql, results in queries.items():
            for idx, relations in results.items():
                result = list(attr_desc_iterator(parse(rql).children[0], idx, idx))
                self.assertEqual(result, relations)

    def test_subquery_callfunc(self):
        rql = (
            "Any A,B,C,COUNT(D) GROUPBY A,B,C WITH A,B,C,D BEING "
            "(Any YEAR(CD), MONTH(CD), S, X WHERE X is CWUser, "
            "X creation_date CD, X in_state S)"
        )
        rqlst = parse(rql)
        select, col = rqlst.locate_subquery(2, "CWUser", None)
        result = list(attr_desc_iterator(select, col, 2))
        self.assertEqual(result, [])

    def test_subquery_callfunc_2(self):
        rql = (
            "Any X,S,L WHERE "
            "X in_state S WITH X, L BEING (Any X,MAX(L) GROUPBY X WHERE "
            "X is CWUser, T wf_info_for X, T creation_date L)"
        )
        rqlst = parse(rql)
        select, col = rqlst.locate_subquery(0, "CWUser", None)
        result = list(attr_desc_iterator(select, col, 0))
        self.assertEqual(result, [(1, "in_state", "subject")])


class ResultSetTC(CubicWebTC):
    def setUp(self):
        super().setUp()
        self.rset = ResultSet(
            [[12, "adim"], [13, "syt"]],
            "Any U,L where U is CWUser, U login L",
            description=[["CWUser", "String"], ["Bar", "String"]],
        )
        self.rset.req = mock_object(vreg=self.vreg, repo=self.repo)

    def compare_urls(self, url1, url2):
        info1 = urlsplit(url1)
        info2 = urlsplit(url2)
        self.assertEqual(info1[:3], info2[:3])
        if info1[3] != info2[3]:
            params1 = dict(pair.split("=") for pair in info1[3].split("&"))
            params2 = dict(pair.split("=") for pair in info1[3].split("&"))
            self.assertDictEqual(params1, params2)

    def test_pickle(self):
        del self.rset.req
        rs2 = pickle.loads(pickle.dumps(self.rset))
        self.assertEqual(self.rset.rows, rs2.rows)
        self.assertEqual(self.rset.rowcount, rs2.rowcount)
        self.assertEqual(self.rset.rql, rs2.rql)
        self.assertEqual(self.rset.description, rs2.description)

    def test_build_url(self):
        with self.admin_access.cnx() as cnx:
            baseurl = cnx.base_url()
            self.compare_urls(
                cnx.build_url("view", vid="foo", rql="yo"),
                f"{baseurl}view?vid=foo&rql=yo",
            )
            self.compare_urls(
                cnx.build_url("view", _restpath="task/title/go"),
                f"{baseurl}task/title/go",
            )
            # self.compare_urls(cnx.build_url('view', _restpath='/task/title/go'),
            #                   '%stask/title/go' % baseurl)
            # empty _restpath should not crash
            self.compare_urls(cnx.build_url("view", _restpath=""), baseurl)

    def test_build(self):
        """test basic build of a ResultSet"""
        rs = ResultSet(
            [1, 2, 3], "CWGroup X", description=["CWGroup", "CWGroup", "CWGroup"]
        )
        self.assertEqual(rs.rowcount, 3)
        self.assertEqual(rs.rows, [1, 2, 3])
        self.assertEqual(rs.description, ["CWGroup", "CWGroup", "CWGroup"])

    def test_limit(self):
        rs = ResultSet(
            [[12000, "adim"], [13000, "syt"], [14000, "nico"]],
            "Any U,L where U is CWUser, U login L",
            description=[["CWUser", "String"]] * 3,
        )
        with self.admin_access.cnx() as cnx:
            rs.req = cnx
            rs.vreg = self.vreg
            self.assertEqual(rs.limit(2).rows, [[12000, "adim"], [13000, "syt"]])
            rs2 = rs.limit(2, offset=1)
            self.assertEqual(rs2.rows, [[13000, "syt"], [14000, "nico"]])
            self.assertEqual(rs2.get_entity(0, 0).cw_row, 0)
            self.assertEqual(rs.limit(2, offset=2).rows, [[14000, "nico"]])
            self.assertEqual(rs.limit(2, offset=3).rows, [])

    def test_limit_2(self):
        with self.admin_access.repo_cnx() as cnx:
            rs = cnx.execute("Any E,U WHERE E is CWEType, E created_by U")
            # get entity on row 9. This will fill its created_by relation cache,
            # with cwuser on row 9 as well
            e1 = rs.get_entity(9, 0)  # noqa
            # get entity on row 10. This will fill its created_by relation cache,
            # with cwuser built on row 9
            e2 = rs.get_entity(10, 0)
            # limit result set from row 10
            rs.limit(1, 10, inplace=True)
            # get back eid
            e = rs.get_entity(0, 0)
            self.assertIs(e2, e)
            # rs.limit has properly removed cwuser for cnxuest cache, but it's
            # still referenced by e/e2 relation cache
            u = e.created_by[0]
            # now ensure this doesn't trigger IndexError because cwuser.cw_row is 9
            # while now rset has only one row
            u.cw_rset[u.cw_row]

    def test_filter(self):
        rs = ResultSet(
            [[12000, "adim"], [13000, "syt"], [14000, "nico"]],
            "Any U,L where U is CWUser, U login L",
            description=[["CWUser", "String"]] * 3,
        )
        with self.admin_access.cnx() as cnx:
            rs.req = cnx
            rs.vreg = cnx.vreg

            def test_filter(entity):
                return entity.login != "nico"

            rs2 = rs.filtered_rset(test_filter)
            self.assertEqual(len(rs2), 2)
            self.assertEqual([login for _, login in rs2], ["adim", "syt"])
            self.assertEqual(rs2.description, rs.description[1:])

    def test_transform(self):
        rs = ResultSet(
            [[12, "adim"], [13, "syt"], [14, "nico"]],
            "Any U,L where U is CWUser, U login L",
            description=[["CWUser", "String"]] * 3,
        )
        with self.admin_access.cnx() as cnx:
            rs.req = cnx

            def test_transform(row, desc):
                return row[1:], desc[1:]

            rs2 = rs.transformed_rset(test_transform)

            self.assertEqual(len(rs2), 3)
            self.assertEqual(list(rs2), [["adim"], ["syt"], ["nico"]])

    def test_sort(self):
        rs = ResultSet(
            [[12000, "adim"], [13000, "syt"], [14000, "nico"]],
            "Any U,L where U is CWUser, U login L",
            description=[["CWUser", "String"]] * 3,
        )
        with self.admin_access.cnx() as cnx:
            rs.req = cnx
            rs.vreg = self.vreg

            rs2 = rs.sorted_rset(lambda e: e.cw_attr_cache["login"])
            self.assertEqual(len(rs2), 3)
            self.assertEqual([login for _, login in rs2], ["adim", "nico", "syt"])
            # make sure rs is unchanged
            self.assertEqual([login for _, login in rs], ["adim", "syt", "nico"])

            rs2 = rs.sorted_rset(lambda e: e.cw_attr_cache["login"], reverse=True)
            self.assertEqual(len(rs2), 3)
            self.assertEqual([login for _, login in rs2], ["syt", "nico", "adim"])
            # make sure rs is unchanged
            self.assertEqual([login for _, login in rs], ["adim", "syt", "nico"])

            rs3 = rs.sorted_rset(lambda row: row[1], col=-1)
            self.assertEqual(len(rs3), 3)
            self.assertEqual([login for _, login in rs3], ["adim", "nico", "syt"])
            # make sure rs is unchanged
            self.assertEqual([login for _, login in rs], ["adim", "syt", "nico"])

    def test_split(self):
        rs = ResultSet(
            [
                [12000, "adim", "Adim chez les pinguins"],
                [12000, "adim", "Jardiner facile"],
                [13000, "syt", "Le carrelage en 42 leçons"],
                [14000, "nico", "La tarte tatin en 15 minutes"],
                [14000, "nico", "L'épluchage du castor commun"],
            ],
            ("Any U, L, T WHERE U is CWUser, U login L," "D created_by U, D title T"),
            description=[["CWUser", "String", "String"]] * 5,
        )
        with self.admin_access.cnx() as cnx:
            rs.req = cnx
            rs.vreg = self.vreg
            rsets = rs.split_rset(lambda e: e.cw_attr_cache["login"])
            self.assertEqual(len(rsets), 3)
            self.assertEqual([login for _, login, _ in rsets[0]], ["adim", "adim"])
            self.assertEqual([login for _, login, _ in rsets[1]], ["syt"])
            self.assertEqual([login for _, login, _ in rsets[2]], ["nico", "nico"])
            # make sure rs is unchanged
            self.assertEqual(
                [login for _, login, _ in rs], ["adim", "adim", "syt", "nico", "nico"]
            )

            rsets = rs.split_rset(lambda e: e.cw_attr_cache["login"], return_dict=True)
            self.assertEqual(len(rsets), 3)
            self.assertEqual([login for _, login, _ in rsets["nico"]], ["nico", "nico"])
            self.assertEqual([login for _, login, _ in rsets["adim"]], ["adim", "adim"])
            self.assertEqual([login for _, login, _ in rsets["syt"]], ["syt"])
            # make sure rs is unchanged
            self.assertEqual(
                [login for _, login, _ in rs], ["adim", "adim", "syt", "nico", "nico"]
            )

            rsets = rs.split_rset(lambda s: s.count("d"), col=2)
            self.assertEqual(len(rsets), 2)
            self.assertEqual(
                [title for _, _, title in rsets[0]],
                [
                    "Adim chez les pinguins",
                    "Jardiner facile",
                    "L'épluchage du castor commun",
                ],
            )
            self.assertEqual(
                [title for _, _, title in rsets[1]],
                ["Le carrelage en 42 leçons", "La tarte tatin en 15 minutes"],
            )
            # make sure rs is unchanged
            self.assertEqual(
                [title for _, _, title in rs],
                [
                    "Adim chez les pinguins",
                    "Jardiner facile",
                    "Le carrelage en 42 leçons",
                    "La tarte tatin en 15 minutes",
                    "L'épluchage du castor commun",
                ],
            )

    def test_cached_syntax_tree(self):
        """make sure syntax tree is cached"""
        rqlst1 = self.rset.syntax_tree()
        rqlst2 = self.rset.syntax_tree()
        self.assertIs(rqlst1, rqlst2)

    def test_get_entity_simple(self):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity(
                "CWUser",
                login="adim",
                upassword="adim",
                surname="di mascio",
                firstname="adrien",
            )
            cnx.drop_entity_cache()
            e = cnx.execute('Any X,T WHERE X login "adim", X surname T').get_entity(
                0, 0
            )
            self.assertEqual(e.cw_attr_cache["surname"], "di mascio")
            self.assertRaises(KeyError, e.cw_attr_cache.__getitem__, "firstname")
            self.assertRaises(KeyError, e.cw_attr_cache.__getitem__, "creation_date")
            self.assertEqual(pprelcachedict(e._cw_related_cache), [])
            e.complete()
            self.assertEqual(e.cw_attr_cache["firstname"], "adrien")
            self.assertEqual(pprelcachedict(e._cw_related_cache), [])

    def test_get_entity_advanced(self):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity("Bookmark", title="zou", path="/view")
            cnx.drop_entity_cache()
            cnx.execute('SET X bookmarked_by Y WHERE X is Bookmark, Y login "anon"')
            rset = cnx.execute(
                "Any X,Y,XT,YN WHERE X bookmarked_by Y, X title XT, Y login YN"
            )

            e = rset.get_entity(0, 0)
            self.assertEqual(e.cw_row, 0)
            self.assertEqual(e.cw_col, 0)
            self.assertEqual(e.cw_attr_cache["title"], "zou")
            self.assertRaises(KeyError, e.cw_attr_cache.__getitem__, "path")
            other_rset = cnx.execute("Any X, P WHERE X is Bookmark, X path P")
            # check that get_entity fetches e from the request's cache, and
            # updates it with attributes from the new rset
            self.assertIs(other_rset.get_entity(0, 0), e)
            self.assertIn("path", e.cw_attr_cache)
            self.assertEqual(pprelcachedict(e._cw_related_cache), [])

            e = rset.get_entity(0, 1)
            self.assertEqual(e.cw_row, 0)
            self.assertEqual(e.cw_col, 1)
            self.assertEqual(e.cw_attr_cache["login"], "anon")
            self.assertRaises(KeyError, e.cw_attr_cache.__getitem__, "firstname")
            self.assertEqual(pprelcachedict(e._cw_related_cache), [])
            e.complete()
            self.assertEqual(e.cw_attr_cache["firstname"], None)
            self.assertEqual(pprelcachedict(e._cw_related_cache), [])

            self.assertRaises(NotAnEntity, rset.get_entity, 0, 2)
            self.assertRaises(NotAnEntity, rset.get_entity, 0, 3)

    def test_get_entity_relation_cache_compt(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute('Any X,S WHERE X in_state S, X login "anon"')
            e = rset.get_entity(0, 0)
            seid = cnx.execute('State X WHERE X name "activated"')[0][0]
            # for_user / in_group are prefetched in CWUser __init__, in_state should
            # be filed from our query rset
            self.assertEqual(
                pprelcachedict(e._cw_related_cache), [("in_state_subject", [seid])]
            )

    def test_get_entity_advanced_prefilled_cache(self):
        with self.admin_access.repo_cnx() as cnx:
            e = cnx.create_entity("Bookmark", title="zou", path="path")
            cnx.commit()
            rset = cnx.execute(
                "Any X, U, S, XT, UL, SN WHERE X created_by U, U in_state S, "
                "X title XT, S name SN, U login UL, X eid %s" % e.eid
            )
            e = rset.get_entity(0, 0)
            self.assertEqual(e.cw_attr_cache["title"], "zou")
            self.assertEqual(
                pprelcachedict(e._cw_related_cache),
                [("created_by_subject", [cnx.user.eid])],
            )
            # first level of recursion
            u = e.created_by[0]
            self.assertEqual(u.cw_attr_cache["login"], "admin")
            self.assertRaises(KeyError, u.cw_attr_cache.__getitem__, "firstname")
            # second level of recursion
            s = u.in_state[0]
            self.assertEqual(s.cw_attr_cache["name"], "activated")
            self.assertRaises(KeyError, s.cw_attr_cache.__getitem__, "description")

    def test_get_entity_recursion(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity(
                "EmailAddress", address="toto", reverse_primary_email=cnx.user.eid
            )
            cnx.commit()

        # get_entity should fill the caches for user and email, even if both
        # entities are already in the connection's entity cache
        with self.admin_access.repo_cnx() as cnx:
            mail = cnx.find("EmailAddress").one()
            rset = cnx.execute("Any X, E WHERE X primary_email E")
            u = rset.get_entity(0, 0)
            self.assertTrue(u.cw_relation_cached("primary_email", "subject"))
            self.assertTrue(mail.cw_relation_cached("primary_email", "object"))

        with self.admin_access.repo_cnx() as cnx:
            mail = cnx.find("EmailAddress").one()
            rset = cnx.execute("Any X, E WHERE X primary_email E")
            rset.get_entity(0, 1)
            self.assertTrue(mail.cw_relation_cached("primary_email", "object"))
            u = cnx.user
            self.assertTrue(u.cw_relation_cached("primary_email", "subject"))

    def test_get_entity_cache_with_left_outer_join(self):
        with self.admin_access.cnx() as cnx:
            eid = cnx.execute(
                'INSERT CWUser E: E login "joe", E upassword "joe", E in_group G '
                'WHERE G name "users"'
            )[0][0]
            rset = cnx.execute(
                "Any X,E WHERE X eid %(x)s, X primary_email E?", {"x": eid}
            )
            e = rset.get_entity(0, 0)
            # if any of the assertion below fails with a KeyError, the relation is not cached
            # related entities should be an empty list
            self.assertEqual(e._cw_related_cache["primary_email_subject"][True], ())
            # related rset should be an empty rset
            cached = e._cw_related_cache["primary_email_subject"][False]
            self.assertIsInstance(cached, ResultSet)
            self.assertEqual(cached.rowcount, 0)

    def test_get_entity_union(self):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity("Bookmark", title="manger", path="path")
            cnx.drop_entity_cache()
            rset = cnx.execute(
                "Any X,N ORDERBY N WITH X,N BEING "
                "((Any X,N WHERE X is Bookmark, X title N)"
                " UNION "
                " (Any X,N WHERE X is CWGroup, X name N))"
            )
            expected = (
                ("CWGroup", "guests"),
                ("CWGroup", "managers"),
                ("Bookmark", "manger"),
                ("CWGroup", "owners"),
                ("CWGroup", "users"),
            )
            for entity in rset.entities():  # test get_entity for each row actually
                etype, n = expected[entity.cw_row]
                self.assertEqual(entity.cw_etype, etype)
                attr = etype == "Bookmark" and "title" or "name"
                self.assertEqual(entity.cw_attr_cache[attr], n)

    def test_one(self):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity(
                "CWUser",
                login="cdevienne",
                upassword="cdevienne",
                surname="de Vienne",
                firstname="Christophe",
            )
            e = cnx.execute('Any X WHERE X login "cdevienne"').one()

            self.assertEqual(e.surname, "de Vienne")

            e = cnx.execute('Any X, N WHERE X login "cdevienne", X surname N').one()
            self.assertEqual(e.surname, "de Vienne")

            e = cnx.execute('Any N, X WHERE X login "cdevienne", X surname N').one(
                col=1
            )
            self.assertEqual(e.surname, "de Vienne")

    def test_one_no_rows(self):
        with self.admin_access.cnx() as cnx:
            with self.assertRaises(NoResultError):
                cnx.execute('Any X WHERE X login "patanok"').one()

    def test_one_multiple_rows(self):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity(
                "CWUser",
                login="cdevienne",
                upassword="cdevienne",
                surname="de Vienne",
                firstname="Christophe",
            )

            cnx.create_entity(
                "CWUser",
                login="adim",
                upassword="adim",
                surname="di mascio",
                firstname="adrien",
            )

            with self.assertRaises(MultipleResultsError):
                cnx.execute("Any X WHERE X is CWUser").one()

    def test_first(self):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity(
                "CWUser",
                login="cdevienne",
                upassword="cdevienne",
                surname="de Vienne",
                firstname="Christophe",
            )
            e = cnx.execute('Any X WHERE X login "cdevienne"').first()
            self.assertEqual(e.surname, "de Vienne")

            e = cnx.execute('Any X, N WHERE X login "cdevienne", X surname N').first()
            self.assertEqual(e.surname, "de Vienne")

            e = cnx.execute('Any N, X WHERE X login "cdevienne", X surname N').first(
                col=1
            )
            self.assertEqual(e.surname, "de Vienne")

    def test_first_no_rows(self):
        with self.admin_access.cnx() as cnx:
            with self.assertRaises(NoResultError):
                cnx.execute('Any X WHERE X login "patanok"').first()

    def test_first_multiple_rows(self):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity(
                "CWUser",
                login="user1",
                upassword="cdevienne",
                surname="de Vienne",
                firstname="Christophe",
            )
            cnx.create_entity(
                "CWUser",
                login="user2",
                upassword="adim",
                surname="di mascio",
                firstname="adrien",
            )

            e = cnx.execute(
                "Any X ORDERBY X WHERE X is CWUser, " 'X login LIKE "user%"'
            ).first()
            self.assertEqual(e.login, "user1")

    def test_last(self):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity(
                "CWUser",
                login="cdevienne",
                upassword="cdevienne",
                surname="de Vienne",
                firstname="Christophe",
            )
            e = cnx.execute('Any X WHERE X login "cdevienne"').last()
            self.assertEqual(e.surname, "de Vienne")

            e = cnx.execute('Any X, N WHERE X login "cdevienne", X surname N').last()
            self.assertEqual(e.surname, "de Vienne")

            e = cnx.execute('Any N, X WHERE X login "cdevienne", X surname N').last(
                col=1
            )
            self.assertEqual(e.surname, "de Vienne")

    def test_last_no_rows(self):
        with self.admin_access.cnx() as cnx:
            with self.assertRaises(NoResultError):
                cnx.execute('Any X WHERE X login "patanok"').last()

    def test_last_multiple_rows(self):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity(
                "CWUser",
                login="user1",
                upassword="cdevienne",
                surname="de Vienne",
                firstname="Christophe",
            )
            cnx.create_entity(
                "CWUser",
                login="user2",
                upassword="adim",
                surname="di mascio",
                firstname="adrien",
            )

            e = cnx.execute(
                "Any X ORDERBY X WHERE X is CWUser, " 'X login LIKE "user%"'
            ).last()
            self.assertEqual(e.login, "user2")

    def test_related_entity_optional(self):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity("Bookmark", title="aaaa", path="path")
            rset = cnx.execute("Any B,U,L WHERE B bookmarked_by U?, U login L")
            entity, rtype = rset.related_entity(0, 2)
            self.assertEqual(entity, None)
            self.assertEqual(rtype, None)

    def test_related_entity_union_subquery_1(self):
        with self.admin_access.cnx() as cnx:
            e = cnx.create_entity("Bookmark", title="aaaa", path="path")
            rset = cnx.execute(
                "Any X,N ORDERBY N WITH X,N BEING "
                "((Any X,N WHERE X is CWGroup, X name N)"
                " UNION "
                " (Any X,N WHERE X is Bookmark, X title N))"
            )
            entity, rtype = rset.related_entity(0, 1)
            self.assertEqual(entity.eid, e.eid)
            self.assertEqual(rtype, "title")
            self.assertEqual(entity.title, "aaaa")
            entity, rtype = rset.related_entity(1, 1)
            self.assertEqual(entity.cw_etype, "CWGroup")
            self.assertEqual(rtype, "name")
            self.assertEqual(entity.name, "guests")

    def test_related_entity_union_subquery_2(self):
        with self.admin_access.cnx() as cnx:
            e = cnx.create_entity("Bookmark", title="aaaa", path="path")
            rset = cnx.execute(
                "Any X,N ORDERBY N WHERE X is Bookmark WITH X,N BEING "
                "((Any X,N WHERE X is CWGroup, X name N)"
                " UNION "
                " (Any X,N WHERE X is Bookmark, X title N))"
            )
            entity, rtype = rset.related_entity(0, 1)
            self.assertEqual(entity.eid, e.eid)
            self.assertEqual(rtype, "title")
            self.assertEqual(entity.title, "aaaa")

    def test_related_entity_union_subquery_3(self):
        with self.admin_access.cnx() as cnx:
            e = cnx.create_entity("Bookmark", title="aaaa", path="path")
            rset = cnx.execute(
                "Any X,N ORDERBY N WITH N,X BEING "
                "((Any N,X WHERE X is CWGroup, X name N)"
                " UNION "
                " (Any N,X WHERE X is Bookmark, X title N))"
            )
            entity, rtype = rset.related_entity(0, 1)
            self.assertEqual(entity.eid, e.eid)
            self.assertEqual(rtype, "title")
            self.assertEqual(entity.title, "aaaa")

    def test_related_entity_union_subquery_4(self):
        with self.admin_access.cnx() as cnx:
            e = cnx.create_entity("Bookmark", title="aaaa", path="path")
            rset = cnx.execute(
                "Any X,X, N ORDERBY N WITH X,N BEING "
                "((Any X,N WHERE X is CWGroup, X name N)"
                " UNION "
                " (Any X,N WHERE X is Bookmark, X title N))"
            )
            entity, rtype = rset.related_entity(0, 2)
            self.assertEqual(entity.eid, e.eid)
            self.assertEqual(rtype, "title")
            self.assertEqual(entity.title, "aaaa")

    def test_related_entity_trap_subquery(self):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity("Bookmark", title="test bookmark", path="")
            cnx.execute('SET B bookmarked_by U WHERE U login "admin"')
            rset = cnx.execute(
                "Any B,T,L WHERE B bookmarked_by U, U login L "
                "WITH B,T BEING (Any B,T WHERE B is Bookmark, B title T)"
            )
            rset.related_entity(0, 2)

    def test_related_entity_subquery_outerjoin(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute(
                "Any X,S,L WHERE X in_state S "
                "WITH X, L BEING (Any X,MAX(L) GROUPBY X "
                "WHERE X is CWUser, T? wf_info_for X, T creation_date L)"
            )
            self.assertEqual(len(rset), 2)
            rset.related_entity(0, 1)
            rset.related_entity(0, 2)

    def test_entities(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute("Any U,G WHERE U in_group G")
            # make sure we have at least one element
            self.assertTrue(rset)
            self.assertEqual({e.e_schema.type for e in rset.entities(0)}, {"CWUser"})
            self.assertEqual({e.e_schema.type for e in rset.entities(1)}, {"CWGroup"})

    def test_iter_rows_with_entities(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute(
                "Any U,UN,G,GN WHERE U in_group G, U login UN, G name GN"
            )
            # make sure we have at least one element
            self.assertTrue(rset)
            out = list(rset.iter_rows_with_entities())[0]
            self.assertEqual(out[0].login, out[1])
            self.assertEqual(out[2].name, out[3])

    def test_printable_rql(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute("CWEType X WHERE X final FALSE")
            self.assertEqual(
                rset.printable_rql(), "Any X WHERE X final FALSE, X is CWEType"
            )

    def test_searched_text(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute('Any X WHERE X has_text "foobar"')
            self.assertEqual(rset.searched_text(), "foobar")
            rset = cnx.execute("Any X WHERE X has_text %(text)s", {"text": "foo"})
            self.assertEqual(rset.searched_text(), "foo")

    def test_count_users_by_date(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute(
                "Any D, COUNT(U) GROUPBY D " "WHERE U is CWUser, U creation_date D"
            )
            self.assertEqual(rset.related_entity(0, 0), (None, None))

    def test_str(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute("(Any X,N WHERE X is CWGroup, X name N)")
            self.assertIsInstance(str(rset), str)
            self.assertEqual(len(str(rset).splitlines()), 1)

    def test_repr(self):
        with self.admin_access.cnx() as cnx:
            rset = cnx.execute("(Any X,N WHERE X is CWGroup, X name N)")
            self.assertIsInstance(repr(rset), str)
            self.assertGreater(len(repr(rset).splitlines()), 1)

            rset = cnx.execute('(Any X WHERE X is CWGroup, X name "managers")')
            self.assertIsInstance(str(rset), str)
            self.assertEqual(len(str(rset).splitlines()), 1)

    def test_slice(self):
        rs = ResultSet(
            [
                [12000, "adim", "Adim chez les pinguins"],
                [12000, "adim", "Jardiner facile"],
                [13000, "syt", "Le carrelage en 42 leçons"],
                [14000, "nico", "La tarte tatin en 15 minutes"],
                [14000, "nico", "L'épluchage du castor commun"],
            ],
            ("Any U, L, T WHERE U is CWUser, U login L," "D created_by U, D title T"),
            description=[["CWUser", "String", "String"]] * 5,
        )
        self.assertEqual(
            rs[1::2],
            [
                [12000, "adim", "Jardiner facile"],
                [14000, "nico", "La tarte tatin en 15 minutes"],
            ],
        )

    def test_nonregr_symmetric_relation(self):
        # see https://www.cubicweb.org/ticket/4739253
        with self.admin_access.client_cnx() as cnx:
            p1 = cnx.create_entity("Personne", nom="sylvain")
            cnx.create_entity("Personne", nom="denis", connait=p1)
            cnx.commit()
            rset = cnx.execute("Any X,Y WHERE X connait Y")
            rset.get_entity(0, 1)  # used to raise KeyError


if __name__ == "__main__":
    unittest_main()
