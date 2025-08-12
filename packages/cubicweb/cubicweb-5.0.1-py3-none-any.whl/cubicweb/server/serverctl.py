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
"""cubicweb-ctl commands and command handlers specific to the repository"""
import os

# *ctl module should limit the number of import to be imported as quickly as
# possible (for cubicweb-ctl reactivity, necessary for instance for usable bash
# completion). So import locally in command helpers.
import sched
import sys
from contextlib import contextmanager

from glob import glob
from tempfile import NamedTemporaryFile

from logilab.common.configuration import Configuration, merge_options
from logilab.common.shellutils import ASK, generate_password
from logilab.database import get_db_helper, get_connection

from cubicweb import (
    AuthenticationError,
    ExecutionError,
    ConfigurationError,
)
from cubicweb.cwctl import CWCTL, check_options_consistency, ConfigureInstanceCommand
from cubicweb.server import SOURCE_TYPES
from cubicweb.server import checkintegrity
from cubicweb.server.check_unused_index import check_unused_index
from cubicweb.server.serverconfig import (
    USER_OPTIONS,
    SourceConfiguration,
    ask_source_config,
    generate_source_config,
)
from cubicweb.cwconfig import CubicWebConfiguration
from cubicweb.toolsutils import Command, CommandHandler, underline_title


# utility functions ###########################################################


def source_cnx(source, dbname=None, special_privs=False, interactive=True):
    """open and return a connection to the system database defined in the
    given server.serverconfig
    """
    from getpass import getpass

    dbhost = source.get("db-host")
    if dbname is None:
        dbname = source["db-name"]
    driver = source["db-driver"]
    dbhelper = get_db_helper(driver)
    if interactive:
        print(f"-> connecting to {driver} database", end=" ")
        if dbhost:
            print(f"{dbname}@{dbhost}", end=" ")
        else:
            print(dbname, end=" ")
    if dbhelper.users_support:
        if not interactive or (not special_privs and source.get("db-user")):
            user = source.get("db-user", os.environ.get("USER", ""))
            if interactive:
                print("as", user)
            password = source.get("db-password")
        else:
            print()
            if special_privs:
                print("WARNING")
                print(
                    "the user will need the following special access rights "
                    "on the database:"
                )
                print(special_privs)
                print()
            default_user = source.get("db-user", os.environ.get("USER", ""))
            user = input(f"Connect as user ? [{default_user!r}]: ")
            user = user.strip() or default_user
            if user == source.get("db-user"):
                password = source.get("db-password")
            else:
                password = getpass("password: ")
    else:
        user = password = None
    extra_args = source.get("db-extra-arguments")
    extra = extra_args and {"extra_args": extra_args} or {}
    cnx = get_connection(
        driver,
        dbhost,
        dbname,
        user,
        password=password,
        port=source.get("db-port"),
        schema=source.get("db-namespace"),
        **extra,
    )
    try:
        cnx.logged_user = user
    except AttributeError:
        # C object, __slots__
        from logilab.database import _SimpleConnectionWrapper

        cnx = _SimpleConnectionWrapper(cnx)
        cnx.logged_user = user
    return cnx


def _db_sys_cnx(source, special_privs, interactive=True):
    """return a connection on the RDMS system table (to create/drop a user or a
    database)
    """
    import logilab.common as lgp

    lgp.USE_MX_DATETIME = False
    # connect on the dbms system base to create our base
    system_db = get_db_helper(source["db-driver"]).system_database()
    cnx = source_cnx(
        source, system_db, special_privs=special_privs, interactive=interactive
    )
    # disable autocommit (isolation_level(1)) because DROP and
    # CREATE DATABASE can't be executed in a transaction
    set_isolation_level = getattr(cnx, "set_isolation_level", None)
    if set_isolation_level is not None:
        # set_isolation_level() is psycopg specific
        set_isolation_level(0)
    return cnx


def repo_cnx(config):
    """return a in-memory repository and a repoapi connection to it"""
    from cubicweb import repoapi
    from cubicweb.server.utils import manager_userpasswd

    db_driver = config.system_source_config.get("db-driver")
    if db_driver == "sqlite":
        if not os.path.exists(config.system_source_config.get("db-name")):
            print("Your database does not exist.")
            sys.exit(1)
        from sqlite3 import OperationalError
    else:
        from psycopg2 import OperationalError
    try:
        login = config.default_admin_config["login"]
        pwd = config.default_admin_config["password"]
    except KeyError:
        login, pwd = manager_userpasswd()
    while True:
        try:
            repo = repoapi.get_repository(config=config)
            cnx = repoapi.connect(repo, login, password=pwd)
            return repo, cnx
        except AuthenticationError:
            print("-> Error: wrong user/password.")
            # reset cubes else we'll have an assertion error on next retry
            config._cubes = None
        except (
            OperationalError
        ) as exc:  # sqlite or psycopg2 driver, depending on db_driver
            print(f"OperationalError: {exc}")
            sys.exit(1)
        login, pwd = manager_userpasswd()


# repository specific command handlers ########################################


