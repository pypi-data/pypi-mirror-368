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
"""Some utilities for CubicWeb server/clients."""

import base64
import datetime
import decimal
import json
import random
import re
from functools import wraps
from inspect import getfullargspec as getargspec
from itertools import repeat
from logging import getLogger
from uuid import uuid4

from logilab.common.date import ustrftime
from logilab.mtconverter import xml_escape

from cubicweb import Binary

_MARKER = object()

# initialize random seed from current time
random.seed()


def format_and_escape_string(value, *args, escape=True):
    if args:
        try:
            if escape:
                if isinstance(args[0], dict):
                    value = value % {
                        key: xml_escape(str(value)) if value else value
                        for key, value in args[0].items()
                    }
                else:
                    value = value % tuple(xml_escape(str(x)) if x else x for x in args)
            else:
                if isinstance(args[0], dict):
                    value = value % args[0]
                else:
                    value = value % args
        except Exception:
            # for debugging, the exception is often hidden otherwise
            import traceback

            traceback.print_exc()
            print(f'text: "{value}"')
            print(f'arguments: "{args}"')
            raise

    return value


def admincnx(appid):
    from cubicweb import repoapi
    from cubicweb.cwconfig import CubicWebConfiguration
    from cubicweb.server.repository import Repository

    config = CubicWebConfiguration.config_for(appid)

    login = config.default_admin_config["login"]
    password = config.default_admin_config["password"]

    repo = Repository(config)
    repo.bootstrap()
    return repoapi.connect(repo, login, password=password)


def make_uid(key=None):
    """Return a unique identifier string.

    if specified, `key` is used to prefix the generated uid so it can be used
    for instance as a DOM id or as sql table name.

    See uuid.uuid4 documentation for the shape of the generated identifier, but
    this is basically a 32 bits hexadecimal string.
    """
    if key is None:
        return uuid4().hex
    return str(key) + uuid4().hex


def support_args(callable, *argnames):
    """return true if the callable support given argument names"""
    if isinstance(callable, type):
        callable = callable.__init__
    argspec = getargspec(callable)
    if argspec[2]:
        return True
    for argname in argnames:
        if argname not in argspec[0]:
            return False
    return True


class wrap_on_write:
    """Sometimes it is convenient to NOT write some container element
    if it happens that there is nothing to be written within,
    but this cannot be known beforehand.
    Hence one can do this:

    .. sourcecode:: python

       with wrap_on_write(w, '<div class="foo">', '</div>') as wow:
           component.render_stuff(wow)
    """

    def __init__(self, w, tag, closetag=None):
        self.written = False
        self.tag = tag
        self.closetag = closetag
        self.w = w

    def __enter__(self):
        return self

    def __call__(self, data, *args, escape=True):
        if self.written is False:
            self.w(self.tag)
            self.written = True
        self.w(data, *args, escape=escape)

    def __exit__(self, exctype, value, traceback):
        if self.written is True:
            if self.closetag:
                self.w(self.closetag)
            else:
                self.w(self.tag.replace("<", "</", 1))


# use networkX instead ?
# http://networkx.lanl.gov/reference/algorithms.traversal.html#module-networkx.algorithms.traversal.astar
def transitive_closure_of(entity, rtype, _seen=None):
    """return transitive closure *for the subgraph starting from the given
    entity* (eg 'parent' entities are not included in the results)
    """
    if _seen is None:
        _seen = set()
    _seen.add(entity.eid)
    yield entity
    for child in getattr(entity, rtype):
        if child.eid in _seen:
            continue
        for subchild in transitive_closure_of(child, rtype, _seen):
            yield subchild


class RepeatList:
    """fake a list with the same element in each row"""

    __slots__ = ("_size", "_item")

    def __init__(self, size, item):
        self._size = size
        self._item = item

    def __repr__(self):
        return "<cubicweb.utils.RepeatList at %s item=%s size=%s>" % (
            id(self),
            self._item,
            self._size,
        )

    def __len__(self):
        return self._size

    def __iter__(self):
        return repeat(self._item, self._size)

    def __getitem__(self, index):
        if isinstance(index, slice):
            # XXX could be more efficient, but do we bother?
            return ([self._item] * self._size)[index]
        return self._item

    def __delitem__(self, idc):
        assert self._size > 0
        self._size -= 1

    def __add__(self, other):
        if isinstance(other, RepeatList):
            if other._item == self._item:
                return RepeatList(self._size + other._size, self._item)
            return ([self._item] * self._size) + other[:]
        return ([self._item] * self._size) + other

    def __radd__(self, other):
        if isinstance(other, RepeatList):
            if other._item == self._item:
                return RepeatList(self._size + other._size, self._item)
            return other[:] + ([self._item] * self._size)
        return other[:] + ([self._item] * self._size)

    def __eq__(self, other):
        if isinstance(other, RepeatList):
            return other._size == self._size and other._item == self._item
        return self[:] == other

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        raise NotImplementedError

    def pop(self, i):
        self._size -= 1


