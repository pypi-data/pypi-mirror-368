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
"""Base classes and utilities for cubicweb tests"""

import sys
from contextlib import contextmanager
from inspect import isgeneratorfunction
from itertools import chain
from os.path import dirname, join, abspath
from unittest import TestCase

import yams.schema
from logilab.common.debugger import Debugger
from logilab.common.decorators import cached, classproperty, clear_cache, iclassmethod
from logilab.common.testlib import Tags
from logilab.common.textutils import unormalize

from cubicweb import (
    AuthenticationError,
    BadConnectionId,
)
from cubicweb import devtools, repoapi, server
from cubicweb.devtools import (
    SYSTEM_ENTITIES,
)
from cubicweb.devtools import DEFAULT_EMPTY_DB_ID
from cubicweb.devtools.apptest_config import (
    ApptestConfiguration,
    MAILBOX,
)
from cubicweb.server.hook import SendMailOp
from cubicweb.server.session import Connection
from cubicweb.utils import json, make_uid


# provide a data directory for the test class ##################################


class BaseTestCase(TestCase):
    @classproperty
    @cached
    def datadir(cls):  # pylint: disable=E0213
        """helper attribute holding the standard test's data directory"""
        mod = sys.modules[cls.__module__]
        return join(dirname(abspath(mod.__file__)), "data")

    # cache it (use a class method to cache on class since TestCase is
    # instantiated for each test run)

    @classmethod
    def datapath(cls, *fname):
        """joins the object's datadir and `fname`"""
        return join(cls.datadir, *fname)


# low-level utilities ##########################################################


class CubicWebDebugger(Debugger):
    """special debugger class providing a 'view' function which saves some
    html into a temporary file and open a web browser to examinate it.
    """

    def do_view(self, arg):
        import webbrowser

        data = self._getval(arg)
        with open("/tmp/toto.html", "w") as toto:
            toto.write(data)
        webbrowser.open("file:///tmp/toto.html")


def line_context_filter(line_no, center, before=3, after=None):
    """return true if line are in context

    if after is None: after = before
    """
    if after is None:
        after = before
    return center - before <= line_no <= center + after


def unprotected_entities(schema, strict=False):
    """returned a set of each non final entity type, excluding "system" entities
    (eg CWGroup, CWUser...)
    """
    if strict:
        protected_entities = yams.schema.BASE_TYPES
    else:
        protected_entities = yams.schema.BASE_TYPES.union(SYSTEM_ENTITIES)
    return set(schema.entities()) - protected_entities


class JsonValidator:
    def parse_string(self, data):
        return json.loads(data.decode("ascii"))


@contextmanager
def real_error_handling(app):
    """By default, CubicWebTC `app` attribute (ie the publisher) is monkey
    patched so that unexpected error are raised rather than going through the
    `error_handler` method.

    By using this context manager you disable this monkey-patching temporarily.
    Hence when publishihng a request no error will be raised, you'll get
    req.status_out set to an HTTP error status code and the generated page will
    usually hold a traceback as HTML.

    >>> with real_error_handling(app):
    >>>     page = app.handle_request(req)
    """
    # remove the monkey patched error handler
    fake_error_handler = app.error_handler
    del app.error_handler
    # return the app
    yield app
    # restore
    app.error_handler = fake_error_handler


# Repoaccess utility ###############################################3###########


class Session:
    """In-memory user session"""

    def __init__(self, repo, user):
        self.user = user  # XXX deprecate and store only a login.
        self.repo = repo
        self.sessionid = make_uid(unormalize(user.login))
        self.data = {}

    def __str__(self):
        return f"<session {self.user.login} (0x{id(self):x})>"

    @property
    def anonymous_session(self):
        # XXX for now, anonymous_user only exists in webconfig (and testconfig).
        # It will only be present inside all-in-one instance.
        # there is plan to move it down to global config.
        if not hasattr(self.repo.config, "anonymous_user"):
            # not a web or test config, no anonymous user
            return False
        return self.user.login == self.repo.config.anonymous_user()[0]

    def new_cnx(self):
        """Return a new Connection object linked to the session

        The returned Connection will *not* be managed by the Session.
        """
        cnx = Connection(self.repo, self.user)
        cnx.session = self
        return cnx


