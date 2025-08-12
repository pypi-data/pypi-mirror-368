# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""Tests for cubicweb.pyramid.config module."""

import os
from os import path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from cubicweb.pyramid import config
from cubicweb.pyramid.pyramidctl import _generate_pyramid_ini_file


class PyramidConfigTC(TestCase):
    def test_get_random_secret_key(self):
        with patch("random.SystemRandom.choice", return_value="0") as patched_choice:
            secret = config.get_random_secret_key()
        self.assertEqual(patched_choice.call_count, 50)
        self.assertEqual(secret, "0" * 50)

    def test_write_pyramid_ini(self):
        with TemporaryDirectory() as instancedir:
            pyramid_ini_path = path.join(instancedir, "pyramid.ini")
            with patch(
                "random.SystemRandom.choice", return_value="0"
            ) as patched_choice:
                _generate_pyramid_ini_file(pyramid_ini_path)
            with open(path.join(instancedir, "pyramid.ini")) as f:
                lines = f.readlines()

        self.assertEqual(patched_choice.call_count, 50 * 3)

        secret = "0" * 50

        for option in (
            "cubicweb.session.secret",
            "cubicweb.auth.authtkt.persistent.secret",
            "cubicweb.auth.authtkt.session.secret",
        ):
            self.assertIn(f"{option} = {secret}\n", lines)

        for option in (
            "cubicweb.auth.authtkt.persistent.secure",
            "cubicweb.auth.authtkt.session.secure",
        ):
            self.assertIn(f"{option} = no\n", lines)

    def test_write_development_ini(self):
        with TemporaryDirectory() as instancedir:
            appid = "pyramid-instance"
            os.makedirs(path.join(instancedir, appid))
            os.environ["CW_INSTANCES_DIR"] = instancedir
            try:
                with patch(
                    "random.SystemRandom.choice", return_value="0"
                ) as patched_choice:
                    _generate_pyramid_ini_file(
                        os.path.join(instancedir, appid, "pyramid.ini")
                    )
            finally:
                os.environ.pop("CW_INSTANCES_DIR")
            with open(path.join(instancedir, appid, "pyramid.ini")) as f:
                lines = f.readlines()
        self.assertEqual(patched_choice.call_count, 50 * 3)
        secret = "0" * 50
        for option in (
            "cubicweb.session.secret",
            "cubicweb.auth.authtkt.persistent.secret",
            "cubicweb.auth.authtkt.session.secret",
        ):
            self.assertIn(f"{option} = {secret}\n", lines)
        self.assertIn("cubicweb.auth.authtkt.session.secure = no\n", lines)
        self.assertIn("cubicweb.auth.authtkt.persistent.secure = no\n", lines)


if __name__ == "__main__":
    import unittest

    unittest.main()
