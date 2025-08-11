from urllib.parse import urljoin

from cubicweb.devtools import BASE_URL
from cubicweb_web.devtools.testlib import PyramidWebCWTC
from cubicweb_web.views.basecontrollers import ViewController


class ControllerWithCSRFCheckDisabled(ViewController):
    require_csrf = False


class CustomControllerWithoutCSRFTest(PyramidWebCWTC):
    def test_controller_without_csrf(self):
        self.webapp.login()
        url = urljoin(BASE_URL, "cwuser", self.webapp.admin_login)
        kwargs = {
            "do_not_grab_the_crsf_token": True,
            "do_not_inject_origin": True,
        }

        # failed with 400 because we didn't send the csrf token
        self.webapp.post(
            url,
            params={},
            status=400,
            **kwargs,
        )

        # activate the custom controller that has require_csrf = False
        self.vreg.register_and_replace(ControllerWithCSRFCheckDisabled, ViewController)

        # request works without the csrf token
        self.webapp.post(
            url,
            params="test",
            **kwargs,
        )
        self.webapp.post(
            url,
            params={},
            **kwargs,
        )
        self.webapp.post(
            url,
            params=[],
            **kwargs,
        )

        # request works without the csrf token
        self.webapp.post_json(
            url,
            params={},
            **kwargs,
        )
        self.webapp.post_json(
            url,
            params=[],
            **kwargs,
        )

        # request works without the csrf token
        self.webapp.put_json(
            url,
            params={},
            **kwargs,
        )


class CSRFTest(PyramidWebCWTC):
    def test_pyramid_route_csrf_token_is_present(self):
        res = self.webapp.get(urljoin(BASE_URL, "login"))
        self.assertIn("csrf_token", res.form.fields)

    def test_pyramid_route_csrf_bad_token(self):
        self.webapp.post(
            urljoin(BASE_URL, "login"),
            {
                "__login": self.admlogin,
                "__password": self.admpassword,
                "csrf_token": "bad_token",
            },
            status=400,
        )

    def test_pyramid_route_csrf_no_token(self):
        self.webapp.post(
            urljoin(BASE_URL, "login"),
            {
                "__login": self.admlogin,
                "__password": self.admpassword,
                "csrf_token": None,
            },
            status=400,
        )

    def test_pyramid_route_csrf_bad_origin(self):
        self.webapp.post(
            urljoin(BASE_URL, "login"),
            {"__login": self.admlogin, "__password": self.admpassword},
            headers={"Origin": "bad_origin.net"},
            status=400,
        )

    def test_pyramid_route_csrf_no_origin(self):
        self.webapp.post(
            urljoin(BASE_URL, "login"),
            {"__login": self.admlogin, "__password": self.admpassword},
            do_not_inject_origin=True,
            status=400,
        )

    def test_cubicweb_route_csrf_token_is_present(self):
        self.webapp.post(
            urljoin(BASE_URL, "validateform"),
            {
                "__form_id": "edition",
                "__type:6": "CWUser",
                "eid": 6,
                "firstname-subject:6": "loutre",
            },
        )

    def test_cubicweb_route_no_csrf_token(self):
        self.webapp.post(
            urljoin(BASE_URL, "validateform"),
            {
                "__form_id": "edition",
                "__type:6": "CWUser",
                "eid": 6,
                "firstname-subject:6": "loutre",
                "csrf_token": None,
            },
            status=400,
        )

    def test_cubicweb_route_bad_origin(self):
        self.webapp.post(
            urljoin(BASE_URL, "validateform"),
            {
                "__form_id": "edition",
                "__type:6": "CWUser",
                "eid": 6,
                "firstname-subject:6": "loutre",
            },
            headers={"Origin": "bad_origin.net"},
            status=400,
        )

    def test_cubicweb_route_csrf_no_origin(self):
        self.webapp.post(
            urljoin(BASE_URL, "validateform"),
            {
                "__form_id": "edition",
                "__type:6": "CWUser",
                "eid": 6,
                "firstname-subject:6": "loutre",
            },
            do_not_inject_origin=True,
            status=400,
        )

    def test_pyramid_route_csrf_token_post_json(self):
        self.webapp.login()
        self.webapp.post_json(
            urljoin(BASE_URL, "cwuser", self.webapp.admin_login),
            params={},
            status=200,
        )

    def test_pyramid_route_csrf_token_put_json(self):
        self.webapp.login()
        self.webapp.put_json(
            urljoin(BASE_URL, "cwuser", self.webapp.admin_login),
            params={},
            status=200,
        )
