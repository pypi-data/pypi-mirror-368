"""Specific views for address book entities (eg PhoneNumber and PostalAddress)

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb_web.view import EntityView
from cubicweb.predicates import is_instance
from cubicweb_web.views import baseviews, uicfg

uicfg.indexview_etype_section["PhoneNumber"] = "subobject"
uicfg.indexview_etype_section["PostalAddress"] = "subobject"
uicfg.indexview_etype_section["IMAddress"] = "subobject"

uicfg.autoform_section.tag_attribute(("PostalAddress", "latitude"), "main", "hidden")
uicfg.autoform_section.tag_attribute(("PostalAddress", "longitude"), "main", "hidden")


class PhoneNumberInContextView(baseviews.InContextView):
    __select__ = is_instance("PhoneNumber")

    def cell_call(self, row, col=0):
        self.w(xml_escape(self.cw_rset.get_entity(row, col).dc_title()))


class PhoneNumberListItemView(baseviews.ListItemView):
    __select__ = is_instance("PhoneNumber")

    def cell_call(self, row, col=0, vid=None):
        entity = self.cw_rset.get_entity(row, col)
        self.w(
            '<div class="tel"><span class="type">%s</span> %s</div>'
            % (xml_escape(entity.type), xml_escape(entity.number))
        )


class PhoneNumberSipView(EntityView):
    __regid__ = "sip"
    __select__ = is_instance("PhoneNumber")

    def cell_call(self, row, col, contexteid=None):
        entity = self.cw_rset.get_entity(row, col)
        self.w('<div class="phonenumber">')
        number = xml_escape(entity.number)
        self.w(f"<a href=\"sip:{number.replace(' ', '')}\">{number}</a>")
        self.w("</div>")


class PostalAddressInContextView(baseviews.InContextView):
    __select__ = is_instance("PostalAddress")

    def cell_call(self, row, col, contexteid=None):
        entity = self.cw_rset.get_entity(row, col)
        self.w('<div class="adr">')
        if entity.street:  # may be set optional by client cubes
            self.w(f'<div class="street-address">{xml_escape(entity.street)}')
            if entity.street2:
                self.w("<br/>")
                self.w(xml_escape(entity.street2))  # FIXME div-class
            self.w("</div>")
        if entity.postalcode:
            self.w(
                f'<span class="postal-code">{xml_escape(entity.postalcode)}</span> - '
            )
        if entity.city:
            self.w(f'<span class="locality">{xml_escape(entity.city)}</span>')
        if entity.state:
            self.w("<br/>")
            self.w(f'<span class="region">{xml_escape(entity.state)}</span>')
        if entity.country:
            self.w("<br/>")
            self.w(f'<span class="country-name">{xml_escape(entity.country)}</span>')
        self.w("</div>\n")
