# copyright 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""unit tests for database value generator"""

import datetime
import os.path as osp
import re

from logilab.common.testlib import TestCase, unittest_main

from cubicweb.devtools.apptest_config import ApptestConfiguration
from cubicweb.devtools.fill import ValueGenerator, make_tel

DATADIR = osp.join(osp.abspath(osp.dirname(__file__)), "data")
ISODATE_SRE = re.compile(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})$")


class MyValueGenerator(ValueGenerator):
    def generate_Bug_severity(self, entity, index):
        return "dangerous"

    def generate_Any_description(self, entity, index, format=None):
        return "yo"


class ValueGeneratorTC(TestCase):
    """test case for ValueGenerator"""

    def _choice_func(self, etype, attrname):
        try:
            return getattr(self, f"_available_{etype}_{attrname}")(etype, attrname)
        except AttributeError:
            return None

    def _available_Person_firstname(self, etype, attrname):
        return [
            f.strip()
            for f in open(osp.join(DATADIR, "firstnames.txt"), encoding="latin1")
        ]

    def setUp(self):
        config = ApptestConfiguration("data", __file__)
        config.bootstrap_cubes()
        schema = config.load_schema()
        e_schema = schema.entity_schema_for("Person")
        self.person_valgen = ValueGenerator(e_schema, self._choice_func)
        e_schema = schema.entity_schema_for("Bug")
        self.bug_valgen = MyValueGenerator(e_schema)
        self.config = config

    def test_string(self):
        """test string generation"""
        surname = self.person_valgen.generate_attribute_value({}, "surname", 12)
        self.assertEqual(surname, "é&surname12")

    def test_domain_value(self):
        """test value generation from a given domain value"""
        firstname = self.person_valgen.generate_attribute_value({}, "firstname", 12)
        possible_choices = self._choice_func("Person", "firstname")
        self.assertIn(
            firstname, possible_choices, f"{firstname} not in {possible_choices}"
        )

    def test_choice(self):
        """test choice generation"""
        # Test for random index
        for index in range(5):
            sx_value = self.person_valgen.generate_attribute_value(
                {}, "civility", index
            )
            self.assertIn(sx_value, ("Mr", "Mrs", "Ms"))

    def test_integer(self):
        """test integer generation"""
        # Test for random index
        for index in range(5):
            cost_value = self.bug_valgen.generate_attribute_value({}, "cost", index)
            self.assertIn(cost_value, list(range(index + 1)))

    def test_date(self):
        """test date generation"""
        # Test for random index
        for index in range(10):
            date_value = self.person_valgen.generate_attribute_value(
                {}, "birthday", index
            )
            self.assertIsInstance(date_value, datetime.date)

    def test_phone(self):
        """tests make_tel utility"""
        self.assertEqual(make_tel(22030405), "22 03 04 05")

    def test_customized_generation(self):
        self.assertEqual(
            self.bug_valgen.generate_attribute_value({}, "severity", 12), "dangerous"
        )
        self.assertEqual(
            self.bug_valgen.generate_attribute_value({}, "description", 12), "yo"
        )
        self.assertEqual(
            self.person_valgen.generate_attribute_value({}, "description", 12), "yo"
        )


if __name__ == "__main__":
    unittest_main()
