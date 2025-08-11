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

import hashlib

from cubicweb_web.views import tableview
from cubicweb.server import Service
from cubicweb.predicates import has_related_entities, match_user_groups

from cubicweb_web.views.ajaxcontroller import ajaxfunc
from cubicweb_web.views.ibreadcrumbs import IBreadCrumbsAdapter
from cubicweb_web.views import xmlrss


xmlrss.RSSIconBox.visible = True


class TestService(Service):
    __regid__ = "test_service"
    __select__ = Service.__select__ & match_user_groups("managers")
    passed_here = []

    def call(self, msg):
        self.passed_here.append(msg)
        return "babar"


def _recursive_replace_stream_by_md5(tree):
    """Search for streams (i.e. object that have a 'read' method) in a tree
    (whose branches are lists or tuples), and substitute them by their md5 hash,
    leaving other leafs identical. A copy of the tree with only lists as
    branches is returned.
    """
    if not isinstance(tree, (list, tuple)):
        if hasattr(tree, "read"):
            return hashlib.md5(tree.read()).hexdigest()
        if hasattr(tree, "file"):
            return tree.filename, hashlib.md5(tree.file.read()).hexdigest()
        return tree
    else:
        return [_recursive_replace_stream_by_md5(value) for value in tree]


@ajaxfunc(output_type="json")
def fileupload(self):
    """Return a json copy of the web request form in which uploaded files
    are read and the received streams are replaced by their md5 hash.
    """
    try:
        result_dict = {}
        for key, value in self._cw.form.items():
            result_dict[key] = _recursive_replace_stream_by_md5(value)
        return result_dict
    except Exception as ex:
        import traceback as tb

        tb.print_exc(ex)


class FolderIBreadCrumbsAdapter(IBreadCrumbsAdapter):
    __select__ = IBreadCrumbsAdapter.__select__ & has_related_entities("filed_under")

    def parent_entity(self):
        return self.entity.filed_under[0]


class CustomRsetTableView(tableview.RsetTableView):
    __regid__ = "mytable"
