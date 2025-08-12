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
"""
.. _ResourceMode:

Resource mode
-------------

Standard resource mode
``````````````````````

A resource *mode* is a predefined set of settings for various resources
directories, such as cubes, instances, etc. to ease development with the
framework. There are two running modes with *CubicWeb*:

* **system**: resources are searched / created in the system directories (eg
  usually requiring root access):

  - instances are stored in :file:`<INSTALL_PREFIX>/etc/cubicweb.d`
  - temporary files (such as pid file) in :file:`<INSTALL_PREFIX>/var/run/cubicweb`

  where `<INSTALL_PREFIX>` is the detected installation prefix ('/usr/local' for
  instance).

* **user**: resources are searched / created in the user home directory:

  - instances are stored in :file:`~/etc/cubicweb.d`
  - temporary files (such as pid file) in :file:`/tmp`


.. _CubicwebWithinVirtualEnv:

Within virtual environment
``````````````````````````

When installed within a virtualenv, CubicWeb will look for instances data as in
user mode by default, that is in $HOME/etc/cubicweb.d. However the
CW_INSTANCES_DIR environment variable should be preferably used.

.. _virtualenv: http://pypi.python.org/pypi/virtualenv


Custom resource location
````````````````````````

Notice that each resource path may be explicitly set using an environment
variable if the default doesn't suit your needs. Here are the default resource
directories that are affected according to mode:

* **system**: ::

        CW_INSTANCES_DIR = <INSTALL_PREFIX>/etc/cubicweb.d/
        CW_INSTANCES_DATA_DIR = <INSTALL_PREFIX>/var/lib/cubicweb/instances/
        CW_RUNTIME_DIR = <INSTALL_PREFIX>/var/run/cubicweb/

* **user**: ::

        CW_INSTANCES_DIR = ~/etc/cubicweb.d/
        CW_INSTANCES_DATA_DIR = ~/etc/cubicweb.d/
        CW_RUNTIME_DIR = /tmp

Cubes search path is also affected, see the :ref:`Cube` section.


Setting Cubicweb Mode
`````````````````````

By default, the mode is set to 'system' for standard installation. The mode is
set to 'user' if `cubicweb is used from a mercurial repository`_. You can force
this by setting the :envvar:`CW_MODE` environment variable to either 'user' or
'system' so you can easily:

* use system wide installation but user specific instances and all, without root
  privileges on the system (`export CW_MODE=user`)

* use local checkout of cubicweb on system wide instances (requires root
  privileges on the system (`export CW_MODE=system`)

If you've a doubt about the mode you're currently running, check the first line
outputed by the :command:`cubicweb-ctl list` command.

.. _`cubicweb is used from a mercurial repository`: CubicwebDevelopmentMod_


.. _CubicwebDevelopmentMod:

Development Mode (source)
`````````````````````````

If :file:`.hg` directory is found into the cubicweb package, there are
specific resource rules.

`<CW_SOFTWARE_ROOT>` is the source checkout's ``cubicweb`` directory:

* cubicweb migration files are searched in `<CW_SOFTWARE_ROOT>/misc/migration`
  instead of `<INSTALL_PREFIX>/share/cubicweb/migration/`.


Development Mode (virtualenv)
`````````````````````````````

If a virtualenv is found to be activated (i.e. a VIRTUAL_ENV variable is found
in environment), the virtualenv root is used as `<INSTALL_PREFIX>`. This, in
particular, makes it possible to work in `setuptools development mode`_
(``python setup.py develop``) without any further configuration.

.. _`setuptools development mode`: https://pythonhosted.org/setuptools/setuptools.html#development-mode

.. _ConfigurationEnv:

Environment configuration
-------------------------

Python
``````

If you installed *CubicWeb* by cloning the Mercurial shell repository or from source
distribution, then you will need to update the environment variable PYTHONPATH by
adding the path to `cubicweb`:

Add the following lines to either :file:`.bashrc` or :file:`.bash_profile` to
configure your development environment ::

    export PYTHONPATH=/full/path/to/grshell-cubicweb

If you installed *CubicWeb* with packages, no configuration is required and your
new cubes will be placed in `/usr/share/cubicweb/cubes` and your instances will
be placed in `/etc/cubicweb.d`.


CubicWeb
````````

Here are all environment variables that may be used to configure *CubicWeb*:

.. envvar:: CW_MODE

   Resource mode: user or system, as explained in :ref:`ResourceMode`.

.. envvar:: CW_INSTANCES_DIR

   Directory where cubicweb instances will be found.

.. envvar:: CW_INSTANCES_DATA_DIR

   Directory where cubicweb instances data will be written (backup file...)

.. envvar:: CW_RUNTIME_DIR

   Directory where pid files will be written
"""

import importlib
import logging
import logging.config
import os
import pkgutil
import stat
import sys
from os.path import (
    exists,
    join,
    expanduser,
    abspath,
    basename,
    dirname,
    splitext,
    realpath,
)
from smtplib import SMTP, SMTPAuthenticationError
from threading import Lock
from warnings import filterwarnings

from logilab.common.configuration import (
    Configuration,
    Method,
    ConfigurationMixIn,
    merge_options,
    _validate as lgc_validate,
    REQUIRED,
    OptionError,
)
from logilab.common.decorators import cached
from logilab.common.logging_ext import set_log_methods, init_log

from cubicweb import CW_MIGRATION_MAP, ConfigurationError, Binary, _
from cubicweb.server import SOURCE_TYPES
from cubicweb.server.serverconfig import SourceConfiguration, generate_source_config
from cubicweb.toolsutils import (
    create_dir,
    option_value_from_env,
    read_config,
    restrict_perms_to_user,
)

if sys.version_info < (3, 10):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata

CONFIG_HELP_MESSAGE = """# This file is generated by CubicWeb. It describes all instance options.
    # All these options can be overridden by environment variables, which should
    # be named with the following pattern: CW_<OPTION_NAME> where OPTION_NAME is
    # the name of the option in uppercase and '-' converted in '_'.
    #
    # For example, the host option is replaced by the environment variable CW_HOST.
    # connections-pooler-enabled is overridden by CW_CONNECTIONS_POOLER_ENABLED

    """

SMTP_LOCK = Lock()


def _cube_pkgname(cube):
    if not cube.startswith("cubicweb_"):
        return "cubicweb_" + cube
    return cube


def _expand_modname(modname, recursive=True):
    """expand modules names `modname` if exists by recursively walking
    submodules and subpackages and yield (submodname, filepath) including
    `modname` itself

    If the file ends with .pyc or .pyo (python bytecode) also check that the
    corresponding source .py file exists before yielding.

    If `recursive` is False skip subpackages.
    """
    try:
        spec = importlib.util.find_spec(modname)
    except ImportError:
        return
    if not spec:
        return

    def check_source_file(filepath):
        if filepath[-4:] in (".pyc", ".pyo"):
            if not exists(filepath[:-1]):
                return False
        return True

    filepath = spec.origin
    if filepath is None or not check_source_file(filepath):
        return
    yield modname, filepath
    loader = spec.loader
    if loader.is_package(modname):
        path = dirname(filepath)
        for subloader, subname, ispkg in pkgutil.walk_packages([path]):
            submodname = ".".join([modname, subname])
            if not ispkg:
                filepath = subloader.find_spec(subname).origin
                if check_source_file(filepath):
                    yield submodname, filepath
            elif recursive:
                for x in _expand_modname(submodname, recursive=True):
                    yield x


