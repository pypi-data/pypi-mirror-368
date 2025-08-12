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
"""unittests for cw.devtools.testlib module"""
from logilab.common.registry import yes
from logilab.common.testlib import unittest_main

from cubicweb.devtools.testlib import CubicWebTC


class RepoInstancesConsistencyTC(CubicWebTC):
    test_db_id = "RepoInstancesConsistencyTC"

    def pre_setup_database(self, cnx, config):
        self.assertIs(cnx.repo, config.repository())

    def test_pre_setup(self):
        pass


class CWUtilitiesTC(CubicWebTC):
    def test_temporary_permissions_eschema(self):
        eschema = self.schema["CWUser"]
        with self.temporary_permissions(CWUser={"read": ()}):
            self.assertEqual(eschema.permissions["read"], ())
            self.assertTrue(eschema.permissions["add"])
        self.assertTrue(eschema.permissions["read"], ())

    def test_temporary_permissions_rdef(self):
        rdef = self.schema["CWUser"].relation_definition("in_group")
        with self.temporary_permissions((rdef, {"read": ()})):
            self.assertEqual(rdef.permissions["read"], ())
            self.assertTrue(rdef.permissions["add"])
        self.assertTrue(rdef.permissions["read"], ())

    def test_temporary_permissions_rdef_with_exception(self):
        rdef = self.schema["CWUser"].relation_definition("in_group")
        try:
            with self.temporary_permissions((rdef, {"read": ()})):
                self.assertEqual(rdef.permissions["read"], ())
                self.assertTrue(rdef.permissions["add"])
                raise ValueError("goto")
        except ValueError:
            self.assertTrue(rdef.permissions["read"], ())
        else:
            self.fail("exception was caught unexpectedly")

    def test_temporary_appobjects_registered(self):
        class AnAppobject:
            __registries__ = ("hip",)
            __regid__ = "hop"
            __select__ = yes()
            registered = None

            @classmethod
            def __registered__(cls, reg):
                cls.registered = reg

        with self.temporary_appobjects(AnAppobject):
            self.assertEqual(self.vreg["hip"], AnAppobject.registered)
            self.assertIn(AnAppobject, self.vreg["hip"]["hop"])
        self.assertNotIn(AnAppobject, self.vreg["hip"]["hop"])

    def test_login(self):
        """Calling login should not break hook control"""
        with self.admin_access.repo_cnx() as cnx:
            self.hook_executed = False
            self.create_user(cnx, "babar")
            cnx.commit()

        from cubicweb.server import hook
        from cubicweb.predicates import is_instance

        class MyHook(hook.Hook):
            __regid__ = "whatever"
            __select__ = hook.Hook.__select__ & is_instance("CWProperty")
            category = "test-hook"
            events = ("after_add_entity",)
            test = self

            def __call__(self):
                self.test.hook_executed = True

        with self.new_access("babar").repo_cnx() as cnx:
            with self.temporary_appobjects(MyHook):
                with cnx.allow_all_hooks_but("test-hook"):
                    cnx.create_entity("CWProperty", pkey="ui.language", value="en")
                    cnx.commit()
                    self.assertFalse(self.hook_executed)


class RepoAccessTC(CubicWebTC):
    def test_repo_connection(self):
        acc = self.new_access("admin")
        with acc.repo_cnx() as cnx:
            rset = cnx.execute("Any X WHERE X is CWUser")
            self.assertTrue(rset)

    def test_client_connection(self):
        acc = self.new_access("admin")
        with acc.client_cnx() as cnx:
            rset = cnx.execute("Any X WHERE X is CWUser")
            self.assertTrue(rset)

    def test_admin_access(self):
        with self.admin_access.client_cnx() as cnx:
            self.assertEqual("admin", cnx.user.login)


if __name__ == "__main__":
    unittest_main()