def handle_writing_constraints(method):
    @wraps(method)
    def wrapper(self, value, *args, escape=True):
        if self.tracewrites:
            from traceback import format_stack

            stack = format_stack(None)[:-1]
            escaped_stack = xml_escape(json_dumps("\n".join(stack)))
            escaped_html = xml_escape(value).replace("\n", "<br/>\n")
            tpl = '<span onclick="alert(%s)">%s</span>'
            value = tpl % (escaped_stack, escaped_html)
        return method(self, value, *args, escape=escape)

    return wrapper


class UStringIO(list):
    """a file wrapper which automatically encode unicode string to an encoding
    specifed in the constructor
    """

    def __init__(self, tracewrites=False, *args, **kwargs):
        self.tracewrites = tracewrites
        super(UStringIO, self).__init__(*args, **kwargs)

    def __bool__(self):
        return True

    __nonzero__ = __bool__

    def write(self, value, *args, escape=True):
        if self.tracewrites:
            from traceback import format_stack

            stack = format_stack(None)[:-1]
            escaped_stack = xml_escape(json_dumps("\n".join(stack)))
            escaped_html = xml_escape(value).replace("\n", "<br/>\n")
            tpl = '<span onclick="alert(%s)">%s</span>'
            value = tpl % (escaped_stack, escaped_html)

        value = format_and_escape_string(value, *args, escape=escape)

        self.append(value)

    @handle_writing_constraints
    def write_front(self, value, *args, escape=True):
        value = format_and_escape_string(value, *args, escape=escape)

        self.insert(0, value)

    def getvalue(self):
        return "".join(self)

    def __repr__(self):
        return "<%s at %#x>" % (self.__class__.__name__, id(self))


class CubicWebJsonEncoder(json.JSONEncoder):
    """define a json encoder to be able to encode yams std types"""

    def default(self, obj):
        if hasattr(obj, "__json_encode__"):
            return xml_escape_from_dict(obj.__json_encode__())
        if isinstance(obj, datetime.datetime):
            return ustrftime(obj, "%Y/%m/%d %H:%M:%S")
        elif isinstance(obj, datetime.date):
            return ustrftime(obj, "%Y/%m/%d")
        elif isinstance(obj, datetime.time):
            return obj.strftime("%H:%M:%S")
        elif isinstance(obj, datetime.timedelta):
            return (obj.days * 24 * 60 * 60) + obj.seconds
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, Binary):
            return base64.b64encode(obj.getvalue()).decode("ascii")
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            # we never ever want to fail because of an unknown type,
            # just return None in those cases.
            return None


def json_dumps(value, **kwargs):
    return json.dumps(value, cls=CubicWebJsonEncoder, **kwargs)


def xml_escape_from_dict(data):
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = xml_escape(value)
    return data


class JSString(str):
    """use this string sub class in values given to :func:`js_dumps` to
    insert raw javascript chain in some JSON string
    """


def _dict2js(d, predictable=False):
    if predictable:
        it = sorted(d.items())
    else:
        it = d.items()
    res = [
        js_dumps(key, predictable) + ": " + js_dumps(val, predictable)
        for key, val in it
    ]
    return "{%s}" % ", ".join(res)


def _list2js(a_list, predictable=False):
    return f"[{', '.join([js_dumps(val, predictable) for val in a_list])}]"


def js_dumps(something, predictable=False):
    """similar as :func:`json_dumps`, except values which are instances of
    :class:`JSString` are expected to be valid javascript and will be output
    as is

    >>> js_dumps({'hop': JSString('$.hop'), 'bar': None}, predictable=True)
    '{bar: null, hop: $.hop}'
    >>> js_dumps({'hop': '$.hop'})
    '{hop: "$.hop"}'
    >>> js_dumps({'hip': {'hop': JSString('momo')}})
    '{hip: {hop: momo}}'
    """
    if isinstance(something, dict):
        return _dict2js(something, predictable)
    if isinstance(something, list):
        return _list2js(something, predictable)
    if isinstance(something, JSString):
        return something
    return json_dumps(something, sort_keys=predictable)


PERCENT_IN_URLQUOTE_RE = re.compile(r"%(?=[0-9a-fA-F]{2})")


def js_href(javascript_code):
    """Generate a "javascript: ..." string for an href attribute.

    Some % which may be interpreted in a href context will be escaped.

    In an href attribute, url-quotes-looking fragments are interpreted before
    being given to the javascript engine. Valid url quotes are in the form
    ``%xx`` with xx being a byte in hexadecimal form. This means that ``%toto``
    will be unaltered but ``%babar`` will be mangled because ``ba`` is the
    hexadecimal representation of 186.

    >>> js_href('alert("babar");')
    'javascript: alert("babar");'
    >>> js_href('alert("%babar");')
    'javascript: alert("%25babar");'
    >>> js_href('alert("%toto %babar");')
    'javascript: alert("%toto %25babar");'
    >>> js_href('alert("%1337%");')
    'javascript: alert("%251337%");'
    """
    return "javascript: " + PERCENT_IN_URLQUOTE_RE.sub(r"%25", javascript_code)


def get_pdb():
    "return ipdb if its installed, otherwise pdb"
    try:
        import ipdb
    except ImportError:
        import pdb

        return pdb
    else:
        return ipdb


logger = getLogger("cubicweb.utils")
