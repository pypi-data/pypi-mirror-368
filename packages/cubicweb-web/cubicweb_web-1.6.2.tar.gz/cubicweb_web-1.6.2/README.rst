CubicWeb Legacy Web module
--------------------------
This cube provides a dynamic view selection system. This system allows
semi-automatic XHTML/XML/JSON/text generation, based on context.
All this was once available in CubicWeb 3 as a `cubicweb.web` module.

This code is still maintained, however we no longer add new features.

How to use it?
--------------
This cube can be used like every other cubes. You just have to add it in your
application dependencies and/or add it when creating your instance.
However, you may need some configuration in order to have cubicweb views
working as expected. In pyramid.ini file (which is located in your instance
directory), you should disable default CubicWeb 4 html views by writing::

    cubicweb.content-negociation.html-default = yes

