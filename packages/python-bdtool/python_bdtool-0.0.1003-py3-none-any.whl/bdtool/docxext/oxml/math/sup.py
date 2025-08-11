"""Custom element classes related to sup (CT_mSup)."""
from __future__ import annotations

from docx.oxml.parser import OxmlElement, register_element_cls
from bdtool.docxext.oxml.math.block import CT_mBlock

class CT_mSup(CT_mBlock):
    """`<m:sup>` element, containing the properties and element for a sup."""

register_element_cls("m:sup", CT_mSup)