class RepositoryCreateHandler(CommandHandler):
    cmdname = "create"
    cfgname = "repository"

    def bootstrap(self, cubes, automatic=False, inputlevel=0):
        """create an instance by copying files from the given cube and by asking
        information necessary to build required configuration files
        """
        config = self.config
        if not automatic:
            print(underline_title("Configuring the repository"))
            config.input_config("email", inputlevel)
            print("\n" + underline_title("Configuring the sources"))
        # hack to make Method('default_instance_id') usable in db option defs
        # (in native.py)
        sconfig = SourceConfiguration(config, options=SOURCE_TYPES["native"].options)
        if not automatic:
            sconfig.input_config(inputlevel=inputlevel)
            print()
        sourcescfg = {"system": sconfig}
        if automatic:
            # XXX modify a copy
            password = generate_password()
            print(f"-> set administrator account to admin / {password}")
            USER_OPTIONS[1][1]["default"] = password
            sconfig = Configuration(options=USER_OPTIONS)
        else:
            sconfig = Configuration(options=USER_OPTIONS)
            sconfig.input_config(inputlevel=inputlevel)
        sourcescfg["admin"] = sconfig
        config.write_sources_file(sourcescfg)
        # remember selected cubes for later initialization of the database
        config.write_bootstrap_cubes_file(cubes)

    def postcreate(self, automatic=False, inputlevel=0):
        if automatic:
            CWCTL.run(["db-create", "--automatic", self.config.appid])
        elif ASK.confirm("Run db-create to create the system database ?"):
            CWCTL.run(
                ["db-create", "--config-level", str(inputlevel), self.config.appid]
            )
        else:
            print(
                "-> nevermind, you can do it later with "
                '"cubicweb-ctl db-create %s".' % self.config.appid
            )


@contextmanager
def db_transaction(source, privilege):
    """Open a transaction to the instance database"""
    cnx = source_cnx(source, special_privs=privilege)
    cursor = cnx.cursor()
    try:
        yield cursor
    except Exception:
        cnx.rollback()
        cnx.close()
        raise
    else:
        cnx.commit()
        cnx.close()


@contextmanager
def db_sys_transaction(source, privilege):
    """Open a transaction to the system database"""
    cnx = _db_sys_cnx(source, privilege)
    cursor = cnx.cursor()
    try:
        yield cursor
    except Exception:
        cnx.rollback()
        cnx.close()
        raise
    else:
        cnx.commit()
        cnx.close()


class RepositoryDeleteHandler(CommandHandler):
    cmdname = "delete"
    cfgname = "repository"

    def _drop_namespace(self, source):
        db_namespace = source.get("db-namespace")
        with db_transaction(source, privilege="DROP SCHEMA") as cursor:
            helper = get_db_helper(source["db-driver"])
            helper.drop_schema(cursor, db_namespace)
            print(f"-> database schema {db_namespace} dropped")

    def _drop_database(self, source):
        if source["db-driver"] == "sqlite":
            print(f"deleting database file {source['db-name']}")
            os.unlink(source["db-name"])
            print(f"-> database {source['db-name']} dropped.")
        else:
            with db_sys_transaction(source, privilege="DROP DATABASE") as cursor:
                print(f"dropping database {source['db-name']}")
                cursor.execute(f"DROP DATABASE \"{source['db-name']}\"")
                print(f"-> database {source['db-name']} dropped.")

    def _drop_user(self, source):
        user = source["db-user"] or None
        if user is not None:
            with db_sys_transaction(source, privilege="DROP USER") as cursor:
                print(f"dropping user {user}")
                cursor.execute(f"DROP USER {user}")

    def _cleanup_steps(self, source):
        # 1/ delete namespace if used
        db_namespace = source.get("db-namespace")
        if db_namespace:
            yield (
                f'Delete database namespace "{db_namespace}"',
                self._drop_namespace,
                True,
            )
        # 2/ delete database
        yield (f"Delete database \"{source['db-name']}\"", self._drop_database, True)
        # 3/ delete user
        helper = get_db_helper(source["db-driver"])
        if source["db-user"] and helper.users_support:
            # XXX should check we are not connected as user
            yield (f"Delete user \"{source['db-user']}\"", self._drop_user, False)

    def cleanup(self):
        """remove instance's configuration and database"""
        source = self.config.system_source_config
        for msg, step, default in self._cleanup_steps(source):
            if ASK.confirm(msg, default_is_yes=default):
                try:
                    step(source)
                except Exception as exc:
                    print("ERROR", exc)
                    if ASK.confirm(
                        "An error occurred. Continue anyway?", default_is_yes=False
                    ):
                        continue
                    raise ExecutionError(str(exc))


# repository specific commands ################################################


def createdb(helper, source, dbcnx, cursor, **kwargs):
    if dbcnx.logged_user != source["db-user"]:
        helper.create_database(
            cursor,
            source["db-name"],
            source["db-user"],
            source["db-encoding"],
            **kwargs,
        )
    else:
        helper.create_database(
            cursor, source["db-name"], dbencoding=source["db-encoding"], **kwargs
        )


