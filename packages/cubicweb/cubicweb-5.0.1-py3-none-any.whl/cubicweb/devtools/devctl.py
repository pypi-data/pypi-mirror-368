# copyright 2003-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""additional cubicweb-ctl commands and command handlers for cubicweb and
cubicweb's cubes development
"""
# *ctl module should limit the number of import to be imported as quickly as
# possible (for cubicweb-ctl reactivity, necessary for instance for usable bash
# completion). So import locally in command helpers.

import json
import shutil
import sys
import tempfile
from urllib.request import urlopen
from urllib.error import URLError
from datetime import datetime, date
from os import getcwd, mkdir, chdir, path as osp

import pkg_resources
from logilab.common import STD_BLACKLIST
from logilab.common.fileutils import ensure_fs_mode
from logilab.common.modutils import clean_sys_modules
from logilab.common.shellutils import find

from cubicweb import CW_SOFTWARE_ROOT as BASEDIR, BadCommandUsage, ExecutionError
from cubicweb.__pkginfo__ import version as cubicwebversion
from cubicweb.cwconfig import CubicWebConfiguration
from cubicweb.cwctl import CWCTL
from cubicweb.i18n import execute2
from cubicweb.schema import CubicWebSchema
from cubicweb.schema_exporters import JSONSchemaExporter, TypescriptSchemaExporter
from cubicweb.toolsutils import SKEL_EXCLUDE, Command, copy_skeleton, underline_title

__docformat__ = "restructuredtext en"


STD_BLACKLIST = set(STD_BLACKLIST)
STD_BLACKLIST.add(".tox")
STD_BLACKLIST.add("test")
STD_BLACKLIST.add("node_modules")


class DevConfiguration(CubicWebConfiguration):
    """dummy config to get full library schema and appobjects for
    a cube or for cubicweb (without a home)
    """

    creating = True
    cleanup_unused_appobjects = False

    def __init__(self, *cubes):
        super(DevConfiguration, self).__init__(cubes and cubes[0] or None)
        if cubes:
            self._cubes = self.reorder_cubes(
                self.expand_cubes(cubes, with_recommends=True)
            )
            self.load_site_cubicweb()
        else:
            self._cubes = ()

    @property
    def apphome(self):
        return None

    def available_languages(self):
        return self.cw_languages()

    def main_config_file(self):
        return None

    def init_log(self):
        pass

    def load_configuration(self, **kw):
        pass

    def default_log_file(self):
        return None

    def default_stats_file(self):
        return None


def generate_schema_pot(w, cubedir=None):
    """generate a pot file with schema specific i18n messages

    notice that relation definitions description and static vocabulary
    should be marked using '_' and extracted using xgettext
    """
    from cubicweb.cwvreg import CWRegistryStore

    if cubedir:
        cube = osp.split(cubedir)[-1]
        if cube.startswith("cubicweb_"):
            cube = cube[len("cubicweb_") :]
        # XXX Cube `web` must be installed in order for i18ncube to work as we
        # use appobjects registered by it in _generate_schema_pot.
        config = DevConfiguration(cube)
        depcubes = list(config._cubes)
        depcubes.remove(cube)
        libconfig = DevConfiguration(*depcubes)
    else:
        config = DevConfiguration()
        cube = libconfig = None
    clean_sys_modules(config.appobjects_modnames())
    schema = config.load_schema(remove_unused_relation_types=False)
    vreg = CWRegistryStore(config)
    # set_schema triggers objects registrations
    vreg.set_schema(schema)
    w(DEFAULT_POT_HEAD)
    _generate_schema_pot(w, vreg, schema, libconfig=libconfig)


def _generate_schema_pot(w, vreg, schema, libconfig=None):
    from cubicweb.i18n import add_msg
    from cubicweb.schema import NO_I18NCONTEXT, CONSTRAINTS

    w(
        "# schema pot file, generated on %s\n"
        % datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    )
    w("# \n")
    w("# singular and plural forms for each entity type\n")
    w("\n")
    vregdone = set()
    if libconfig is not None:
        # processing a cube, libconfig being a config with all its dependencies
        # (cubicweb incl.)
        from cubicweb.cwvreg import CWRegistryStore

        libschema = libconfig.load_schema(remove_unused_relation_types=False)
        clean_sys_modules(libconfig.appobjects_modnames())
        libvreg = CWRegistryStore(libconfig)
        libvreg.set_schema(libschema)  # trigger objects registration
        # prefill vregdone set
        list(_iter_vreg_objids(libvreg, vregdone))

    else:
        # processing cubicweb itself
        libschema = {}
        for cstrtype in CONSTRAINTS:
            add_msg(w, cstrtype)

    done = set()
    for eschema in sorted(schema.entities()):
        if eschema.type in libschema:
            done.add(eschema.description)
    for eschema in sorted(schema.entities()):
        etype = eschema.type
        if etype not in libschema:
            add_msg(w, etype)
            add_msg(w, f"{etype}_plural")
            if not eschema.final:
                add_msg(w, f"This {etype}:")
                add_msg(w, f"New {etype}")
                add_msg(w, f"add a {etype}")  # AddNewAction
                if libconfig is not None:  # processing a cube
                    # As of 3.20.3 we no longer use it, but keeping this string
                    # allows developers to run i18ncube with new cubicweb and still
                    # have the right translations at runtime for older versions
                    add_msg(w, f"This {etype}")
            if eschema.description and eschema.description not in done:
                done.add(eschema.description)
                add_msg(w, eschema.description)
        if eschema.final:
            continue
    w("# subject and object forms for each relation type\n")
    w("# (no object form for final or symmetric relation types)\n")
    w("\n")
    for rschema in sorted(schema.relations()):
        if rschema.type in libschema:
            done.add(rschema.type)
            done.add(rschema.description)
    for rschema in sorted(schema.relations()):
        rtype = rschema.type
        if rtype not in libschema:
            # bw compat, necessary until all translation of relation are done
            # properly...
            add_msg(w, rtype)
            done.add(rtype)
            if rschema.description and rschema.description not in done:
                add_msg(w, rschema.description)
            done.add(rschema.description)
            librschema = None
        else:
            librschema = libschema.relation_schema_for(rtype)
        # add context information only for non-metadata rtypes
        if rschema not in NO_I18NCONTEXT:
            libsubjects = librschema and librschema.subjects() or ()
            for subjschema in rschema.subjects():
                if subjschema not in libsubjects:
                    add_msg(w, rtype, subjschema.type)
        if not (rschema.final or rschema.symmetric):
            if rschema not in NO_I18NCONTEXT:
                libobjects = librschema and librschema.objects() or ()
                for objschema in rschema.objects():
                    if objschema not in libobjects:
                        add_msg(w, f"{rtype}_object", objschema.type)
            if rtype not in libschema:
                # bw compat, necessary until all translation of relation are
                # done properly...
                add_msg(w, f"{rtype}_object")
        for rdef in rschema.relation_definitions.values():
            if not rdef.description or rdef.description in done:
                continue
            if (
                librschema is None
                or (rdef.subject, rdef.object) not in librschema.relation_definitions
                or librschema.relation_definitions[
                    (rdef.subject, rdef.object)
                ].description
                != rdef.description
            ):
                add_msg(w, rdef.description)
            done.add(rdef.description)
    for objid in _iter_vreg_objids(vreg, vregdone):
        add_msg(w, f"{objid}_description")
        add_msg(w, objid)


def _iter_vreg_objids(vreg, done):
    for reg, objdict in vreg.items():
        if reg in ("boxes", "contentnavigation"):
            continue
        for objects in objdict.values():
            for obj in objects:
                objid = f"{reg}_{obj.__regid__}"
                if objid in done:
                    break
                pdefs = getattr(obj, "cw_property_defs", {})
                if pdefs:
                    yield objid
                    done.add(objid)
                    break


DEFAULT_POT_HEAD = (
    r"""msgid ""
