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
"""unit/functional tests for cubicweb.server.hook"""

import unittest

from logilab.common.testlib import mock_object

from cubicweb.devtools import fake
from cubicweb.devtools.apptest_config import ApptestConfiguration
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.hooks import integrity, syncschema
from cubicweb.server import hook


class OperationsTC(CubicWebTC):
    def test_late_operation(self):
        with self.admin_access.repo_cnx() as cnx:
            l1 = hook.LateOperation(cnx)
            l2 = hook.LateOperation(cnx)
            l3 = hook.Operation(cnx)
            self.assertEqual(cnx.pending_operations, [l3, l1, l2])

    def test_single_last_operation(self):
        with self.admin_access.repo_cnx() as cnx:
            l0 = hook.SingleLastOperation(cnx)
            l1 = hook.LateOperation(cnx)
            l2 = hook.LateOperation(cnx)
            l3 = hook.Operation(cnx)
            self.assertEqual(cnx.pending_operations, [l3, l1, l2, l0])
            l4 = hook.SingleLastOperation(cnx)
            self.assertEqual(cnx.pending_operations, [l3, l1, l2, l4])

    def test_global_operation_order(self):
        with self.admin_access.repo_cnx() as cnx:
            op1 = syncschema.RDefDelOp(cnx)
            op2 = integrity._CheckORelationOp(cnx)
            op3 = syncschema.MemSchemaNotifyChanges(cnx)
            self.assertEqual([op1, op2, op3], cnx.pending_operations)


class HookCalled(Exception):
    pass


def setUpModule():
    global config, schema
    config = ApptestConfiguration("data", __file__)
    config.bootstrap_cubes()
    schema = config.load_schema()


def tearDownModule(*args):
    global config, schema
    del config, schema


class AddAnyHook(hook.Hook):
    __regid__ = "addany"
    category = "cat1"
    events = ("before_add_entity",)

    def __call__(self):
        raise HookCalled()


class HooksRegistryTC(unittest.TestCase):
    def setUp(self):
        """called before each test from this class"""
        self.vreg = mock_object(config=config, schema=schema)
        self.o = hook.HooksRegistry(self.vreg)

    def test_register_bad_hook1(self):
        class _Hook(hook.Hook):
            events = ("before_add_entiti",)

        with self.assertRaises(Exception) as cm:
            self.o.register(_Hook)
        self.assertEqual(
            str(cm.exception), f"bad event before_add_entiti on {__name__}._Hook"
        )

    def test_register_bad_hook2(self):
        class _Hook(hook.Hook):
            events = None

        with self.assertRaises(Exception) as cm:
            self.o.register(_Hook)
        self.assertEqual(
            str(cm.exception), f"bad .events attribute None on {__name__}._Hook"
        )

    def test_register_bad_hook3(self):
        class _Hook(hook.Hook):
            events = "before_add_entity"

        with self.assertRaises(Exception) as cm:
            self.o.register(_Hook)
        self.assertEqual(str(cm.exception), f"bad event b on {__name__}._Hook")

    def test_call_hook(self):
        self.o.register(AddAnyHook)
        active_hooks = set(["cat1"])
        cw = fake.FakeConnection()
        cw.is_hook_activated = lambda cls: cls.category in active_hooks
        # active hook is called
        self.assertRaises(HookCalled, self.o.call_hooks, "before_add_entity", cw)
        # inactive hook is not called
        active_hooks.remove("cat1")
        self.o.call_hooks("before_add_entity", cw)
        # reactivated hook is called
        active_hooks.add("cat1")
        self.assertRaises(HookCalled, self.o.call_hooks, "before_add_entity", cw)
        # unregisterd hook is not called
        self.o.unregister(AddAnyHook)
        self.o.call_hooks("before_add_entity", cw)


class SystemHooksTC(CubicWebTC):
    def test_startup_shutdown(self):
        import hooks  # cubicweb/server/test/data/hooks.py

        self.assertEqual(hooks.CALLED_EVENTS["server_startup"], True)
        # don't actually call repository.shutdown !
        self.repo.hm.call_hooks("server_shutdown", repo=self.repo)
        self.assertEqual(hooks.CALLED_EVENTS["server_shutdown"], True)


if __name__ == "__main__":
    unittest.main()