class CreateInstanceDBCommand(Command):
    """Create the system database of an instance (run after 'create').

    You will be prompted for a login / password to use to connect to
    the system database.  The given user should have almost all rights
    on the database (ie a super user on the DBMS allowed to create
    database, users, languages...).

    <instance>
      the identifier of the instance to initialize.
    """

    name = "db-create"
    arguments = "<instance>"
    min_args = max_args = 1
    options = (
        (
            "automatic",
            {
                "short": "a",
                "action": "store_true",
                "default": False,
                "help": (
                    "automatic mode: never ask and use default answer to every "
                    "question. this may require that your login match a database super "
                    "user (allowed to create database & all). If the database already "
                    "exists and --drop is not provided, this command does nothing."
                ),
            },
        ),
        (
            "config-level",
            {
                "short": "l",
                "type": "int",
                "metavar": "<level>",
                "default": 0,
                "help": (
                    "configuration level (0..2): 0 will ask for essential "
                    "configuration parameters only while 2 will ask for all parameters"
                ),
            },
        ),
        (
            "create-db",
            {
                "short": "c",
                "type": "yn",
                "metavar": "<y or n>",
                "default": True,
                "help": "create the database (yes by default)",
            },
        ),
        (
            "drop",
            {
                "short": "d",
                "type": "yn",
                "metavar": "<y or n>",
                "default": None,
                "help": "Delete the database before creation if it exists (asked by default)",
            },
        ),
    )

    def run(self, args):
        """run the command with its specific arguments"""
        check_options_consistency(self.config)
        automatic = self.get("automatic")
        drop_db = self.get("drop")
        appid = args.pop()
        config = CubicWebConfiguration.config_for(appid)
        source = config.system_source_config
        dbname = source["db-name"]
        driver = source["db-driver"]
        helper = get_db_helper(driver)

        def should_drop_db():
            """Return True if the database should be dropped.

            The logic is following:
                - if drop_db is set then respect the user choice (either True or False)
                - if drop_db is not set then drop only in non automatic mode and
                  the user confirm the deletion
            """
            if drop_db is not None:
                return drop_db
            if automatic:
                return False
            drop_db_question = f"Database {dbname} already exists. Drop it?"
            return ASK.confirm(drop_db_question)

        if driver == "sqlite":
            if os.path.exists(dbname) and should_drop_db():
                os.unlink(dbname)
        elif self.config.create_db:
            print("\n" + underline_title("Creating the system database"))
            # connect on the dbms system base to create our base
            dbcnx = _db_sys_cnx(
                source, "CREATE/DROP DATABASE and / or USER", interactive=not automatic
            )
            cursor = dbcnx.cursor()
            try:
                if helper.users_support:
                    user = source["db-user"]
                    if not helper.user_exists(cursor, user) and (
                        automatic
                        or ASK.confirm(f"Create db user {user} ?", default_is_yes=False)
                    ):
                        helper.create_user(source["db-user"], source.get("db-password"))
                        print(f"-> user {user} created.")
                if dbname in helper.list_databases(cursor):
                    if should_drop_db():
                        cursor.execute(f'DROP DATABASE "{dbname}"')
                    else:
                        print(
                            "The database %s already exists, but automatically dropping it "
                            "is currently forbidden. You may want to run "
                            '"cubicweb-ctl db-create --drop=y %s" to continue or '
                            '"cubicweb-ctl db-create --help" to get help.'
                            % (dbname, config.appid)
                        )
                        raise Exception("Not allowed to drop existing database.")
                createdb(helper, source, dbcnx, cursor)
                dbcnx.commit()
                print(f"-> database {dbname} created.")
            except BaseException:
                dbcnx.rollback()
                raise
        cnx = source_cnx(
            source, special_privs="CREATE LANGUAGE/SCHEMA", interactive=not automatic
        )
        cursor = cnx.cursor()
        helper.init_fti_extensions(cursor)
        namespace = source.get("db-namespace")
        if namespace and (
            automatic
            or ASK.confirm(f"Create schema {namespace} in database {dbname} ?")
        ):
            helper.create_schema(cursor, namespace)
        cnx.commit()
        # postgres specific stuff
        if driver == "postgres":
            # install plpgsql language
            langs = ("plpgsql",)
            for extlang in langs:
                if automatic or ASK.confirm(f"Create language {extlang} ?"):
                    try:
                        helper.create_language(cursor, extlang)
                    except Exception as exc:
                        print("-> ERROR:", exc)
                        print(
                            "-> could not create language %s, "
                            "some stored procedures might be unusable" % extlang
                        )
                        cnx.rollback()
                    else:
                        cnx.commit()
        print(
            "-> database for instance %s created and necessary extensions installed."
            % appid
        )
        print()
        if automatic:
            CWCTL.run(["db-init", "--automatic", "--config-level", "0", config.appid])
        elif ASK.confirm("Run db-init to initialize the system database ?"):
            CWCTL.run(
                [
                    "db-init",
                    "--config-level",
                    str(self.config.config_level),
                    config.appid,
                ]
            )
        else:
            print(
                "-> nevermind, you can do it later with "
                '"cubicweb-ctl db-init %s".' % config.appid
            )


class InitInstanceCommand(Command):
    """Initialize the system database of an instance (run after 'db-create').

    Notice this will be done using user specified in the sources files, so this
    user should have the create tables grant permissions on the database.

    <instance>
      the identifier of the instance to initialize.
    """

    name = "db-init"
    arguments = "<instance>"
    min_args = max_args = 1
    options = (
        (
            "automatic",
            {
                "short": "a",
                "action": "store_true",
                "default": False,
                "help": (
                    "automatic mode: never ask and use default answer to every "
                    "question."
                ),
            },
        ),
        (
            "config-level",
            {
                "short": "l",
                "type": "int",
                "default": 0,
                "help": (
                    "level threshold for questions asked when configuring "
                    "another source"
                ),
            },
        ),
        (
            "drop",
            {
                "short": "d",
                "action": "store_true",
                "default": False,
                "help": (
                    "insert drop statements to remove previously existant "
                    "tables, indexes... (no by default)"
                ),
            },
        ),
    )

    def run(self, args):
        check_options_consistency(self.config)
        print("\n" + underline_title("Initializing the system database"))
        from cubicweb.server import init_repository

        appid = args[0]
        config = CubicWebConfiguration.config_for(appid)
        try:
            system = config.system_source_config
            extra_args = system.get("db-extra-arguments")
            extra = extra_args and {"extra_args": extra_args} or {}
            get_connection(
                system["db-driver"],
                database=system["db-name"],
                host=system.get("db-host"),
                port=system.get("db-port"),
                user=system.get("db-user") or "",
                password=system.get("db-password") or "",
                schema=system.get("db-namespace"),
                **extra,
            )
        except Exception as ex:
            raise ConfigurationError(
                "You seem to have provided wrong connection information in "
                "the %s file. Resolve this first (error: %s)."
                % (config.sources_file(), str(ex).strip())
            )
        init_repository(config, drop=self.config.drop)
        if not self.config.automatic:
            while ASK.confirm("Enter another source ?", default_is_yes=False):
                CWCTL.run(
                    [
                        "source-add",
                        "--config-level",
                        str(self.config.config_level),
                        config.appid,
                    ]
                )


