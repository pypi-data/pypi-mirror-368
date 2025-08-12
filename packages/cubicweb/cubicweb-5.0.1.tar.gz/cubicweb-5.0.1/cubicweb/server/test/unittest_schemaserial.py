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
"""unit tests for schema rql (de)serialization"""

from logilab.database import get_db_helper
from yams import register_base_type, unregister_base_type

from cubicweb import Binary
from cubicweb.devtools.apptest_config import ApptestConfiguration
from cubicweb.devtools.testlib import BaseTestCase as TestCase, CubicWebTC
from cubicweb.schema import CubicWebSchemaLoader
from cubicweb.server.schemaserial import (
    updateeschema2rql,
    updaterschema2rql,
    rschema2rql,
    eschema2rql,
    rdef2rql,
    specialize2rql,
    _erperms2rql as erperms2rql,
)

schema = config = None


def setUpModule(*args):
    register_base_type("BabarTestType", ("jungle_speed",))
    helper = get_db_helper("sqlite")
    helper.TYPE_MAPPING["BabarTestType"] = "TEXT"
    helper.TYPE_CONVERTERS["BabarTestType"] = lambda x: f'"{x}"'

    global schema, config
    loader = CubicWebSchemaLoader()
    config = ApptestConfiguration("data-schemaserial", __file__)
    config.bootstrap_cubes()
    schema = loader.load(config)


def tearDownModule(*args):
    global schema, config
    schema = config = None

    unregister_base_type("BabarTestType")
    helper = get_db_helper("sqlite")
    helper.TYPE_MAPPING.pop("BabarTestType", None)
    helper.TYPE_CONVERTERS.pop("BabarTestType", None)


cstrtypemap = {
    "RQLConstraint": "RQLConstraint_eid",
    "SizeConstraint": "SizeConstraint_eid",
    "StaticVocabularyConstraint": "StaticVocabularyConstraint_eid",
    "FormatConstraint": "FormatConstraint_eid",
}


