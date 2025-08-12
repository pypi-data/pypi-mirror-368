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
"""Some i18n/gettext utilities."""
import os
from glob import glob
from os.path import join, basename, splitext, exists

from cubicweb.toolsutils import create_dir


def add_msg(w, msgid, msgctx=None):
    """write an empty pot msgid definition"""
    if msgctx:
        w(f'msgctxt "{msgctx}"\n')
    msgid = msgid.replace('"', r"\"").splitlines()
    if len(msgid) > 1:
        w('msgid ""\n')
        for line in msgid:
            w('"%s"' % line.replace('"', r"\""))
    else:
        w(f'msgid "{msgid[0]}"\n')
    w('msgstr ""\n\n')


def execute2(args):
    # XXX replace this with check_output in Python 2.7
    from subprocess import Popen, PIPE, CalledProcessError

    p = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        exc = CalledProcessError(p.returncode, args[0])
        exc.cmd = args
        exc.data = (out, err)
        raise exc


def available_catalogs(i18ndir=None):
    if i18ndir is None:
        wildcard = "*.po"
    else:
        wildcard = join(i18ndir, "*.po")
    for popath in glob(wildcard):
        lang = splitext(basename(popath))[0]
        yield lang, popath


def compile_i18n_catalogs(sourcedirs, destdir, langs):
    """generate .mo files for a set of languages into the `destdir` i18n directory"""
    from subprocess import CalledProcessError
    from logilab.common.fileutils import ensure_fs_mode

    print(f"-> compiling message catalogs to {destdir}")
    errors = []
    for lang in langs:
        langdir = join(destdir, lang, "LC_MESSAGES")
        if not exists(langdir):
            create_dir(langdir)
        pofiles = [join(path, f"{lang}.po") for path in sourcedirs]
        pofiles = [pof for pof in pofiles if exists(pof)]
        mergedpo = join(destdir, f"{lang}_merged.po")
        try:
            # merge instance/cubes messages catalogs with the stdlib's one
            cmd = [
                "msgcat",
                "--use-first",
                "--sort-output",
                "--strict",
                "-o",
                mergedpo,
            ] + pofiles
            execute2(cmd)
            # make sure the .mo file is writeable and compiles with *msgfmt*
            applmo = join(destdir, lang, "LC_MESSAGES", "cubicweb.mo")
            try:
                ensure_fs_mode(applmo)
            except OSError:
                pass  # suppose not exists
            execute2(["msgfmt", mergedpo, "-o", applmo])
        except CalledProcessError as exc:
            errors.append(
                "while handling language %s:\ncmd:\n%s\nstdout:\n%s\nstderr:\n%s\n"
                % (lang, exc.cmd, repr(exc.data[0]), repr(exc.data[1]))
            )
        except Exception as exc:
            errors.append(f"while handling language {lang}: {exc}")
        try:
            # clean everything
            os.unlink(mergedpo)
        except Exception:
            continue
    return errors