class AddSourceCommand(Command):
    """Add a data source to an instance.

    <instance>
      the identifier of the instance to initialize.
    """

    name = "source-add"
    arguments = "<instance>"
    min_args = max_args = 1
    options = (
        (
            "config-level",
            {
                "short": "l",
                "type": "int",
                "default": 1,
                "help": "level threshold for questions asked when configuring another source",
            },
        ),
    )

    def run(self, args):
        appid = args[0]
        config = CubicWebConfiguration.config_for(appid)
        repo, cnx = repo_cnx(config)
        repo.hm.call_hooks("server_maintenance", repo=repo)
        try:
            with cnx:
                used = set(
                    n for n, in cnx.execute("Any SN WHERE S is CWSource, S name SN")
                )
                cubes = repo.get_cubes()
                while True:
                    type = input(f"source type ({', '.join(sorted(SOURCE_TYPES))}): ")
                    if type not in SOURCE_TYPES:
                        print("-> unknown source type, use one of the available types.")
                        continue
                    sourcemodule = SOURCE_TYPES[type].module
                    if not sourcemodule.startswith("cubicweb."):
                        # module names look like cubes.mycube.themodule
                        sourcecube = SOURCE_TYPES[type].module.split(".", 2)[1]
                        # if the source adapter is coming from an external component,
                        # ensure it's specified in used cubes
                        if sourcecube not in cubes:
                            print(
                                "-> this source type require the %s cube which is "
                                "not used by the instance."
                            )
                            continue
                    break
                while True:
                    parser = input(
                        f"parser type ({', '.join(sorted(repo.vreg['parsers']))}): "
                    )
                    if parser in repo.vreg["parsers"]:
                        break
                    print(
                        "-> unknown parser identifier, use one of the available types."
                    )
                while True:
                    sourceuri = input(
                        "source identifier (a unique name used to "
                        "tell sources apart): "
                    ).strip()
                    if not sourceuri:
                        print("-> mandatory.")
                    else:
                        sourceuri = str(sourceuri, sys.stdin.encoding)
                        if sourceuri in used:
                            print("-> uri already used, choose another one.")
                        else:
                            break
                url = input("source URL (leave empty for none): ").strip()
                url = str(url) if url else None
                # XXX configurable inputlevel
                sconfig = ask_source_config(
                    config, type, inputlevel=self.config.config_level
                )
                cfgstr = str(generate_source_config(sconfig), sys.stdin.encoding)
                cnx.create_entity(
                    "CWSource",
                    name=sourceuri,
                    type=str(type),
                    config=cfgstr,
                    parser=str(parser),
                    url=str(url),
                )
                cnx.commit()
        finally:
            repo.hm.call_hooks("server_shutdown")


class GrantUserOnInstanceCommand(Command):
    """Grant a database user on a repository system database.

    <instance>
      the identifier of the instance
    <user>
      the database's user requiring grant access
    """

    name = "db-grant-user"
    arguments = "<instance> <user>"
    min_args = max_args = 2
    options = (
        (
            "set-owner",
            {
                "short": "o",
                "type": "yn",
                "metavar": "<yes or no>",
                "default": False,
                "help": "Set the user as tables owner if yes (no by default).",
            },
        ),
    )

    def run(self, args):
        """run the command with its specific arguments"""
        from cubicweb.server.sqlutils import sqlexec, sqlgrants

        appid, user = args
        config = CubicWebConfiguration.config_for(appid)
        source = config.system_source_config
        set_owner = self.config.set_owner
        cnx = source_cnx(source, special_privs="GRANT")
        cursor = cnx.cursor()
        schema = config.load_schema()
        try:
            sqlexec(
                sqlgrants(schema, source["db-driver"], user, set_owner=set_owner),
                cursor,
            )
        except Exception as ex:
            cnx.rollback()
            import traceback

            traceback.print_exc()
            print("-> an error occurred:", ex)
        else:
            cnx.commit()
            print(f"-> rights granted to {appid} on instance {user}.")


class ResetAdminPasswordCommand(Command):
    """Reset the administrator password.

    <instance>
      the identifier of the instance
    """

    name = "reset-admin-pwd"
    arguments = "<instance>"
    min_args = max_args = 1
    options = (
        (
            "password",
            {
                "short": "p",
                "type": "string",
                "metavar": "<new-password>",
                "default": None,
                "help": (
                    "Use this password instead of prompt for one.\n"
                    "/!\\ THIS IS AN INSECURE PRACTICE /!\\ \n"
                    "the password will appear in shell history"
                ),
            },
        ),
    )

    def run(self, args):
        """run the command with its specific arguments"""
        from cubicweb.server.utils import crypt_password, manager_userpasswd

        appid = args[0]
        config = CubicWebConfiguration.config_for(appid)
        sourcescfg = config.read_sources_file()
        try:
            adminlogin = sourcescfg["admin"]["login"]
        except KeyError:
            print("-> Error: could not get cubicweb administrator login.")
            sys.exit(1)
        cnx = source_cnx(sourcescfg["system"])
        driver = sourcescfg["system"]["db-driver"]
        dbhelper = get_db_helper(driver)
        cursor = cnx.cursor()
        # check admin exists
        cursor.execute(
            "SELECT * FROM cw_CWUser WHERE cw_login=%(l)s", {"l": adminlogin}
        )
        if not cursor.fetchall():
            print(
                "-> error: admin user %r specified in sources doesn't exist "
                "in the database" % adminlogin
            )
            print("   fix your sources file before running this command")
            cnx.close()
            sys.exit(1)
        if self.config.password is None:
            # ask for a new password
            msg = f"new password for {adminlogin}"
            _, pwd = manager_userpasswd(adminlogin, confirm=True, passwdmsg=msg)
        else:
            pwd = self.config.password
        try:
            cursor.execute(
                "UPDATE cw_CWUser SET cw_upassword=%(p)s WHERE cw_login=%(l)s",
                {"p": dbhelper.binary_value(crypt_password(pwd)), "l": adminlogin},
            )
            sconfig = Configuration(options=USER_OPTIONS)
            sconfig["login"] = adminlogin
            sconfig["password"] = pwd
            sourcescfg["admin"] = sconfig
            config.write_sources_file(sourcescfg)
        except Exception as ex:
            cnx.rollback()
            import traceback

            traceback.print_exc()
            print("-> an error occurred:", ex)
        else:
            cnx.commit()
            print("-> password reset, sources file regenerated.")
        cnx.close()