# persistent options definition
PERSISTENT_OPTIONS = (
    (
        "encoding",
        {
            "type": "string",
            "default": "UTF-8",
            "help": _("user interface encoding"),
            "group": "ui",
            "sitewide": True,
        },
    ),
    (
        "language",
        {
            "type": "string",
            "default": "en",
            "vocabulary": Method("available_languages"),
            "help": _("language of the user interface"),
            "group": "ui",
        },
    ),
    (
        "date-format",
        {
            "type": "string",
            "default": "%Y/%m/%d",
            "help": _(
                'how to format date in the ui (see <a href="http://docs.python.org/library/datetime.html#strftime-strptime-behavior">this page</a> for format description)'
            ),
            "group": "ui",
        },
    ),
    (
        "datetime-format",
        {
            "type": "string",
            "default": "%Y/%m/%d %H:%M",
            "help": _(
                'how to format date and time in the ui (see <a href="http://docs.python.org/library/datetime.html#strftime-strptime-behavior">this page</a> for format description)'
            ),
            "group": "ui",
        },
    ),
    (
        "time-format",
        {
            "type": "string",
            "default": "%H:%M",
            "help": _(
                'how to format time in the ui (see <a href="http://docs.python.org/library/datetime.html#strftime-strptime-behavior">this page</a> for format description)'
            ),
            "group": "ui",
        },
    ),
    (
        "float-format",
        {
            "type": "string",
            "default": "%.3f",
            "help": _("how to format float numbers in the ui"),
            "group": "ui",
        },
    ),
    (
        "default-text-format",
        {
            "type": "choice",
            "choices": ("text/plain", "text/rest", "text/html", "text/markdown"),
            "default": "text/plain",
            "help": _("default text format for rich text fields."),
            "group": "ui",
        },
    ),
    (
        "short-line-size",
        {
            "type": "int",
            "default": 80,
            "help": _("maximum number of characters in short description"),
            "group": "navigation",
        },
    ),
)


def register_persistent_options(options):
    global PERSISTENT_OPTIONS
    PERSISTENT_OPTIONS = merge_options(PERSISTENT_OPTIONS + options)


CFGTYPE2ETYPE_MAP = {
    "string": "String",
    "choice": "String",
    "yn": "Boolean",
    "int": "Int",
    "float": "Float",
}


_INSTALL_PREFIX = os.environ.get("CW_INSTALL_PREFIX", sys.prefix)
_USR_INSTALL = _INSTALL_PREFIX == "/usr"


