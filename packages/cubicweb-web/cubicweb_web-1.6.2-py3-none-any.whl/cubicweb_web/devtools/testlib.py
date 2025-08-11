import json
import re
import sys
from contextlib import contextmanager
from math import log
from urllib.parse import urlparse, parse_qs, unquote, urljoin

from cubicweb.devtools import (
    DEFAULT_EMPTY_DB_ID,
    VIEW_VALIDATORS,
    BASE_URL,
    SYSTEM_RELATIONS,
)
from cubicweb.devtools.apptest_config import (
    ApptestConfiguration,
    PostgresApptestConfiguration,
)
from cubicweb.devtools.fake import FakeCWRegistryStore, FakeConfig
from cubicweb.devtools.fill import insert_entity_queries, make_relations_queries
from cubicweb.devtools.htmlparser import (
    XMLValidator,
    VALMAP,
    XMLSyntaxValidator,
    DTDValidator,
    HTMLValidator,
)
from cubicweb.devtools.testlib import (
    CubicWebTC,
    RepoAccess,
    Session,
    not_selected,
    JsonValidator,
    line_context_filter,
    real_error_handling,
    unprotected_entities,
    CubicWebDebugger,
)
from cubicweb.pyramid.test import PyramidCWTest, CustomTestApp
from cubicweb.sobjects.notification import NotificationView
from cubicweb.uilib import eid_param
from logilab.common.decorators import cachedproperty
from logilab.common.deprecation import class_deprecated
from logilab.common.registry import NoSelectableObject
from logilab.common.testlib import Tags, nocoverage
from pyramid.csrf import LegacySessionCSRFStoragePolicy
from pyramid.interfaces import ICSRFStoragePolicy
from pyramid.testing import DummyRequest
from webtest import AppError
from yams import ValidationError

from cubicweb_web._exceptions import Redirect
from cubicweb_web.application import CubicWebPublisher
from cubicweb_web.request import CubicWebRequestBase
from cubicweb_web.webconfig import WebAllInOneConfiguration


class WebApptestConfiguration(ApptestConfiguration, WebAllInOneConfiguration):
    pass


class WebPostgresApptestConfiguration(
    PostgresApptestConfiguration, WebAllInOneConfiguration
):
    pass


class FakeRequest(CubicWebRequestBase):
    """test implementation of an cubicweb request object"""

    def __init__(self, *args, **kwargs):
        if not (args or "vreg" in kwargs):
            kwargs["vreg"] = FakeCWRegistryStore(FakeConfig(), initlog=False)
        self._http_method = kwargs.pop("method", "GET")
        self._url = kwargs.pop("url", None)
        if self._url is None:
            self._url = "view?rql=Blop&vid=blop"
        super().__init__(*args, **kwargs)
        self._session_data = {}
        self._request = DummyRequest()
        self._csrf_storage = LegacySessionCSRFStoragePolicy()
        self._request.registry.registerUtility(
            self._csrf_storage, provided=ICSRFStoragePolicy
        )

    def set_cookie(
        self, name, value, maxage=300, expires=None, secure=False, httponly=False
    ):
        super().set_cookie(name, value, maxage, expires, secure, httponly)
        cookie = self.get_response_header("Set-Cookie")
        self._headers_in.setHeader("Cookie", cookie)

    # Implement request abstract API
    def http_method(self):
        return self._http_method

    def relative_path(self, includeparams=True):
        """return the normalized path of the request (ie at least relative
        to the instance's root, but some other normalization may be needed
        so that the returned path may be used to compare to generated urls
        """
        if self._url.startswith(BASE_URL):
            url = self._url[len(BASE_URL) :]
        else:
            url = self._url
        if includeparams:
            return url
        return url.split("?", 1)[0]

    def set_request_header(self, header, value, raw=False):
        """set an incoming HTTP header (for test purpose only)"""
        if isinstance(value, str):
            value = [value]
        if raw:
            # adding encoded header is important, else page content
            # will be reconverted back to unicode and apart unefficiency, this
            # may cause decoding problem (e.g. when downloading a file)
            self._headers_in.setRawHeaders(header, value)
        else:
            self._headers_in.setHeader(header, value)  #

    def get_response_header(self, header, default=None, raw=False):
        """return output header (for test purpose only)"""
        if raw:
            return self.headers_out.getRawHeaders(header, [default])[0]
        return self.headers_out.getHeader(header, default)

    def build_url_params(self, **kwargs):
        # overriden to get predictable resultts
        args = []
        for param, values in sorted(kwargs.items()):
            if not isinstance(values, (list, tuple)):
                values = (values,)
            for value in values:
                assert value is not None
                args.append("{}={}".format(param, self.url_quote(value)))
        return "&".join(args)


