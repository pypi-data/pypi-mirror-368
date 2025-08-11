from cubicweb_web.devtools.testlib import PyramidWebCWTC


def redirect_rule(req, url, matchdict):
    return f"{url}/test"


class UrlRedirectTC(PyramidWebCWTC):
    def includeme(self, config):
        config.add_redirection_rule(r"^/\w+$", redirect_rule)
        config.add_redirection_rule(
            r"^/do-not-keep-query", redirect_rule, keep_query_component=False
        )

    def test_redirect_rules(self):
        res = self.webapp.get("/123456", status="*")
        self.assertEqual(res.status_int, 303)
        self.assertEqual(res.location, f"{res.request.application_url}/123456/test")

    def test_redirect_rules_with_param(self):
        res = self.webapp.get(
            "/123456", params={"poulet": "frie", "frite": "non"}, status="*"
        )
        self.assertEqual(res.status_int, 303)
        self.assertEqual(
            res.location,
            f"{res.request.application_url}/123456/test?poulet=frie&frite=non",
        )
        res = self.webapp.get(
            "/do-not-keep-query", params={"poulet": "frie", "frite": "non"}, status="*"
        )
        self.assertEqual(res.status_int, 303)
        self.assertEqual(
            res.location,
            f"{res.request.application_url}/do-not-keep-query/test",
        )


if __name__ == "__main__":
    import unittest

    unittest.main()