class Schema2RQLTC(TestCase):
    def test_eschema2rql1(self):
        self.assertListEqual(
            [
                (
                    "INSERT CWEType X: X description %(description)s,X final %(final)s,X name %(name)s",
                    {
                        "description": (
                            "define a final relation: "
                            "link a final relation type from a non final entity "
                            "to a final entity type. used to build the instance schema"
                        ),
                        "name": "CWAttribute",
                        "final": False,
                    },
                )
            ],
            list(eschema2rql(schema.entity_schema_for("CWAttribute"))),
        )

    def test_eschema2rql2(self):
        self.assertListEqual(
            [
                (
                    "INSERT CWEType X: X description %(description)s,X final %(final)s,X name %(name)s",
                    {"description": "", "final": True, "name": "String"},
                )
            ],
            list(eschema2rql(schema.entity_schema_for("String"))),
        )

    def test_eschema2rql_specialization(self):
        # x: None since eschema.eid are None
        self.assertListEqual(
            [
                (
                    "SET X specializes ET WHERE X eid %(x)s, ET eid %(et)s",
                    {"et": None, "x": None},
                ),
                (
                    "SET X specializes ET WHERE X eid %(x)s, ET eid %(et)s",
                    {"et": None, "x": None},
                ),
            ],
            sorted(specialize2rql(schema)),
        )

    def test_esche2rql_custom_type(self):
        expected = [
            (
                "INSERT CWEType X: X description %(description)s,X final %(final)s,"
                "X name %(name)s",
                {"description": "", "name": "BabarTestType", "final": True},
            )
        ]
        got = list(eschema2rql(schema.entity_schema_for("BabarTestType")))
        self.assertListEqual(expected, got)

    def test_rschema2rql1(self):
        self.assertListEqual(
            [
                (
                    "INSERT CWRType X: X description %(description)s,X final %(final)s,"
                    "X fulltext_container %(fulltext_container)s,X inlined %(inlined)s,"
                    "X name %(name)s,X symmetric %(symmetric)s",
                    {
                        "description": (
                            "link a relation definition to its relation type"
                        ),
                        "symmetric": False,
                        "name": "relation_type",
                        "final": False,
                        "fulltext_container": None,
                        "inlined": True,
                    },
                ),
                (
                    "INSERT CWRelation X: X cardinality %(cardinality)s,X composite %(composite)s,"
                    "X description %(description)s,X ordernum %(ordernum)s,X relation_type ER,"
                    "X from_entity SE,X to_entity OE WHERE SE eid %(se)s,ER eid %(rt)s,OE eid %(oe)s",
                    {
                        "se": None,
                        "rt": None,
                        "oe": None,
                        "description": "",
                        "composite": "object",
                        "cardinality": "1*",
                        "ordernum": 1,
                    },
                ),
                (
                    "INSERT CWConstraint X: X value %(value)s, X cstrtype CT, EDEF constrained_by X "
                    "WHERE CT eid %(ct)s, EDEF eid %(x)s",
                    {
                        "x": None,
                        "ct": "RQLConstraint_eid",
                        "value": '{"expression": "O final TRUE", "mainvars": ["O"], "msg": null}',
                    },
                ),
                (
                    "INSERT CWRelation X: X cardinality %(cardinality)s,X composite %(composite)s,"
                    "X description %(description)s,X ordernum %(ordernum)s,X relation_type ER,"
                    "X from_entity SE,X to_entity OE WHERE SE eid %(se)s,ER eid %(rt)s,OE eid %(oe)s",
                    {
                        "se": None,
                        "rt": None,
                        "oe": None,
                        "description": "",
                        "composite": "object",
                        "ordernum": 1,
                        "cardinality": "1*",
                    },
                ),
                (
                    "INSERT CWConstraint X: X value %(value)s, X cstrtype CT, EDEF constrained_by X "
                    "WHERE CT eid %(ct)s, EDEF eid %(x)s",
                    {
                        "x": None,
                        "ct": "RQLConstraint_eid",
                        "value": '{"expression": "O final FALSE", "mainvars": ["O"], "msg": null}',
                    },
                ),
            ],
            list(rschema2rql(schema.relation_schema_for("relation_type"), cstrtypemap)),
        )

    def test_rschema2rql2(self):
        self.assertListEqual(
            [
                (
                    "INSERT CWRType X: X description %(description)s,X final %(final)s,"
                    "X fulltext_container %(fulltext_container)s,X inlined %(inlined)s,"
                    "X name %(name)s,X symmetric %(symmetric)s",
                    {
                        "description": "",
                        "symmetric": False,
                        "name": "add_permission",
                        "final": False,
                        "fulltext_container": None,
                        "inlined": False,
                    },
                ),
                (
                    "INSERT CWRelation X: X cardinality %(cardinality)s,X composite %(composite)s,"
                    "X description %(description)s,X ordernum %(ordernum)s,X relation_type ER,"
                    "X from_entity SE,X to_entity OE WHERE SE eid %(se)s,ER eid %(rt)s,OE eid %(oe)s",
                    {
                        "se": None,
                        "rt": None,
                        "oe": None,
                        "description": (
                            "groups allowed to add entities/relations of this type"
                        ),
                        "composite": None,
                        "ordernum": 9999,
                        "cardinality": "**",
                    },
                ),
                (
                    "INSERT CWRelation X: X cardinality %(cardinality)s,X composite %(composite)s,"
                    "X description %(description)s,X ordernum %(ordernum)s,X relation_type ER,"
                    "X from_entity SE,X to_entity OE WHERE SE eid %(se)s,ER eid %(rt)s,OE eid %(oe)s",
                    {
                        "se": None,
                        "rt": None,
                        "oe": None,
                        "description": "rql expression allowing to add entities/relations of this type",
                        "composite": "subject",
                        "ordernum": 9999,
                        "cardinality": "*?",
                    },
                ),
                (
                    "INSERT CWRelation X: X cardinality %(cardinality)s,X composite %(composite)s,"
                    "X description %(description)s,X ordernum %(ordernum)s,X relation_type ER,"
                    "X from_entity SE,X to_entity OE WHERE SE eid %(se)s,ER eid %(rt)s,OE eid %(oe)s",
                    {
                        "se": None,
                        "rt": None,
                        "oe": None,
                        "description": (
                            "groups allowed to add entities/relations of this type"
                        ),
                        "composite": None,
                        "ordernum": 9999,
                        "cardinality": "**",
                    },
                ),
                (
                    "INSERT CWRelation X: X cardinality %(cardinality)s,X composite %(composite)s,"
                    "X description %(description)s,X ordernum %(ordernum)s,X relation_type ER,"
                    "X from_entity SE,X to_entity OE WHERE SE eid %(se)s,ER eid %(rt)s,OE eid %(oe)s",
                    {
                        "se": None,
                        "rt": None,
                        "oe": None,
                        "description": "rql expression allowing to add entities/relations of this type",
                        "composite": "subject",
                        "ordernum": 9999,
                        "cardinality": "*?",
                    },
                ),
                (
                    "INSERT CWRelation X: X cardinality %(cardinality)s,X composite %(composite)s,"
                    "X description %(description)s,X ordernum %(ordernum)s,X relation_type ER,"
                    "X from_entity SE,X to_entity OE WHERE SE eid %(se)s,ER eid %(rt)s,OE eid %(oe)s",
                    {
                        "cardinality": "**",
                        "composite": None,
                        "description": (
                            "groups allowed to add entities/relations of this type"
                        ),
                        "oe": None,
                        "ordernum": 9999,
                        "rt": None,
                        "se": None,
                    },
                ),
                (
                    "INSERT CWRelation X: X cardinality %(cardinality)s,X composite %(composite)s,"
                    "X description %(description)s,X ordernum %(ordernum)s,X relation_type ER,"
                    "X from_entity SE,X to_entity OE WHERE SE eid %(se)s,ER eid %(rt)s,OE eid %(oe)s",
                    {
                        "cardinality": "*?",
                        "composite": "subject",
                        "description": "rql expression allowing to add entities/relations of this type",
                        "oe": None,
                        "ordernum": 9999,
                        "rt": None,
                        "se": None,
                    },
                ),
            ],
            list(
                rschema2rql(schema.relation_schema_for("add_permission"), cstrtypemap)
            ),
        )

    def test_rschema2rql3(self):
        self.assertListEqual(
            [
                (
                    "INSERT CWRType X: X description %(description)s,X final %(final)s,"
                    "X fulltext_container %(fulltext_container)s,X inlined %(inlined)s,"
                    "X name %(name)s,X symmetric %(symmetric)s",
                    {
                        "description": "",
                        "symmetric": False,
                        "name": "cardinality",
                        "final": True,
                        "fulltext_container": None,
                        "inlined": False,
                    },
                ),
                (
                    "INSERT CWAttribute X: X cardinality %(cardinality)s,X defaultval %(defaultval)s,"
                    "X description %(description)s,X formula %(formula)s,X fulltextindexed %(fulltextindexed)s,"
                    "X indexed %(indexed)s,X internationalizable %(internationalizable)s,"
                    "X ordernum %(ordernum)s,X relation_type ER,X from_entity SE,"
                    "X to_entity OE WHERE SE eid %(se)s,ER eid %(rt)s,OE eid %(oe)s",
                    {
                        "se": None,
                        "rt": None,
                        "oe": None,
                        "description": "subject/object cardinality",
                        "internationalizable": True,
                        "fulltextindexed": False,
                        "ordernum": 5,
                        "defaultval": None,
                        "indexed": False,
                        "formula": None,
                        "cardinality": "?1",
                    },
                ),
                (
                    "INSERT CWConstraint X: X value %(value)s, X cstrtype CT, EDEF constrained_by X "
                    "WHERE CT eid %(ct)s, EDEF eid %(x)s",
                    {
                        "x": None,
                        "ct": "SizeConstraint_eid",
                        "value": '{"max": 2, "min": null, "msg": null}',
                    },
                ),
                (
                    "INSERT CWConstraint X: X value %(value)s, X cstrtype CT, EDEF constrained_by X "
                    "WHERE CT eid %(ct)s, EDEF eid %(x)s",
                    {
                        "x": None,
                        "ct": "StaticVocabularyConstraint_eid",
                        "value": '{"msg": null, "values": ["?1", "11"]}',
                    },
                ),
                (
                    "INSERT CWAttribute X: X cardinality %(cardinality)s,X defaultval %(defaultval)s,"
                    "X description %(description)s,X formula %(formula)s,X fulltextindexed %(fulltextindexed)s,"
                    "X indexed %(indexed)s,X internationalizable %(internationalizable)s,"
                    "X ordernum %(ordernum)s,X relation_type ER,X from_entity SE,X to_entity OE "
                    "WHERE SE eid %(se)s,ER eid %(rt)s,OE eid %(oe)s",
                    {
                        "se": None,
                        "rt": None,
                        "oe": None,
                        "description": "subject/object cardinality",
                        "internationalizable": True,
                        "fulltextindexed": False,
                        "ordernum": 5,
                        "defaultval": None,
                        "indexed": False,
                        "formula": None,
                        "cardinality": "?1",
                    },
                ),
                (
                    "INSERT CWConstraint X: X value %(value)s, X cstrtype CT, EDEF constrained_by X "
                    "WHERE CT eid %(ct)s, EDEF eid %(x)s",
                    {
                        "x": None,
                        "ct": "SizeConstraint_eid",
                        "value": '{"max": 2, "min": null, "msg": null}',
                    },
                ),
                (
                    "INSERT CWConstraint X: X value %(value)s, X cstrtype CT, EDEF constrained_by X "
                    "WHERE CT eid %(ct)s, EDEF eid %(x)s",
                    {
                        "x": None,
                        "ct": "StaticVocabularyConstraint_eid",
                        "value": (
                            '{"msg": null, "values": ["?*", "1*", "+*", "**", "?+", "1+", "++", "*+", "?1", '
                            '"11", "+1", "*1", "??", "1?", "+?", "*?"]}'
                        ),
                    },
                ),
            ],
            list(rschema2rql(schema.relation_schema_for("cardinality"), cstrtypemap)),
        )

    def test_rschema2rql_custom_type(self):
        expected = [
            (
                "INSERT CWRType X: X description %(description)s,X final %(final)s,"
                "X fulltext_container %(fulltext_container)s,X inlined %(inlined)s,"
                "X name %(name)s,X symmetric %(symmetric)s",
                {
                    "description": "",
                    "final": True,
                    "fulltext_container": None,
                    "inlined": False,
                    "name": "custom_field_of_jungle",
                    "symmetric": False,
                },
            ),
            (
                "INSERT CWAttribute X: X cardinality %(cardinality)s,"
                "X defaultval %(defaultval)s,X description %(description)s,"
                "X extra_props %(extra_props)s,X formula %(formula)s,X indexed %(indexed)s,"
                "X ordernum %(ordernum)s,X relation_type ER,X from_entity SE,"
                "X to_entity OE WHERE SE eid %(se)s,ER eid %(rt)s,OE eid %(oe)s",
                {
                    "cardinality": "?1",
                    "defaultval": None,
                    "description": "",
                    "extra_props": b'{"jungle_speed": 42}',
                    "formula": None,
                    "indexed": False,
                    "oe": None,
                    "ordernum": 4,
                    "rt": None,
                    "se": None,
                },
            ),
        ]

        got = list(
            rschema2rql(
                schema.relation_schema_for("custom_field_of_jungle"), cstrtypemap
            )
        )
        self.assertEqual(2, len(got))
        # this is a custom type attribute with an extra parameter
        self.assertIn("extra_props", got[1][1])
        # this extr
        extra_props = got[1][1]["extra_props"]
        self.assertIsInstance(extra_props, Binary)
        got[1][1]["extra_props"] = got[1][1]["extra_props"].getvalue()
        self.assertListEqual(expected, got)

    def test_rdef2rql(self):
        self.assertListEqual(
            [
                (
                    "INSERT CWAttribute X: X cardinality %(cardinality)s,X defaultval %(defaultval)s,"
                    "X description %(description)s,X formula %(formula)s,X fulltextindexed %(fulltextindexed)s,"
                    "X indexed %(indexed)s,X internationalizable %(internationalizable)s,"
                    "X ordernum %(ordernum)s,X relation_type ER,X from_entity SE,"
                    "X to_entity OE WHERE SE eid %(se)s,ER eid %(rt)s,OE eid %(oe)s",
                    {
                        "se": None,
                        "rt": None,
                        "oe": None,
                        "description": "",
                        "internationalizable": True,
                        "fulltextindexed": False,
                        "ordernum": 3,
                        "defaultval": Binary.zpickle("text/plain"),
                        "indexed": False,
                        "formula": None,
                        "cardinality": "?1",
                    },
                ),
                (
                    "INSERT CWConstraint X: X value %(value)s, X cstrtype CT, EDEF constrained_by X "
                    "WHERE CT eid %(ct)s, EDEF eid %(x)s",
                    {
                        "x": None,
                        "value": (
                            '{"msg": null, "values": ["text/rest", "text/markdown", '
                            '"text/html", "text/plain"]}'
                        ),
                        "ct": "FormatConstraint_eid",
                    },
                ),
                (
                    "INSERT CWConstraint X: X value %(value)s, X cstrtype CT, EDEF constrained_by X "
                    "WHERE CT eid %(ct)s, EDEF eid %(x)s",
                    {
                        "x": None,
                        "value": '{"max": 50, "min": null, "msg": null}',
                        "ct": "SizeConstraint_eid",
                    },
                ),
            ],
            list(
                rdef2rql(
                    schema["description_format"].relation_definitions[
                        ("CWRType", "String")
                    ],
                    cstrtypemap,
                )
            ),
        )

    def test_updateeschema2rql1(self):
        self.assertListEqual(
            [
                (
                    "SET X description %(description)s,X final %(final)s,"
                    "X name %(name)s WHERE X eid %(x)s",
                    {
                        "description": (
                            "define a final relation: link a final relation type from"
                            " a non final entity to a final entity type. used to build the instance schema"
                        ),
                        "x": 1,
                        "final": False,
                        "name": "CWAttribute",
                    },
                )
            ],
            list(updateeschema2rql(schema.entity_schema_for("CWAttribute"), 1)),
        )

    def test_updateeschema2rql2(self):
        self.assertListEqual(
            [
                (
                    "SET X description %(description)s,X final %(final)s,"
                    "X name %(name)s WHERE X eid %(x)s",
                    {"description": "", "x": 1, "final": True, "name": "String"},
                )
            ],
            list(updateeschema2rql(schema.entity_schema_for("String"), 1)),
        )

    def test_updaterschema2rql1(self):
        self.assertListEqual(
            [
                (
                    "SET X description %(description)s,X final %(final)s,"
                    "X fulltext_container %(fulltext_container)s,X inlined %(inlined)s,"
                    "X name %(name)s,X symmetric %(symmetric)s WHERE X eid %(x)s",
                    {
                        "x": 1,
                        "symmetric": False,
                        "description": (
                            "link a relation definition to its relation type"
                        ),
                        "final": False,
                        "fulltext_container": None,
                        "inlined": True,
                        "name": "relation_type",
                    },
                )
            ],
            list(updaterschema2rql(schema.relation_schema_for("relation_type"), 1)),
        )

    def test_updaterschema2rql2(self):
        expected = [
            (
                "SET X description %(description)s,X final %(final)s,"
                "X fulltext_container %(fulltext_container)s,X inlined %(inlined)s,"
                "X name %(name)s,X symmetric %(symmetric)s WHERE X eid %(x)s",
                {
                    "x": 1,
                    "symmetric": False,
                    "description": "",
                    "final": False,
                    "fulltext_container": None,
                    "inlined": False,
                    "name": "add_permission",
                },
            )
        ]
        for i, (rql, args) in enumerate(
            updaterschema2rql(schema.relation_schema_for("add_permission"), 1)
        ):
            with self.subTest(i=i):
                self.assertEqual((rql, args), expected[i])


