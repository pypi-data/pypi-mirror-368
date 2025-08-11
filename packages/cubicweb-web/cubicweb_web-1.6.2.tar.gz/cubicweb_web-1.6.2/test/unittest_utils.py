# copyright 2003-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""unit tests for module cubicweb.utils"""
from urllib.parse import urljoin

from cubicweb.devtools import BASE_URL

from cubicweb_web.devtools.testlib import WebCWTC
from cubicweb_web.utils import HTMLHead


class HTMLHeadTC(WebCWTC):
    DATADIR_URL = urljoin(BASE_URL, "/data/")

    def htmlhead(self, datadir_url):
        with self.admin_access.web_request() as req:
            req.datadir_url = datadir_url
            head = HTMLHead(req)
            return head

    def test_concat_urls(self):
        base_url = self.DATADIR_URL
        head = self.htmlhead(base_url)
        urls = [base_url + "bob1.js", base_url + "bob2.js", base_url + "bob3.js"]
        result = head.concat_urls(urls)
        expected = urljoin(self.DATADIR_URL, "??bob1.js,bob2.js,bob3.js")
        self.assertEqual(result, expected)

    def test_group_urls(self):
        base_url = self.DATADIR_URL
        head = self.htmlhead(base_url)
        urls_spec = [
            (base_url + "bob0.js", None),
            (base_url + "bob1.js", None),
            ("http://ext.com/bob2.js", None),
            ("http://ext.com/bob3.js", None),
            (base_url + "bob4.css", "all"),
            (base_url + "bob5.css", "all"),
            (base_url + "bob6.css", "print"),
            (base_url + "bob7.css", "print"),
            (base_url + "bob8.css", ("all", "[if IE 8]")),
            (base_url + "bob9.css", ("print", "[if IE 8]")),
        ]
        result = head.group_urls(urls_spec)
        expected = [
            (base_url + "??bob0.js,bob1.js", None),
            ("http://ext.com/bob2.js", None),
            ("http://ext.com/bob3.js", None),
            (base_url + "??bob4.css,bob5.css", "all"),
            (base_url + "??bob6.css,bob7.css", "print"),
            (base_url + "bob8.css", ("all", "[if IE 8]")),
            (base_url + "bob9.css", ("print", "[if IE 8]")),
        ]
        self.assertEqual(list(result), expected)

    def test_getvalue_with_concat(self):
        self.config.global_set_option("concat-resources", True)
        base_url = self.DATADIR_URL
        head = self.htmlhead(base_url)
        head.add_js(base_url + "bob0.js")
        head.add_js(base_url + "bob1.js")
        head.add_js("http://ext.com/bob2.js")
        head.add_js("http://ext.com/bob3.js")
        head.add_css(base_url + "bob4.css")
        head.add_css(base_url + "bob5.css")
        head.add_css(base_url + "bob6.css", "print")
        head.add_css(base_url + "bob7.css", "print")
        result = head.getvalue()
        expected = f"""<head>
<link rel="stylesheet" type="text/css" media="all" href="{self.DATADIR_URL}??bob4.css,bob5.css"/>
<link rel="stylesheet" type="text/css" media="print" href="{self.DATADIR_URL}??bob6.css,bob7.css"/>
<script type="text/javascript" src="{self.DATADIR_URL}??bob0.js,bob1.js"></script>
<script type="text/javascript" src="http://ext.com/bob2.js"></script>
<script type="text/javascript" src="http://ext.com/bob3.js"></script>
</head>
"""  # noqa
        self.assertEqual(result, expected)

    def test_getvalue_without_concat(self):
        self.config.global_set_option("concat-resources", False)
        try:
            base_url = self.DATADIR_URL
            head = self.htmlhead(base_url)
            head.add_js(base_url + "bob0.js")
            head.add_js(base_url + "bob1.js")
            head.add_js("http://ext.com/bob2.js")
            head.add_js("http://ext.com/bob3.js")
            head.write_front(
                '<script type="text/javascript">console.log("FIRST SCRIPT ADDED HERE")</script>\n'
            )
            head.add_css(base_url + "bob4.css")
            head.add_css(base_url + "bob5.css")
            head.add_css(base_url + "bob6.css", "print")
            head.add_css(base_url + "bob7.css", "print")
            result = head.getvalue()
            expected = f"""<head>
<script type="text/javascript">console.log("FIRST SCRIPT ADDED HERE")</script>
<link rel="stylesheet" type="text/css" media="all" href="{self.DATADIR_URL}bob4.css"/>
<link rel="stylesheet" type="text/css" media="all" href="{self.DATADIR_URL}bob5.css"/>
<link rel="stylesheet" type="text/css" media="print" href="{self.DATADIR_URL}bob6.css"/>
<link rel="stylesheet" type="text/css" media="print" href="{self.DATADIR_URL}bob7.css"/>
<script type="text/javascript" src="{self.DATADIR_URL}bob0.js"></script>
<script type="text/javascript" src="{self.DATADIR_URL}bob1.js"></script>
<script type="text/javascript" src="http://ext.com/bob2.js"></script>
<script type="text/javascript" src="http://ext.com/bob3.js"></script>
</head>
"""
            self.assertEqual(result, expected)
        finally:
            self.config.global_set_option("concat-resources", True)

    def test_add_js_attribute(self):
        self.config.global_set_option("concat-resources", False)
        try:
            base_url = self.DATADIR_URL
            head = self.htmlhead(base_url)
            head.add_js(base_url + "bob0.js", script_attributes={"defer": True})
            head.add_js(
                "http://ext.com/bob2.js",
                script_attributes={"async": True, "integrity": "sha256-lala"},
            )
            result = head.getvalue()
            expected = f"""<head>
<script type="text/javascript" src="{self.DATADIR_URL}bob0.js" defer></script>
<script type="text/javascript" src="http://ext.com/bob2.js" async integrity="sha256-lala"></script>
</head>
"""
            self.assertEqual(result, expected)
        finally:
            self.config.global_set_option("concat-resources", True)


if __name__ == "__main__":
    import unittest

    unittest.main()
