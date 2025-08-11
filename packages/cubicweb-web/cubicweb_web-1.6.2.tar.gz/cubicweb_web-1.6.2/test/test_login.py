from os.path import join
from shutil import rmtree

from urllib.parse import urlparse, urljoin

from cubicweb.devtools import BASE_URL
from cubicweb_web.devtools.testlib import PyramidWebCWTC


class LoginTestLangUrlPrefix(PyramidWebCWTC):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config.global_set_option("language-mode", "url-prefix")

    def test_login_password_login_lang_prefix(self):
        res = self.webapp.post(
            urljoin(BASE_URL, "fr/login"),
            {"__login": self.admlogin, "__password": self.admpassword},
        )
        self.assertEqual(res.status_int, 303)

        res = self.webapp.get(urljoin(BASE_URL, "fr/login"))
        self.assertEqual(res.status_int, 303)


class LoginTest(PyramidWebCWTC):
    def test_login_form(self):
        res = self.webapp.get(urljoin(BASE_URL, "login"))
        self.assertIn("__login", res.text)

    def test_login_password_login(self):
        res = self.webapp.post(
            urljoin(BASE_URL, "login"),
            {"__login": self.admlogin, "__password": self.admpassword},
        )
        self.assertEqual(res.status_int, 303)

        res = self.webapp.get(urljoin(BASE_URL, "login"))
        self.assertEqual(res.status_int, 303)

    def test_login_password_login_cookie_expires(self):
        res = self.webapp.post(
            urljoin(BASE_URL, "login"),
            {"__login": self.admlogin, "__password": self.admpassword},
        )
        self.assertEqual(res.status_int, 303)

        cookies = self.webapp.cookiejar._cookies[urlparse(BASE_URL).netloc]["/"]
        self.assertNotIn("pauth_tkt", cookies)
        self.assertIn("auth_tkt", cookies)
        self.assertIsNone(cookies["auth_tkt"].expires)

        res = self.webapp.logout()
        self.assertEqual(res.status_int, 303)

        self.assertNotIn("auth_tkt", cookies)
        self.assertNotIn("pauth_tkt", cookies)

        res = self.webapp.post(
            urljoin(BASE_URL, "login"),
            {
                "__login": self.admlogin,
                "__password": self.admpassword,
                "__setauthcookie": 1,
            },
        )
        self.assertEqual(res.status_int, 303)

        cookies = self.webapp.cookiejar._cookies[urlparse(BASE_URL).netloc]["/"]
        self.assertNotIn("auth_tkt", cookies)
        self.assertIn("pauth_tkt", cookies)
        self.assertIsNotNone(cookies["pauth_tkt"].expires)

    def test_login_bad_password(self):
        self.config.i18ncompile(["en", "fr"])
        try:
            self.config._gettext_init()
            res = self.webapp.post(
                urljoin(BASE_URL, "login"),
                {"__login": self.admlogin, "__password": "empty"},
                headers={"Accept-Language": "fr"},
                status=403,
            )
        finally:
            rmtree(join(self.config.apphome, "i18n"))
        self.assertIn("\xc9chec de l&#39;authentification", res.text)

    def test_same_site_lax_by_default(self):
        res = self.webapp.post(
            urljoin(BASE_URL, "login"),
            {"__login": self.admlogin, "__password": self.admpassword},
        )
        for cookie in res.headers.getall("Set-Cookie"):
            self.assertIn("SameSite=Lax", cookie)
        self.assertGreater(len(res.headers.getall("Set-Cookie")), 0)


class LoginRedirectionTC(PyramidWebCWTC):
    anonymous_allowed = False

    def setUp(self):
        self.route_prefix = urlparse(BASE_URL).path
        return super().setUp()

    def test_redirect_to_cubicweb_page_with_arguments(self):
        res = self.webapp.get(urljoin(BASE_URL, "cwsource?args=42"), status=303)
        self.assertIn(
            f"/login?postlogin_path={self.route_prefix}cwsource%3Fargs%3D42", res.text
        )

    def test_redirect_to_cubicweb_page_without_arguments(self):
        res = self.webapp.get(urljoin(BASE_URL, "cwsource"), status=303)
        self.assertIn(f"/login?postlogin_path={self.route_prefix}cwsource", res.text)

    def test_redirect_to_main_page_with_arguments(self):
        res = self.webapp.get(urljoin(BASE_URL, "?args=42"), status=303)
        self.assertIn(
            f"/login?postlogin_path={self.route_prefix}%3Fargs%3D42", res.text
        )


class CookieParametersTC(PyramidWebCWTC):
    settings = {
        **PyramidWebCWTC.settings,
        "cubicweb.auth.authtkt.session.samesite": "None",
    }

    def test_same_site_set_from_config(self):
        res = self.webapp.post(
            urljoin(BASE_URL, "login"),
            {"__login": self.admlogin, "__password": self.admpassword},
        )
        for cookie in res.headers.getall("Set-Cookie"):
            self.assertIn("SameSite=None", cookie)
        self.assertGreater(len(res.headers.getall("Set-Cookie")), 0)


if __name__ == "__main__":
    from unittest import main

    main()
