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
"""unittest for cubicweb.dataimport.stores"""

from unittest.mock import patch, Mock
import datetime as DT

import pytz

from cubicweb.dataimport import stores
from cubicweb.devtools.testlib import CubicWebTC


class RQLObjectStoreTC(CubicWebTC):
    store_impl = stores.RQLObjectStore
    insert_group_attrs = dict(name="grp")
    insert_user_attrs = dict(login="lgn", upassword="pwd")
    source_name = "system"
    user_extid = None

    def test_base(self):
        with self.admin_access.repo_cnx() as cnx:
            store = self.store_impl(cnx)
            # Check data insertion
            group_eid = store.prepare_insert_entity(
                "CWGroup", **self.insert_group_attrs
            )
            user_eid = store.prepare_insert_entity("CWUser", **self.insert_user_attrs)
            store.prepare_insert_relation(user_eid, "in_group", group_eid)
            store.flush()
            store.commit()
            store.finish()
            user = cnx.execute('CWUser X WHERE X login "lgn"').one()
            self.assertEqual(user_eid, user.eid)
            self.assertTrue(user.creation_date)
            self.assertTrue(user.modification_date)
            self.assertTrue(user.cwuri)
            self.assertEqual(user.created_by[0].eid, cnx.user.eid)
            self.assertEqual(user.owned_by[0].eid, cnx.user.eid)
            self.assertEqual(user.cw_source[0].name, self.source_name)
            groups = cnx.execute('CWGroup X WHERE U in_group X, U login "lgn"')
            self.assertEqual(group_eid, groups.one().eid)
            # Check data update
            store.prepare_update_entity("CWGroup", group_eid, name="new_grp")
            store.flush()
            store.commit()
            store.finish()
            self.assertFalse(cnx.execute('CWGroup X WHERE X name "grp"'))
            self.assertTrue(cnx.execute('CWGroup X WHERE X name "new_grp"'))
            # Check data update with wrong type
            with self.assertRaises(AssertionError):
                store.prepare_update_entity("CWUser", group_eid, name="new_user")
            store.flush()
            store.commit()
            store.finish()
            self.assertFalse(cnx.execute('CWGroup X WHERE X name "new_user"'))
            self.assertTrue(cnx.execute('CWGroup X WHERE X name "new_grp"'))

    def test_store_rollback_on_error(self):
        """assert that the import is rolledback error"""

        class FakeException(Exception):
            pass

        with self.admin_access.repo_cnx() as cnx:
            cnx.rollback = Mock(wraps=cnx.rollback)
            try:
                with stores.RQLObjectStore(cnx) as store:
                    store.prepare_insert_entity("CWGroup", name="toto")
                    store.flush()
                    raise FakeException
            except FakeException:
                # something went wrong during the import, make sure the
                # transaction has been rolled back.
                cnx.rollback.assert_called_once()

            cnx.commit()
            # rollback has been called, but let's make sure that no cwgroups has
            # been created with the name "toto"
            rset = cnx.execute("Any X WHERE X is CWGroup, X name %(n)s", {"n": "toto"})
            self.assertEqual(len(rset), 0)

    @patch("cubicweb.dataimport.stores.RQLObjectStore.finish")
    @patch("cubicweb.dataimport.stores.RQLObjectStore.flush")
    def test_store_finish_called_on_flush_failure(self, flush, finish):
        """assert that the 'store.finish' and 'store.flush' are called if
        no exception is raised during import"""

        with self.admin_access.repo_cnx() as cnx:
            with stores.RQLObjectStore(cnx) as store:
                store.prepare_insert_entity("CWGroup", name="toto")

            flush.assert_called_once()
            finish.assert_called_once()


class NoHookRQLObjectStoreTC(RQLObjectStoreTC):
    store_impl = stores.NoHookRQLObjectStore


class NoHookRQLObjectStoreWithCustomMDGenStoreTC(RQLObjectStoreTC):
    insert_group_attrs = RQLObjectStoreTC.insert_group_attrs.copy()
    insert_group_attrs["cwuri"] = "http://somewhere.com/group/1"
    insert_user_attrs = RQLObjectStoreTC.insert_user_attrs.copy()
    insert_user_attrs["cwuri"] = "http://somewhere.com/user/1"
    source_name = "test"
    user_extid = b"http://somewhere.com/user/1"

    def store_impl(self, cnx):
        source = cnx.create_entity("CWSource", type="datafeed", name="test", url="test")
        cnx.commit()
        metagen = stores.MetadataGenerator(
            cnx, source=cnx.repo.source_by_eid(source.eid)
        )
        return stores.NoHookRQLObjectStore(cnx, metagen)


class MetadataGeneratorWrapperTC(CubicWebTC):
    @staticmethod
    def metagenerator_impl(cnx):
        return stores._MetaGeneratorBWCompatWrapper(stores.MetadataGenerator(cnx))

    _etype_rels = staticmethod(lambda x: x._mdgen._etype_rels)

    def test_dont_generate_relation_to_internal_manager(self):
        with self.admin_access.repo_cnx() as cnx:
            metagen = self.metagenerator_impl(cnx)
            self.assertIn("created_by", self._etype_rels(metagen))
            self.assertIn("owned_by", self._etype_rels(metagen))
        with self.repo.internal_cnx() as cnx:
            metagen = self.metagenerator_impl(cnx)
            self.assertNotIn("created_by", self._etype_rels(metagen))
            self.assertNotIn("owned_by", self._etype_rels(metagen))

    def test_dont_generate_specified_values(self):
        with self.admin_access.repo_cnx() as cnx:
            metagen = self.metagenerator_impl(cnx)
            # hijack gen_modification_date to ensure we don't go through it
            metagen.gen_modification_date = None
            md = DT.datetime.now(pytz.utc) - DT.timedelta(days=1)
            entity, rels = metagen.base_etype_dicts("CWUser")
            entity.cw_edited.update(dict(modification_date=md))
            metagen.init_entity(entity)
            self.assertEqual(entity.cw_edited["modification_date"], md)


class MetadataGeneratorTC(CubicWebTC):
    def test_dont_generate_relation_to_internal_manager(self):
        with self.admin_access.repo_cnx() as cnx:
            metagen = stores.MetadataGenerator(cnx)
            self.assertIn("created_by", metagen.etype_rels("CWUser"))
            self.assertIn("owned_by", metagen.etype_rels("CWUser"))
        with self.repo.internal_cnx() as cnx:
            metagen = stores.MetadataGenerator(cnx)
            self.assertNotIn("created_by", metagen.etype_rels("CWUser"))
            self.assertNotIn("owned_by", metagen.etype_rels("CWUser"))

    def test_dont_generate_specified_values(self):
        with self.admin_access.repo_cnx() as cnx:
            metagen = stores.MetadataGenerator(cnx)
            # hijack gen_modification_date to ensure we don't go through it
            metagen.gen_modification_date = None
            md = DT.datetime.now(pytz.utc) - DT.timedelta(days=1)
            attrs = metagen.base_etype_attrs("CWUser")
            attrs.update(dict(modification_date=md))
            metagen.init_entity_attrs("CWUser", 1, attrs)
            self.assertEqual(attrs["modification_date"], md)


if __name__ == "__main__":
    import unittest

    unittest.main()
