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
"""Tests for notification sobjects"""
from cubicweb.devtools import BASE_URL
from cubicweb.devtools.testlib import CubicWebTC, MAILBOX


class NotificationTC(CubicWebTC):
    def test_recipients_finder(self):
        with self.admin_access.cnx() as cnx:
            urset = cnx.execute('CWUser X WHERE X login "admin"')
            cnx.execute(
                'INSERT EmailAddress X: X address "admin@logilab.fr", U primary_email X'
                " WHERE U eid %(x)s",
                {"x": urset[0][0]},
            )
            cnx.execute(
                'INSERT CWProperty X: X pkey "ui.language", X value "fr", X for_user U '
                "WHERE U eid %(x)s",
                {"x": urset[0][0]},
            )
            cnx.commit()  # commit so that admin get its properties updated
            finder = self.vreg["services"].select("recipients_finder", cnx, rset=urset)
            self.set_option("default-recipients-mode", "none")
            self.assertEqual(finder.recipients(), [])
            self.set_option("default-recipients-mode", "users")
            self.assertEqual(finder.recipients(), [cnx.user])
            self.set_option("default-recipients-mode", "default-dest-addrs")
            self.set_option("default-dest-addrs", "abcd@logilab.fr, efgh@logilab.fr")
            self.assertEqual(
                list(finder.recipients()),
                [("abcd@logilab.fr", "en"), ("efgh@logilab.fr", "en")],
            )

    def test_status_change_view(self):
        with self.admin_access.cnx() as cnx:
            u = self.create_user(cnx, "toto")
            iwfable = u.cw_adapt_to("IWorkflowable")
            iwfable.fire_transition("deactivate", comment="yeah")
            self.assertFalse(MAILBOX)
            cnx.commit()
            self.assertEqual(len(MAILBOX), 1)
            email = MAILBOX[0]
            self.assertEqual(
                email.content,
                f"""
admin changed status from <activated> to <deactivated> for entity
'toto'

yeah

url: {BASE_URL}cwuser/toto
""",
            )
            self.assertEqual(email.subject, f"status changed CWUser #{u.eid} (admin)")


if __name__ == "__main__":
    from logilab.common.testlib import unittest_main

    unittest_main()
