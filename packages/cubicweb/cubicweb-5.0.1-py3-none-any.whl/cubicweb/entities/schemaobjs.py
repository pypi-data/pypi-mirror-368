# copyright 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""schema definition related entities"""


from logilab.common.decorators import cached
from yams.schema import role_name

from yams import ValidationError
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.schema import ERQLExpression, RRQLExpression


class CWEType(AnyEntity):
    __regid__ = "CWEType"
    fetch_attrs, cw_fetch_order = fetch_config(["name"])

    def dc_title(self):
        return f"{self.name} ({self._cw._(self.name)})"

    def dc_long_title(self):
        stereotypes = []
        _ = self._cw._
        if self.final:
            stereotypes.append(_("final"))
        if stereotypes:
            return f"{self.dc_title()} <<{', '.join(stereotypes)}>>"
        return self.dc_title()


class CWRType(AnyEntity):
    __regid__ = "CWRType"
    fetch_attrs, cw_fetch_order = fetch_config(["name"])

    def dc_title(self):
        return f"{self.name} ({self._cw._(self.name)})"

    def dc_long_title(self):
        stereotypes = []
        _ = self._cw._
        if self.symmetric:
            stereotypes.append(_("symmetric"))
        if self.inlined:
            stereotypes.append(_("inlined"))
        if self.final:
            stereotypes.append(_("final"))
        if stereotypes:
            return f"{self.dc_title()} <<{', '.join(stereotypes)}>>"
        return self.dc_title()

    def check_inlined_allowed(self):
        """check inlining is possible, raise ValidationError if not possible"""
        # don't use the persistent schema, we may miss cardinality changes
        # in the same transaction
        for rdef in self.reverse_relation_type:
            card = rdef.cardinality[0]
            if card not in "?1":
                qname = role_name("inlined", "subject")
                rtype = self.name
                stype = rdef.stype
                otype = rdef.otype
                msg = self._cw._(
                    "can't set inlined=True, "
                    "%(stype)s %(rtype)s %(otype)s "
                    "has cardinality=%(card)s"
                )
                raise ValidationError(self.eid, {qname: msg % locals()})


class CWRelation(AnyEntity):
    __regid__ = "CWRelation"
    fetch_attrs = fetch_config(["cardinality"])[0]

    def dc_title(self):
        return "{} {} {}".format(
            self.from_entity[0].name,
            self.relation_type[0].name,
            self.to_entity[0].name,
        )

    def dc_long_title(self):
        card = self.cardinality
        scard, ocard = "", ""
        if card[0] != "1":
            scard = f"[{card[0]}]"
        if card[1] != "1":
            ocard = f"[{card[1]}]"
        return "{} {}{}{} {}".format(
            self.from_entity[0].name,
            scard,
            self.relation_type[0].name,
            ocard,
            self.to_entity[0].name,
        )

    @property
    def rtype(self):
        return self.relation_type[0]

    @property
    def stype(self):
        return self.from_entity[0]

    @property
    def otype(self):
        return self.to_entity[0]

    def yams_schema(self):
        rschema = self._cw.vreg.schema.relation_schema_for(self.rtype.name)
        return rschema.relation_definitions[(self.stype.name, self.otype.name)]


class CWAttribute(CWRelation):
    __regid__ = "CWAttribute"

    def dc_long_title(self):
        card = self.cardinality
        scard = ""
        if card[0] == "1":
            scard = "+"
        return "{} {}{} {}".format(
            self.from_entity[0].name,
            scard,
            self.relation_type[0].name,
            self.to_entity[0].name,
        )


class CWConstraint(AnyEntity):
    __regid__ = "CWConstraint"
    fetch_attrs, cw_fetch_order = fetch_config(["value"])

    def __repr__(self):
        return "<Entity {} {} of type {} {} at {}>".format(
            self.e_schema,
            self.eid,
            self.type,
            list(self.cw_attr_cache),
            id(self),
        )

    def dc_title(self):
        return f"{self.cstrtype[0].name}({self.value or ''})"

    @property
    def type(self):
        return self.cstrtype[0].name


class RQLExpression(AnyEntity):
    __regid__ = "RQLExpression"
    fetch_attrs, cw_fetch_order = fetch_config(["exprtype", "mainvars", "expression"])

    def dc_title(self):
        return self.expression or ""

    def dc_long_title(self):
        return f"{self.exprtype}({self.expression or ''})"

    @property
    def expression_of(self):
        for rel in (
            "read_permission",
            "add_permission",
            "delete_permission",
            "update_permission",
            "condition",
        ):
            values = getattr(self, f"reverse_{rel}")
            if values:
                return values[0]

    @cached
    def _rqlexpr(self):
        if self.exprtype == "ERQLExpression":
            return ERQLExpression(self.expression, self.mainvars, self.eid)
        # if self.exprtype == 'RRQLExpression':
        return RRQLExpression(self.expression, self.mainvars, self.eid)

    def check_expression(self, *args, **kwargs):
        return self._rqlexpr().check(*args, **kwargs)