class Perms2RQLTC(TestCase):
    GROUP_MAPPING = {
        "managers": 0,
        "users": 1,
        "guests": 2,
        "owners": 3,
    }

    def test_eperms2rql1(self):
        self.assertListEqual(
            [
                ("SET X read_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 0}),
                ("SET X read_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 1}),
                ("SET X read_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 2}),
                ("SET X add_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 0}),
                ("SET X update_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 0}),
                ("SET X delete_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 0}),
            ],
            [
                (rql, kwargs)
                for rql, kwargs in erperms2rql(
                    schema.entity_schema_for("CWEType"), self.GROUP_MAPPING
                )
            ],
        )

    def test_rperms2rql2(self):
        self.assertListEqual(
            [
                ("SET X read_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 0}),
                ("SET X read_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 1}),
                ("SET X read_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 2}),
                ("SET X add_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 0}),
                ("SET X delete_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 0}),
            ],
            [
                (rql, kwargs)
                for rql, kwargs in erperms2rql(
                    schema.relation_schema_for("read_permission").relation_definition(
                        "CWEType", "CWGroup"
                    ),
                    self.GROUP_MAPPING,
                )
            ],
        )

    def test_rperms2rql3(self):
        self.assertListEqual(
            [
                ("SET X read_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 0}),
                ("SET X read_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 1}),
                ("SET X read_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 2}),
                ("SET X add_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 0}),
                ("SET X update_permission Y WHERE Y eid %(g)s, X eid %(x)s", {"g": 0}),
            ],
            [
                (rql, kwargs)
                for rql, kwargs in erperms2rql(
                    schema.relation_schema_for("name").relation_definition(
                        "CWEType", "String"
                    ),
                    self.GROUP_MAPPING,
                )
            ],
        )


class ComputedAttributeAndRelationTC(CubicWebTC):
    appid = "data-cwep002"

    def test(self):
        # force to read schema from the database
        self.repo.set_schema(self.repo.deserialize_schema(), resetvreg=False)
        schema = self.repo.schema
        self.assertEqual(
            [("Company", "Person")], sorted(schema["has_employee"].relation_definitions)
        )
        self.assertEqual(
            schema["has_employee"]
            .relation_definition("Company", "Person")
            .permissions["read"],
            ("managers",),
        )
        self.assertEqual("O works_for S", schema["has_employee"].rule)
        self.assertEqual(
            [("Company", "Int")], sorted(schema["total_salary"].relation_definitions)
        )
        self.assertEqual(
            "Any SUM(SA) GROUPBY X WHERE P works_for X, P salary SA",
            schema["total_salary"].relation_definitions["Company", "Int"].formula,
        )


if __name__ == "__main__":
    from unittest import main

    main()
