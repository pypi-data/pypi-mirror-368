# copyright 2003-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""unit tests for module cubicweb.utils"""

import base64
import datetime
import decimal
import doctest
import re
from unittest import TestCase

from cubicweb import Binary, Unauthorized
from cubicweb.entity import Entity
from cubicweb.utils import make_uid, UStringIO, RepeatList

try:
    from cubicweb.utils import CubicWebJsonEncoder, json
except ImportError:
    json = None


class MakeUidTC(TestCase):
    def test_1(self):
        self.assertNotEqual(make_uid("xyz"), make_uid("abcd"))
        self.assertNotEqual(make_uid("xyz"), make_uid("xyz"))

    def test_2(self):
        d = set()
        while len(d) < 10000:
            uid = make_uid("xyz")
            if uid in d:
                self.fail(len(d))
            if re.match(r"\d", uid):
                self.fail(
                    "make_uid must not return something begining with "
                    "some numeric character, got %s" % uid
                )
            d.add(uid)


class UStringIOTC(TestCase):
    def test_boolean_value(self):
        self.assertTrue(UStringIO())


class RepeatListTC(TestCase):
    def test_base(self):
        r_list = RepeatList(3, (1, 3))
        self.assertEqual(r_list[0], (1, 3))
        self.assertEqual(r_list[2], (1, 3))
        self.assertEqual(r_list[-1], (1, 3))
        self.assertEqual(len(r_list), 3)
        # XXX
        self.assertEqual(r_list[4], (1, 3))

        self.assertFalse(RepeatList(0, None))

    def test_slice(self):
        r_list = RepeatList(3, (1, 3))
        self.assertEqual(r_list[0:1], [(1, 3)])
        self.assertEqual(r_list[0:4], [(1, 3)] * 3)
        self.assertEqual(r_list[:], [(1, 3)] * 3)

    def test_iter(self):
        self.assertEqual(list(RepeatList(3, (1, 3))), [(1, 3)] * 3)

    def test_add(self):
        r_list = RepeatList(3, (1, 3))
        self.assertEqual(r_list + [(1, 4)], [(1, 3)] * 3 + [(1, 4)])
        self.assertEqual([(1, 4)] + r_list, [(1, 4)] + [(1, 3)] * 3)
        self.assertEqual(r_list + RepeatList(2, (2, 3)), [(1, 3)] * 3 + [(2, 3)] * 2)

        x = r_list + RepeatList(2, (1, 3))
        self.assertIsInstance(x, RepeatList)
        self.assertEqual(len(x), 5)
        self.assertEqual(x[0], (1, 3))

        x = r_list + [(1, 3)] * 2
        self.assertEqual(x, [(1, 3)] * 5)

    def test_eq(self):
        self.assertEqual(RepeatList(3, (1, 3)), [(1, 3)] * 3)

    def test_pop(self):
        r_list = RepeatList(3, (1, 3))
        r_list.pop(2)
        self.assertEqual(r_list, [(1, 3)] * 2)


class JSONEncoderTC(TestCase):
    def setUp(self):
        if json is None:
            self.skipTest("json not available")

    def encode(self, value):
        return json.dumps(value, cls=CubicWebJsonEncoder)

    def test_encoding_dates(self):
        self.assertEqual(
            self.encode(datetime.datetime(2009, 9, 9, 20, 30)), '"2009/09/09 20:30:00"'
        )
        self.assertEqual(self.encode(datetime.date(2009, 9, 9)), '"2009/09/09"')
        self.assertEqual(self.encode(datetime.time(20, 30)), '"20:30:00"')

    def test_encoding_decimal(self):
        self.assertEqual(self.encode(decimal.Decimal("1.2")), "1.2")

    def test_encoding_bare_entity(self):
        e = Entity(None)
        e.cw_attr_cache["pouet"] = "hop"
        e.eid = 2
        self.assertEqual(json.loads(self.encode(e)), {"pouet": "hop", "eid": 2})

    def test_encoding_entity_in_list(self):
        e = Entity(None)
        e.cw_attr_cache["pouet"] = "hop"
        e.eid = 2
        self.assertEqual(json.loads(self.encode([e])), [{"pouet": "hop", "eid": 2}])

    def test_encoding_binary(self):
        for content in (b"he he", b"h\xe9 hxe9"):
            with self.subTest(content=content):
                encoded = self.encode(Binary(content))
                self.assertEqual(base64.b64decode(encoded), content)

    def test_encoding_unknown_stuff(self):
        self.assertEqual(self.encode(TestCase), "null")


def UnauthorizedTC(TestCase):
    def _test(self, func):
        self.assertEqual(
            func(Unauthorized()), "You are not allowed to perform this operation"
        )
        self.assertEqual(func(Unauthorized("a")), "a")
        self.assertEqual(
            func(Unauthorized("a", "b")),
            "You are not allowed to perform a operation on b",
        )
        self.assertEqual(func(Unauthorized("a", "b", "c")), "a b c")

    def test_str(self):
        self._test(str)


def load_tests(loader, tests, ignore):
    import cubicweb.utils

    tests.addTests(doctest.DocTestSuite(cubicweb.utils))
    return tests


if __name__ == "__main__":
    import unittest

    unittest.main()
