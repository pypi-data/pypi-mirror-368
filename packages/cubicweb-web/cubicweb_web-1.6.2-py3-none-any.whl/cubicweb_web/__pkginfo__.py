"""cubicweb_web application packaging information"""

from importlib.metadata import metadata

modname = "web"
distname = "cubicweb-" + modname

cubicweb_metadata = metadata(distname).json

version = cubicweb_metadata["version"]
numversion = [int(number) for number in version.split(".")]

description = cubicweb_metadata["description"]
author, author_email = cubicweb_metadata["author_email"].split()
web = cubicweb_metadata["project_url"][-1].split(", ")[-1]
license = cubicweb_metadata["license"]
classifiers = cubicweb_metadata["classifier"]
