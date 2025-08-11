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

from os.path import join

from logilab.common.testlib import unittest_main, TestCase

from cubicweb import CW_SOFTWARE_ROOT as BASE
from cubicweb.cwvreg import CWRegistryStore, UnknownProperty
from cubicweb.entity import EntityAdapter

from cubicweb_web.devtools.testlib import WebCWTC, WebApptestConfiguration


class YesSchema:
    def __contains__(self, something):
        return True


class VRegistryTC(TestCase):
    def setUp(self):
        config = WebApptestConfiguration("data", __file__)
        self.vreg = CWRegistryStore(config)
        config.bootstrap_cubes()
        self.vreg.schema = config.load_schema()
        self.cubicweb_web_dir = self.vreg.config.cube_dir("web")
        self.webviewsdir = join(self.cubicweb_web_dir, "views")

    def test_load_interface_based_vojects(self):
        self.vreg.init_registration([self.webviewsdir])
        self.vreg.load_file(
            join(BASE, "entities", "__init__.py"), "cubicweb.entities.__init__"
        )
        self.vreg.load_file(
            join(self.webviewsdir, "idownloadable.py"),
            "cubicweb_web.views.idownloadable",
        )
        self.vreg.load_file(
            join(self.webviewsdir, "primary.py"), "cubicweb_web.views.primary"
        )
        self.assertEqual(len(self.vreg["views"]["primary"]), 2)
        self.vreg.initialization_completed()
        self.assertEqual(len(self.vreg["views"]["primary"]), 1)

    def test_load_subinterface_based_appobjects(self):
        self.vreg.register_modnames(["cubicweb_web.views.idownloadable"])
        # check downloadlink was kicked
        self.assertFalse(self.vreg["views"].get("downloadlink"))
        # we've to emulate register_objects to add custom MyCard objects
        path = [
            join(BASE, "entities", "__init__.py"),
            join(BASE, "entities", "adapters.py"),
            join(self.cubicweb_web_dir, "views", "idownloadable.py"),
        ]
        filemods = self.vreg.init_registration(path, None)
        for filepath, modname in filemods:
            try:
                self.vreg.load_file(filepath, modname)
            except ImportError:
                pass

        class CardIDownloadableAdapter(EntityAdapter):
            __regid__ = "IDownloadable"

        self.vreg._loadedmods[__name__] = {}
        self.vreg.register(CardIDownloadableAdapter)
        self.vreg.initialization_completed()
        # check progressbar isn't kicked
        self.assertEqual(len(self.vreg["views"]["downloadlink"]), 1)

    def test_properties(self):
        self.vreg.reset()
        self.assertNotIn("system.version.cubicweb", self.vreg["propertydefs"])
        self.assertTrue(self.vreg.property_info("system.version.cubicweb"))
        self.assertRaises(
            UnknownProperty, self.vreg.property_info, "a.non.existent.key"
        )


class CWVregTC(WebCWTC):
    def test_property_default_overriding(self):
        # see data/views.py
        from cubicweb_web.views.xmlrss import RSSIconBox

        self.assertEqual(
            self.vreg.property_info(RSSIconBox._cwpropkey("visible"))["default"], True
        )


if __name__ == "__main__":
    unittest_main()