class CubicWebConfiguration(ConfigurationMixIn):
    """base class for cubicweb server and web configurations"""

    # to set in concrete configuration
    name = "repository"
    # log messages format (see logging module documentation for available keys)
    log_format = "%(asctime)s - (%(name)s) %(levelname)s: %(message)s"
    # the format below can be useful to debug multi thread issues:
    # log_format = '%(asctime)s - [%(threadName)s] (%(name)s) %(levelname)s: %(message)s'
    # nor remove appobjects based on unused interface [???]
    cleanup_unused_appobjects = True

    # read the schema from the database
    read_instance_schema = True
    # set this to true to get a minimal repository, for instance to get cubes
    # information on commands such as i18ninstance, db-restore, etc...
    quick_start = False
    # check user's state at login time
    consider_user_state = True

    # should some hooks be deactivated during [pre|post]create script execution
    free_wheel = False

    # list of enables sources when sources restriction is necessary
    # (eg repository initialization at least)
    enabled_sources = None

    if "VIRTUAL_ENV" in os.environ:
        mode = os.environ.get("CW_MODE", "user")
    else:
        mode = os.environ.get("CW_MODE", "system")
    assert mode in ("system", "user"), '"CW_MODE" should be either "user" or "system"'

    if mode == "user":
        _INSTANCES_DIR = expanduser("~/etc/cubicweb.d/")
    # mode == system'
    elif _USR_INSTALL:
        _INSTANCES_DIR = "/etc/cubicweb.d/"
    else:
        _INSTANCES_DIR = join(_INSTALL_PREFIX, "etc", "cubicweb.d")

    # set to true during repair (shell, migration) to allow some things which
    # wouldn't be possible otherwise
    repairing = False

    # set by upgrade command
    verbosity = 0
    cmdline_options = None

    smtp_cls = SMTP

    options = (
        (
            "log-threshold",
            {
                "type": "string",  # XXX use a dedicated type?
                "default": "WARNING",
                "help": "server's log level",
                "group": "main",
                "level": 1,
            },
        ),
        (
            "umask",
            {
                "type": "int",
                "default": 0o077,
                "help": "permission umask for files created by the server",
                "group": "main",
                "level": 2,
            },
        ),
        # common configuration options which are potentially required as soon as
        # you're using "base" application objects (ie to really server/web
        # specific)
        (
            "base-url",
            {
                "type": "string",
                "default": None,
                "help": "web server root url",
                "group": "main",
                "level": 1,
            },
        ),
        (
            "receives-base-url-path",
            {
                "type": "yn",
                "default": True,
                "help": "will the instance receives and handle a sub path if present on its base-url",
                "group": "main",
                "level": 1,
            },
        ),
        (
            "allow-email-login",
            {
                "type": "yn",
                "default": False,
                "help": "allow users to login with their primary email if set",
                "group": "main",
                "level": 2,
            },
        ),
        (
            "mangle-emails",
            {
                "type": "yn",
                "default": False,
                "help": "don't display actual email addresses but mangle them if \
this option is set to yes",
                "group": "email",
                "level": 3,
            },
        ),
        (
            "debug",
            {
                "type": "yn",
                "default": False,
                "help": "activate debug mode on startup, disabled by default",
                "group": "main",
                "level": 3,
            },
        ),
        (
            "log-file",
            {
                "type": "string",
                "default": Method("default_log_file"),
                "help": "file where output logs should be written",
                "group": "main",
                "level": 2,
            },
        ),
        # email configuration
        (
            "smtp-host",
            {
                "type": "string",
                "default": "mail",
                "help": "hostname of the SMTP mail server",
                "group": "email",
                "level": 1,
            },
        ),
        (
            "smtp-port",
            {
                "type": "int",
                "default": 25,
                "help": "listening port of the SMTP mail server",
                "group": "email",
                "level": 1,
            },
        ),
        (
            "smtp-username",
            {
                "default": "",
                "help": "username for SMTP mail server if auth is required",
                "group": "email",
                "level": 2,
            },
        ),
        (
            "smtp-password",
            {
                "default": "",
                "help": "password for SMTP mail server if auth is required",
                "group": "email",
                "level": 2,
            },
        ),
        (
            "sender-name",
            {
                "type": "string",
                "default": Method("default_instance_id"),
                "help": (
                    "name used as HELO name for outgoing emails from the repository."
                ),
                "group": "email",
                "level": 2,
            },
        ),
        (
            "sender-addr",
            {
                "type": "string",
                "default": "cubicweb@mydomain.com",
                "help": (
                    "email address used as HELO address for outgoing emails from the "
                    "repository"
                ),
                "group": "email",
                "level": 1,
            },
        ),
        (
            "sender-x-cw-header",
            {
                "type": "string",
                "default": Method("default_instance_id"),
                "help": "Value of the header X-CW for outgoing emails.",
                "group": "email",
                "level": 3,
            },
        ),
        (
            "logstat-interval",
            {
                "type": "int",
                "default": 0,
                "help": (
                    "interval (in seconds) at which stats are dumped in the logstat file; set 0 to "
                    "disable"
                ),
                "group": "main",
                "level": 2,
            },
        ),
        (
            "logstat-file",
            {
                "type": "string",
                "default": Method("default_stats_file"),
                "help": "file where stats for the instance should be written",
                "group": "main",
                "level": 2,
            },
        ),
        # ctl configuration
        (
            "host",
            {
                "type": "string",
                "default": "localhost",
                "help": "host name if not correctly detectable through gethostname",
                "group": "main",
                "level": 1,
            },
        ),
        (
            "pid-file",
            {
                "type": "string",
                "default": Method("default_pid_file"),
                "help": "repository's pid file",
                "group": "main",
                "level": 2,
            },
        ),
        (
            "uid",
            {
                "type": "string",
                "default": None,
                "help": (
                    "unix user, if this option is set, use the specified user to start \
the repository rather than the user running the command"
                ),
                "group": "main",
                "level": (mode == "installed") and 0 or 1,
            },
        ),
        (
            "cleanup-session-time",
            {
                "type": "time",
                "default": "24h",
                "help": (
                    "duration of inactivity after which a session "
                    "will be closed, to limit memory consumption (avoid sessions that "
                    "never expire and cause memory leak when http-session-time is 0, or "
                    "because of bad client that never closes their connection). "
                    "So notice that even if http-session-time is 0 and the user don't "
                    "close his browser, he will have to reauthenticate after this time "
                    "of inactivity. Default to 24h."
                ),
                "group": "main",
                "level": 3,
            },
        ),
        (
            "connections-pooler-enabled",
            {
                "type": "yn",
                "default": True,
                "help": "Enable the connection pooler. Set to no if you use an external database pooler (e.g. pgbouncer)",
                "group": "main",
                "level": 3,
            },
        ),
        (
            "connections-pool-max-size",
            {
                "type": "int",
                "default": 0,
                "help": "Maximum, per process, number of database connections. Default 0 (unlimited)",
                "group": "main",
                "level": 3,
            },
        ),
        (
            "connections-pool-min-size",
            {
                "type": "int",
                "default": 0,
                "help": "Minimum, per process, number of database connections.",
                "group": "main",
                "level": 3,
            },
        ),
        (
            "connections-pool-idle-timeout",
            {
                "type": "int",
                "default": 600,
                "help": "Start closing connection if the pool hasn't been empty for this many seconds",
                "group": "main",
                "level": 3,
            },
        ),
        (
            "rql-cache-size",
            {
                "type": "int",
                "default": 3000,
                "help": "size of the parsed rql cache size.",
                "group": "main",
                "level": 3,
            },
        ),
        (
            "undo-enabled",
            {
                "type": "yn",
                "default": False,
                "help": "enable undo support",
                "group": "main",
                "level": 3,
            },
        ),
        (
            "keep-transaction-lifetime",
            {
                "type": "int",
                "default": 7,
                "help": "number of days during which transaction records should be \
kept (hence undoable).",
                "group": "main",
                "level": 3,
            },
        ),
        (
            "multi-sources-etypes",
            {
                "type": "csv",
                "default": (),
                "help": "defines which entity types from this repository are used \
by some other instances. You should set this properly for these instances to \
detect updates / deletions.",
                "group": "main",
                "level": 3,
            },
        ),
        (
            "delay-full-text-indexation",
            {
                "type": "yn",
                "default": False,
                "help": (
                    "When full text indexation of entity has a too important cost"
                    " to be done when entity are added/modified by users, activate this "
                    "option and setup a job using cubicweb-ctl db-rebuild-fti on your "
                    "system (using cron for instance)."
                ),
                "group": "main",
                "level": 3,
            },
        ),
        # email configuration
        (
            "default-recipients-mode",
            {
                "type": "choice",
                "choices": ("default-dest-addrs", "users", "none"),
                "default": "default-dest-addrs",
                "help": 'when a notification should be sent with no specific rules \
to find recipients, recipients will be found according to this mode. Available \
modes are "default-dest-addrs" (emails specified in the configuration \
variable with the same name), "users" (every users which has activated \
account with an email set), "none" (no notification).',
                "group": "email",
                "level": 2,
            },
        ),
        (
            "default-dest-addrs",
            {
                "type": "csv",
                "default": (),
                "help": "comma separated list of email addresses that will be used \
as default recipient when an email is sent and the notification has no \
specific recipient rules.",
                "group": "email",
                "level": 2,
            },
        ),
        (
            "supervising-addrs",
            {
                "type": "csv",
                "default": (),
                "help": "comma separated list of email addresses that will be \
notified of every changes.",
                "group": "email",
                "level": 2,
            },
        ),
        (
            "anonymous-user",
            {
                "type": "string",
                "default": None,
                "help": (
                    "login of the CubicWeb user account to use for anonymous "
                    "user (if you want to allow anonymous)"
                ),
                "group": "web",
                "level": 1,
            },
        ),
        (
            "anonymous-password",
            {
                "type": "string",
                "default": None,
                "help": (
                    "password of the CubicWeb user account to use for anonymous user, "
                    "if anonymous-user is set"
                ),
                "group": "web",
                "level": 1,
            },
        ),
        (
            "cleanup-anonymous-session-time",
            {
                "type": "time",
                "default": "5min",
                "help": (
                    "Same as cleanup-session-time but specific to anonymous "
                    "sessions. You can have a much smaller timeout here since it will be "
                    "transparent to the user. Default to 5min."
                ),
                "group": "web",
                "level": 3,
            },
        ),
        # dbdump configuration
        (
            "dump-s3-endpoint-url",
            {
                "type": "string",
                "default": None,
                "help": "S3 endpoint url for database dump/restore (without protocol)",
                "group": "dbdump",
                "level": 3,
            },
        ),
        (
            "dump-s3-bucket-name",
            {
                "type": "string",
                "default": None,
                "help": "S3 bucket name for database dump/restore",
                "group": "dbdump",
                "level": 3,
            },
        ),
        (
            "dump-s3-access-key",
            {
                "type": "string",
                "default": None,
                "help": "S3 access key for database dump/restore",
                "group": "dbdump",
                "level": 3,
            },
        ),
        (
            "dump-s3-secret-key",
            {
                "type": "string",
                "default": None,
                "help": "S3 secret key for database dump/restore",
                "group": "dbdump",
                "level": 3,
            },
        ),
        (
            "dump-s3-region",
            {
                "type": "string",
                "default": None,
                "help": "S3 region name of buckets for database dump/restore",
                "group": "dbdump",
                "level": 3,
            },
        ),
        (
            "dump-s3-secure",
            {
                "type": "yn",
                "default": True,
                "help": "Activate the secure flag to use TLS connection with S3",
                "group": "dbdump",
                "level": 3,
            },
        ),
        (
            "dump-s3-cert-check",
            {
                "type": "yn",
                "default": True,
                "help": "Activate the verification of the certificat for HTTPS connections",
                "group": "dbdump",
                "level": 3,
            },
        ),
    )

    def load_defaults(self) -> None:
        """overload the parent `load_defaults` to load REQUIRED variables with
        environment values
        """
        for opt, optdict in self.options:
            action = optdict.get("action")
            if action != "callback":
                # callback action have no default
                default = self.option_default(opt, optdict)
                if default is REQUIRED:
                    # the next two lines are different from the parent's method.
                    # In the parent's, we always continue.
                    # In this case, we continue only if the value can not be
                    # read from the environment
                    default = option_value_from_env(opt)
                    if default is None:
                        continue
                self.set_option(opt, default, action, optdict)

    def __getitem__(self, key):
        """Get configuration option, by first looking at environment."""
        file_value = super(CubicWebConfiguration, self).__getitem__(key)
        value = option_value_from_env(key, file_value)
        if value is not None:
            option_def = self.get_option_def(key)
            value = lgc_validate(value, option_def)
        return value

    # static and class methods used to get instance independant resources ##
    @staticmethod
    def cubicweb_version():
        """return installed cubicweb version"""
        from logilab.common.changelog import Version

        str_base_version = importlib_metadata.version("cubicweb")
        version = tuple([int(x) for x in str_base_version.split(".")])
        assert len(version) == 3, version
        return Version(version)

    @staticmethod
    def persistent_options_configuration():
        return Configuration(options=PERSISTENT_OPTIONS)

    @classmethod
    def i18n_lib_dir(cls):
        """return instance's i18n directory"""
        return join(dirname(__file__), "i18n")

    @classmethod
    def cw_languages(cls):
        for fname in os.listdir(join(cls.i18n_lib_dir())):
            if fname.endswith(".po"):
                yield splitext(fname)[0]

    @classmethod
    def available_cubes(cls):
        """Return a list of available cube names.

        For cube as package, name is equal to python package's name.
        """
        cubes = set()
        for entry_point in importlib_metadata.entry_points(group="cubicweb.cubes"):
            try:
                module = entry_point.load()
            except ImportError:
                continue
            else:
                modname = module.__name__
                if not modname.startswith("cubicweb_"):
                    cls.warning(
                        "entry point %s does not appear to be a cube", entry_point
                    )
                    continue
                cubes.add(modname)

        def sortkey(cube):
            """Preserve sorting with "cubicweb_" prefix."""
            prefix = "cubicweb_"
            if cube.startswith(prefix):
                # add a suffix to have a deterministic sorting between
                # 'cubicweb_<cube>' and '<cube>' (useful in tests with "hash
                # randomization" turned on).
                return cube[len(prefix) :] + "~"
            return cube

        return sorted(cubes, key=sortkey)

    @classmethod
    def cube_dir(cls, cube):
        """return the cube directory for the given cube id, raise
        `ConfigurationError` if it doesn't exist
        """
        pkgname = _cube_pkgname(cube)
        loader = importlib.util.find_spec(pkgname)
        if loader:
            return dirname(loader.origin)
        raise ConfigurationError(
            f"no module {pkgname} while searching in cube '{cube}'"
        )

    @classmethod
    def cube_migration_scripts_dir(cls, cube):
        """cube migration scripts directory"""
        return join(cls.cube_dir(cube), "migration")

    @classmethod
    def cube_pkginfo(cls, cube):
        """return the information module for the given cube"""
        cube = CW_MIGRATION_MAP.get(cube, cube)
        pkgname = _cube_pkgname(cube)
        return importlib.import_module(f"{pkgname}.__pkginfo__")

    @classmethod
    def cube_version(cls, cube):
        """return the version of the cube located in the given directory"""
        from logilab.common.changelog import Version

        version = cls.cube_pkginfo(cube).numversion
        assert len(version) == 3, version
        return Version(version)

    @classmethod
    def _cube_deps(cls, cube, key):
        """return cubicweb cubes used by the given cube"""
        pkginfo = cls.cube_pkginfo(cube)
        try:
            # explicit __xxx_cubes__ attribute
            deps = getattr(pkginfo, key)
        except AttributeError:
            # deduce cubes from generic __xxx__ attribute
            try:
                gendeps = getattr(pkginfo, key.replace("_cubes", ""))
            except AttributeError:
                deps = {}
            else:
                deps = dict(
                    (x[len("cubicweb-") :], v)
                    for x, v in gendeps.items()
                    if x.startswith("cubicweb-")
                )
        for depcube in deps:
            try:
                newname = CW_MIGRATION_MAP[depcube]
            except KeyError:
                pass
            else:
                deps[newname] = deps.pop(depcube)
        return deps

    @classmethod
    def cube_depends_cubicweb_version(cls, cube):
        # XXX no backward compat (see _cube_deps above)
        try:
            pkginfo = cls.cube_pkginfo(cube)
            deps = getattr(pkginfo, "__depends__")
            return deps.get("cubicweb")
        except AttributeError:
            return None

    @classmethod
    def cube_dependencies(cls, cube):
        """return cubicweb cubes used by the given cube"""
        return cls._cube_deps(cube, "__depends_cubes__")

    @classmethod
    def cube_recommends(cls, cube):
        """return cubicweb cubes recommended by the given cube"""
        return cls._cube_deps(cube, "__recommends_cubes__")

    @classmethod
    def expand_cubes(cls, cubes, with_recommends=False):
        """expand the given list of top level cubes used by adding recursivly
        each cube dependencies
        """
        cubes = list(cubes)
        todo = cubes[:]
        if with_recommends:
            available = set(cls.available_cubes())
        while todo:
            cube = todo.pop(0)
            for depcube in cls.cube_dependencies(cube):
                if depcube not in cubes:
                    cubes.append(depcube)
                    todo.append(depcube)
            if with_recommends:
                for depcube in cls.cube_recommends(cube):
                    if depcube not in cubes and depcube in available:
                        cubes.append(depcube)
                        todo.append(depcube)
        return cubes

    @classmethod
    def reorder_cubes(cls, cubes):
        """reorder cubes from the top level cubes to inner dependencies
        cubes
        """
        from logilab.common.graph import ordered_nodes, UnorderableGraph

        graph = {}
        for cube in cubes:
            cube = CW_MIGRATION_MAP.get(cube, cube)
            graph[cube] = set(
                dep for dep in cls.cube_dependencies(cube) if dep in cubes
            )
            graph[cube] |= set(dep for dep in cls.cube_recommends(cube) if dep in cubes)
        try:
            return ordered_nodes(graph)
        except UnorderableGraph as ex:
            raise ConfigurationError(ex)

    @classmethod
    def load_available_configs(cls):
        for confmod in (
            "cubicweb_web.webconfig",
            "cubicweb.server.serverconfig",
            "cubicweb.pyramid.config",
        ):
            try:
                __import__(confmod)
            except ImportError as exc:
                cls.warning("failed to load config module %s (%s)", confmod, exc)

    @classmethod
    def load_cwctl_plugins(cls):
        for ctlmod in (
            "cubicweb.server.serverctl",
            "cubicweb.devtools.devctl",
            "cubicweb.pyramid.pyramidctl",
        ):
            try:
                __import__(ctlmod)
            except ImportError as exc:
                cls.warning("failed to load cubicweb-ctl plugin %s (%s)", ctlmod, exc)
                continue
            cls.info("loaded cubicweb-ctl plugin %s", ctlmod)

        for cube in cls.available_cubes():
            cubedir = cls.cube_dir(cube)
            pluginfile = join(cubedir, "ccplugin.py")
            initfile = join(cubedir, "__init__.py")
            pkgname = _cube_pkgname(cube)
            if exists(pluginfile):
                try:
                    __import__(pkgname + ".ccplugin")
                    cls.info("loaded cubicweb-ctl plugin from %s", cube)
                except Exception:
                    cls.exception("while loading plugin %s", pluginfile)
            elif exists(initfile):
                try:
                    __import__(pkgname)
                except Exception:
                    cls.exception("while loading cube %s", cube)
            else:
                cls.warning("no __init__ file in cube %s", cube)

    cubicweb_appobject_path = {"entities", "sobjects", "hooks"}
    cube_appobject_path = {"entities", "sobjects", "hooks"}

    def __init__(self, appid, debugmode=False, creating=False, log_to_file=False):
        self.appid = appid

        # set to true while creating an instance
        self.creating = creating

        if debugmode:
            # in python 2.7, DeprecationWarning are not shown anymore by default
            filterwarnings("default", category=DeprecationWarning)

        register_stored_procedures()
        self._cubes = None
        super(CubicWebConfiguration, self).__init__()
        self.debugmode = debugmode
        self.log_to_file = log_to_file
        self.adjust_sys_path()
        self.load_defaults()

        # will be properly initialized later by _gettext_init
        self.translations = {"en": (str, lambda ctx, msgid: str(msgid))}
        self._site_loaded = set()

        fake_gettext = (str, lambda ctx, msgid: str(msgid))
        for lang in self.available_languages():
            self.translations[lang] = fake_gettext

        self._cubes = None
        self.load_file_configuration(self.main_config_file())

    def adjust_sys_path(self):
        # adding apphome to python path is not usually necessary in production
        # environments, but necessary for tests
        if self.apphome and self.apphome not in sys.path:
            sys.path.insert(0, self.apphome)

    def init_log(self, logthreshold=None, force=False, logfile=None, syslog=None):
        """init the log service"""
        if not force and hasattr(self, "_logging_initialized"):
            return
        self._logging_initialized = True

        if logthreshold is None:
            if self.debugmode:
                logthreshold = "DEBUG"
            else:
                logthreshold = self["log-threshold"]
        init_log(not self.log_to_file, syslog, logthreshold, logfile, self.log_format)

        # configure simpleTal logger
        logging.getLogger("simpleTAL").setLevel(logging.ERROR)

        self.init_log(logthreshold, logfile=self.get("log-file"))
        # read a config file if it exists
        logconfig = join(self.apphome, "logging.conf")
        if exists(logconfig):
            logging.config.fileConfig(logconfig)

    def schema_modnames(self):
        modnames = []
        for name in ("bootstrap", "base", "workflow", "Bookmark"):
            modnames.append(("cubicweb", "cubicweb.schemas." + name))
        for cube in reversed(self.cubes()):
            for modname, filepath in _expand_modname(
                f"{_cube_pkgname(cube)}.schema", recursive=False
            ):
                modnames.append((cube, modname))
        if self.apphome:
            apphome = realpath(self.apphome)
            for modname, filepath in _expand_modname("schema", recursive=False):
                if realpath(filepath).startswith(apphome):
                    modnames.append(("data", modname))
        return modnames

    def appobjects_modnames(self):
        modnames = []
        for name in self._sorted_appobjects(self.cubicweb_appobject_path):
            for modname, filepath in _expand_modname("cubicweb." + name):
                modnames.append(modname)

        for cube in reversed(self.cubes()):
            modnames.extend(self.appobjects_cube_modnames(cube))

        if self.apphome:
            cube_submodnames = self._sorted_appobjects(self.cube_appobject_path)
            apphome = realpath(self.apphome)
            for name in cube_submodnames:
                for modname, filepath in _expand_modname(name):
                    # ensure file is in apphome
                    if realpath(filepath).startswith(apphome):
                        modnames.append(modname)

        return modnames

    @property
    def apphome(self):
        return join(self.instances_dir(), self.appid)

    def load_site_cubicweb(self, cubes=()):
        """load site_cubicweb file for `cubes`"""
        for cube in reversed(cubes or self.cubes()):
            if cube in self._site_loaded:
                continue
            try:
                self._load_site_cubicweb(cube)
                self._site_loaded.add(cube)
            except ImportError:
                continue
        if self.apphome is not None:
            # Would occur, e.g., upon `cubicweb-ctl i18ncube <cube>`.
            self._load_site_cubicweb(None)

    def _load_site_cubicweb(self, cube):
        """Load site_cubicweb.py from `cube` (or apphome if cube is None)."""
        mod = None

        if cube is not None:
            modname = _cube_pkgname(cube)
            __import__(modname)
            modname = modname + ".site_cubicweb"
            __import__(modname)
            mod = sys.modules[modname]
        else:
            import types
            import importlib.machinery

            apphome_site = join(self.apphome, "site_cubicweb.py")
            if exists(apphome_site):
                loader = importlib.machinery.SourceFileLoader(
                    "site_cubicweb", apphome_site
                )
                mod = types.ModuleType(loader.name)
                loader.exec_module(mod)
            else:
                mod = None

        # overridden to register cube specific options
        if getattr(mod, "options", None):
            self.register_options(mod.options)
            self.load_defaults()

    def cwproperty_definitions(self):
        cfg = self.persistent_options_configuration()
        for section, options in cfg.options_by_section():
            section = section.lower()
            for optname, optdict, value in options:
                key = f"{section}.{optname}"
                type, vocab = self.map_option(optdict)
                default = cfg.option_default(optname, optdict)
                pdef = {
                    "type": type,
                    "vocabulary": vocab,
                    "default": default,
                    "help": optdict["help"],
                    "sitewide": optdict.get("sitewide", False),
                }
                yield key, pdef

    def map_option(self, optdict):
        try:
            vocab = optdict["choices"]
        except KeyError:
            vocab = optdict.get("vocabulary")
            if isinstance(vocab, Method):
                vocab = getattr(self, vocab.method, ())
        return CFGTYPE2ETYPE_MAP[optdict["type"]], vocab

    def default_instance_id(self):
        """return the instance identifier, useful for option which need this
        as default value
        """
        return self.appid

    _cubes = None

    @classmethod
    def _warn_pyramid_cube(cls):
        cls.warning(
            "cubicweb-pyramid got integrated into CubicWeb; "
            "remove it from your project's dependencies"
        )

    def init_cubes(self, cubes):
        cubes = list(cubes)
        if "pyramid" in cubes:
            self._warn_pyramid_cube()
            cubes.remove("pyramid")

        self._cubes = self.reorder_cubes(cubes)

        # load cubes'__init__.py file first
        for cube in cubes:
            importlib.import_module(_cube_pkgname(cube))

        self.load_site_cubicweb()

        # reload config file in cases options are defined in cubes __init__
        # or site_cubicweb files
        self.load_file_configuration(self.main_config_file())

        # configuration initialization hook
        self.load_configuration(**(self.cmdline_options or {}))

    def cubes(self):
        """return the list of cubes used by this instance

        result is ordered from the top level cubes to inner dependencies
        cubes
        """
        assert self._cubes is not None, "cubes not initialized"
        return self._cubes

    def cubes_path(self):
        """return the list of path to cubes used by this instance, from outer
        most to inner most cubes
        """
        return [self.cube_dir(p) for p in self.cubes()]

    # these are overridden by set_log_methods below
    # only defining here to prevent pylint from complaining
    @classmethod
    def debug(cls, msg, *a, **kw):
        pass

    @classmethod
    def instances_dir(cls):
        """return the control directory"""
        return abspath(os.environ.get("CW_INSTANCES_DIR", cls._INSTANCES_DIR))

    @classmethod
    def migration_scripts_dir(cls):
        """cubicweb migration scripts directory"""
        mdir = join(dirname(__file__), "misc", "migration")
        assert exists(mdir), f"migration path {mdir} does not exist"
        return mdir

    @classmethod
    def config_for(
        cls, appid, config=None, debugmode=False, log_to_file=False, creating=False
    ):
        """return a configuration instance for the given instance identifier"""
        cls.load_available_configs()
        try:
            from cubicweb_web.webconfig import WebAllInOneConfiguration

            configcls = WebAllInOneConfiguration
        except ImportError:
            from cubicweb.pyramid.config import AllInOneConfiguration

            configcls = AllInOneConfiguration

        return configcls(appid, debugmode, creating, log_to_file=log_to_file)

    @classmethod
    def instance_home(cls, appid):
        """return the home directory of the instance with the given
        instance id
        """
        home = join(cls.instances_dir(), appid)
        if not exists(home):
            raise ConfigurationError(
                f'no such instance {appid} (check it exists with "cubicweb-ctl list")'
            )
        return home

    MODES = ("common", "repository", "Any")
    MCOMPAT = {
        "all-in-one": MODES,
    }

    @classmethod
    def accept_mode(cls, mode):
        # assert mode in cls.MODES, mode
        return mode in cls.MCOMPAT[cls.name]

    # default configuration methods ###########################################

    def default_log_file(self):
        """return default path to the log file of the instance'server"""
        if self.mode == "user":
            import tempfile

            basepath = join(
                tempfile.gettempdir(), f"{basename(self.appid)}-{self.name}"
            )
            path = basepath + ".log"
            i = 1
            while exists(path) and i < 100:  # arbitrary limit to avoid infinite loop
                try:
                    open(path, "a")
                    break
                except IOError:
                    path = f"{basepath}-{i}.log"
                    i += 1
            return path
        if _USR_INSTALL:
            return f"/var/log/cubicweb/{self.appid}-{self.name}.log"
        else:
            log_path = os.path.join(
                _INSTALL_PREFIX, "var", "log", "cubicweb", "%s-%s.log"
            )
            return log_path % (self.appid, self.name)

    def default_stats_file(self):
        """return default path to the stats file of the instance'server"""
        logfile = self.default_log_file()
        if logfile.endswith(".log"):
            logfile = logfile[:-4]
        return logfile + ".stats"

    def default_pid_file(self):
        """return default path to the pid file of the instance'server"""
        if self.mode == "system":
            if _USR_INSTALL:
                default = "/var/run/cubicweb/"
            else:
                default = os.path.join(_INSTALL_PREFIX, "var", "run", "cubicweb")
        else:
            import tempfile

            default = tempfile.gettempdir()
        # runtime directory created on startup if necessary, don't check it
        # exists
        rtdir = abspath(os.environ.get("CW_RUNTIME_DIR", default))
        return join(rtdir, f"{self.appid}-{self.name}.pid")

    # config -> repository

    def repository(self, vreg=None):
        """Return a new bootstrapped repository."""
        from cubicweb.server.repository import Repository

        repo = Repository(self, vreg=vreg)
        repo.bootstrap()
        return repo

    # instance methods used to get instance specific resources #############

    @property
    def appdatahome(self):
        if self.mode == "system":
            if _USR_INSTALL:
                iddir = os.path.join("/var", "lib", "cubicweb", "instances")
            else:
                iddir = os.path.join(
                    _INSTALL_PREFIX, "var", "lib", "cubicweb", "instances"
                )
        else:
            iddir = self.instances_dir()
        iddir = abspath(os.environ.get("CW_INSTANCES_DATA_DIR", iddir))
        return join(iddir, self.appid)

    def add_cubes(self, cubes):
        """add given cubes to the list of used cubes"""
        if not isinstance(cubes, list):
            cubes = list(cubes)
        self._cubes = self.reorder_cubes(list(self._cubes) + cubes)
        self.load_site_cubicweb(cubes)

    def main_config_file(self):
        """return instance's control configuration file"""
        return join(self.apphome, f"{self.name}.conf")

    def save(self):
        """write down current configuration"""
        with open(self.main_config_file(), "w") as fobj:
            self.generate_config(fobj, header_message=CONFIG_HELP_MESSAGE)

    def check_writeable_uid_directory(self, path):
        """check given directory path exists, belongs to the user running the
        server process and is writeable.

        If not, try to fix this, letting exception propagate when not possible.
        """
        if not exists(path):
            self.info("creating %s directory", path)
            try:
                os.makedirs(path)
            except OSError as ex:
                self.warning("error while creating %s directory: %s", path, ex)
                return
        self.ensure_uid(path)

    def get_uid(self):
        if self["uid"]:
            try:
                uid = int(self["uid"])
            except ValueError:
                from pwd import getpwnam

                uid = getpwnam(self["uid"]).pw_uid
        else:
            uid = os.getuid()
        return uid

    def ensure_uid(self, path, enforce_write=False):
        if not exists(path):
            return
        uid = self.get_uid()
        if uid is None:
            return
        fstat = os.stat(path)
        if fstat.st_uid != uid:
            self.info("giving ownership of %s to %s", path, self["uid"])
            try:
                os.chown(path, uid, os.getgid())
            except OSError as ex:
                self.warning(
                    "error while giving ownership of %s to %s: %s",
                    path,
                    self["uid"],
                    ex,
                )

        if enforce_write and not (fstat.st_mode & stat.S_IWUSR):
            self.info("forcing write permission on %s", path)
            try:
                os.chmod(path, fstat.st_mode | stat.S_IWUSR)
            except OSError as ex:
                self.warning("error while forcing write permission on %s: %s", path, ex)

    def ensure_uid_directory(self, path, enforce_write=False):
        self.check_writeable_uid_directory(path)
        for dirpath, dirnames, filenames in os.walk(path):
            for name in filenames:
                self.ensure_uid(join(dirpath, name), enforce_write)
        return path

    @cached
    def instance_md5_version(self):
        from hashlib import md5  # pylint: disable=E0611

        infos = []
        for pkg in sorted(self.cubes()):
            version = self.cube_version(pkg)
            infos.append(f"{pkg}-{version}")
        infos.append(f"cubicweb-{str(self.cubicweb_version())}")
        return md5((";".join(infos)).encode("ascii")).hexdigest()

    def load_configuration(self, **kw):
        """load instance's configuration files"""
        super(CubicWebConfiguration, self).load_configuration(**kw)
        if self.apphome and not self.creating:
            # init gettext
            self._gettext_init()

        self._init_base_url()

    def _generate_base_url(self):
        # normalize base url(s)
        base_url = self["base-url"] or self.default_base_url()

        if base_url and base_url[-1] != "/":
            base_url += "/"

        return base_url

    def _init_base_url(self):
        if not (self.repairing or self.creating):
            self.global_set_option("base-url", self._generate_base_url())

    def default_base_url(self):
        from socket import getfqdn

        return f"http://{self['host'] or getfqdn().lower()}:{self['port'] or 8080}/"

    def available_languages(self, *args):
        """return available translation for an instance, by looking for
        compiled catalog

        take *args to be usable as a vocabulary method
        """
        from glob import glob

        yield "en"  # ensure 'en' is yielded even if no .mo found
        for path in glob(join(self.apphome, "i18n", "*", "LC_MESSAGES")):
            lang = path.split(os.sep)[-2]
            if lang != "en":
                yield lang

    def _gettext_init(self):
        """set language for gettext"""
        from cubicweb.cwgettext import translation

        path = join(self.apphome, "i18n")
        for language in self.available_languages():
            self.info("loading language %s", language)
            try:
                tr = translation("cubicweb", path, languages=[language])
                self.translations[language] = (tr.ugettext, tr.upgettext)
            except IOError:
                if self.mode != "test":
                    # in test contexts, data/i18n does not exist, hence
                    # logging will only pollute the logs
                    self.exception(
                        "localisation support error for language %s", language
                    )

    @staticmethod
    def _sorted_appobjects(appobjects):
        appobjects = sorted(appobjects)
        try:
            index = appobjects.index("entities")
        except ValueError:
            pass
        else:
            # put entities first
            appobjects.insert(0, appobjects.pop(index))
        return appobjects

    def appobjects_cube_modnames(self, cube):
        modnames = []
        cube_modname = _cube_pkgname(cube)
        cube_submodnames = self._sorted_appobjects(self.cube_appobject_path)
        for name in cube_submodnames:
            for modname, filepath in _expand_modname(".".join([cube_modname, name])):
                modnames.append(modname)
        return modnames

    sources_mode = None

    def set_sources_mode(self, sources):
        self.sources_mode = sources

    def i18ncompile(self, langs=None):
        from cubicweb import i18n

        if langs is None:
            langs = self.available_languages()
        i18ndir = join(self.apphome, "i18n")
        if not exists(i18ndir):
            create_dir(i18ndir)
        sourcedirs = [join(path, "i18n") for path in self.cubes_path()]
        sourcedirs.append(self.i18n_lib_dir())
        return i18n.compile_i18n_catalogs(sourcedirs, i18ndir, langs)

    def sendmails(self, msgs, fromaddr=None):
        """msgs: list of 2-uple (message object, recipients). Return False
        if connection to the smtp server failed, else True.
        """
        server, port = self["smtp-host"], self["smtp-port"]
        smtp_user, smtp_password = self["smtp-username"], self["smtp-password"]
        if fromaddr is None:
            fromaddr = f"{self['sender-name']} <{self['sender-addr']}>"
        SMTP_LOCK.acquire()
        try:
            try:
                smtp = self.smtp_cls(server, port)
                try:
                    if smtp_user and smtp_password:
                        smtp.login(smtp_user, smtp_password)
                except SMTPAuthenticationError as exception:
                    self.exception(
                        "cannot log in to SMTP server %s:%s (%s)",
                        server,
                        port,
                        exception,
                    )
            except Exception as ex:
                self.exception(
                    "can't connect to smtp server %s:%s (%s)", server, port, ex
                )
                if self.mode == "test":
                    raise
                return False
            for msg, recipients in msgs:
                try:
                    smtp.sendmail(msg.get("From", fromaddr), recipients, msg.as_bytes())
                except Exception as ex:
                    self.exception("error sending mail to %s (%s)", recipients, ex)
                    if self.mode == "test":
                        raise
            smtp.close()
        finally:
            SMTP_LOCK.release()
        return True

    info = warning = error = critical = exception = debug

    def bootstrap_cubes(self):
        from logilab.common.textutils import splitstrip

        with open(join(self.apphome, "bootstrap_cubes")) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                self.init_cubes(self.expand_cubes(splitstrip(line)))
                break
            else:
                # no cubes
                self.init_cubes(())

    def write_bootstrap_cubes_file(self, cubes):
        stream = open(join(self.apphome, "bootstrap_cubes"), "w")
        stream.write("# this is a generated file only used for bootstraping\n")
        stream.write("# you should not have to edit this\n")
        stream.write(f"{','.join(cubes)}\n")
        stream.close()

    def sources_file(self):
        return join(self.apphome, "sources")

    # this method has to be cached since when the server is running using a
    # restricted user, this user usually don't have access to the sources
    # configuration file (#16102)
    @cached
    def read_sources_file(self):
        """return a dictionary of values found in the sources file"""
        return read_config(self.sources_file(), raise_if_unreadable=True)

    def source_enabled(self, source):
        if self.sources_mode is not None:
            if "migration" in self.sources_mode:
                assert len(self.sources_mode) == 1
                if source.connect_for_migration:
                    return True
                print("not connecting to source", source.uri, "during migration")
                return False
            if "all" in self.sources_mode:
                assert len(self.sources_mode) == 1
                return True
            return source.uri in self.sources_mode
        if self.quick_start:
            return source.uri == "system"
        return not source.disabled and (
            not self.enabled_sources or source.uri in self.enabled_sources
        )

    def write_sources_file(self, sourcescfg):
        """serialize repository'sources configuration into a INI like file"""
        sourcesfile = self.sources_file()
        if exists(sourcesfile):
            import shutil

            shutil.copy(sourcesfile, sourcesfile + ".bak")
        stream = open(sourcesfile, "w")
        stream.write(CONFIG_HELP_MESSAGE)
        for section in ("admin", "system"):
            sconfig = sourcescfg[section]
            if isinstance(sconfig, dict):
                # get a Configuration object
                assert section == "system", f"{section!r} is not system"
                _sconfig = SourceConfiguration(
                    self, options=SOURCE_TYPES["native"].options
                )
                for attr, val in sconfig.items():
                    try:
                        _sconfig.set_option(attr, val)
                    except OptionError:
                        # skip adapter, may be present on pre 3.10 instances
                        if attr != "adapter":
                            self.error(f"skip unknown option {attr} in sources file")
                sconfig = _sconfig
            stream.write(f"[{section}]\n{generate_source_config(sconfig)}\n")
        restrict_perms_to_user(sourcesfile)

    def load_schema(self, expand_cubes=False, **kwargs):
        from cubicweb.schema import CubicWebSchemaLoader

        if expand_cubes:
            # in case some new dependencies have been introduced, we have to
            # reinitialize cubes so the full filesystem schema is read
            origcubes = self.cubes()
            self._cubes = None
            self.init_cubes(self.expand_cubes(origcubes))
        schema = CubicWebSchemaLoader().load(self, **kwargs)
        if expand_cubes:
            # restore original value
            self._cubes = origcubes
        return schema

    def load_bootstrap_schema(self):
        from cubicweb.schema import BootstrapSchemaLoader

        schema = BootstrapSchemaLoader().load(self)
        schema.name = "bootstrap"
        return schema

    def migration_handler(
        self,
        schema=None,
        interactive=True,
        cnx=None,
        repo=None,
        connect=True,
        verbosity=None,
    ):
        """return a migration handler instance"""
        from cubicweb.server.migractions import ServerMigrationHelper

        if verbosity is None:
            verbosity = getattr(self, "verbosity", 0)
        return ServerMigrationHelper(
            self,
            schema,
            interactive=interactive,
            cnx=cnx,
            repo=repo,
            connect=connect,
            verbosity=verbosity,
        )

    def anonymous_user(self):
        """return a login and password to use for anonymous users.

        None may be returned for both if anonymous connection is not
        allowed or if an empty login is used in configuration
        """
        try:
            user = self["anonymous-user"] or None
            passwd = self["anonymous-password"]
        except KeyError:
            user, passwd = None, None
        except UnicodeDecodeError:
            raise ConfigurationError("anonymous information should only contains ascii")
        return user, passwd

    @property
    def system_source_config(self):
        return self.read_sources_file()["system"]

    @property
    def default_admin_config(self):
        return self.read_sources_file()["admin"]