class WebRepoAccess(RepoAccess):
    def __init__(self, repo, login, requestcls):
        super().__init__(repo, login)
        self.requestcls = requestcls

    @contextmanager
    def web_request(self, url=None, headers={}, method="GET", **kwargs):
        """Context manager returning a web request pre-linked to a client cnx

        To commit and rollback use::

            req.cnx.commit()
            req.cnx.rolback()
        """
        session = kwargs.pop("session", Session(self._repo, self._user))
        req = self.requestcls(
            self._repo.vreg, url=url, headers=headers, method=method, form=kwargs
        )
        with self.cnx() as cnx:
            # web request expect a session attribute on cnx referencing the web session
            cnx.session = session
            req.set_cnx(cnx)
            yield req


class WebCWTC(CubicWebTC):
    """abstract class for test using an apptest environment

    attributes:

    * `vreg`, the vregistry
    * `schema`, self.vreg.schema
    * `config`, cubicweb configuration
    * `cnx`, repoapi connection to the repository using an admin user
    * `session`, server side session associated to `cnx`
    * `app`, the cubicweb publisher (for web testing)
    * `repo`, the repository object
    * `admlogin`, login of the admin user
    * `admpassword`, password of the admin user
    * `shell`, create and use shell environment
    * `anonymous_allowed`: flag telling if anonymous browsing should be allowed
    """

    appid = "data"
    configcls = WebApptestConfiguration
    requestcls = FakeRequest
    tags = Tags("cubicweb", "cw_repo")
    test_db_id = DEFAULT_EMPTY_DB_ID

    # anonymous is logged by default in cubicweb test cases
    anonymous_allowed = True

    def __init__(self, *args, **kwargs):
        self.repo = None
        self._open_access = set()
        super(CubicWebTC, self).__init__(*args, **kwargs)

    # repository connection handling ###########################################

    def new_access(self, login):
        """provide a new RepoAccess object for a given user

        The access is automatically closed at the end of the test."""
        access = WebRepoAccess(self.repo, login, self.requestcls)
        self._open_access.add(access)
        return access

    def pviews(self, req, rset):
        return sorted(
            (a.__regid__, a.__class__)
            for a in self.vreg["views"].possible_views(req, rset=rset)
        )

    def pactions(
        self,
        req,
        rset,
        skipcategories=("addrelated", "siteactions", "useractions", "footer", "manage"),
    ):
        return [
            (a.__regid__, a.__class__)
            for a in self.vreg["actions"].poss_visible_objects(req, rset=rset)
            if a.category not in skipcategories
        ]

    def pactions_by_cats(self, req, rset, categories=("addrelated",)):
        return [
            (a.__regid__, a.__class__)
            for a in self.vreg["actions"].poss_visible_objects(req, rset=rset)
            if a.category in categories
        ]

    def pactionsdict(
        self,
        req,
        rset,
        skipcategories=("addrelated", "siteactions", "useractions", "footer", "manage"),
    ):
        res = {}
        for a in self.vreg["actions"].poss_visible_objects(req, rset=rset):
            if a.category not in skipcategories:
                res.setdefault(a.category, []).append(a.__class__)
        return res

    def action_submenu(self, req, rset, id):
        return self._test_action(self.vreg["actions"].select(id, req, rset=rset))

    def _test_action(self, action):
        class fake_menu(list):
            @property
            def items(self):
                return self

        class fake_box:
            def action_link(self, action, **kwargs):
                return (action.title, action.url())

        submenu = fake_menu()
        action.fill_menu(fake_box(), submenu)
        return submenu

    def list_views_for(self, rset):
        """returns the list of views that can be applied on `rset`"""
        req = rset.req
        only_once_vids = ("primary", "secondary", "text")
        req.data["ex"] = ValueError("whatever")
        viewsvreg = self.vreg["views"]
        for vid, views in viewsvreg.items():
            if vid[0] == "_":
                continue
            if rset.rowcount > 1 and vid in only_once_vids:
                continue
            views = [
                view
                for view in views
                if view.category != "startupview"
                and not issubclass(view, NotificationView)
                and not isinstance(view, class_deprecated)
            ]
            if views:
                try:
                    view = viewsvreg._select_best(views, req, rset=rset)
                    if view is None:
                        raise NoSelectableObject((req,), {"rset": rset}, views)
                    if view.linkable():
                        yield view
                    else:
                        not_selected(self.vreg, view)
                    # else the view is expected to be used as subview and should
                    # not be tested directly
                except NoSelectableObject:
                    continue

    def list_actions_for(self, rset):
        """returns the list of actions that can be applied on `rset`"""
        req = rset.req
        for action in self.vreg["actions"].possible_objects(req, rset=rset):
            yield action

    def list_boxes_for(self, rset):
        """returns the list of boxes that can be applied on `rset`"""
        req = rset.req
        for box in self.vreg["ctxcomponents"].possible_objects(
            req, rset=rset, view=None
        ):
            yield box

    def list_startup_views(self):
        """returns the list of startup views"""
        with self.admin_access.web_request() as req:
            for view in self.vreg["views"].possible_views(req, None):
                if view.category == "startupview":
                    yield view.__regid__
                else:
                    not_selected(self.vreg, view)

    # web ui testing utilities #################################################

    @cachedproperty
    def app(self):
        """return a cubicweb publisher"""
        publisher = CubicWebPublisher(self.repo, self.config)

        def raise_error_handler(*args, **kwargs):
            raise

        publisher.error_handler = raise_error_handler
        return publisher

    @contextmanager
    def remote_calling(self, fname, *args, **kwargs):
        """remote json call simulation"""
        args = [json.dumps(arg) for arg in args]
        with self.admin_access.web_request(
            fname=fname, pageid="123", arg=args, **kwargs
        ) as req:
            ctrl = self.vreg["controllers"].select("ajax", req)
            yield ctrl.publish(), req

    def app_handle_request(self, req):
        return self.app.core_handle(req)

    def ctrl_publish(self, req, ctrl="edit", rset=None):
        """call the publish method of the edit controller"""
        ctrl = self.vreg["controllers"].select(ctrl, req, appli=self.app)
        try:
            result = ctrl.publish(rset)
            req.cnx.commit()
        except Redirect:
            req.cnx.commit()
            raise
        return result

    @staticmethod
    def fake_form(formid, field_dict=None, entity_field_dicts=()):
        """Build _cw.form dictionnary to fake posting of some standard cubicweb form

        * `formid`, the form id, usually form's __regid__

        * `field_dict`, dictionary of name:value for fields that are not tied to an entity

        * `entity_field_dicts`, list of (entity, dictionary) where dictionary contains name:value
          for fields that are not tied to the given entity
        """
        assert (
            field_dict or entity_field_dicts
        ), "field_dict and entity_field_dicts arguments must not be both unspecified"
        if field_dict is None:
            field_dict = {}
        form = {"__form_id": formid}
        fields = []
        for field, value in field_dict.items():
            fields.append(field)
            form[field] = value

        def _add_entity_field(entity, field, value):
            entity_fields.append(field)
            form[eid_param(field, entity.eid)] = value

        for entity, field_dict in entity_field_dicts:
            if "__maineid" not in form:
                form["__maineid"] = entity.eid
            entity_fields = []
            form.setdefault("eid", []).append(entity.eid)
            _add_entity_field(entity, "__type", entity.cw_etype)
            for field, value in field_dict.items():
                _add_entity_field(entity, field, value)
            if entity_fields:
                form[eid_param("_cw_entity_fields", entity.eid)] = ",".join(
                    entity_fields
                )
        if fields:
            form["_cw_fields"] = ",".join(sorted(fields))
        return form

    @contextmanager
    def admin_request_from_url(self, url):
        """parses `url` and builds the corresponding CW-web request

        req.form will be setup using the url's query string
        """
        with self.admin_access.web_request(url=url) as req:
            if isinstance(url, str):
                url = url.encode(
                    req.encoding
                )  # req.setup_params() expects encoded strings
            querystring = urlparse(url)[-2]
            params = parse_qs(querystring)
            req.setup_params(params)
            yield req

    @staticmethod
    def _parse_location(req, location):
        try:
            path, params = location.split("?", 1)
        except ValueError:
            path = location
            params = {}
        else:

            def cleanup(p):
                return (p[0], unquote(p[1]))

            params = dict(cleanup(p.split("=", 1)) for p in params.split("&") if p)
        if path.startswith(req.base_url()):  # may be relative
            path = path[len(req.base_url()) :]
        return path, params

    def expect_redirect(self, callback, req):
        """call the given callback with req as argument, expecting to get a
        Redirect exception
        """
        try:
            callback(req)
        except Redirect as ex:
            return self._parse_location(req, ex.location)
        else:
            self.fail("expected a Redirect exception")

    def expect_redirect_handle_request(self, req, path="edit"):
        """call the publish method of the application publisher, expecting to
        get a Redirect exception
        """
        if req.relative_path(False) != path:
            req._url = path
        self.app_handle_request(req)
        self.assertTrue(300 <= req.status_out < 400, req.status_out)
        location = req.get_response_header("location")
        return self._parse_location(req, location)

    # content validation #######################################################

    # validators are used to validate (XML, DTD, whatever) view's content
    # validators availables are :
    #  DTDValidator : validates XML + declared DTD
    #  SaxOnlyValidator : guarantees XML is well formed
    #  None : do not try to validate anything
    # validators used must be imported from from.devtools.htmlparser
    content_type_validators = {
        # maps MIME type : validator name
        #
        # do not set html validators here, we need HTMLValidator for html
        # snippets
        # 'text/html': DTDValidator,
        # 'application/xhtml+xml': DTDValidator,
        "application/xml": XMLValidator,
        "text/xml": XMLValidator,
        "application/json": JsonValidator,
        "text/plain": None,
        "text/comma-separated-values": None,
        "text/x-vcard": None,
        "text/calendar": None,
        "image/png": None,
    }
    # maps vid : validator name (override content_type_validators)
    vid_validators = dict(
        (vid, VALMAP[valkey]) for vid, valkey in VIEW_VALIDATORS.items()
    )

    def view(self, vid, rset=None, req=None, template="main-template", **kwargs):
        """This method tests the view `vid` on `rset` using `template`

        If no error occurred while rendering the view, the HTML is analyzed
        and parsed.

        :returns: an instance of `cubicweb.devtools.htmlparser.PageInfo`
                  encapsulation the generated HTML
        """
        if req is None:
            assert rset is not None, "you must supply at least one of rset or req"
            req = rset.req
        req.form["vid"] = vid
        viewsreg = self.vreg["views"]
        view = viewsreg.select(vid, req, rset=rset, **kwargs)
        if template is None:  # raw view testing, no template
            viewfunc = view.render
        else:
            kwargs["view"] = view

            def viewfunc(**k):
                return viewsreg.main_template(req, template, rset=rset, **kwargs)

        return self._test_view(viewfunc, view, template, kwargs)

    def _test_view(self, viewfunc, view, template="main-template", kwargs={}):
        """this method does the actual call to the view

        If no error occurred while rendering the view, the HTML is analyzed
        and parsed.

        :returns: an instance of `cubicweb.devtools.htmlparser.PageInfo`
                  encapsulation the generated HTML
        """
        try:
            output = viewfunc(**kwargs)
        except Exception:
            # hijack exception: generative tests stop when the exception
            # is not an AssertionError
            klass, exc, tcbk = sys.exc_info()
            try:
                msg = "[%s in %s] %s" % (klass, view.__regid__, exc)
            except Exception:
                msg = "[%s in %s] undisplayable exception" % (klass, view.__regid__)
            raise AssertionError(msg).with_traceback(sys.exc_info()[-1])
        return self._check_html(output, view, template)

    def get_validator(self, view=None, content_type=None, output=None):
        if view is not None:
            try:
                return self.vid_validators[view.__regid__]()
            except KeyError:
                if content_type is None:
                    content_type = view.content_type
        if content_type is None:
            content_type = "text/html"
        if content_type in ("text/html", "application/xhtml+xml") and output:
            if output.startswith(b"<!DOCTYPE html>"):
                # only check XML well-formness since HTMLValidator isn't html5
                # compatible and won't like various other extensions
                default_validator = XMLSyntaxValidator
            elif output.startswith(b"<?xml"):
                default_validator = DTDValidator
            else:
                default_validator = HTMLValidator
        else:
            default_validator = None
        validatorclass = self.content_type_validators.get(
            content_type, default_validator
        )
        if validatorclass is None:
            return
        return validatorclass()

    @nocoverage
    def _check_html(self, output, view, template="main-template"):
        """raises an exception if the HTML is invalid"""
        output = output.strip()
        if isinstance(output, str):
            # XXX
            output = output.encode("utf-8")
        validator = self.get_validator(view, output=output)
        if validator is None:
            return output  # return raw output if no validator is defined
        if isinstance(validator, DTDValidator):
            # XXX remove <canvas> used in progress widget, unknown in html dtd
            output = re.sub("<canvas.*?></canvas>", "", output)
        return self.assertWellFormed(validator, output.strip(), context=view)

    def assertWellFormed(self, validator, content, context=None):
        try:
            return validator.parse_string(content)
        except Exception:
            # hijack exception: generative tests stop when the exception
            # is not an AssertionError
            klass, exc, tcbk = sys.exc_info()
            if context is None:
                msg = "[%s]" % (klass,)
            else:
                msg = "[%s in %s view] " % (klass, context)
            msg = msg.encode(sys.getdefaultencoding(), "replace")

            try:
                str_exc = str(exc)
            except Exception:
                str_exc = "undisplayable exception"
            msg += str_exc.encode(sys.getdefaultencoding(), "replace")
            if content is not None:
                position = getattr(exc, "position", (0,))[0]
                if position:
                    # define filter
                    if isinstance(content, str):
                        content = content.encode(sys.getdefaultencoding(), "replace")
                    content = validator.preprocess_data(content)
                    content = content.splitlines()
                    width = int(log(len(content), 10)) + 1
                    line_template = b" %" + (b"%i" % width) + b"i: %s"
                    error_line_template = b">%" + (b"%i" % width) + b"i: %s"
                    # XXX no need to iterate the whole file except to get
                    # the line number
                    content = b"\n".join(
                        (
                            line_template
                            if (idx + 1) != position
                            else error_line_template
                        )
                        % (idx + 1, line)
                        for idx, line in enumerate(content)
                        if line_context_filter(idx + 1, position)
                    )
                    msg += b"\nfor content:\n%s" % content
            exc = AssertionError(msg.decode())
            exc.__traceback__ = tcbk
            raise exc

    def assertDocTestFile(self, testfile):
        # doctest returns tuple (failure_count, test_count)
        with self.admin_access.shell() as mih:
            result = mih.process_script(testfile)
        if result[0] and result[1]:
            raise self.failureException("doctest file '%s' failed" % testfile)


