"""Custom element classes related to sub and sup."""
from __future__ import annotations

from docx.oxml.parser import OxmlElement, register_element_cls
from bdtool.docxext.oxml.math.block import CT_mBlock


class CT_msSubSup(CT_mBlock):
    """`<m:sSubSup>` element, containing the properties and element for a sub."""
    
    
class CT_msSub(CT_mBlock):
    """`<m:sSub>` element, containing the properties and element for a sub."""

class CT_msSup(CT_mBlock):
    """`<m:sSup>` element, containing the properties and element for a sub."""
    
class CT_mSub(CT_mBlock):
    """`<m:sub>` element, containing the properties and element for a sub."""


class CT_mSup(CT_mBlock):
    """`<m:sup>` element, containing the properties and element for a sup."""

register_element_cls("m:sSubSup", CT_msSubSup)
register_element_cls("m:sSub", CT_msSub)
register_element_cls("m:sSup", CT_msSup)
register_element_cls("m:sub", CT_mSub)
register_element_cls("m:sup", CT_mSup)