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
"""Associate url's path to view identifier / rql queries.

CubicWeb finds all registered URLPathEvaluators, orders them according
to their ``priority`` attribute and calls their ``evaluate_path()``
method. The first that returns something and doesn't raise a
``PathDontMatch`` exception wins.

Here is the default evaluator chain:

1. :class:`cubicweb_web.views.urlpublishing.RawPathEvaluator` handles
   unique url segments that match exactly one of the registered
   controller's *__regid__*. Urls such as */view?*, */edit?*, */json?*
   fall in that category;

2. :class:`cubicweb_web.views.urlpublishing.EidPathEvaluator` handles
   unique url segments that are eids (e.g. */1234*);

3. :class:`cubicweb_web.views.urlpublishing.URLRewriteEvaluator`
   selects all urlrewriter components, sorts them according to their
   priority, call their ``rewrite()`` method, the first one that
   doesn't raise a ``KeyError`` wins. This is where the
   :mod:`cubicweb_web.views.urlrewrite` and
   :class:`cubicweb_web.views.urlrewrite.SimpleReqRewriter` comes into
   play;

4. :class:`cubicweb_web.views.urlpublishing.RestPathEvaluator` handles
   urls based on entity types and attributes : <etype>((/<attribute
   name>])?/<attribute value>)?  This is why ``cwuser/carlos`` works;

5. :class:`cubicweb_web.views.urlpublishing.ActionPathEvaluator`
   handles any of the previous paths with an additional trailing
   "/<action>" segment, <action> being one of the registered actions'
   __regid__.


.. note::

 Actionpath executes a query whose results is lost
 because of redirecting instead of direct traversal.
"""

import logging
import warnings

from urllib.parse import urlparse

from rql import TypeResolverException

from cubicweb import RegistryException
from cubicweb_web import NotFound, Redirect, component, views
from cubicweb_web.utils import url_path_starts_with_prefix, remove_prefix_from_url_path

logger = logging.getLogger(__name__)


class PathDontMatch(Exception):
    """exception used by url evaluators to notify they can't evaluate
    a path
    """


class URLPublisherComponent(component.Component):
    """Associate url path to view identifier / rql queries, by
    applying a chain of urlpathevaluator components.

    An evaluator is a URLPathEvaluator subclass with an .evaluate_path
    method taking the request object and the path to publish as
    argument.  It will either return a publishing method identifier
    and an rql query on success or raise a `PathDontMatch` exception
    on failure. URL evaluators are called according to their
    `priority` attribute, with 0 as the greatest priority and greater
    values as lower priority. The first evaluator returning a result
    or raising something else than `PathDontMatch` will stop the
    handlers chain.
    """

    __regid__ = "urlpublisher"
    vreg = None  # XXX necessary until property for deprecation warning is on appobject

    def __init__(self, vreg, default_method="view"):
        super().__init__()
        self.vreg = vreg
        self.default_method = default_method
        evaluators = []
        for evaluatorcls in vreg["components"]["urlpathevaluator"]:
            # instantiation needed
            evaluator = evaluatorcls(self)
            evaluators.append(evaluator)
        self.evaluators = sorted(evaluators, key=lambda x: x.priority)

    def process(self, req, path):
        """Given a URL (essentially characterized by a path on the
        server, but additional information may be found in the request
        object), return a publishing method identifier
        (e.g. controller) and an optional result set.

        :type req: `cubicweb_web.request.CubicWebRequestBase`
        :param req: the request object

        :type path: str
        :param path: the path of the resource to publish. If empty, None or "/"
                     "view" is used as the default path.

        :rtype: tuple(str, `cubicweb.rset.ResultSet` or None)
        :return: the publishing method identifier and an optional result set

        :raise NotFound: if no handler is able to decode the given path
        """

        base_url = self.vreg.config["base-url"]
        route_prefix = urlparse(base_url).path.lstrip("/")

        datadir_url = self.vreg.config["datadir-url"]
        datadir_route_prefix = urlparse(datadir_url).path if datadir_url else None

        if self.vreg.config["receives-base-url-path"] and (
            route_prefix or datadir_route_prefix
        ):
            # we are not dealing with a data url configured on datadir-url
            # case of custom datadir-url is handle in DataController
            if not (
                datadir_url and url_path_starts_with_prefix(path, datadir_route_prefix)
            ):
                if not url_path_starts_with_prefix(path, route_prefix):
                    logger.warning(
                        f"Error 404: instance has recieved the request '{req}' with path '{path}' but "
                        f"it doesn't start with the route_prefix '{route_prefix}'"
                    )
                    raise NotFound()

                path = remove_prefix_from_url_path(path, route_prefix)

        elif route_prefix:
            warnings.warn(
                "in your configuration your base url "
                f"'{self.vreg.config['base-url']}' has a route prefix: "
                f"'{route_prefix}' but the option 'receives-base-url-path' is set to False.\n\n"
                "You should set it to True and avoid relying on nginx/apache for url rewritting."
            )

        parts = [part for part in path.split("/") if part != ""] or [
            self.default_method
        ]

        if not [part for part in path.split("/") if part != ""]:
            logger.debug(
                f"couldn't extract parts from url path {path}, use default method "
                f"{self.default_method} instead"
            )

        language_mode = self.vreg.config.get("language-mode")
        if (
            language_mode == "url-prefix"
            and parts
            and parts[0] in self.vreg.config.available_languages()
        ):
            # language from URL
            req.set_language(parts.pop(0))
            path = "/".join(parts)
            # if parts only contains lang, use 'view' default path
            if not parts:
                parts = (self.default_method,)
        elif language_mode in ("http-negotiation", "url-prefix"):
            # negotiated language
            lang = req.negotiated_language()
            if lang:
                if language_mode == "http-negotiation":
                    req.set_language_from_req(lang)
                else:
                    req.set_language(lang)
        origin_rql = req.form.get("rql")
        if origin_rql:
            if parts[0] in self.vreg["controllers"]:
                return parts[0], None
            return "view", None
        for evaluator in self.evaluators:
            try:
                logger.debug(
                    f"try evaluator '{evaluator}' on request {req} with '{parts}'"
                )
                pmid, rset = evaluator.evaluate_path(req, parts[:])
                break
            except PathDontMatch:
                continue
        else:
            logger.debug(f"failed to get an evaluator for url {req}, raise 404")
            raise NotFound(path)

        logger.debug(f"evaluator {evaluator} matched on request {req}")

        # Store if the final rql (changed by evaluator.evaluate_path) comes from
        # the end user (?rql=Any X Where is CWUser) or comes from a rewrite rule
        # such as SimpleReqRewriter.
        new_rql = req.form.get("rql")
        req._rql_rewritten = origin_rql != new_rql

        if pmid is None:
            pmid = self.default_method
        return pmid, rset