def _remote_dump(host, appid, output, sudo=False):
    # XXX generate unique/portable file name
    from datetime import date

    filename = f"{appid}-{date.today().strftime('%Y-%m-%d')}.tgz"
    dmpcmd = f"cubicweb-ctl db-dump -o /tmp/{filename} {appid}"
    if sudo:
        dmpcmd = f"sudo {dmpcmd}"
    dmpcmd = f'ssh -t {host} "{dmpcmd}"'
    print(dmpcmd)
    if os.system(dmpcmd):
        raise ExecutionError("Error while dumping the database")
    if output is None:
        output = filename
    cmd = f"scp {host}:/tmp/{filename} {output}"
    print(cmd)
    if os.system(cmd):
        raise ExecutionError(f"Error while retrieving the dump at /tmp/{filename}")
    rmcmd = f'ssh -t {host} "rm -f /tmp/{filename}"'
    print(rmcmd)
    if os.system(rmcmd) and not ASK.confirm(
        "An error occurred while deleting remote dump at /tmp/%s. "
        "Continue anyway?" % filename
    ):
        raise ExecutionError(f"Error while deleting remote dump at /tmp/{filename}")


def _local_dump(appid, output, format="native"):
    config = CubicWebConfiguration.config_for(appid)
    config.quick_start = True
    mih = config.migration_handler(verbosity=1)
    backupfile = mih.backup_database(output, askconfirm=False, format=format)
    mih.shutdown()
    return backupfile


def _get_s3_client(url, bucket, **kwargs):
    try:
        from minio import Minio
    except ImportError:
        raise ExecutionError(
            "Minio module is missing, s3 dump cannot be used. Install it with pip install .[s3]"
        )

    if not url:
        print("dump-s3-endpoint-url is not defined in all-in-one.conf")
        return

    # open s3 connection
    client = Minio(url, **kwargs)

    if not bucket:
        print("dump-s3-bucket-name is not defined in all-in-one.conf")
        return

    if not client.bucket_exists(bucket):
        print(f"dump-s3-bucket-name {bucket} do not exists")
        return

    return client


def _s3_dump(appid, output, clean, format="native"):
    config = CubicWebConfiguration.config_for(appid)
    s3_bucket_name = config.get("dump-s3-bucket-name")

    # open s3 connection
    client = _get_s3_client(
        config.get("dump-s3-endpoint-url"),
        s3_bucket_name,
        access_key=config.get("dump-s3-access-key"),
        secret_key=config.get("dump-s3-secret-key"),
        region=config.get("dump-s3-region"),
        secure=config.get("dump-s3-secure"),
        cert_check=config.get("dump-s3-cert-check"),
    )

    # create backup in tmp file
    backupfile = _local_dump(appid, None, format=format)
    backupname = os.path.basename(backupfile)
    backuppath = output if output else backupname

    # push to s3
    client.fput_object(s3_bucket_name, backuppath, backupfile)
    print(f"-> backup file {backupname} pushed to S3 bucket {s3_bucket_name}")

    # clean
    if clean or ASK.confirm(f"Delete local backup {backupname}?"):
        os.remove(backupfile)
        print(f"-> {backupname} has been deleted successfully")


def _local_restore(appid, backupfile, drop, format="native"):
    config = CubicWebConfiguration.config_for(appid)
    config.verbosity = 1  # else we won't be asked for confirmation on problems
    config.quick_start = True
    mih = config.migration_handler(connect=False, verbosity=1)
    mih.restore_database(backupfile, drop, askconfirm=False, format=format)
    repo = mih.repo
    # version of the database
    dbversions = repo.get_versions()
    mih.shutdown()
    if not dbversions:
        print(
            "bad or missing version information in the database, don't upgrade file system"
        )
        return
    # version of installed software
    eversion = dbversions["cubicweb"]
    status = instance_status(config, eversion, dbversions)
    # * database version > installed software
    if status == "needsoftupgrade":
        print(
            "** The database of %s is more recent than the installed software!"
            % config.appid
        )
        print(
            "** Upgrade your software, then migrate the database by running the command"
        )
        print(f"** 'cubicweb-ctl upgrade {config.appid}'")
        return
    # * database version < installed software, an upgrade will be necessary
    #   anyway, just rewrite vc.conf and warn user he has to upgrade
    elif status == "needapplupgrade":
        print(
            f"** The database of {config.appid} is older than the installed software."
        )
        print("** Migrate the database by running the command")
        print(f"** 'cubicweb-ctl upgrade {config.appid}'")
        return
    # * database version = installed software, database version = instance fs version
    #   ok!


def instance_status(config, cubicwebapplversion, vcconf):
    cubicwebversion = config.cubicweb_version()
    if cubicwebapplversion > cubicwebversion:
        return "needsoftupgrade"
    if cubicwebapplversion < cubicwebversion:
        return "needapplupgrade"
    for cube in config.cubes():
        try:
            softversion = config.cube_version(cube)
        except ConfigurationError:
            print(
                "-> Error: no cube version information for %s, "
                "please check that the cube is installed." % cube
            )
            continue
        try:
            applversion = vcconf[cube]
        except KeyError:
            print(
                "-> Error: no cube version information for %s in version configuration."
                % cube
            )
            continue
        if softversion == applversion:
            continue
        if softversion > applversion:
            return "needsoftupgrade"
        elif softversion < applversion:
            return "needapplupgrade"
    return None


