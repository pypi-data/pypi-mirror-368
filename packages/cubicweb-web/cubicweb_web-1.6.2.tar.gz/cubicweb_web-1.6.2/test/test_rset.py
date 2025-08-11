# copyright 2023-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
from logilab.common.testlib import unittest_main

from cubicweb_web.devtools.testlib import WebCWTC


class ResultSetCWTC(WebCWTC):
    def test_possible_actions_cache(self):
        with self.admin_access.web_request() as req:
            rset = req.execute(
                "Any D, COUNT(U) GROUPBY D WHERE U is CWUser, U creation_date D"
            )
            rset.possible_actions(argument="Value")
            self.assertRaises(ValueError, rset.possible_actions, argument="OtherValue")
            self.assertRaises(ValueError, rset.possible_actions, other_argument="Value")


if __name__ == "__main__":
    unittest_main()
