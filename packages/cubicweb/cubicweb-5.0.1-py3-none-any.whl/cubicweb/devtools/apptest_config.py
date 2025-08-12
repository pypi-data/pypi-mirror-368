# copyright 2003-2023 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
import logging
from os.path import abspath, join, dirname

from logilab.common.umessage import message_from_string

from cubicweb import ExecutionError
from cubicweb.devtools import (
    DEFAULT_PSQL_SOURCES,
    DEFAULT_SOURCES,
    BASE_URL,
)
from cubicweb.pyramid.config import AllInOneConfiguration


# email handling, to test emails sent by an application ########################

MAILBOX = []


class Email:
    """you'll get instances of Email into MAILBOX during tests that trigger
    some notification.

    * `msg` is the original message object

    * `recipients` is a list of email address which are the recipients of this
      message
    """

    def __init__(self, fromaddr, recipients, msg):
        self.fromaddr = fromaddr
        self.recipients = recipients
        self.msg = msg

    @property
    def message(self):
        return message_from_string(self.msg)

    @property
    def subject(self):
        return self.message.get("Subject")

    @property
    def content(self):
        return self.message.get_payload(decode=True)

    def __repr__(self):
        return "<Email to %s with subject %s>" % (
            ",".join(self.recipients),
            self.message.get("Subject"),
        )


# the trick to get email into MAILBOX instead of actually sent: monkey patch
# cwconfig.SMTP object
class MockSMTP:
    def __init__(self, server, port):
        pass

    def close(self):
        pass

    def sendmail(self, fromaddr, recipients, msg):
        MAILBOX.append(Email(fromaddr, recipients, msg.decode("utf-8")))


class ApptestConfiguration(AllInOneConfiguration):
    name = "all-in-one"  # so it search for all-in-one.conf, not repository.conf
    mode = "test"
    read_instance_schema = False
    init_repository = True
    skip_db_create_and_restore = False
    default_sources = DEFAULT_SOURCES
    smtp_cls = MockSMTP

    def available_languages(self, *args):
        return self.cw_languages()

    def __init__(self, appid, test_module_file, log_threshold=logging.CRITICAL + 10):
        # must be set before calling parent __init__
        apphome = abspath(join(dirname(test_module_file), appid))
        self._apphome = apphome
        super().__init__(appid)
        self.init_log(log_threshold, force=True)
        # need this, usually triggered by cubicweb-ctl
        self.load_cwctl_plugins()
        self.test_module_file = test_module_file

    # By default anonymous login are allow but some test need to deny of to
    # change the default user. Set it to None to prevent anonymous login.
    anonymous_credential = ("anon", "anon")

    def anonymous_user(self):
        if not self.anonymous_credential:
            return None, None
        return self.anonymous_credential

    def set_anonymous_allowed(self, allowed, anonuser="anon"):
        if allowed:
            self.anonymous_credential = (anonuser, anonuser)
        else:
            self.anonymous_credential = None

    @property
    def apphome(self):
        return self._apphome

    appdatahome = apphome

    def load_configuration(self, **kw):
        super().load_configuration(**kw)
        # no undo support in tests
        self.global_set_option("undo-enabled", "n")

    def bootstrap_cubes(self):
        try:
            super().bootstrap_cubes()
        except IOError:
            # no cubes
            self.init_cubes(())

    def read_sources_file(self):
        """By default, we run tests with the sqlite DB backend.  One may use its
        own configuration by just creating a 'sources' file in the test
        directory from which tests are launched or by specifying an alternative
        sources file using self.sourcefile.
        """
        if getattr(self, "sourcefile", None):
            raise Exception(
                "sourcefile isn't supported anymore, specify your database "
                "configuration using proper configuration class (e.g. "
                "PostgresApptestConfiguration)"
            )
        try:
            super().read_sources_file()
            raise Exception(
                "test configuration shouldn't provide a sources file, specify your "
                "database configuration using proper configuration class (e.g. "
                "PostgresApptestConfiguration)"
            )
        except ExecutionError:
            pass
        return self.default_sources

    # web config methods needed here for cases when we use this config as a web
    # config

    def default_base_url(self):
        return BASE_URL


class PostgresApptestConfiguration(ApptestConfiguration):
    default_sources = DEFAULT_PSQL_SOURCES
