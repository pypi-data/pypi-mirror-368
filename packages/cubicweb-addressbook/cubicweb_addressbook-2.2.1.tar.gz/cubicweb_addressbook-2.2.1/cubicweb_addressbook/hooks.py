"""addressbook hooks

:organization: Logilab
:copyright: 2001-2011 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

__docformat__ = "restructuredtext en"


from cubicweb.predicates import is_instance
from cubicweb.server.hook import Hook

from cubicweb_geocoding import geocoding


class AutoSetLatLng(Hook):
    __regid__ = "auto_lat_lng_hook"
    __select__ = is_instance("PostalAddress")
    events = ("before_add_entity", "before_update_entity")

    def __call__(self):
        gmapkey = self._cw.vreg.config.get("gmap-key")
        if not gmapkey:
            return
        geoattrs = {"street", "street2", "postalcode", "city", "country"}
        changed_attrs = set(self.entity.cw_edited)
        if (
            geoattrs & changed_attrs
            and not self.entity.cw_attr_cache.get("latitude")
            and not self.entity.cw_attr_cache.get("longitude")
        ):
            try:
                latlng = geocoding.get_latlng(self.entity.dc_long_title(), gmapkey)
            except geocoding.UnknownAddress:
                self._cw.warning(
                    "unable to get latitude / longitude for %s", self.entity.eid
                )
            else:
                self.entity.cw_edited.update(latlng)
