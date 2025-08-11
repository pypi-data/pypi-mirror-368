# pylint: disable-msg=W0622
"""cubicweb-addressbook packaging information"""

modname = "addressbook"
distname = f"cubicweb-{modname}"

numversion = (2, 2, 1)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
description = "address book component for the CubicWeb framework"
author = "Logilab"
author_email = "contact@logilab.fr"
web = f"https://forge.extranet.logilab.fr/cubicweb/cubes/{distname}"
classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: JavaScript",
]

__depends__ = {
    "cubicweb": ">= 4.5.3, < 6.0.0",
    "cubicweb-web": ">= 1.4.2, < 2.0.0",
    "cubicweb-geocoding": ">= 1.0.0, < 2.0.0",
}