class PyramidWebTestApp(CustomTestApp):
    def __init__(self, *args, admin_login, admin_password, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin_login = admin_login
        self.admin_password = admin_password
        self._ident_cookie = None
        self._csrf_token = None

    def reset(self):
        super().reset()
        self._ident_cookie = None
        self._csrf_token = None

    def post(
        self,
        route,
        params="",
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
                kwargs["headers"]["Origin"] = BASE_URL
            elif "headers" not in kwargs:
                kwargs["headers"] = {"Origin": BASE_URL}

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
                kwargs["headers"]["Origin"] = BASE_URL
            elif "headers" not in kwargs:
                kwargs["headers"] = {"Origin": BASE_URL}
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

    def delete(
        self,
        route,
        params="",
        do_not_grab_the_crsf_token=False,
        do_not_inject_origin=False,
        **kwargs,
    ):
        kwargs = self._inject_params_to_kwargs(
            do_not_grab_the_crsf_token, do_not_inject_origin, **kwargs
        )
        return super().delete(route, params, **kwargs)

    def get_csrf_token(self):
        if "csrf_token" in self.cookies:
            return self.cookies["csrf_token"]

        try:
            self.get(BASE_URL)
        except AppError as e:
            # url doesn't exist or forbidden
            if "404" in e.args[0] or "403" in e.args[0]:
                try:
                    response = self.get(urljoin(BASE_URL, "login"))
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

        response = self.post(urljoin(BASE_URL, "login"), arguments, status=status)

        assert response.status_int == status

        return response

    def logout(self):
        response = self.get(urljoin(BASE_URL, "logout"))
        self.reset()
        return response


class PyramidWebCWTC(PyramidCWTest, WebCWTC):
    settings = {
        "cubicweb.includes": ["cubicweb.pyramid.auth", "cubicweb.pyramid.session"]
    }

    def includeme(self, config):
        PyramidCWTest.includeme(self, config)
        config.registry.settings["pyramid.csrf_trusted_origins"] = BASE_URL.lstrip(
            "https://"
        )

    def url_publish(self, url, data=None):
        """takes `url`, uses application's app_resolver to find the appropriate
        controller and result set, then publishes the result.

        To simulate post of www-form-encoded data, give a `data` dictionary
        containing desired key/value associations.

        This should pretty much correspond to what occurs in a real CW server
        except the apache-rewriter component is not called.
        """
        with self.admin_request_from_url(url) as req:
            if data is not None:
                req.form.update(data)
            ctrlid, rset = self.app.url_resolver.process(req, req.relative_path(False))
            return self.ctrl_publish(req, ctrlid, rset)

    def http_publish(self, url, data=None):
        """like `url_publish`, except this returns a http response, even in case
        of errors. You may give form parameters using the `data` argument.
        """
        with self.admin_request_from_url(url) as req:
            if data is not None:
                req.form.update(data)
            with real_error_handling(self.app):
                result = self.app_handle_request(req)
            return result, req

    def build_webapp(self):
        self.webapp = PyramidWebTestApp(
            self.pyramid_config.make_wsgi_app(),
            extra_environ={"wsgi.url_scheme": "https"},
            admin_login=self.admlogin,
            admin_password=self.admpassword,
        )

    def tearDown(self):
        del self.webapp
        super().tearDown()


def how_many_dict(schema, cnx, how_many, skip):
    """given a schema, compute how many entities by type we need to be able to
    satisfy relations cardinality.

    The `how_many` argument tells how many entities of which type we want at
    least.

    Return a dictionary with entity types as key, and the number of entities for
    this type as value.
    """
    relmap = {}
    for rschema in schema.relations():
        if rschema.final:
            continue
        for subj, obj in rschema.relation_definitions:
            card = rschema.relation_definition(subj, obj).cardinality
            # if the relation is mandatory, we'll need at least as many subj and
            # obj to satisfy it
            if card[0] in "1+" and card[1] in "1?":
                # subj has to be linked to at least one obj,
                # but obj can be linked to only one subj
                # -> we need at least as many subj as obj to satisfy
                #    cardinalities for this relation
                relmap.setdefault((rschema, subj), []).append(str(obj))
            if card[1] in "1+" and card[0] in "1?":
                # reverse subj and obj in the above explanation
                relmap.setdefault((rschema, obj), []).append(str(subj))
    unprotected = unprotected_entities(schema)
    for etype in skip:  # XXX (syt) duh? explain or kill
        unprotected.add(etype)
    howmanydict = {}
    # step 1, compute a base number of each entity types: number of already
    # existing entities of this type + `how_many`
    for etype in unprotected_entities(schema, strict=True):
        howmanydict[str(etype)] = cnx.execute("Any COUNT(X) WHERE X is %s" % etype)[0][
            0
        ]
        if etype in unprotected:
            howmanydict[str(etype)] += how_many
    # step 2, augment nb entity per types to satisfy cardinality constraints,
    # by recomputing for each relation that constrained an entity type:
    #
    # new num for etype = max(current num, sum(num for possible target etypes))
    #
    # XXX we should first check there is no cycle then propagate changes
    for (rschema, etype), targets in relmap.items():
        relfactor = sum(howmanydict[e] for e in targets)
        howmanydict[str(etype)] = max(relfactor, howmanydict[etype])
    return howmanydict


class AutoPopulateTest(WebCWTC):
    """base class for test with auto-populating of the database"""

    __abstract__ = True

    test_db_id = "autopopulate"

    tags = WebCWTC.tags | Tags("autopopulated")

    pdbclass = CubicWebDebugger
    # this is a hook to be able to define a list of rql queries
    # that are application dependent and cannot be guessed automatically
    application_rql = []

    no_auto_populate = ()
    ignored_relations = set()

    def to_test_etypes(self):
        return unprotected_entities(self.schema, strict=True)

    def custom_populate(self, how_many, cnx):
        pass

    def post_populate(self, cnx):
        pass

    @nocoverage
    def auto_populate(self, how_many):
        """this method populates the database with `how_many` entities
        of each possible type. It also inserts random relations between them
        """
        with self.admin_access.cnx() as cnx:
            with cnx.security_enabled(read=False, write=False):
                self._auto_populate(cnx, how_many)
                cnx.commit()

    def _auto_populate(self, cnx, how_many):
        self.custom_populate(how_many, cnx)
        vreg = self.vreg
        howmanydict = how_many_dict(self.schema, cnx, how_many, self.no_auto_populate)
        for etype in unprotected_entities(self.schema):
            if etype in self.no_auto_populate:
                continue
            nb = howmanydict.get(etype, how_many)
            for rql, args in insert_entity_queries(etype, self.schema, vreg, nb):
                cnx.execute(rql, args)
        edict = {}
        for etype in unprotected_entities(self.schema, strict=True):
            rset = cnx.execute("%s X" % etype)
            edict[str(etype)] = set(row[0] for row in rset.rows)
        existingrels = {}
        ignored_relations = SYSTEM_RELATIONS | self.ignored_relations
        for rschema in self.schema.relations():
            if rschema.final or rschema in ignored_relations or rschema.rule:
                continue
            rset = cnx.execute("DISTINCT Any X,Y WHERE X %s Y" % rschema)
            existingrels.setdefault(rschema.type, set()).update((x, y) for x, y in rset)
        q = make_relations_queries(
            self.schema, edict, cnx, ignored_relations, existingrels=existingrels
        )
        for rql, args in q:
            try:
                cnx.execute(rql, args)
            except ValidationError as ex:
                # failed to satisfy some constraint
                print("error in automatic db population", ex)
                cnx.commit_state = None  # reset uncommitable flag
        self.post_populate(cnx)

    def iter_individual_rsets(self, etypes=None, limit=None):
        etypes = etypes or self.to_test_etypes()
        with self.admin_access.web_request() as req:
            for etype in etypes:
                if limit:
                    rql = "Any X LIMIT %s WHERE X is %s" % (limit, etype)
                else:
                    rql = "Any X WHERE X is %s" % etype
                rset = req.execute(rql)
                for row in range(len(rset)):
                    if limit and row > limit:
                        break
                    # XXX iirk
                    rset2 = rset.limit(limit=1, offset=row)
                    yield rset2

    def iter_automatic_rsets(self, limit=10):
        """generates basic resultsets for each entity type"""
        etypes = self.to_test_etypes()
        if not etypes:
            return
        with self.admin_access.web_request() as req:
            for etype in etypes:
                yield req.execute("Any X LIMIT %s WHERE X is %s" % (limit, etype))
            etype1 = etypes.pop()
            try:
                etype2 = etypes.pop()
            except KeyError:
                etype2 = etype1
            # test a mixed query (DISTINCT/GROUP to avoid getting duplicate
            # X which make muledit view failing for instance (html validation fails
            # because of some duplicate "id" attributes)
            yield req.execute(
                "DISTINCT Any X, MAX(Y) GROUPBY X WHERE X is %s, Y is %s"
                % (etype1, etype2)
            )
            # test some application-specific queries if defined
            for rql in self.application_rql:
                yield req.execute(rql)

    def _test_everything_for(self, rset):
        """this method tries to find everything that can be tested
        for `rset` and yields a callable test (as needed in generative tests)
        """
        propdefs = self.vreg["propertydefs"]
        # make all components visible
        for k, v in propdefs.items():
            if k.endswith("visible") and not v["default"]:
                propdefs[k]["default"] = True
        for view in self.list_views_for(rset):
            backup_rset = rset.copy(rset.rows, rset.description)
            with self.subTest(name=self._testname(rset, view.__regid__, "view")):
                self.view(
                    view.__regid__, rset, rset.req.reset_headers(), "main-template"
                )
            # We have to do this because some views modify the
            # resultset's syntax tree
            rset = backup_rset
        for action in self.list_actions_for(rset):
            with self.subTest(name=self._testname(rset, action.__regid__, "action")):
                self._test_action(action)
        for box in self.list_boxes_for(rset):
            self.w_list = []
            w = self.mocked_up_w
            with self.subTest(name=self._testname(rset, box.__regid__, "box")):
                box.render(w)

    def mocked_up_w(self, text, *args, escape=True):
        # we don't care about escape here since we are in a test context
        if not args:
            self.w_list.append(text)
        elif isinstance(args[0], dict):
            self.w_list.append(text % args[0])
        else:
            self.w_list.append(text % args)

    @staticmethod
    def _testname(rset, objid, objtype):
        return "%s_%s_%s" % ("_".join(rset.column_types(0)), objid, objtype)


class AutomaticWebTest(AutoPopulateTest):
    """import this if you wan automatic tests to be ran"""

    tags = AutoPopulateTest.tags | Tags("web", "generated")

    def setUp(self):
        if self.__class__ is AutomaticWebTest:
            # Prevent direct use of AutomaticWebTest to avoid database caching
            # issues.
            return
        super().setUp()

        # access to self.app for proper initialization of the authentication
        # machinery (else some views may fail)
        self.app

    def test_one_each_config(self):
        self.auto_populate(1)
        for rset in self.iter_automatic_rsets(limit=1):
            self._test_everything_for(rset)

    def test_ten_each_config(self):
        self.auto_populate(10)
        for rset in self.iter_automatic_rsets(limit=10):
            self._test_everything_for(rset)

    def test_startup_views(self):
        for vid in self.list_startup_views():
            with self.admin_access.web_request() as req:
                with self.subTest(vid=vid):
                    self.view(vid, None, req)