msgstr ""
"Project-Id-Version: cubicweb %s\n"
"PO-Revision-Date: 2008-03-28 18:14+0100\n"
"Last-Translator: Logilab Team <contact@logilab.fr>\n"
"Language-Team: fr <contact@logilab.fr>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: cubicweb-devtools\n"
"Plural-Forms: nplurals=2; plural=(n > 1);\n"

"""
    % cubicwebversion
)


class UpdateCubicWebCatalogCommand(Command):
    """Update i18n catalogs for cubicweb library.

    It will regenerate cubicweb/i18n/xx.po files. You'll have then to edit those
    files to add translations of newly added messages.
    """

    name = "i18ncubicweb"
    min_args = max_args = 0

    def run(self, args):
        """run the command with its specific arguments"""
        import shutil
        import tempfile
        import yams
        from logilab.common.fileutils import ensure_fs_mode
        from logilab.common.shellutils import globfind, rm
        from logilab.common.modutils import get_module_files
        from cubicweb.i18n import execute2

        tempdir = tempfile.mkdtemp(prefix="cw-")
        cwi18ndir = CubicWebConfiguration.i18n_lib_dir()
        print("-> extract messages:", end=" ")
        print("schema", end=" ")
        schemapot = osp.join(tempdir, "schema.pot")
        potfiles = [schemapot]
        potfiles.append(schemapot)
        # explicit close necessary else the file may not be yet flushed when
        # we'll using it below
        schemapotstream = open(schemapot, "w")
        generate_schema_pot(schemapotstream.write, cubedir=None)
        schemapotstream.close()
        print("-> generate .pot files.")
        pyfiles = get_module_files(BASEDIR)
        pyfiles += globfind(osp.join(BASEDIR, "misc", "migration"), "*.py")
        pyfiles += globfind(osp.join(BASEDIR, "pyramid"), "*.py")
        schemafiles = globfind(osp.join(BASEDIR, "schemas"), "*.py")
        for id, files, lang in [
            ("pycubicweb", pyfiles, None),
            ("schemadescr", schemafiles, None),
            ("yams", get_module_files(yams.__path__[0]), None),
        ]:
            potfile = osp.join(tempdir, f"{id}.pot")
            cmd = [
                "xgettext",
                "--from-code=UTF-8",
                "--no-location",
                "--omit-header",
                "-k_",
            ]
            if lang is not None:
                cmd.extend(["-L", lang])
            cmd.extend(["-o", potfile])
            cmd.extend(files)
            execute2(cmd)
            if osp.exists(potfile):
                potfiles.append(potfile)
            else:
                print(f"-> WARNING: {potfile} file was not generated")
        print(f"-> merging {len(potfiles)} .pot files")
        cubicwebpot = osp.join(tempdir, "cubicweb.pot")
        cmd = ["msgcat", "-o", cubicwebpot] + potfiles
        execute2(cmd)
        print("-> merging main pot file with existing translations.")
        chdir(cwi18ndir)
        toedit = []
        for lang in CubicWebConfiguration.cw_languages():
            target = f"{lang}.po"
            cmd = [
                "msgmerge",
                "-N",
                "--sort-output",
                "-o",
                target + "new",
                target,
                cubicwebpot,
            ]
            execute2(cmd)
            ensure_fs_mode(target)
            shutil.move(f"{target}new", target)
            toedit.append(osp.abspath(target))
        # cleanup
        rm(tempdir)
        # instructions pour la suite
        print("-> regenerated CubicWeb's .po catalogs.")
        print("\nYou can now edit the following files:")
        print("* " + "\n* ".join(toedit))
        print('when you are done, run "cubicweb-ctl i18ncube yourcube".')


class UpdateCubeCatalogCommand(Command):
    """Update i18n catalogs for cubes. If no cube is specified, update
    catalogs of all registered cubes.
    """

    name = "i18ncube"
    arguments = "[<cube>...]"

    def run(self, args):
        """run the command with its specific arguments"""
        if args:
            cubes = [DevConfiguration.cube_dir(cube) for cube in args]
        else:
            cubes = [
                DevConfiguration.cube_dir(cube)
                for cube in DevConfiguration.available_cubes()
            ]
            cubes = [
                cubepath for cubepath in cubes if osp.exists(osp.join(cubepath, "i18n"))
            ]
        if not update_cubes_catalogs(cubes):
            raise ExecutionError("update cubes i18n catalog failed")


def update_cubes_catalogs(cubes):
    from subprocess import CalledProcessError

    for cubedir in cubes:
        if not osp.isdir(cubedir):
            print(f"-> ignoring {cubedir} that is not a directory.")
            continue
        try:
            toedit = update_cube_catalogs(cubedir)
        except CalledProcessError as exc:
            print("\n*** error while updating catalogs for cube", cubedir)
            print(f"cmd:\n{exc.cmd}")
            print("stdout:\n%s\nstderr:\n%s" % exc.data)
        except Exception:
            import traceback

            traceback.print_exc()
            print("*** error while updating catalogs for cube", cubedir)
            return False
        else:
            # instructions pour la suite
            if toedit:
                print(f"-> regenerated .po catalogs for cube {cubedir}.")
                print("\nYou can now edit the following files:")
                print("* " + "\n* ".join(toedit))
                print(
                    'When you are done, run "cubicweb-ctl i18ninstance '
                    '<yourinstance>" to see changes in your instances.'
                )
            return True


class I18nCubeMessageExtractor:
    """This class encapsulates all the xgettext extraction logic

    ``generate_pot_file`` is the main entry point called by the ``i18ncube``
    command. A cube might decide to customize extractors to ignore a given
    directory or to extract messages from a new file type (e.g. .jinja2 files)

    For each file type, the class must define two methods:

    - ``collect_{filetype}()`` that must return the list of files
      xgettext should inspect,

    - ``extract_{filetype}(files)`` that calls xgettext and returns the
      path to the generated ``pot`` file
    """

    blacklist = STD_BLACKLIST
    formats = ["js", "py"]

    def __init__(self, workdir, cubedir):
        self.workdir = workdir
        self.cubedir = cubedir

    def generate_pot_file(self):
        """main entry point: return the generated ``cube.pot`` file

        This function first generates all the pot files (schema,
        py, js) and then merges them in a single ``cube.pot`` that will
        be used to eventually update the ``i18n/*.po`` files.
        """
        potfiles = self.generate_pot_files()
        potfile = osp.join(self.workdir, "cube.pot")
        print(f"-> merging {len(potfiles)} .pot files")
        cmd = ["msgcat", "-o", potfile]
        cmd.extend(potfiles)
        execute2(cmd)
        return potfile if osp.exists(potfile) else None

    def find(self, exts, blacklist=None):
        """collect files with extensions ``exts`` in the cube directory"""
        if blacklist is None:
            blacklist = self.blacklist
        return find(self.cubedir, exts, blacklist=blacklist)

    def generate_pot_files(self):
        """generate and return the list of all ``pot`` files for the cube

        - static-messages.pot,
        - schema.pot,
        - one ``pot`` file for each inspected format (.py, .js, etc.)
        """
        print("-> extracting messages:", end=" ")
        potfiles = []
        # static messages
        if osp.exists(osp.join("i18n", "static-messages.pot")):
            potfiles.append(osp.join("i18n", "static-messages.pot"))
        # messages from schema
        potfiles.append(self.schemapot())
        # messages from sourcecode
        for fmt in self.formats:
            collector = getattr(self, f"collect_{fmt}")
            extractor = getattr(self, f"extract_{fmt}")
            files = collector()
            if files:
                potfile = extractor(files)
                if potfile:
                    potfiles.append(potfile)
        return potfiles

    def schemapot(self):
        """generate the ``schema.pot`` file"""
        schemapot = osp.join(self.workdir, "schema.pot")
        print("schema", end=" ")
        # explicit close necessary else the file may not be yet flushed when
        # we'll using it below
        schemapotstream = open(schemapot, "w")
        generate_schema_pot(schemapotstream.write, self.cubedir)
        schemapotstream.close()
        return schemapot

    def _xgettext(self, files, output, k="_", extraopts=""):
        """shortcut to execute the xgettext command and return output file"""
        tmppotfile = osp.join(self.workdir, output)
        cmd = (
            [
                "xgettext",
                "--from-code=UTF-8",
                "--no-location",
                "--omit-header",
                "-k" + k,
                "-o",
                tmppotfile,
            ]
            + extraopts.split()
            + files
        )
        execute2(cmd)
        if osp.exists(tmppotfile):
            return tmppotfile

    def collect_js(self):
        print("Javascript")
        return [
            jsfile
            for jsfile in self.find(".js")
            if osp.basename(jsfile).startswith("cub")
        ]

    def extract_js(self, files):
        return self._xgettext(
            files, output="js.pot", extraopts="-L java --from-code=utf-8"
        )

    def collect_py(self):
        print("-> creating cube-specific catalog")
        return self.find(".py")

    def extract_py(self, files):
        return self._xgettext(files, output="py.pot")


def update_cube_catalogs(cubedir):
    cubedir = osp.abspath(osp.normpath(cubedir))
    workdir = tempfile.mkdtemp()
    try:
        cubename = osp.basename(cubedir)
        if cubename.startswith("cubicweb_"):  # new layout
            distname = cubename
            cubename = cubename[len("cubicweb_") :]
        else:
            distname = "cubicweb_" + cubename
        print("cubedir", cubedir)
        extract_cls = I18nCubeMessageExtractor
        try:
            extract_cls = pkg_resources.load_entry_point(
                distname, "cubicweb.i18ncube", cubename
            )
        except (pkg_resources.DistributionNotFound, ImportError):
            pass  # no customization found
        print(underline_title(f"Updating i18n catalogs for cube {cubename}"))
        chdir(cubedir)
        extractor = extract_cls(workdir, cubedir)
        potfile = extractor.generate_pot_file()
        if potfile is None:
            print("no message catalog for cube", cubename, "nothing to translate")
            return ()
        print("-> merging main pot file with existing translations:", end=" ")
        chdir("i18n")
        toedit = []
        for lang in CubicWebConfiguration.cw_languages():
            print(lang, end=" ")
            cubepo = f"{lang}.po"
            if not osp.exists(cubepo):
                shutil.copy(potfile, cubepo)
            else:
                cmd = ["msgmerge", "-N", "-s", "-o", cubepo + "new", cubepo, potfile]
                execute2(cmd)
                ensure_fs_mode(cubepo)
                shutil.move(f"{cubepo}new", cubepo)
            toedit.append(osp.abspath(cubepo))
        print()
        return toedit
    finally:
        # cleanup
        shutil.rmtree(workdir)


class NewCubeCommand(Command):
    """Create a new cube.

    <cubename>
      the name of the new cube. It should be a valid python module name.
    """

    name = "newcube"
    arguments = "<cubename>"
    min_args = max_args = 1
    options = (
        (
            "layout",
            {
                "short": "L",
                "type": "choice",
                "metavar": "<cube layout>",
                "default": "simple",
                "choices": ("simple", "full", "web"),
                "help": 'cube layout. You\'ll get a minimal cube with the "simple" \
layout, and a full featured cube with "full" layout.',
            },
        ),
        (
            "directory",
            {
                "short": "d",
                "type": "string",
                "metavar": "<cubes directory>",
                "help": "directory where the new cube should be created",
            },
        ),
        (
            "verbose",
            {
                "short": "v",
                "type": "yn",
                "metavar": "<verbose>",
                "default": "n",
                "help": "verbose mode: will ask all possible configuration questions",
            },
        ),
        (
            "short-description",
            {
                "short": "s",
                "type": "string",
                "metavar": "<short description>",
                "help": "short description for the cube",
            },
        ),
        (
            "author",
            {
                "short": "a",
                "type": "string",
                "metavar": "<author>",
                "default": "LOGILAB S.A. (Paris, FRANCE)",
                "help": "cube author",
            },
        ),
        (
            "author-email",
            {
                "short": "e",
                "type": "string",
                "metavar": "<email>",
                "default": "contact@logilab.fr",
                "help": "cube author's email",
            },
        ),
        (
            "author-web-site",
            {
                "short": "w",
                "type": "string",
                "metavar": "<web site>",
                "default": "https://www.logilab.fr",
                "help": "cube author's web site",
            },
        ),
        (
            "license",
            {
                "short": "l",
                "type": "choice",
                "metavar": "<license>",
                "default": "LGPL",
                "choices": ("GPL", "LGPL", ""),
                "help": "cube license",
            },
        ),
    )

    LICENSES = {
        "LGPL": """\
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
""",
        "GPL": """\
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2.1 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.
""",
        "": "# INSERT LICENSE HERE",
    }

    AUTOMATIC_WEB_TEST = """
\"\"\"%(distname)s automatic tests


uncomment code below if you want to activate automatic test for your cube:

.. sourcecode:: python

    from cubicweb.devtools.testlib import AutomaticWebTest

    class AutomaticWebTest(AutomaticWebTest):
        '''provides `to_test_etypes` and/or `list_startup_views` implementation
        to limit test scope
        '''

        def to_test_etypes(self):
            '''only test views for entities of the returned types'''
            return set(('My', 'Cube', 'Entity', 'Types'))

        def list_startup_views(self):
            '''only test startup views of the returned identifiers'''
            return ('some', 'startup', 'views')
\"\"\"\
"""

    def run(self, args):
        import re

        cubename = args[0]

        if not re.match("[_A-Za-z][_A-Za-z0-9]*$", cubename):
            raise BadCommandUsage("cube name must be a valid python module name")

        verbose = self.get("verbose")
        destdir = self.get("directory")

        if not destdir:
            destdir = getcwd()
        elif not osp.isdir(destdir):
            print("-> creating cubes directory", destdir)

            try:
                mkdir(destdir)
            except OSError as err:
                self.fail(f"failed to create directory {destdir!r}\n({err})")

        distname = f"cubicweb-{cubename.lower().replace('_', '-')}"
        cubedir = osp.join(destdir, distname)

        if osp.exists(cubedir):
            self.fail(f"{cubedir} already exists!")

        skeldir = osp.join(BASEDIR, "skeleton")
        longdesc = shortdesc = self["short-description"] or input(
            "Enter a short description for your cube: "
        )

        if verbose:
            longdesc = input(
                "Enter a long description (leave empty to reuse the short one): "
            )

        version = cubicwebversion.split(".")[0]
        dependencies = {
            "cubicweb": f">= {version}.0.0, < {int(version) + 1}.0.0",
        }

        additionnal_tests = ""
        if self["layout"] == "web":
            print("Downloading latest cubicweb-web release number...")
            try:
                cubicweb_web_json = json.load(
                    urlopen("https://pypi.org/pypi/cubicweb-web/json", timeout=10)
                )
            except URLError as e:
                print(
                    f"Error: failed to get cubicweb-web latest version number because of '{e}', "
                    "default to None"
                )
                dependencies["cubicweb-web"] = "None"
            else:
                latest_release = sorted(cubicweb_web_json["releases"].keys())[-1]
                next_major = f"{int(latest_release.split('.')[0]) + 1}.0.0"

                dependencies["cubicweb-web"] = f">= {latest_release}, < {next_major}"

            additionnal_tests = self.AUTOMATIC_WEB_TEST % {"distname": distname}

        if verbose:
            dependencies.update(self._ask_for_dependencies())

        context = {
            "cubename": cubename,
            "distname": distname,
            "shortdesc": shortdesc,
            "longdesc": longdesc or shortdesc,
            "dependencies": str(dependencies).replace(
                "'", '"'
            ),  # to respect black formatting
            "additionnal-tests": additionnal_tests,
            "version": cubicwebversion,
            "year": str(date.today().year),
            "author": self["author"],
            "author-email": self["author-email"],
            "author-web-site": self["author-web-site"],
            "license": self["license"],
            "long-license": self.LICENSES[self["license"]],
        }

        exclude = SKEL_EXCLUDE
        if self["layout"] == "simple":
            exclude += (
                "sobjects.py*",
                "precreate.py*",
                "realdb_test*",
                "cubes.*",
                "uiprops.py*",
            )

        copy_skeleton(skeldir, cubedir, context, exclude=exclude)

    def _ask_for_dependencies(self):
        from logilab.common.shellutils import ASK
        from logilab.common.textutils import splitstrip

        depcubes = []
        for cube in CubicWebConfiguration.available_cubes():
            answer = ASK.ask(
                f"Depends on cube {cube}? ", ("N", "y", "skip", "type"), "N"
            )
            if answer == "y":
                depcubes.append(cube)
            if answer == "type":
                depcubes = splitstrip(input("type dependencies: "))
                break
            elif answer == "skip":
                break
        return dict(
            ("cubicweb-" + cube, CubicWebConfiguration.cube_version(cube))
            for cube in depcubes
        )


class ExamineLogCommand(Command):
    """Examine a rql log file.

    Will print out the following table

      Percentage; Cumulative Time (clock); Cumulative Time (CPU); Occurences; Query

    sorted by descending cumulative time (clock). Time are expressed in seconds.

    Chances are the lines at the top are the ones that will bring the higher
    benefit after optimisation. Start there.
    """

    arguments = "rql.log"
    name = "exlog"
    options = ()

    def run(self, args):
        import re

        requests = {}
        for filepath in args:
            try:
                stream = open(filepath)
            except OSError as ex:
                raise BadCommandUsage(f"can't open rql log file {filepath}: {ex}")
            for lineno, line in enumerate(stream):
                if " WHERE " not in line:
                    continue
                try:
                    rql, time = line.split("--")
                    rql = re.sub(r"(\'\w+': \d*)", "", rql)
                    if "{" in rql:
                        rql = rql[: rql.index("{")]
                    req = requests.setdefault(rql, [])
                    time.strip()
                    chunks = time.split()
                    clocktime = float(chunks[0][1:])
                    cputime = float(chunks[-3])
                    req.append((clocktime, cputime))
                except Exception as exc:
                    sys.stderr.write(f"Line {lineno}: {exc} ({line})\n")
        stat = []
        for rql, times in requests.items():
            stat.append(
                (
                    sum(time[0] for time in times),
                    sum(time[1] for time in times),
                    len(times),
                    rql,
                )
            )
        stat.sort()
        stat.reverse()
        total_time = sum(clocktime for clocktime, cputime, occ, rql in stat) * 0.01
        print(
            "Percentage;Cumulative Time (clock);Cumulative Time (CPU);Occurences;Query"
        )
        for clocktime, cputime, occ, rql in stat:
            print(
                "%.2f;%.2f;%.2f;%s;%s"
                % (clocktime / total_time, clocktime, cputime, occ, rql)
            )


class GenerateSchema(Command):
    """Generate schema image for the given cube"""

    name = "schema"
    arguments = "<cube>"
    min_args = max_args = 1
    options = [
        (
            "output-file",
            {
                "type": "string",
                "default": None,
                "metavar": "<file>",
                "short": "o",
                "help": "output image file",
                "input": False,
            },
        ),
        (
            "viewer",
            {
                "type": "string",
                "default": None,
                "short": "d",
                "metavar": "<cmd>",
                "help": "command use to view the generated file (empty for none)",
            },
        ),
        (
            "show-meta",
            {
                "action": "store_true",
                "default": False,
                "short": "m",
                "metavar": "<yN>",
                "help": "include meta and internal entities in schema",
            },
        ),
        (
            "show-workflow",
            {
                "action": "store_true",
                "default": False,
                "short": "w",
                "metavar": "<yN>",
                "help": "include workflow entities in schema",
            },
        ),
        (
            "show-cw-user",
            {
                "action": "store_true",
                "default": False,
                "metavar": "<yN>",
                "help": "include cubicweb user entities in schema",
            },
        ),
        (
            "exclude-type",
            {
                "type": "string",
                "default": "",
                "short": "x",
                "metavar": "<types>",
                "help": "coma separated list of entity types to remove from view",
            },
        ),
        (
            "include-type",
            {
                "type": "string",
                "default": "",
                "short": "i",
                "metavar": "<types>",
                "help": "coma separated list of entity types to include in view",
            },
        ),
        (
            "show-etype",
            {
                "type": "string",
                "default": "",
                "metavar": "<etype>",
                "help": "show graph of this etype and its neighbours",
            },
        ),
    ]

    def run(self, args):
        from subprocess import Popen
        from tempfile import NamedTemporaryFile
        from logilab.common.textutils import splitstrip
        from logilab.common.graph import DotBackend
        from yams import schema2dot as s2d, BASE_TYPES
        from cubicweb.schema import (
            META_RTYPES,
            SCHEMA_TYPES,
            SYSTEM_RTYPES,
            WORKFLOW_TYPES,
            INTERNAL_TYPES,
        )

        cubes = splitstrip(args[0])
        dev_conf = DevConfiguration(*cubes)
        schema = dev_conf.load_schema()
        out, viewer = self["output-file"], self["viewer"]
        if out is None:
            tmp_file = NamedTemporaryFile(suffix=".svg")
            out = tmp_file.name
        skiptypes = BASE_TYPES | SCHEMA_TYPES
        if not self["show-meta"]:
            skiptypes |= META_RTYPES | SYSTEM_RTYPES | INTERNAL_TYPES
        if not self["show-workflow"]:
            skiptypes |= WORKFLOW_TYPES
        if not self["show-cw-user"]:
            skiptypes |= set(("CWUser", "CWGroup", "EmailAddress"))
        skiptypes |= set(self["exclude-type"].split(","))
        skiptypes -= set(self["include-type"].split(","))

        if not self["show-etype"]:
            s2d.schema2dot(schema, out, skiptypes=skiptypes)
        else:
            etype = self["show-etype"]
            visitor = s2d.OneHopESchemaVisitor(schema[etype], skiptypes=skiptypes)
            propshdlr = s2d.SchemaDotPropsHandler(visitor)
            backend = DotBackend(
                "schema",
                "BT",
                ratio="compress",
                size=None,
                renderer="dot",
                additionnal_param={"overlap": "false", "splines": "true", "sep": "0.2"},
            )
            generator = s2d.GraphGenerator(backend)
            generator.generate(visitor, propshdlr, out)

        if viewer:
            p = Popen((viewer, out))
            p.wait()


class ExportSchemaCommand(Command):
    """Export instance's schema"""

    name = "export-schema"
    arguments = "<instance_name>"
    min_args = max_args = 1
    options = (
        (
            "format",
            {
                "short": "f",
                "type": "choice",
                "metavar": "export format",
                "choices": ("json", "typescript"),
                "default": "json",
                "help": 'export the instance schema as "typescript" or "json" format.',
            },
        ),
        (
            "type_name",
            {
                "short": "n",
                "type": "string",
                "default": "default",
                "metavar": "<type name>",
                "help": (
                    'name of the exported interface or "default" to use a default '
                    "export (typescript only)"
                ),
                "group": "typescript",
            },
        ),
        (
            "output_file",
            {
                "short": "o",
                "type": "string",
                "metavar": "<output file>",
                "help": "Export the instance schema as typescript or json format.",
            },
        ),
    )

    def _get_schema(self, appid: str) -> CubicWebSchema:
        cwconfig = DevConfiguration.config_for(appid)
        cwconfig.quick_start = True  # Avoid loading all appbojects
        repo = cwconfig.repository()
        return repo.schema

    def _get_exporter(self):
        file_format = self.get("format")
        assert file_format in ["json", "typescript"]
        if file_format == "json":
            exporter = JSONSchemaExporter()
        else:  # typescript
            type_name = self.get("type_name")
            exporter = TypescriptSchemaExporter(type_name)
        return exporter

    def _get_output_file(self):
        output_file = self.get("output_file")
        if output_file:
            return output_file
        return {
            "json": "schema.json",
            "typescript": "schema.ts",
        }[self.get("format")]

    def run(self, args):
        instance_name = args[0]
        schema = self._get_schema(instance_name)
        exporter = self._get_exporter()
        with open(self._get_output_file(), mode="w") as f:
            f.write(exporter.export(schema))


class RenderConfigCommand(Command):
    """Renders the actual configuration used by the instance.

    The configuration can be read from all-in-one.conf or environment variable.
    This command enables to quickly the find truth.

    <instance>
      the name of the instance
    """

    name = "config"
    arguments = "<instance>"
    min_args = max_args = 1

    def run(self, args):
        appid = args[0]

        from cubicweb.cwconfig import CubicWebConfiguration

        config = CubicWebConfiguration.config_for(appid)
        config.quick_start = True
        config.repository()  # needed to load all cubes configuration

        for option_name, _option_parameters in sorted(config.options):
            try:
                value = config[option_name]
            except KeyError:
                continue

            print(f"{option_name} = {repr(value)}")


for cmdcls in (
    UpdateCubicWebCatalogCommand,
    UpdateCubeCatalogCommand,
    NewCubeCommand,
    ExamineLogCommand,
    GenerateSchema,
    ExportSchemaCommand,
    RenderConfigCommand,
):
    CWCTL.register(cmdcls)
