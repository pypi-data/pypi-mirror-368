import json

from cubicweb.utils import UStringIO
from logilab.mtconverter import xml_escape


class HTMLHead(UStringIO):
    """wraps HTML header's stream

    Request objects use a HTMLHead instance to ease adding of
    javascripts and stylesheets
    """

    js_unload_code = """if (typeof(pageDataUnloaded) == 'undefined') {
    jQuery(window).unload(unloadPageData);
    pageDataUnloaded = true;
}"""
    script_opening = '<script type="text/javascript">\n'
    script_closing = "\n</script>"

    def __init__(self, req, *args, **kwargs):
        super(HTMLHead, self).__init__(*args, **kwargs)
        self.jsvars = []
        self.jsfiles = []
        self.cssfiles = []
        self.post_inlined_scripts = []
        self.pagedata_unload = False
        self._cw = req
        self.datadir_url = req.datadir_url

    def add_raw(self, rawheader):
        self.write(rawheader)

    def define_var(self, var, value, override=True):
        """adds a javascript var declaration / assginment in the header

        :param var: the variable name
        :param value: the variable value (as a raw python value,
                      it will be jsonized later)
        :param override: if False, don't set the variable value if the variable
                         is already defined. Default is True.
        """
        self.jsvars.append((var, value, override))

    def add_post_inline_script(self, content):
        self.post_inlined_scripts.append(content)

    def add_onload(self, jscode):
        self.add_post_inline_script(
            """$(cw).one('server-response', function(event) {
%s});"""
            % jscode
        )

    def add_js(self, jsfile, script_attributes={}):
        """adds `jsfile` to the list of javascripts used in the webpage

        This function checks if the file has already been added
        :param jsfile: the script's URL
        :param script_attributes: a dictionary of <script> attributes
            e.g. {"defer": True, "integrity": "sha256-..."}
            The attributes are not taken into account if the global option
            'concat-resources' is set to True
        """
        # XXX: if a script is added twice with different attributes, only the first
        #   call to add this script will be taken into account
        if jsfile not in [_jsfile["src"] for _jsfile in self.jsfiles]:
            self.jsfiles.append({"src": jsfile, **script_attributes})

    def add_css(self, cssfile, media="all"):
        """adds `cssfile` to the list of javascripts used in the webpage

        This function checks if the file has already been added
        :param cssfile: the stylesheet's URL
        """
        if (cssfile, media) not in self.cssfiles:
            self.cssfiles.append((cssfile, media))

    def add_unload_pagedata(self):
        """registers onunload callback to clean page data on server"""
        if not self.pagedata_unload:
            self.post_inlined_scripts.append(self.js_unload_code)
            self.pagedata_unload = True

    def concat_urls(self, urls):
        """concatenates urls into one url usable by Apache mod_concat

        This method returns the url without modifying it if there is only
        one element in the list
        :param urls: list of local urls/filenames to concatenate
        """
        if len(urls) == 1:
            return urls[0]
        len_prefix = len(self.datadir_url)
        concated = ",".join(url[len_prefix:] for url in urls)
        return "%s??%s" % (self.datadir_url, concated)

    def group_urls(self, urls_spec):
        """parses urls_spec in order to generate concatenated urls
        for js and css includes

        This method checks if the file is local and if it shares options
        with direct neighbors
        :param urls_spec: entire list of urls/filenames to inspect
        """
        concatable = []
        prev_islocal = False
        prev_key = None
        for url, key in urls_spec:
            islocal = url.startswith(self.datadir_url)
            if concatable and (islocal != prev_islocal or key != prev_key):
                yield (self.concat_urls(concatable), prev_key)
                del concatable[:]
            if not islocal:
                yield (url, key)
            else:
                concatable.append(url)
            prev_islocal = islocal
            prev_key = key
        if concatable:
            yield (self.concat_urls(concatable), prev_key)

    def getvalue(self, skiphead=False):
        """reimplement getvalue to provide a consistent (and somewhat browser
        optimzed cf. http://stevesouders.com/cuzillion) order in external
        resources declaration
        """
        w = self.write
        # 1/ variable declaration if any
        if self.jsvars:
            if skiphead:
                w("<cubicweb:script>")
            else:
                w(self.script_opening)
            for var, value, override in self.jsvars:
                vardecl = "%s = %s;" % (var, json.dumps(value))
                if not override:
                    vardecl = 'if (typeof %s == "undefined") {%s}' % (var, vardecl)
                w(vardecl + "\n")
            if skiphead:
                w("</cubicweb:script>")
            else:
                w(self.script_closing)
        # 2/ css files
        if self.datadir_url and self._cw.vreg.config["concat-resources"]:
            cssfiles = self.group_urls(self.cssfiles)
            jsfiles = (
                {"src": src}
                for src, _ in self.group_urls(
                    (jsfile["src"], None) for jsfile in self.jsfiles
                )
            )
        else:
            cssfiles = self.cssfiles
            jsfiles = self.jsfiles
        for cssfile, media in cssfiles:
            w(
                '<link rel="stylesheet" type="text/css" media="%s" href="%s"/>\n'
                % (media, xml_escape(cssfile))
            )
        # 3/ js files
        for jsfile in jsfiles:
            script_attributes = [
                f'{key}="{val}"' if val is not True else f"{key}"
                for key, val in jsfile.items()
            ]
            if skiphead:
                # Don't insert <script> tags directly as they would be
                # interpreted directly by some browsers (e.g. IE).
                # Use <cubicweb:script> tags instead and let
                # `loadAjaxHtmlHead` handle the script insertion / execution.
                w(
                    '<cubicweb:script src="%s"></cubicweb:script>\n'
                    % xml_escape(jsfile["src"])
                )
                # FIXME: a probably better implementation might be to add
                #        JS or CSS urls in a JS list that loadAjaxHtmlHead
                #        would iterate on and postprocess:
                #            cw._ajax_js_scripts.push('myscript.js')
                #        Then, in loadAjaxHtmlHead, do something like:
                #            jQuery.each(cw._ajax_js_script, jQuery.getScript)
            else:
                w(
                    '<script type="text/javascript" %s></script>\n'
                    % " ".join(script_attributes)
                )
        # 4/ post inlined scripts (i.e. scripts depending on other JS files)
        if self.post_inlined_scripts:
            if skiphead:
                for script in self.post_inlined_scripts:
                    w("<cubicweb:script>")
                    w(xml_escape(script))
                    w("</cubicweb:script>")
            else:
                w(self.script_opening)
                w("\n\n".join(self.post_inlined_scripts))
                w(self.script_closing)
        # at the start of this function, the parent UStringIO may already have
        # data in it, so we can't w(u'<head>\n') at the top. Instead, we create
        # a temporary UStringIO to get the same debugging output formatting
        # if debugging is enabled.
        headtag = UStringIO(tracewrites=self.tracewrites)
        if not skiphead:
            headtag.write("<head>\n")
            w("</head>\n")
        return headtag.getvalue() + super(HTMLHead, self).getvalue()


