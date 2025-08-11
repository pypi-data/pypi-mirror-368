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
"""unit tests for cubicweb.web.views.entities module"""
from cubicweb import Binary
from cubicweb.devtools import BASE_URL
from cubicweb.entity import can_use_rest_path
from cubicweb.uilib import soup2xhtml
from cubicweb.entities.test.unittest_base import BaseEntityTC

from cubicweb_web.devtools.testlib import WebCWTC


class HTMLtransformTC(BaseEntityTC):
    def test_sanitized_html(self):
        with self.admin_access.repo_cnx() as cnx:
            c = cnx.create_entity(
                "Company",
                name="Babar",
                description="""
Title
=====

Elephant management best practices.

.. raw:: html

   <script>alert("coucou")</script>
""",
                description_format="text/rest",
            )
            cnx.commit()
            c.cw_clear_all_caches()
            self.assertIn(
                "alert", c.printable_value("description", format="text/plain")
            )
            self.assertNotIn(
                "alert", c.printable_value("description", format="text/html")
            )


class EntityCWTC(WebCWTC):
    def setUp(self):
        super().setUp()
        self.backup_dict = {}
        for cls in self.vreg["etypes"].iter_classes():
            self.backup_dict[cls] = (cls.fetch_attrs, cls.cw_fetch_order)

    def tearDown(self):
        super().tearDown()
        for cls in self.vreg["etypes"].iter_classes():
            cls.fetch_attrs, cls.cw_fetch_order = self.backup_dict[cls]

    def test_markdown_printable_value_string(self):
        with self.admin_access.web_request() as req:
            e = req.create_entity(
                "Card",
                title="rest markdown",
                content='This is [an example](http://example.com/ "Title") inline link`',
                content_format="text/markdown",
            )
            self.assertEqual(
                '<p>This is <a href="http://example.com/" '
                'title="Title">an example</a> inline link`</p>',
                e.printable_value("content"),
            )

    def test_printable_value_string(self):
        with self.admin_access.web_request() as req:
            e = req.create_entity(
                "Card",
                title="rest test",
                content="du :eid:`1:*ReST*`",
                content_format="text/rest",
            )
            self.assertEqual(
                e.printable_value("content"),
                f'<p>du <a class="reference" href="{BASE_URL}cwsource/system">*ReST*</a></p>',
            )
            e.cw_attr_cache["content"] = (
                'du <em>html</em> <ref rql="CWUser X">users</ref>'
            )
            e.cw_attr_cache["content_format"] = "text/html"
            self.assertEqual(
                e.printable_value("content"),
                f'du <em>html</em> <a href="{BASE_URL}view?rql=CWUser%20X">users</a>',
            )
            e.cw_attr_cache["content"] = "du *texte*"
            e.cw_attr_cache["content_format"] = "text/plain"
            self.assertEqual(
                e.printable_value("content").replace("\n", ""), "<p>du *texte*<br/></p>"
            )
            e.cw_attr_cache["title"] = "zou"
            e.cw_attr_cache[
                "content"
            ] = """\
a title
=======
du :eid:`1:*ReST*`"""
            e.cw_attr_cache["content_format"] = "text/rest"
            self.assertEqual(
                e.printable_value("content", format="text/plain"),
                e.cw_attr_cache["content"],
            )

            e.cw_attr_cache["content"] = "<b>yo (zou éà ;)</b>"
            e.cw_attr_cache["content_format"] = "text/html"
            self.assertEqual(
                e.printable_value("content", format="text/plain").strip(),
                "**yo (zou éà ;)**",
            )

    def test_printable_value_bytes(self):
        with self.admin_access.web_request() as req:
            e = req.create_entity(
                "FakeFile",
                data=Binary(b"lambda x: 1"),
                data_format="text/x-python",
                data_encoding="ascii",
                data_name="toto.py",
            )
            from cubicweb import mttransforms

            if mttransforms.HAS_PYGMENTS_TRANSFORMS:
                import pygments

                if tuple(int(i) for i in pygments.__version__.split(".")[:3]) >= (
                    2,
                    1,
                    1,
                ):
                    span = "<span/>"
                else:
                    span = ""
                if tuple(int(i) for i in pygments.__version__.split(".")[:2]) >= (1, 3):
                    mi = "mi"
                else:
                    mi = "mf"

                self.assertEqual(
                    e.printable_value("data"),
                    """<div class="highlight"><pre>%s<span class="k">lambda</span> <span class="n">x</span><span class="p">:</span> <span class="%s">1</span>
</pre></div>"""
                    % (span, mi),
                )
            else:
                self.assertEqual(
                    e.printable_value("data"),
                    """<pre class="python">
    <span style="color: #C00000;">lambda</span> <span style="color: #000000;">x</span><span style="color: #0000C0;">:</span> <span style="color: #0080C0;">1</span>
</pre>""",
                )

            e = req.create_entity(
                "FakeFile",
                data=Binary("*héhéhé*".encode()),
                data_format="text/rest",
                data_encoding="utf-8",
                data_name="toto.txt",
            )
            e = req.entity_from_eid(e.eid)
            self.assertEqual(e.printable_value("data"), "<p><em>héhéhé</em></p>")

        with self.admin_access.web_request() as req:
            e = req.create_entity(
                "FakeFile",
                data=Binary("*héhéhé*".encode()),
                data_format="text/rest",
                data_encoding="utf-8",
                data_name="toto.txt",
            )
            self.assertEqual(e.printable_value("data"), "<p><em>héhéhé</em></p>")

    def test_printable_value_bad_html(self):
        """make sure we don't crash if we try to render invalid XHTML strings"""
        with self.admin_access.web_request() as req:
            e = req.create_entity(
                "Card",
                title="bad html",
                content="<div>R&D<br>",
                content_format="text/html",
            )
            tidy = lambda x: x.replace("\n", "")
            self.assertEqual(
                tidy(e.printable_value("content")), "<div>R&amp;D<br/></div>"
            )
            e.cw_attr_cache["content"] = "yo !! R&D <div> pas fermé"
            self.assertEqual(
                tidy(e.printable_value("content")),
                "yo !! R&amp;D <div> pas fermé</div>",
            )
            e.cw_attr_cache["content"] = "R&D"
            self.assertEqual(tidy(e.printable_value("content")), "R&amp;D")
            e.cw_attr_cache["content"] = "R&D;"
            self.assertEqual(tidy(e.printable_value("content")), "R&amp;D;")
            e.cw_attr_cache["content"] = "yo !! R&amp;D <div> pas fermé"
            self.assertEqual(
                tidy(e.printable_value("content")),
                "yo !! R&amp;D <div> pas fermé</div>",
            )
            e.cw_attr_cache["content"] = "été <div> été"
            self.assertEqual(tidy(e.printable_value("content")), "été <div> été</div>")
            e.cw_attr_cache["content"] = "C&apos;est un exemple s&eacute;rieux"
            self.assertEqual(
                tidy(e.printable_value("content")), "C'est un exemple sérieux"
            )
            # make sure valid xhtml is left untouched
            e.cw_attr_cache["content"] = "<div>R&amp;D<br/></div>"
            self.assertEqual(e.printable_value("content"), e.cw_attr_cache["content"])
            e.cw_attr_cache["content"] = "<div>été</div>"
            self.assertEqual(e.printable_value("content"), e.cw_attr_cache["content"])
            e.cw_attr_cache["content"] = "été"
            self.assertEqual(e.printable_value("content"), e.cw_attr_cache["content"])
            e.cw_attr_cache["content"] = "hop\r\nhop\nhip\rmomo"
            self.assertEqual(e.printable_value("content"), "hop\nhop\nhip\nmomo")

    def test_printable_value_bad_html_ms(self):
        with self.admin_access.web_request() as req:
            e = req.create_entity(
                "Card",
                title="bad html",
                content="<div>R&D<br>",
                content_format="text/html",
            )
            e.cw_attr_cache["content"] = (
                '<div x:foo="bar">ms orifice produces weird html</div>'
            )
            # Caution! current implementation of soup2xhtml strips first div element
            content = soup2xhtml(e.printable_value("content"), "utf-8")
            self.assertMultiLineEqual(
                content, "<div>ms orifice produces weird html</div>"
            )

    def test_fulltextindex(self):
        with self.admin_access.web_request() as req:
            e = self.vreg["etypes"].etype_class("FakeFile")(req)
            e.cw_attr_cache["description"] = "du <em>html</em>"
            e.cw_attr_cache["description_format"] = "text/html"
            e.cw_attr_cache["data"] = Binary(b"some <em>data</em>")
            e.cw_attr_cache["data_name"] = "an html file"
            e.cw_attr_cache["data_format"] = "text/html"
            e.cw_attr_cache["data_encoding"] = "ascii"
            e._cw.transaction_data.clear()
            words = e.cw_adapt_to("IFTIndexable").get_words()
            words["C"].sort()
            self.assertEqual(
                {"C": sorted(["an", "html", "file", "du", "html", "some", "data"])},
                words,
            )

    def test_rest_path(self):
        with self.admin_access.web_request() as req:
            note = req.create_entity("Note", type="z")
            self.assertEqual(note.rest_path(), "note/%s" % note.eid)
            # unique attr
            tag = req.create_entity("Tag", name="x")
            self.assertEqual(tag.rest_path(), "tag/x")
            # test explicit rest_attr
            person = req.create_entity("Personne", prenom="john", nom="doe")
            self.assertEqual(person.rest_path(), "personne/doe")
            # ambiguity test
            person2 = req.create_entity("Personne", prenom="remi", nom="doe")
            person.cw_clear_all_caches()
            self.assertEqual(person.rest_path(), str(person.eid))
            self.assertEqual(person2.rest_path(), str(person2.eid))

            # test explicit int rest_attr
            janze = req.create_entity("Ville", insee=35150)
            self.assertEqual(janze.rest_path(), "ville/35150")

            # unique attr with None value (nom in this case)
            friend = req.create_entity("Ami", prenom="bob")
            self.assertEqual(friend.rest_path(), str(friend.eid))
            # 'ref' below is created without the unique but not required
            # attribute, make sur that the unique _and_ required 'ean' is used
            # as the rest attribute
            ref = req.create_entity("Reference", ean="42-1337-42")
            self.assertEqual(ref.rest_path(), "reference/42-1337-42")

    def test_can_use_rest_path(self):
        self.assertTrue(can_use_rest_path("zobi"))
        # don't use rest if we have /, ? or & in the path (breaks mod_proxy)
        self.assertFalse(can_use_rest_path("zo/bi"))
        self.assertFalse(can_use_rest_path("zo&bi"))
        self.assertFalse(can_use_rest_path("zo?bi"))

    def test_request_cache(self):
        with self.admin_access.web_request() as req:
            user = req.execute('CWUser X WHERE X login "admin"').get_entity(0, 0)
            state = user.in_state[0]
            samestate = req.execute('State X WHERE X name "activated"').get_entity(0, 0)
            self.assertIs(state, samestate)


if __name__ == "__main__":
    from logilab.common.testlib import unittest_main

    unittest_main()