class URLPathEvaluator(component.Component):
    __abstract__ = True
    __regid__ = "urlpathevaluator"
    vreg = None  # XXX necessary until property for deprecation warning is on appobject

    def __init__(self, urlpublisher):
        self.urlpublisher = urlpublisher
        self.vreg = urlpublisher.vreg


class RawPathEvaluator(URLPathEvaluator):
    """handle path of the form::

    <publishing_method>?parameters...
    """

    priority = 0

    def evaluate_path(self, req, parts):
        if len(parts) == 1 and parts[0] in self.vreg["controllers"]:
            return parts[0], None
        logging.debug(
            f"{self} doesn't match request {req} because parts {parts} is not of length one "
            f"or first element of part is not in available controllers: {self.vreg['controllers']}"
        )
        raise PathDontMatch()


class EidPathEvaluator(URLPathEvaluator):
    """handle path with the form::

    <eid>
    """

    priority = 1

    def evaluate_path(self, req, parts):
        if len(parts) != 1:
            logging.debug(
                f"{self} doesn't match request {req} because parts {parts} is not of length one"
            )
            raise PathDontMatch()
        try:
            rset = req.execute("Any X WHERE X eid %(x)s", {"x": int(parts[0])})
        except ValueError as e:
            logging.debug(
                f"{self} doesn't match request {req} because exception {e} got raised while trying "
                f"to convert '{parts[0]}' into an int then runt the query "
                f"'Any X WHERE X eid {parts[0]}'"
            )
            raise PathDontMatch()
        if rset.rowcount == 0:
            logging.debug(
                f"{self} query 'Any X WHERE X eid {parts[0]}' returned nothing, raise 404"
            )
            raise NotFound()
        return None, rset