class DBDumpCommand(Command):
    """Backup the system database of an instance.

    <instance>
      the identifier of the instance to backup
      format [[user@]host:]appname
    """

    name = "db-dump"
    arguments = "<instance>"
    min_args = max_args = 1
    options = (
        (
            "output",
            {
                "short": "o",
                "type": "string",
                "metavar": "<file>",
                "default": None,
                "help": "Specify the backup file where the backup will be stored.",
            },
        ),
        (
            "s3",
            {
                "action": "store_true",
                "default": False,
                "help": "Push created local dump to S3 bucket.",
            },
        ),
        (
            "s3-clean",
            {
                "action": "store_true",
                "default": False,
                "help": "Delete local backup after created (and pushed to S3)",
            },
        ),
        (
            "sudo",
            {
                "short": "s",
                "action": "store_true",
                "default": False,
                "help": "Use sudo on the remote host.",
            },
        ),
        (
            "format",
            {
                "short": "f",
                "default": "native",
                "type": "choice",
                "choices": ("native", "portable"),
                "help": (
                    '"native" format uses db backend utilities to dump the database. '
                    '"portable" format uses a database independent format'
                ),
            },
        ),
    )

    def run(self, args):
        appid = args[0]
        if self.config.s3:
            _s3_dump(
                appid,
                self.config.output,
                self.config.s3_clean,
                format=self.config.format,
            )
        elif ":" in appid:
            host, appid = appid.split(":")
            _remote_dump(host, appid, self.config.output, self.config.sudo)
        else:
            _local_dump(appid, self.config.output, format=self.config.format)


class DBRestoreCommand(Command):
    """Restore the system database of an instance.

    <instance>
      the identifier of the instance to restore
    """

    name = "db-restore"
    arguments = "<instance> <backupfile>"
    min_args = 1
    max_args = 2

    options = (
        (
            "no-drop",
            {
                "short": "n",
                "action": "store_true",
                "default": False,
                "help": (
                    "for some reason the database doesn't exist and so "
                    "should not be dropped."
                ),
            },
        ),
        (
            "s3",
            {
                "action": "store_true",
                "default": False,
                "help": "Pull dump from S3 bucket.",
            },
        ),
        (
            "latest",
            {
                "action": "store_true",
                "default": False,
                "help": "Restore latest backup file of directory or s3 bucket.",
            },
        ),
        (
            "format",
            {
                "short": "f",
                "default": "native",
                "type": "choice",
                "choices": ("native", "portable"),
                "help": "the format used when dumping the database",
            },
        ),
    )

    def _get_latest_filename_from_s3_bucket(self, client, bucket_name):
        files = client.list_objects(bucket_name)
        latest_file = None
        for file in files:
            if not latest_file or file.last_modified > latest_file.last_modified:
                latest_file = file

        if not latest_file:
            raise ExecutionError(f"No file found in S3 bucket {bucket_name}")

        return latest_file.object_name

    def _get_latest_filename_from_path(self, directory):
        files = glob(f"{directory}/*")
        if not files:
            raise ExecutionError(f"No file found in {directory}")
        return max(files, key=os.path.getctime)

    def _get_dump_from_s3(self, appid, filepath, get_latest=False):
        # fget_object(bucket_name, object_name, file_path, request_headers=None, ssec=None, version_id=None, extra_query_params=None, tmp_file_path=None)
        config = CubicWebConfiguration.config_for(appid)
        s3_bucket_name = config.get("dump-s3-bucket-name")

        # open s3 connection
        client = _get_s3_client(
            config.get("dump-s3-endpoint-url"),
            s3_bucket_name,
            access_key=config.get("dump-s3-access-key"),
            secret_key=config.get("dump-s3-secret-key"),
            region=config.get("dump-s3-region"),
            secure=config.get("dump-s3-secure"),
            cert_check=config.get("dump-s3-cert-check"),
        )

        if get_latest:
            filepath = self._get_latest_filename_from_s3_bucket(client, s3_bucket_name)

        tmpfile = NamedTemporaryFile(suffix=f".{filepath.split('.', maxsplit=1)[-1]}")

        # download file to tmp file
        client.fget_object(s3_bucket_name, filepath, tmpfile.name)
        print(f"-> {filepath} has been downloaded as {tmpfile.name}")

        return tmpfile

    def run(self, args):
        appid = args[0]
        backupfile = None
        if len(args) == 2:
            backupfile = args[1]

        if self.config.format == "portable":
            # we need to ensure a DB exist before restoring from portable format
            if not self.config.no_drop:
                try:
                    CWCTL.run(["db-create", "--automatic", appid])
                except SystemExit as exc:
                    # continue if the command exited with status 0 (success)
                    if exc.code:
                        raise

        if self.config.s3:
            tmpfile = self._get_dump_from_s3(appid, backupfile, self.config.latest)
            backupfile = tmpfile.name

        # if --latest, backupfile must be a directory path.
        # get latest file in this directory
        if not self.config.s3 and self.config.latest:
            backupfile = self._get_latest_filename_from_path(backupfile)

        _local_restore(
            appid, backupfile, drop=not self.config.no_drop, format=self.config.format
        )

        # clean
        if self.config.s3:
            print(f"-> delete {tmpfile.name}")
            tmpfile.close()

        if self.config.format == "portable":
            try:
                CWCTL.run(["db-rebuild-fti", appid])
            except SystemExit as exc:
                if exc.code:
                    raise


