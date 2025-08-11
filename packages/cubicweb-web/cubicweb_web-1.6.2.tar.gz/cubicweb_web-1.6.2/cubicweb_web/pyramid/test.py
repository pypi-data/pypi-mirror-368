import sys
import webtest

from cubicweb.pyramid.test import PyramidCWTest, ACCEPTED_ORIGINS


class TestApp(webtest.TestApp):
    def __init__(self, *args, admin_login, admin_password, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin_login = admin_login
        self.admin_password = admin_password
        self._csrf_token = None

    def reset(self):
        super().reset()
        self._csrf_token = None

    def login(self, user=None, password=None, status=303, additional_arguments=None):
        """Log the current http session for the provided credential

        If no user is provided, admin connection are used.
        """
        if user is None:
            user = self.admin_login
            password = self.admin_password
        if password is None:
            password = user

        arguments = {"__login": user, "__password": password}
        if additional_arguments:
            arguments.update(additional_arguments)

        response = self.post("/login", arguments, status=status)

        assert response.status_int == status

        return response

    def logout(self):
        response = self.get("/logout")
        self.reset()
        return response

    def post(
        self,
        route,
        params=None,
        do_not_grab_the_crsf_token=False,
        do_not_inject_origin=False,
        **kwargs,
    ):
        if params is None:
            params = {}

        if (
            isinstance(params, dict)
            and not do_not_grab_the_crsf_token
            and "csrf_token" not in params
        ):
            csrf_token = self.get_csrf_token()

            # "application/json" doesn't submit token in form params but as header value
            if kwargs.get("headers", {}).get("Content-Type") != "application/json":
                if "csrf_token" not in params:
                    params["csrf_token"] = csrf_token
            else:
                if "headers" in kwargs:
                    kwargs["headers"]["X-CSRF-Token"] = csrf_token
                else:
                    kwargs["headers"] = {"X-CSRF-Token": csrf_token}

        if not do_not_inject_origin:
            if "headers" in kwargs and "Origin" not in kwargs["headers"]:
                kwargs["headers"]["Origin"] = "https://" + ACCEPTED_ORIGINS[0]
            elif "headers" not in kwargs:
                kwargs["headers"] = {"Origin": "https://" + ACCEPTED_ORIGINS[0]}

        return super().post(route, params, **kwargs)

    def _inject_params_to_kwargs(
        self, do_not_grab_the_crsf_token, do_not_inject_origin, **kwargs
    ):
        if not do_not_grab_the_crsf_token:
            csrf_token = self.get_csrf_token()
            if "headers" in kwargs:
                kwargs["headers"]["X-CSRF-Token"] = csrf_token
            else:
                kwargs["headers"] = {"X-CSRF-Token": csrf_token}
        if not do_not_inject_origin:
            if "headers" in kwargs and "Origin" not in kwargs["headers"]:
                kwargs["headers"]["Origin"] = "https://" + ACCEPTED_ORIGINS[0]
            elif "headers" not in kwargs:
                kwargs["headers"] = {"Origin": "https://" + ACCEPTED_ORIGINS[0]}
        return kwargs

    def post_json(
        self,
        route,
        params=None,
        do_not_grab_the_crsf_token=False,
        do_not_inject_origin=False,
        **kwargs,
    ):
        kwargs = self._inject_params_to_kwargs(
            do_not_grab_the_crsf_token, do_not_inject_origin, **kwargs
        )
        return super().post_json(route, params, **kwargs)

    def put_json(
        self,
        route,
        params=None,
        do_not_grab_the_crsf_token=False,
        do_not_inject_origin=False,
        **kwargs,
    ):
        kwargs = self._inject_params_to_kwargs(
            do_not_grab_the_crsf_token, do_not_inject_origin, **kwargs
        )
        return super().put_json(route, params, **kwargs)

    def get_csrf_token(self):
        if "csrf_token" in self.cookies:
            return self.cookies["csrf_token"]

        try:
            self.get("/")
        except webtest.app.AppError as e:
            # url doesn't exist or forbidden
            if "404" in e.args[0] or "403" in e.args[0]:
                try:
                    response = self.get("/login")
                except Exception as e:
                    sys.stderr.write(
                        f"ERROR: failed to do a GET on '/' and on '/login' to get the csrf token because: {e}\n"
                    )
                    raise
                else:
                    if "csrf_token" in self.cookies:
                        return self.cookies["csrf_token"]
                    return response.form.fields["csrf_token"][0].value
            else:
                sys.stderr.write(
                    f"ERROR: failed to do a GET on '/' to get the csrf token because: {e}\n"
                )
                raise
        else:
            return self.cookies["csrf_token"]


class PyramidCWTestWithCSRF(PyramidCWTest):
    def includeme(self, config):
        config.registry.settings["pyramid.csrf_trusted_origins"] = ACCEPTED_ORIGINS

    def setUp(self):
        # Skip CubicWebTestTC setUp
        super().setUp()
        self.includeme(self.pyramid_config)
        self.webapp = TestApp(
            self.pyramid_config.make_wsgi_app(),
            extra_environ={"wsgi.url_scheme": "https"},
            admin_login=self.admlogin,
            admin_password=self.admpassword,
        )

    def tearDown(self):
        del self.webapp
        super().tearDown()
