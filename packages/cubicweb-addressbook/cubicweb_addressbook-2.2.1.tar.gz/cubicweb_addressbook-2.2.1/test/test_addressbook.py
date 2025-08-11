import unittest
import os
from cubicweb import devtools
from cubicweb_web.devtools.testlib import (
    AutomaticWebTest,
    WebPostgresApptestConfiguration,
)


def setUpModule():
    """Ensure a PostgreSQL cluster is running and configured

    If PGHOST environment variable is defined, use existing PostgreSQL cluster
    running on PGHOST and PGPORT (default 5432).

    Or start a dedicated PostgreSQL cluster by using
    cubicweb.devtools.startpgcluster()
    """
    config = devtools.DEFAULT_PSQL_SOURCES["system"]
    if config["db-host"] != "REPLACEME":
        return
    if "PGHOST" in os.environ:
        config["db-host"] = os.environ["PGHOST"]
        config["db-port"] = os.environ.get("PGPORT", 5432)
        return
    devtools.startpgcluster(__file__)
    import atexit

    atexit.register(devtools.stoppgcluster, __file__)


class AddressbookAutomaticWebTest(AutomaticWebTest):
    configcls = WebPostgresApptestConfiguration

    def to_test_etypes(self):
        return {"PhoneNumber", "PostalAddress"}

    def list_startup_views(self):
        return ()


del AutomaticWebTest

if __name__ == "__main__":
    unittest.main()