class RepoAccess:
    """An helper to easily create object to access the repo as a specific user

    Each RepoAccess have it own session.

    A repo access can create three type of object:

    .. automethod:: cubicweb.testlib.RepoAccess.cnx
    .. automethod:: cubicweb.testlib.RepoAccess.web_request
    """

    def __init__(self, repo, login):
        self._repo = repo
        self._login = login
        with repo.internal_cnx() as cnx:
            self._user = cnx.find("CWUser", login=login).one()
            self._user.cw_attr_cache["login"] = login

    @contextmanager
    def cnx(self):
        """Context manager returning a server side connection for the user"""
        with repoapi.Connection(self._repo, self._user) as cnx:
            yield cnx

    # aliases for bw compat
    client_cnx = repo_cnx = cnx

    @contextmanager
    def shell(self):
        from cubicweb.server.migractions import ServerMigrationHelper

        with self.cnx() as cnx:
            mih = ServerMigrationHelper(
                None,
                repo=self._repo,
                cnx=cnx,
                interactive=False,
                # hack so it don't try to load fs schema
                schema=1,
            )
            yield mih
            cnx.commit()


# base class for cubicweb tests requiring a full cw environments ###############


class CubicWebTC(BaseTestCase):
    """abstract class for test using an apptest environment

    attributes:

    * `vreg`, the vregistry
    * `schema`, self.vreg.schema
    * `config`, cubicweb configuration
    * `cnx`, repoapi connection to the repository using an admin user
    * `session`, server side session associated to `cnx`
    * `app`, the cubicweb publisher (for web testing)
    * `repo`, the repository object
    * `admlogin`, login of the admin user
    * `admpassword`, password of the admin user
    * `shell`, create and use shell environment
    * `anonymous_allowed`: flag telling if anonymous browsing should be allowed
    """

    appid = "data"
    configcls = ApptestConfiguration
    tags = Tags("cubicweb", "cw_repo")
    test_db_id = DEFAULT_EMPTY_DB_ID

    # anonymous is logged by default in cubicweb test cases
    anonymous_allowed = True

    @classmethod
    def setUpClass(cls):
        test_module_file = sys.modules[cls.__module__].__file__
        assert "config" not in cls.__dict__, (
            "%s has a config class attribute before entering setUpClass. "
            "Let CubicWebTC.setUpClass instantiate it and modify it afterwards." % cls
        )
        cls.config = cls.configcls(cls.appid, test_module_file)
        cls.config.mode = "test"

    def __init__(self, *args, **kwargs):
        self.repo = None
        self._open_access = set()
        super(CubicWebTC, self).__init__(*args, **kwargs)

    def run(self, *args, **kwds):
        testMethod = getattr(self, self._testMethodName)
        if isgeneratorfunction(testMethod):
            raise RuntimeError(
                "%s appears to be a generative test. This is not handled "
                "anymore, use subTest API instead." % self
            )
        return super(CubicWebTC, self).run(*args, **kwds)

    # repository connection handling ###########################################

    def new_access(self, login):
        """provide a new RepoAccess object for a given user

        The access is automatically closed at the end of the test."""
        access = RepoAccess(self.repo, login)
        self._open_access.add(access)
        return access

    def _close_access(self):
        while self._open_access:
            try:
                self._open_access.pop()
            except BadConnectionId:
                continue  # already closed

    def _init_repo(self):
        """init the repository and connection to it."""
        # get or restore and working db.
        db_handler = devtools.get_test_db_handler(self.config, self.init_config)
        db_handler.build_db_cache(self.test_db_id, self.pre_setup_database)
        db_handler.restore_database(self.test_db_id)
        self.repo = db_handler.get_repo(startup=True)
        # get an admin session (without actual login)
        login = db_handler.config.default_admin_config["login"]
        self.admin_access = self.new_access(login)

    # config management ########################################################

    @classmethod  # XXX could be turned into a regular method
    def init_config(cls, config):
        """configuration initialization hooks.

        You may only want to override here the configuraton logic.

        Otherwise, consider to use a different :class:`ApptestConfiguration`
        defined in the `configcls` class attribute.

        This method will be called by the database handler once the config has
        been properly bootstrapped.
        """
        admincfg = config.default_admin_config
        cls.admlogin = admincfg["login"]
        cls.admpassword = admincfg["password"]
        # uncomment the line below if you want rql queries to be logged
        # config.global_set_option('query-log-file',
        #                          '/tmp/test_rql_log.' + `os.getpid()`)
        config.global_set_option("log-file", None)
        # set default-dest-addrs to a dumb email address to avoid mailbox or
        # mail queue pollution
        config.global_set_option("default-dest-addrs", ["whatever"])
        config.global_set_option("sender-addr", "cubicweb-send@logilab.fr")
        config.global_set_option(
            "default-dest-addrs", "cubicweb-default-dest@logilab.fr"
        )
        config.global_set_option("sender-name", "cubicweb-test")
        config.global_set_option("sender-addr", "cubicweb-test@logilab.fr")
        # default_base_url on config class isn't enough for TestServerConfiguration
        config.global_set_option("base-url", config.default_base_url())

    @property
    def vreg(self):
        return self.repo.vreg

    # global resources accessors ###############################################

    @property
    def schema(self):
        """return the application schema"""
        return self.vreg.schema

    def set_option(self, optname, value):
        self.config.global_set_option(optname, value)

    def set_debug(self, debugmode):
        server.set_debug(debugmode)

    def debugged(self, debugmode):
        return server.debugged(debugmode)

    # default test setup and teardown #########################################

    def setUp(self):
        assert hasattr(self, "config"), (
            "It seems that CubicWebTC.setUpClass has not been called. "
            "Missing super() call in %s?" % self.setUpClass
        )
        self.config.set_anonymous_allowed(self.anonymous_allowed)
        # monkey patch send mail operation so emails are sent synchronously
        self._patch_SendMailOp()
        previous_failure = self.__class__.__dict__.get("_repo_init_failed")
        if previous_failure is not None:
            self.skipTest(f"repository is not initialised: {previous_failure!r}")
        try:
            self._init_repo()
        except Exception as ex:
            self.__class__._repo_init_failed = ex
            raise
        self.addCleanup(self._close_access)
        self.setup_database()
        MAILBOX[:] = []  # reset mailbox

        self.previous_log_threshold = self.config.config.log_threshold

        # I want debug all the time because god
        self.config.global_set_option("log-threshold", "DEBUG")
        self.config.init_log(self.config["log-threshold"], force=True)

    def tearDown(self):
        self.config.global_set_option("log-threshold", self.previous_log_threshold)
        self.config.init_log(self.config["log-threshold"], force=True)

        while self._cleanups:
            cleanup, args, kwargs = self._cleanups.pop(-1)
            cleanup(*args, **kwargs)
        self.repo.turn_repo_off()

    def _patch_SendMailOp(self):
        # monkey patch send mail operation so emails are sent synchronously
        _old_mail_postcommit_event = SendMailOp.postcommit_event
        SendMailOp.postcommit_event = SendMailOp.sendmails

        def reverse_SendMailOp_monkey_patch():
            SendMailOp.postcommit_event = _old_mail_postcommit_event

        self.addCleanup(reverse_SendMailOp_monkey_patch)

    def setup_database(self):
        """add your database setup code by overriding this method"""

    @classmethod
    def pre_setup_database(cls, cnx, config):
        """add your pre database setup code by overriding this method

        Do not forget to set the cls.test_db_id value to enable caching of the
        result.
        """

    # user / session management ###############################################

    @iclassmethod  # XXX turn into a class method
    def create_user(
        self,
        req,
        login=None,
        groups=("users",),
        password=None,
        email=None,
        commit=True,
        **kwargs,
    ):
        """create and return a new user entity"""
        if password is None:
            password = login
        user = req.create_entity("CWUser", login=login, upassword=password, **kwargs)
        req.execute(
            "SET X in_group G WHERE X eid %%(x)s, G name IN(%s)"
            % ",".join(repr(str(g)) for g in groups),
            {"x": user.eid},
        )
        if email is not None:
            req.create_entity("EmailAddress", address=email, reverse_primary_email=user)
        user.cw_clear_relation_cache("in_group", "subject")
        if commit:
            getattr(req, "cnx", req).commit()
        return user

    # other utilities #########################################################

    @contextmanager
    def temporary_appobjects(self, *appobjects):
        self.vreg._loadedmods.setdefault(self.__module__, {})
        for obj in appobjects:
            self.vreg.register(obj)
            registered = getattr(obj, "__registered__", None)
            if registered:
                for registry in obj.__registries__:
                    registered(self.vreg[registry])
        try:
            yield
        finally:
            for obj in appobjects:
                self.vreg.unregister(obj)

    @contextmanager
    def temporary_permissions(self, *perm_overrides, **perm_kwoverrides):
        """Set custom schema permissions within context.

        There are two ways to call this method, which may be used together :

        * using positional argument(s):

          .. sourcecode:: python

                rdef = self.schema['CWUser'].rdef('login')
                with self.temporary_permissions((rdef, {'read': ()})):
                    ...


        * using named argument(s):

          .. sourcecode:: python

                with self.temporary_permissions(CWUser={'read': ()}):
                    ...

        Usually the former will be preferred to override permissions on a
        relation definition, while the latter is well suited for entity types.

        The allowed keys in the permission dictionary depend on the schema type
        (entity type / relation definition). Resulting permissions will be
        similar to `orig_permissions.update(partial_perms)`.
        """
        torestore = []
        for erschema, etypeperms in chain(perm_overrides, perm_kwoverrides.items()):
            if isinstance(erschema, str):
                erschema = self.schema[erschema]
            for action, actionperms in etypeperms.items():
                origperms = erschema.permissions[action]
                erschema.set_action_permissions(action, actionperms)
                torestore.append([erschema, action, origperms])
        try:
            yield
        finally:
            for erschema, action, permissions in torestore:
                if action is None:
                    erschema.permissions = permissions
                else:
                    erschema.set_action_permissions(action, permissions)

    def assertModificationDateGreater(self, entity, olddate):
        entity.cw_attr_cache.pop("modification_date", None)
        self.assertGreater(entity.modification_date, olddate)

    def assertMessageEqual(self, req, params, expected_msg):
        msg = req.session.data[params["_cwmsgid"]]
        self.assertEqual(expected_msg, msg)

    def assertPossibleTransitions(self, entity, expected):
        transitions = entity.cw_adapt_to("IWorkflowable").possible_transitions()
        self.assertListEqual(sorted(tr.name for tr in transitions), sorted(expected))

    def set_auth_mode(self, authmode, anonuser=None):
        self.set_option("auth-mode", authmode)
        self.set_option("anonymous-user", anonuser)
        if anonuser is None:
            self.config.anonymous_credential = None
        else:
            self.config.anonymous_credential = (anonuser, anonuser)

    def init_authentication(self, authmode, anonuser=None):
        self.set_auth_mode(authmode, anonuser)
        req = self.requestcls(self.vreg, url="login")
        sh = self.app.session_handler
        authm = sh.session_manager.authmanager
        authm.anoninfo = self.vreg.config.anonymous_user()
        authm.anoninfo = authm.anoninfo[0], {"password": authm.anoninfo[1]}
        # not properly cleaned between tests
        self.open_sessions = sh.session_manager._sessions = {}
        return req

    def assertAuthSuccess(self, req, nbsessions=1):
        session = self.app.get_session(req)
        cnx = session.new_cnx()
        with cnx:
            req.set_cnx(cnx)
        self.assertEqual(len(self.open_sessions), nbsessions, self.open_sessions)
        self.assertEqual(req.user.login, self.admlogin)
        self.assertEqual(session.anonymous_session, False)

    def assertAuthFailure(self, req, nbsessions=0):
        with self.assertRaises(AuthenticationError):
            self.app.get_session(req)
        # +0 since we do not track the opened session
        self.assertEqual(len(self.open_sessions), nbsessions)
        clear_cache(req, "get_authorization")

    # notifications ############################################################

    def assertSentEmail(self, subject, recipients=None, nb_msgs=None):
        """test recipients in system mailbox for given email subject

        :param subject: email subject to find in mailbox
        :param recipients: list of email recipients
        :param nb_msgs: expected number of entries
        :returns: list of matched emails
        """
        messages = [
            email for email in MAILBOX if email.message.get("Subject") == subject
        ]
        if recipients is not None:
            sent_to = set()
            for msg in messages:
                sent_to.update(msg.recipients)
            self.assertSetEqual(set(recipients), sent_to)
        if nb_msgs is not None:
            self.assertEqual(len(MAILBOX), nb_msgs)
        return messages


# registry instrumentization ###################################################


def not_selected(vreg, appobject):
    try:
        vreg._selected[appobject.__class__] -= 1
    except (KeyError, AttributeError):
        pass
