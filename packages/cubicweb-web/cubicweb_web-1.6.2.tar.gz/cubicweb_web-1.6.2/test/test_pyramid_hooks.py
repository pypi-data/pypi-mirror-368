from urllib.parse import urlparse, urljoin

from cubicweb.devtools import BASE_URL
from cubicweb_web.devtools.testlib import PyramidWebCWTC


def set_language(request):
    lang = request.POST.get("lang", None)
    cnx = request.cw_cnx
    if lang is None:
        cnx.execute(
            "DELETE CWProperty X WHERE X for_user U, U eid %(u)s", {"u": cnx.user.eid}
        )
    else:
        cnx.user.set_property("ui.language", lang)
    cnx.commit()

    request.response.text = cnx.user.properties.get("ui.language", "")
    return request.response


def add_remove_group(request):
    add_remove = request.POST["add_remove"]
    cnx = request.cw_cnx
    if add_remove == "add":
        cnx.execute(
            'SET U in_group G WHERE G name "users", U eid %(u)s', {"u": cnx.user.eid}
        )
    else:
        cnx.execute(
            'DELETE U in_group G WHERE G name "users", U eid %(u)s', {"u": cnx.user.eid}
        )
    cnx.commit()

    request.response.text = ",".join(sorted(cnx.user.groups))
    return request.response


class SessionSyncHoooksTC(PyramidWebCWTC):
    def includeme(self, config):
        config.route_prefix = urlparse(BASE_URL).path
        for view in (set_language, add_remove_group):
            config.add_route(view.__name__, "/" + view.__name__)
            config.add_view(view, route_name=view.__name__)

        super().includeme(config)

    def setUp(self):
        super().setUp()
        with self.admin_access.repo_cnx() as cnx:
            self.admin_eid = cnx.user.eid

    def test_sync_props(self):
        # grab the crsf token before login
        response = self.webapp.get(urljoin(BASE_URL, "login"))
        csrf_token = response.forms[0].fields["csrf_token"][0].value

        # initialize a pyramid session using admin credentials
        res = self.webapp.post(
            urljoin(BASE_URL, "login"),
            {"__login": self.admlogin, "__password": self.admpassword},
        )
        self.assertEqual(res.status_int, 303)
        # new property
        res = self.webapp.post(
            urljoin(BASE_URL, "set_language"), {"lang": "fr", "csrf_token": csrf_token}
        )
        self.assertEqual(res.text, "fr")
        # updated property
        res = self.webapp.post(
            urljoin(BASE_URL, "set_language"), {"lang": "en", "csrf_token": csrf_token}
        )
        self.assertEqual(res.text, "en")
        # removed property
        res = self.webapp.post(
            urljoin(BASE_URL, "set_language"), {"csrf_token": csrf_token}
        )
        self.assertEqual(res.text, "")

    def test_sync_groups(self):
        self.webapp.login(self.admlogin, self.admpassword)
        # XXX how to get pyramid request using this session?
        res = self.webapp.post(
            urljoin(BASE_URL, "add_remove_group"), {"add_remove": "add"}
        )
        self.assertEqual(res.text, "managers,users")
        res = self.webapp.post(
            urljoin(BASE_URL, "add_remove_group"), {"add_remove": "remove"}
        )
        self.assertEqual(res.text, "managers")


if __name__ == "__main__":
    from unittest import main

    main()
