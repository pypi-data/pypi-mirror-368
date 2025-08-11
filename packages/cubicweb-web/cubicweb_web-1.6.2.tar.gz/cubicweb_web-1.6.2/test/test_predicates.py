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

from cubicweb.predicates import (
    match_form_params,
)

from cubicweb_web.devtools.testlib import WebCWTC
from cubicweb_web.predicates import paginated_rset
from logilab.common.testlib import unittest_main


class MatchFormParamsCWTC(WebCWTC):
    """tests for match_form_params predicate"""

    def test_keyonly_match(self):
        """test standard usage: ``match_form_params('param1', 'param2')``

        ``param1`` and ``param2`` must be specified in request's form.
        """
        web_request = self.admin_access.web_request
        vid_selector = match_form_params("vid")
        vid_subvid_selector = match_form_params("vid", "subvid")
        # no parameter => KO,KO
        with web_request() as req:
            self.assertEqual(vid_selector(None, req), 0)
            self.assertEqual(vid_subvid_selector(None, req), 0)
        # one expected parameter found => OK,KO
        with web_request(vid="foo") as req:
            self.assertEqual(vid_selector(None, req), 1)
            self.assertEqual(vid_subvid_selector(None, req), 0)
        # all expected parameters found => OK,OK
        with web_request(vid="foo", subvid="bar") as req:
            self.assertEqual(vid_selector(None, req), 1)
            self.assertEqual(vid_subvid_selector(None, req), 2)

    def test_keyvalue_match_one_parameter(self):
        """test dict usage: ``match_form_params(param1=value1)``

        ``param1`` must be specified in the request's form and its value
        must be ``value1``.
        """
        web_request = self.admin_access.web_request
        # test both positional and named parameters
        vid_selector = match_form_params(vid="foo")
        # no parameter => should fail
        with web_request() as req:
            self.assertEqual(vid_selector(None, req), 0)
        # expected parameter found with expected value => OK
        with web_request(vid="foo", subvid="bar") as req:
            self.assertEqual(vid_selector(None, req), 1)
        # expected parameter found but value is incorrect => KO
        with web_request(vid="bar") as req:
            self.assertEqual(vid_selector(None, req), 0)

    def test_keyvalue_match_two_parameters(self):
        """test dict usage: ``match_form_params(param1=value1, param2=value2)``

        ``param1`` and ``param2`` must be specified in the request's form and
        their respective value must be ``value1`` and ``value2``.
        """
        web_request = self.admin_access.web_request
        vid_subvid_selector = match_form_params(vid="list", subvid="tsearch")
        # missing one expected parameter => KO
        with web_request(vid="list") as req:
            self.assertEqual(vid_subvid_selector(None, req), 0)
        # expected parameters found but values are incorrect => KO
        with web_request(vid="list", subvid="foo") as req:
            self.assertEqual(vid_subvid_selector(None, req), 0)
        # expected parameters found and values are correct => OK
        with web_request(vid="list", subvid="tsearch") as req:
            self.assertEqual(vid_subvid_selector(None, req), 2)

    def test_keyvalue_multiple_match(self):
        """test dict usage with multiple values

        i.e. as in ``match_form_params(param1=('value1', 'value2'))``

        ``param1`` must be specified in the request's form and its value
        must be either ``value1`` or ``value2``.
        """
        web_request = self.admin_access.web_request
        vid_subvid_selector = match_form_params(
            vid="list", subvid=("tsearch", "listitem")
        )
        # expected parameters found and values correct => OK
        with web_request(vid="list", subvid="tsearch") as req:
            self.assertEqual(vid_subvid_selector(None, req), 2)
        with web_request(vid="list", subvid="listitem") as req:
            self.assertEqual(vid_subvid_selector(None, req), 2)
        # expected parameters found but values are incorrect => OK
        with web_request(vid="list", subvid="foo") as req:
            self.assertEqual(vid_subvid_selector(None, req), 0)

    def test_invalid_calls(self):
        """checks invalid calls raise a ValueError"""
        # mixing named and positional arguments should fail
        with self.assertRaises(ValueError) as cm:
            match_form_params("list", x="1", y="2")
        self.assertEqual(
            str(cm.exception),
            "match_form_params() can't be called with both "
            "positional and named arguments",
        )
        # using a dict as first and unique argument should fail
        with self.assertRaises(ValueError) as cm:
            match_form_params({"x": 1})
        self.assertEqual(
            str(cm.exception),
            "match_form_params() positional arguments must be strings",
        )


class PaginatedCWTC(WebCWTC):
    """tests for paginated_rset predicate"""

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            for i in range(30):
                cnx.create_entity("CWGroup", name="group%d" % i)
            cnx.commit()

    def test_paginated_rset(self):
        default_nb_pages = 1
        web_request = self.admin_access.web_request
        with web_request() as req:
            rset = req.execute("Any G WHERE G is CWGroup")
        self.assertEqual(len(rset), 34)
        with web_request(vid="list", page_size="10") as req:
            self.assertEqual(paginated_rset()(None, req, rset), default_nb_pages)
        with web_request(vid="list", page_size="20") as req:
            self.assertEqual(paginated_rset()(None, req, rset), default_nb_pages)
        with web_request(vid="list", page_size="50") as req:
            self.assertEqual(paginated_rset()(None, req, rset), 0)
        with web_request(vid="list", page_size="10/") as req:
            self.assertEqual(paginated_rset()(None, req, rset), 0)
        with web_request(vid="list", page_size=".1") as req:
            self.assertEqual(paginated_rset()(None, req, rset), 0)
        with web_request(vid="list", page_size="not_an_int") as req:
            self.assertEqual(paginated_rset()(None, req, rset), 0)


if __name__ == "__main__":
    unittest_main()
