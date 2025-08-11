# copyright 2017-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2014-2016 UNLISH S.A.S. (Montpellier, FRANCE), all rights reserved.
#
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

"""
Url redirection using pyramid
-----------------------------

This module allow to define redirection rules used by pyramid before route selection.

Each rule has to be added with `add_rewriting_rule` method in a pyramid `includeme`
function to be used.

Example of usage :

.. code-block:: ini

    def includeme(config):
        config.add_redirection_rule(r'<a regex>', callback_method, keep_query_components)


The callback_method takes four arguments:

- a pyramid request ;
- the url that has to be matched by the rule ;
- a dictionnary containing all the named subgroups of the regex match ;
- a boolean to decide if we want to keep parameters of the query after the
  redirection (True by default).

It must return a string corresponding to the new url.
"""
import re

from pyramid.httpexceptions import HTTPSeeOther


def add_redirection_rule(config, rule, callback_method, keep_query_component=True):
    """
    Declare a pyramid directive allowing to add a redirection rule.
    Each rewriting rule can then be added in the `includeme` at the end of the file
    by using `config.add_redirection_rule(rule, callback_method`.
    :param config: pyramid configuration, used by pyramid.
    :param rule: a regex used to match uri.
    :param callback_method: a method which return the redirected uri.
    :param keep_query_component: if we want to keep the query component of the URL (the
    part after the first "?") after redirection.
    """
    if not hasattr(config.registry, "redirection_rules"):
        config.registry.redirection_rules = []
    config.registry.redirection_rules.append(
        (re.compile(rule), callback_method, keep_query_component)
    )


def url_redirection_tween_factory(handler, registry):
    """A pyramid tween handler that browse each `redirection_rules` added with
    `add_redirection_rule` directive to find if the current path matches a rule.
    """

    if not hasattr(registry, "redirection_rules"):
        return handler

    def url_redirection_tween(request):
        for (
            rule,
            callback_method,
            keep_query_component,
        ) in request.registry.redirection_rules:
            path = request.path_info
            match = rule.match(path)
            if match:
                redirection_path = callback_method(request, path, match.groupdict())
                if redirection_path and keep_query_component and request.query_string:
                    raise HTTPSeeOther(f"{redirection_path}?{request.query_string}")
                if redirection_path:
                    raise HTTPSeeOther(redirection_path)
        return handler(request)

    return url_redirection_tween


def includeme(config):
    """Add `add_redirection_rule` pyramid directive and `url_redirection_tween`
    pyramid tween handler to the pyramid configuration."""
    config.add_directive("add_redirection_rule", add_redirection_rule)
    config.add_tween(
        "cubicweb_web.pyramid.url_redirection.url_redirection_tween_factory"
    )
