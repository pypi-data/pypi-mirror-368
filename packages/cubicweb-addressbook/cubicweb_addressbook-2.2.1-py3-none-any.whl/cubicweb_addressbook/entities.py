"""Specific entity type for address book entities (eg PhoneNumber and PostalAddress)

:organization: Logilab
:copyright: 2003-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.predicates import is_instance

from cubicweb_geocoding.views import IGeocodableAdapter


class PhoneNumber(AnyEntity):
    __regid__ = "PhoneNumber"
    fetch_attrs = fetch_config(["number", "type"])[0]

    @classmethod
    def cw_fetch_order(cls, select, attr, var):
        if attr == "type":
            return f"phonetype_sort_value({var}) DESC"
        return None

    def dc_title(self):
        return f"{self.number} ({self._cw._(self.type)})"


class PostalAddress(AnyEntity):
    __regid__ = "PostalAddress"
    fetch_attrs, cw_fetch_order = fetch_config(
        ["street", "street2", "postalcode", "city", "country"]
    )

    def dc_long_title(self):
        lines = []
        if self.street:
            lines.append(self.street)
        if self.street2:
            lines.append(self.street2)
        if self.postalcode:
            lines.append(self.postalcode)
        if self.city:
            lines.append(self.city)
        if self.country:
            lines.append(self.country)
        return " ".join(lines)


class PostalAddressIGeocodableAdapter(IGeocodableAdapter):
    __select__ = is_instance("PostalAddress")
