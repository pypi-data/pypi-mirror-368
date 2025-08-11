# copyright 2023-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from logilab.common.registry import Predicate


class paginated_rset(Predicate):
    """Return 1 or more for result set with more rows than one or more page
    size.  You can specify expected number of pages to the initializer (default
    to one), and you'll get that number of pages as score if the result set is
    big enough.

    Page size is searched in (respecting order):
    * a `page_size` argument
    * a `page_size` form parameters
    * the `navigation.page-size` property (see :ref:`PersistentProperties`)
    """

    def __init__(self, nbpages=1):
        assert nbpages > 0
        self.nbpages = nbpages

    def __call__(self, cls, req, rset=None, **kwargs):
        if rset is None:
            return 0
        page_size = kwargs.get("page_size")
        if page_size is None:
            page_size = req.form.get("page_size")

            if page_size is not None:
                if page_size.isdecimal():
                    page_size = int(page_size)
                else:
                    page_size = None

            if page_size is None:
                page_size_prop = getattr(
                    cls, "page_size_property", "navigation.page-size"
                )
                page_size = req.property_value(page_size_prop)
        if len(rset) <= (page_size * self.nbpages):
            return 0
        return self.nbpages
