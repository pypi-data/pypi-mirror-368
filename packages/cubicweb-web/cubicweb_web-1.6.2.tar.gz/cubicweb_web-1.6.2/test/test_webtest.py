import http.client

from logilab.common.testlib import Tags
from pyramid.httpexceptions import HTTPSeeOther

from cubicweb.devtools import BASE_URL

from cubicweb_web.devtools.testlib import PyramidWebCWTC


class CWTTC(PyramidWebCWTC):
    def test_response(self):
        response = self.webapp.get(BASE_URL)
        self.assertEqual(200, response.status_int)

    def test_base_url(self):
        if self.config["base-url"] not in self.webapp.get(BASE_URL).text:
            self.fail("no mention of base url in retrieved page")


class CWTIdentTC(PyramidWebCWTC):
    test_db_id = "webtest-ident"
    anonymous_allowed = False
    tags = PyramidWebCWTC.tags | Tags(("auth",))

    def test_reponse_denied(self):
        res = self.webapp.get(BASE_URL, expect_errors=True)
        self.assertEqual(HTTPSeeOther.code, res.status_int)

    def test_login(self):
        self.login(self.admlogin, self.admpassword)
        res = self.webapp.get(BASE_URL)
        self.assertEqual(http.client.OK, res.status_int)

        self.logout()
        res = self.webapp.get(BASE_URL, expect_errors=True)
        self.assertEqual(HTTPSeeOther.code, res.status_int)


if __name__ == "__main__":
    import unittest

    unittest.main()
