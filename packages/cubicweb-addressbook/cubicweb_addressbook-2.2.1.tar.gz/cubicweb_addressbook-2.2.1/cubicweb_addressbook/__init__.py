"""cubicweb-addressbook"""

from cubicweb import ETYPE_NAME_MAP
from rql.utils import register_function, FunctionDescr

ETYPE_NAME_MAP["Phonenumber"] = "PhoneNumber"
ETYPE_NAME_MAP["Postaladdress"] = "PostalAddress"


class phonetype_sort_value(FunctionDescr):
    supported_backends = (
        "postgres",
        "sqlite",
    )
    rtype = "Int"


try:
    register_function(phonetype_sort_value)
except AssertionError:
    pass


try:
    from cubicweb.server import SQL_CONNECT_HOOKS
except ImportError:  # no server installation
    pass
else:

    def init_sqlite_connexion(cnx):
        def phonetype_sort_value(text):
            return {"mobile": 2, "home": 1, "office": 4, "fax": 0, "secretariat": 3}[
                text
            ]

        cnx.create_function("PHONETYPE_SORT_VALUE", 1, phonetype_sort_value)

    sqlite_hooks = SQL_CONNECT_HOOKS.setdefault("sqlite", [])
    sqlite_hooks.append(init_sqlite_connexion)