class DBCopyCommand(Command):
    """Copy the system database of an instance (backup and restore).

    <src-instance>
      the identifier of the instance to backup
      format [[user@]host:]appname

    <dest-instance>
      the identifier of the instance to restore
    """

    name = "db-copy"
    arguments = "<src-instance> <dest-instance>"
    min_args = max_args = 2
    options = (
        (
            "no-drop",
            {
                "short": "n",
                "action": "store_true",
                "default": False,
                "help": (
                    "For some reason the database doesn't exist and so "
                    "should not be dropped."
                ),
            },
        ),
        (
            "keep-dump",
            {
                "short": "k",
                "action": "store_true",
                "default": False,
                "help": (
                    "Specify that the dump file should not be automatically removed."
                ),
            },
        ),
        (
            "sudo",
            {
                "short": "s",
                "action": "store_true",
                "default": False,
                "help": "Use sudo on the remote host.",
            },
        ),
        (
            "format",
            {
                "short": "f",
                "default": "native",
                "type": "choice",
                "choices": ("native", "portable"),
                "help": (
                    '"native" format uses db backend utilities to dump the database. '
                    '"portable" format uses a database independent format'
                ),
            },
        ),
    )

    def run(self, args):
        import tempfile

        srcappid, destappid = args
        fd, output = tempfile.mkstemp()
        os.close(fd)
        if ":" in srcappid:
            host, srcappid = srcappid.split(":")
            _remote_dump(host, srcappid, output, self.config.sudo)
        else:
            _local_dump(srcappid, output, format=self.config.format)
        _local_restore(destappid, output, not self.config.no_drop, self.config.format)
        if self.config.keep_dump:
            print("-> you can get the dump file at", output)
        else:
            os.remove(output)


class CheckRepositoryCommand(Command):
    """Check integrity of the system database of an instance.

    <instance>
      the identifier of the instance to check
    """

    name = "db-check"
    arguments = "<instance>"
    min_args = max_args = 1
    options = (
        (
            "checks",
            {
                "short": "c",
                "type": "csv",
                "metavar": "<check list>",
                "default": sorted(checkintegrity._CHECKERS),
                "help": (
                    "Comma separated list of check to run. By default run all checks."
                ),
            },
        ),
        (
            "autofix",
            {
                "short": "a",
                "type": "yn",
                "metavar": "<yes or no>",
                "default": False,
                "help": 'Automatically correct integrity problems if this option \
is set to "y" or "yes", else only display them',
            },
        ),
        (
            "reindex",
            {
                "short": "r",
                "type": "yn",
                "metavar": "<yes or no>",
                "default": False,
                "help": 're-indexes the database for full text search if this \
option is set to "y" or "yes" (may be long for large database).',
            },
        ),
        (
            "force",
            {
                "short": "f",
                "action": "store_true",
                "default": False,
                "help": "don't check instance is up to date.",
            },
        ),
    )

    def run(self, args):
        appid = args[0]
        config = CubicWebConfiguration.config_for(appid)
        config.repairing = self.config.force
        repo, _cnx = repo_cnx(config)
        with repo.internal_cnx() as cnx:
            checkintegrity.check(
                repo, cnx, self.config.checks, self.config.reindex, self.config.autofix
            )


class DBIndexSanityCheckCommand(Command):
    """Check database indices of an instance.

    <instance>
      identifier of the instance to check
    """

    arguments = "<instance>"
    name = "db-check-index"
    min_args = 1

    def run(self, args):
        config = CubicWebConfiguration.config_for(args[0])
        repo, cnx = repo_cnx(config)
        with cnx:
            status = checkintegrity.check_indexes(cnx)
        sys.exit(status)


class DBCheckUnusedIndexCommand(Command):
    """Check all indexes in database and return unused ones since the last
    statistic reset (pg_stat_reset()).

    <instance>
      identifier of the instance to check
    """

    arguments = "<instance>"
    name = "db-check-unused-index"
    min_args = 1
    max_args = 1
    options = (
        (
            "min_usage",
            {
                "short": "m",
                "type": "int",
                "default": 0,
                "help": "The minimum usage count to consider an index as used.",
            },
        ),
    )

    def run(self, args):
        config = CubicWebConfiguration.config_for(args[0])
        repo, cnx = repo_cnx(config)
        with cnx:
            status = check_unused_index(cnx, self.config.min_usage)
        sys.exit(status)


class RebuildFTICommand(Command):
    """Rebuild the full-text index of the system database of an instance.

    <instance> [etype(s)]
      the identifier of the instance to rebuild

    If no etype is specified, cubicweb will reindex everything, otherwise
    only specified etypes will be considered.
    """

    name = "db-rebuild-fti"
    arguments = "<instance>"
    min_args = 1

    def run(self, args):
        from cubicweb.server.checkintegrity import reindex_entities

        appid = args.pop(0)
        etypes = args or None
        config = CubicWebConfiguration.config_for(appid)
        repo, cnx = repo_cnx(config)
        with cnx:
            reindex_entities(repo.schema, cnx, etypes=etypes)
            cnx.commit()


class RepositorySchedulerCommand(Command):
    """Start a repository tasks scheduler.

    Initialize a repository and start its tasks scheduler that would run
    registered "looping tasks".

    This is maintenance command that should be kept running along with a web
    instance of a CubicWeb WSGI application (e.g. embeded into a Pyramid
    application).

    <instance>
      the identifier of the instance
    """

    name = "scheduler"
    arguments = "<instance>"
    min_args = max_args = 1
    options = (
        (
            "loglevel",
            {
                "short": "l",
                "type": "choice",
                "metavar": "<log level>",
                "default": "info",
                "choices": ("debug", "info", "warning", "error"),
            },
        ),
    )

    def run(self, args):
        from cubicweb.cwctl import init_cmdline_log_threshold
        from cubicweb.server.repository import Repository

        config = CubicWebConfiguration.config_for(args[0])
        # Log to stdout, since the this command runs in the foreground.
        config.global_set_option("log-file", None)
        init_cmdline_log_threshold(config, self["loglevel"])
        repo = Repository(config, sched.scheduler())
        repo.bootstrap()
        try:
            repo.run_scheduler()
        finally:
            repo.shutdown()