set_log_methods(CubicWebConfiguration, logging.getLogger("cubicweb.configuration"))

# alias to get a configuration instance from an instance id
instance_configuration = CubicWebConfiguration.config_for


_EXT_REGISTERED = False


def register_stored_procedures():
    from logilab.database import FunctionDescr
    from rql.utils import register_function, iter_funcnode_variables
    from rql.nodes import SortTerm, Constant, VariableRef

    global _EXT_REGISTERED
    if _EXT_REGISTERED:
        return
    _EXT_REGISTERED = True

    class COMMA_JOIN(FunctionDescr):
        supported_backends = (
            "postgres",
            "sqlite",
        )
        rtype = "String"

        def st_description(self, funcnode, mainindex, tr):
            return ", ".join(
                sorted(
                    term.get_description(mainindex, tr)
                    for term in iter_funcnode_variables(funcnode)
                )
            )

    register_function(COMMA_JOIN)  # XXX do not expose?

    class CONCAT_STRINGS(COMMA_JOIN):
        aggregat = True

    register_function(CONCAT_STRINGS)  # XXX bw compat

    class GROUP_CONCAT(CONCAT_STRINGS):
        supported_backends = (
            "postgres",
            "sqlite",
        )

    register_function(GROUP_CONCAT)

    class GROUP_LIST(FunctionDescr):
        aggregat = True
        supported_backends = ("postgres",)
        minargs = maxargs = 1
        rtype = "List[Any]"

        def as_sql_postgres(self, args):
            return f"ARRAY_AGG({args[0]})"

    register_function(GROUP_LIST)

    class LIMIT_SIZE(FunctionDescr):
        supported_backends = (
            "postgres",
            "sqlite",
        )
        minargs = maxargs = 3
        rtype = "String"

        def st_description(self, funcnode, mainindex, tr):
            return funcnode.children[0].get_description(mainindex, tr)

    register_function(LIMIT_SIZE)

    class TEXT_LIMIT_SIZE(LIMIT_SIZE):
        supported_backends = (
            "postgres",
            "sqlite",
        )
        minargs = maxargs = 2

    register_function(TEXT_LIMIT_SIZE)

    class FTIRANK(FunctionDescr):
        """return ranking of a variable that must be used as some has_text
        relation subject in the query's restriction. Usually used to sort result
        of full-text search by ranking.
        """

        supported_backends = ("postgres",)
        rtype = "Float"

        def st_check_backend(self, backend, funcnode):
            """overriden so that on backend not supporting fti ranking, the
            function is removed when in an orderby clause, or replaced by a 1.0
            constant.
            """
            if not self.supports(backend):
                parent = funcnode.parent
                while parent is not None and not isinstance(parent, SortTerm):
                    parent = parent.parent
                if isinstance(parent, SortTerm):
                    parent.parent.remove(parent)
                else:
                    funcnode.parent.replace(funcnode, Constant(1.0, "Float"))
                    parent = funcnode
                for vref in parent.iget_nodes(VariableRef):
                    vref.unregister_reference()

    register_function(FTIRANK)

    class FTIHL(FunctionDescr):
        """return fragments of the document with marked search terms

        eg: Any X, FTIHL(C, "hello") WHERE X has_text "hello", X content C
        eg: Any X, FTIHL(C, "hello", "MaxFragments=2") WHERE X has_text "hello", X content C

        options are comma separated.
        See https://www.postgresql.org/docs/current/textsearch-controls.html#TEXTSEARCH-HEADLINE
        for the list of available options
        """

        supported_backends = ("postgres",)
        rtype = "String"
        minargs = 2
        maxargs = 3

        def as_sql_postgres(self, args):
            attr, search_text = args[:2]
            options = args[2] if len(args) == 3 else None

            if not options:
                return f"ts_headline({attr}, plainto_tsquery({search_text}))"
            return f"ts_headline({attr}, plainto_tsquery({search_text}), {options})"

    register_function(FTIHL)

    class FSPATH(FunctionDescr):
        """return path of some bytes attribute stored using the Bytes
        File-System Storage (bfss)
        """

        rtype = "Bytes"  # XXX return a String? potential pb with fs encoding

        def update_cb_stack(self, stack):
            assert len(stack) == 1
            stack[0] = self.source_execute

        def as_sql(self, backend, args):
            raise NotImplementedError(
                "This callback is only available for BytesFileSystemStorage "
                "managed attribute. Is FSPATH() argument BFSS managed?"
            )

        def source_execute(self, source, session, value):
            fpath = source.binary_to_str(value)
            try:
                return Binary(fpath)
            except OSError as ex:
                source.critical("can't open %s: %s", fpath, ex)
                return None

    register_function(FSPATH)