class RestPathEvaluator(URLPathEvaluator):
    """handle path with the form::

    <etype>[[/<attribute name>]/<attribute value>]*
    """

    priority = 3

    def evaluate_path(self, req, parts):
        if not (0 < len(parts) < 4):
            logging.debug(
                f"{self} doesn't match request {req} because parts not (0 < len({parts}) < 4)"
            )
            raise PathDontMatch()
        try:
            _debug_first_part = parts[0]
            etype = self.vreg.case_insensitive_etypes[parts.pop(0).lower()]
        except KeyError:
            logging.debug(
                f"{self} doesn't match request {req} because its first part "
                f"{_debug_first_part.lower()} is not in available etypes: "
                f"{self.vreg.case_insensitive_etypes}"
            )
            raise PathDontMatch()
        cls = self.vreg["etypes"].etype_class(etype)
        if parts:
            if len(parts) == 2:
                attrname = parts.pop(0).lower()
                try:
                    cls.e_schema.subject_relations[attrname]
                except KeyError:
                    logging.debug(
                        f"{self} doesn't match request {req} because its second part {attrname} "
                        f"is not in available subject_relations {cls.e_schema.subject_relations}"
                    )
                    raise PathDontMatch()
            else:
                attrname = cls.cw_rest_attr_info()[0]
            value = req.url_unquote(parts.pop(0))
            return self.handle_etype_attr(req, cls, attrname, value)
        return self.handle_etype(req, cls)

    def set_vid_for_rset(self, req, cls, rset):  # cls is there to ease overriding
        if rset.rowcount == 0:
            raise NotFound()
        if "vid" not in req.form:
            # check_table=False tells vid_from_rset not to try to use a table view if fetch_rql
            # include some non final relation
            req.form["vid"] = views.vid_from_rset(
                req, rset, req.vreg.schema, check_table=False
            )

    def handle_etype(self, req, cls):
        rset = req.execute(cls.fetch_rql(req.user))
        self.set_vid_for_rset(req, cls, rset)
        return None, rset

    def handle_etype_attr(self, req, cls, attrname, value):
        st = cls.fetch_rqlst(req.user, ordermethod=None)
        st.add_constant_restriction(st.get_variable("X"), attrname, "x", "Substitute")
        if attrname == "eid":
            try:
                rset = req.execute(st.as_string(), {"x": int(value)})
            except (ValueError, TypeResolverException):
                logging.debug(
                    f"{self} doesn't match request {req} because the query '{st.as_string()}' with "
                    f"'x = {value}' failed"
                )
                # conflicting eid/type
                raise PathDontMatch()
        else:
            rset = req.execute(st.as_string(), {"x": value})
        self.set_vid_for_rset(req, cls, rset)
        return None, rset


class URLRewriteEvaluator(URLPathEvaluator):
    """tries to find a rewrite rule to apply

    URL rewrite rule definitions are stored in URLRewriter objects
    """

    priority = 2

    def evaluate_path(self, req, parts):
        # uri <=> req._twreq.path or req._twreq.uri
        uri = req.url_unquote("/" + "/".join(parts))
        evaluators = sorted(
            self.vreg["urlrewriting"].all_objects(),
            key=lambda x: x.priority,
            reverse=True,
        )

        for rewritercls in evaluators:
            rewriter = rewritercls(req)
            try:
                logger.debug(f"{self} try to rewrite url using {rewriter}")

                # XXX we might want to chain url rewrites
                return rewriter.rewrite(req, uri)
            except KeyError:
                logger.debug(f"{self} Error: {rewriter} failed to rewrite url")
                continue
        logger.debug(f"{self} couldn't find a rewriter to rewrite url")
        raise PathDontMatch()


class ActionPathEvaluator(URLPathEvaluator):
    """handle path with the form::

    <any evaluator path>/<action>
    """

    priority = 4

    def evaluate_path(self, req, parts):
        if len(parts) < 2:
            logging.debug(
                f"{self} doesn't match request {req} because parts is len(parts) < 2"
            )
            raise PathDontMatch()
        # remove last part and see if this is something like an actions
        # if so, call
        # XXX bad smell: refactor to simpler code
        try:
            actionsreg = self.vreg["actions"]
            requested = parts.pop(-1)
            actions = actionsreg[requested]
        except RegistryException:
            logging.debug(
                f"{self} doesn't match request {req} because parts is len(parts) < 2"
            )
            raise PathDontMatch()
        for evaluator in self.urlpublisher.evaluators:
            logging.debug(f"{self} try to evaluate url using evaluator {evaluator}")

            if evaluator is self or evaluator.priority == 0:
                continue
            try:
                pmid, rset = evaluator.evaluate_path(req, parts[:])
            except PathDontMatch:
                continue
            else:
                try:
                    action = actionsreg._select_best(actions, req, rset=rset)
                    if action is not None:
                        logging.debug(
                            f"{self} evaluator {evaluator} matched, redirect to {action.url()}"
                        )
                        raise Redirect(action.url())
                except RegistryException:
                    pass  # continue searching

        logging.debug(f"{self} couldn't find any evaluator for request {req}")
        raise PathDontMatch()