class SynchronizeSourceCommand(Command):
    """Force sources synchronization.

    <instance>
      the identifier of the instance
    <source>
      names of the sources to synchronize, if empty all sources will be synced.
    """

    name = "source-sync"
    arguments = "<instance> [<source> <source> ...]"
    min_args = 1
    options = (
        (
            "loglevel",
            {
                "short": "l",
                "type": "choice",
                "metavar": "<log level>",
                "default": "info",
                "choices": ("debug", "info", "warning", "error"),
            },
        ),
        (
            "force",
            {
                "short": "f",
                "action": "store_true",
                "default": False,
                "help": (
                    "force source synchronization (ignore synchronization interval)"
                ),
            },
        ),
    )

    def run(self, args):
        from cubicweb import repoapi
        from cubicweb.cwctl import init_cmdline_log_threshold

        config = CubicWebConfiguration.config_for(args[0])
        config.global_set_option("log-file", None)
        config.log_format = "%(levelname)s %(name)s: %(message)s"
        init_cmdline_log_threshold(config, self["loglevel"])
        repo = repoapi.get_repository(config=config)
        repo.hm.call_hooks("server_maintenance", repo=repo)
        errors = False
        with repo.internal_cnx() as cnx:
            sources = []
            if len(args) >= 2:
                for name in args[1:]:
                    try:
                        source = repo.source_by_uri(name)
                    except ValueError:
                        cnx.error(f"no source named {name!r}")
                        errors = True
                    else:
                        sources.append(source)
            else:
                for uri, source in repo.sources_by_uri.items():
                    if (
                        uri != "system"
                        and repo.config.source_enabled(source)
                        and source.config["synchronize"]
                    ):
                        sources.append(source)

            for source in sources:
                try:
                    stats = source.pull_data(
                        cnx, force=self["force"], raise_on_error=True
                    )
                except Exception:
                    cnx.exception("while trying to update source %s", source)
                    errors = True
                else:
                    for key, val in stats.items():
                        if val:
                            print(key, ":", val)

        if errors:
            raise ExecutionError("All sources where not synced")


def permissionshandler(relation, perms):
    from yams.buildobjs import DEFAULT_ATTRPERMS
    from cubicweb.schema import (
        PUB_SYSTEM_ENTITY_PERMS,
        PUB_SYSTEM_REL_PERMS,
        PUB_SYSTEM_ATTR_PERMS,
        RO_REL_PERMS,
        RO_ATTR_PERMS,
    )

    defaultrelperms = (
        DEFAULT_ATTRPERMS,
        PUB_SYSTEM_REL_PERMS,
        PUB_SYSTEM_ATTR_PERMS,
        RO_REL_PERMS,
        RO_ATTR_PERMS,
    )
    defaulteperms = (PUB_SYSTEM_ENTITY_PERMS,)
    # canonicalize vs str/unicode
    for p in ("read", "add", "update", "delete"):
        rule = perms.get(p)
        if rule:
            perms[p] = tuple(rule)
    return perms, perms in defaultrelperms or perms in defaulteperms


class SchemaDiffCommand(Command):
    """Generate a diff between schema and fsschema description.

    <instance>
      the identifier of the instance
    <diff-tool>
      the name of the diff tool to compare the two generated files.
    """

    name = "schema-diff"
    arguments = "<instance> <diff-tool>"
    min_args = max_args = 2

    def run(self, args):
        from yams.diff import schema_diff
        from cubicweb import repoapi

        appid = args.pop(0)
        diff_tool = args.pop(0)
        config = CubicWebConfiguration.config_for(appid)
        config.repairing = True
        repo = repoapi.get_repository(config=config)
        fsschema = config.load_schema(expand_cubes=True)
        schema_diff(
            fsschema, repo.schema, permissionshandler, diff_tool, ignore=("eid",)
        )


for cmdclass in (
    CreateInstanceDBCommand,
    InitInstanceCommand,
    GrantUserOnInstanceCommand,
    ResetAdminPasswordCommand,
    DBDumpCommand,
    DBRestoreCommand,
    DBCopyCommand,
    DBIndexSanityCheckCommand,
    DBCheckUnusedIndexCommand,
    AddSourceCommand,
    CheckRepositoryCommand,
    RebuildFTICommand,
    SynchronizeSourceCommand,
    SchemaDiffCommand,
    RepositorySchedulerCommand,
):
    CWCTL.register(cmdclass)

# extend configure command to set options in sources config file ###############

db_options = (
    (
        "db",
        {
            "short": "d",
            "type": "named",
            "metavar": "[section1.]key1:value1,[section2.]key2:value2",
            "default": None,
            "help": (
                """set <key> in <section> to <value> in "source" configuration file. If
<section> is not specified, it defaults to "system".

Beware that changing admin.login or admin.password using this command
will NOT update the database with new admin credentials.  Use the
reset-admin-pwd command instead.
"""
            ),
        },
    ),
)

ConfigureInstanceCommand.options = merge_options(
    ConfigureInstanceCommand.options + db_options
)

configure_instance = ConfigureInstanceCommand.configure_instance


def configure_instance2(self, appid):
    configure_instance(self, appid)
    if self.config.db is not None:
        appcfg = CubicWebConfiguration.config_for(appid)
        srccfg = appcfg.read_sources_file()
        for key, value in self.config.db.items():
            if "." in key:
                section, key = key.split(".", 1)
            else:
                section = "system"
            try:
                srccfg[section][key] = value
            except KeyError:
                raise ConfigurationError(
                    'unknown configuration key "%s" in section "%s" for source'
                    % (key, section)
                )
        admcfg = Configuration(options=USER_OPTIONS)
        admcfg["login"] = srccfg["admin"]["login"]
        admcfg["password"] = srccfg["admin"]["password"]
        srccfg["admin"] = admcfg
        appcfg.write_sources_file(srccfg)


ConfigureInstanceCommand.configure_instance = configure_instance2