class HTMLStream:
    """represents a HTML page.

    This is used my main templates so that HTML headers can be added
    at any time during the page generation.

    HTMLStream uses the (U)StringIO interface to be compliant with
    existing code.
    """

    def __init__(self, req):
        self.tracehtml = req.tracehtml
        # stream for <head>
        self.head = req.html_headers
        # main stream
        self.body = UStringIO(tracewrites=req.tracehtml)
        # this method will be assigned to self.w in views
        self.write = self.body.write
        self.doctype = ""
        self._htmlattrs = [("lang", req.lang)]
        # keep main_stream's reference on req for easier text/html demoting
        req.main_stream = self

    def add_htmlattr(self, attrname, attrvalue):
        self._htmlattrs.append((attrname, attrvalue))

    def set_htmlattrs(self, attrs):
        self._htmlattrs = attrs

    def set_doctype(self, doctype):
        self.doctype = doctype

    @property
    def htmltag(self):
        attrs = " ".join(
            '%s="%s"' % (attr, xml_escape(value)) for attr, value in self._htmlattrs
        )
        if attrs:
            return '<html xmlns:cubicweb="http://www.cubicweb.org" %s>' % attrs
        return '<html xmlns:cubicweb="http://www.cubicweb.org">'

    def getvalue(self):
        """writes HTML headers, closes </head> tag and writes HTML body"""
        if self.tracehtml:
            css = "\n".join(
                (
                    "span {",
                    "  font-family: monospace;",
                    "  word-break: break-all;",
                    "  word-wrap: break-word;",
                    "}",
                    "span:hover {",
                    "  color: red;",
                    "  text-decoration: underline;",
                    "}",
                )
            )
            style = '<style type="text/css">\n%s\n</style>\n' % css
            return (
                "<!DOCTYPE html>\n"
                + "<html>\n<head>\n%s\n</head>\n" % style
                + "<body>\n"
                + "<span>"
                + xml_escape(self.doctype)
                + "</span><br/>"
                + "<span>"
                + xml_escape(self.htmltag)
                + "</span><br/>"
                + self.head.getvalue()
                + self.body.getvalue()
                + "<span>"
                + xml_escape("</html>")
                + "</span>"
                + "</body>\n</html>"
            )
        return "%s\n%s\n%s\n%s\n</html>" % (
            self.doctype,
            self.htmltag,
            self.head.getvalue(),
            self.body.getvalue(),
        )


def url_path_starts_with_prefix(url_path, prefix):
    return url_path.lstrip("/").startswith(prefix.lstrip("/"))


def remove_prefix_from_url_path(url_path, prefix):
    return url_path.lstrip("/")[len(prefix.lstrip("/")) :]
