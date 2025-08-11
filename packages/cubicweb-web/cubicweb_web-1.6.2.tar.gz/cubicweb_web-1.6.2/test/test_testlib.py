from io import BytesIO

from logilab.common.testlib import TestCase, unittest_main

from cubicweb.devtools import htmlparser

from cubicweb_web.devtools.testlib import WebCWTC

HTML_PAGE = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
  <head><title>need a title</title></head>
  <body>
    <h1>Hello World !</h1>
  </body>
</html>
"""

HTML_PAGE2 = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
 <head><title>need a title</title></head>
 <body>
   <h1>Test</h1>
   <h1>Hello <a href="http://www.google.com">world</a> !</h1>
   <h2>h2 title</h2>
   <h3>h3 title</h3>
   <h2>antoher h2 title</h2>
   <h4>h4 title</h4>
   <p><a href="http://www.logilab.org">Logilab</a> introduces CW !</p>
 </body>
</html>
"""

HTML_PAGE_ERROR = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
 <head><title>need a title</title></head>
 <body>
   Logilab</a> introduces CW !
 </body>
</html>
"""

HTML_NON_STRICT = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
  <head><title>need a title</title></head>
  <body>
    <h1><a href="something.com">title</h1>
  </body>
</html>
"""


class HTMLPageInfoTC(TestCase):
    """test cases for PageInfo"""

    def setUp(self):
        parser = htmlparser.HTMLValidator()
        # disable cleanup that would remove doctype
        parser.preprocess_data = lambda data: data
        self.page_info = parser.parse_string(HTML_PAGE2)

    def test_source1(self):
        """make sure source is stored correctly"""
        self.assertEqual(self.page_info.source, HTML_PAGE2)

    def test_source2(self):
        """make sure source is stored correctly - raise exception"""
        parser = htmlparser.DTDValidator()
        self.assertRaises(AssertionError, parser.parse_string, HTML_PAGE_ERROR)

    def test_has_title_no_level(self):
        """tests h? tags information"""
        self.assertEqual(self.page_info.has_title("Test"), True)
        self.assertEqual(self.page_info.has_title("Test "), False)
        self.assertEqual(self.page_info.has_title("Tes"), False)
        self.assertEqual(self.page_info.has_title("Hello world !"), True)

    def test_has_title_level(self):
        """tests h? tags information"""
        self.assertEqual(self.page_info.has_title("Test", level=1), True)
        self.assertEqual(self.page_info.has_title("Test", level=2), False)
        self.assertEqual(self.page_info.has_title("Test", level=3), False)
        self.assertEqual(self.page_info.has_title("Test", level=4), False)
        self.assertRaises(IndexError, self.page_info.has_title, "Test", level=5)

    def test_has_title_regexp_no_level(self):
        """tests has_title_regexp() with no particular level specified"""
        self.assertEqual(self.page_info.has_title_regexp("h[23] title"), True)

    def test_has_title_regexp_level(self):
        """tests has_title_regexp() with a particular level specified"""
        self.assertEqual(self.page_info.has_title_regexp("h[23] title", 2), True)
        self.assertEqual(self.page_info.has_title_regexp("h[23] title", 3), True)
        self.assertEqual(self.page_info.has_title_regexp("h[23] title", 4), False)

    def test_appears(self):
        """tests PageInfo.appears()"""
        self.assertEqual(self.page_info.appears("CW"), True)
        self.assertEqual(self.page_info.appears("Logilab"), True)
        self.assertEqual(self.page_info.appears("Logilab introduces"), True)
        self.assertEqual(self.page_info.appears("H2 title"), False)

    def test_has_link(self):
        """tests has_link()"""
        self.assertEqual(self.page_info.has_link("Logilab"), True)
        self.assertEqual(self.page_info.has_link("logilab"), False)
        self.assertEqual(
            self.page_info.has_link("Logilab", "http://www.logilab.org"), True
        )
        self.assertEqual(
            self.page_info.has_link("Logilab", "http://www.google.com"), False
        )

    def test_has_link_regexp(self):
        """test has_link_regexp()"""
        self.assertEqual(self.page_info.has_link_regexp("L[oi]gilab"), True)
        self.assertEqual(self.page_info.has_link_regexp("L[ai]gilab"), False)


class FakeFormTC(TestCase):
    def test_fake_form(self):
        class entity:
            cw_etype = "Entity"
            eid = 0

        sio = BytesIO(b"hop\n")
        form = WebCWTC.fake_form(
            "import",
            {
                "file": ("filename.txt", sio),
                "encoding": "utf-8",
            },
            [(entity, {"field": "value"})],
        )
        self.assertEqual(
            form,
            {
                "__form_id": "import",
                "__maineid": 0,
                "__type:0": "Entity",
                "_cw_entity_fields:0": "__type,field",
                "_cw_fields": "encoding,file",
                "eid": [0],
                "encoding": "utf-8",
                "field:0": "value",
                "file": ("filename.txt", sio),
            },
        )


class WebRepoAccessTC(WebCWTC):
    def test_web_request(self):
        acc = self.new_access("admin")
        with acc.web_request(elephant="babar") as req:
            rset = req.execute("Any X WHERE X is CWUser")
            self.assertTrue(rset)
            self.assertEqual("babar", req.form["elephant"])


if __name__ == "__main__":
    unittest_main()
