# pylint: disable-msg=W0622
"""cubicweb-expense application packaging information"""

modname = "expense"
distname = "cubicweb-expense"

numversion = (1, 1, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "Logilab"
author_email = "contact@logilab.fr"
description = "expense component for the CubicWeb framework"
web = "http://www.cubicweb.org/project/%s" % distname
classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: JavaScript",
]

__depends__ = {
    "cubicweb": ">=4.0.0,<6.0.0",
    "cubicweb-web": ">=1.6.0,<2.0.0",
    "cubicweb-addressbook": ">=2.2.1,<3.0.0",
    "cubicweb-file": ">=4.2.0,<5.0.0",
}
