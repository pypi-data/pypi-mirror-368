from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Iterator, List
from docx.oxml.parser import OxmlElement, register_element_cls
from docx.oxml.xmlchemy import BaseOxmlElement, OptionalAttribute, ZeroOrMore, ZeroOrOne, OneAndOnlyOne, RequiredAttribute
from docx.oxml.text.font import CT_RPr
from docx.oxml.simpletypes import ST_String


class CT_ctrlPr(BaseOxmlElement):
    """`<m:ctrlPr>` element, containing the properties and element for a ctrlPr."""
    
    get_or_add_rPr: Callable[[], CT_RPr]
    
    rPr: CT_RPr | None = ZeroOrOne("w:rPr") 
    
    @property
    def style(self) -> str | None:
        """String contained in `w:val` attribute of `w:rStyle` grandchild.

        |None| if that element is not present.
        """
        rPr = self.rPr
        if rPr is None:
            return None
        return rPr.style

    @style.setter
    def style(self, style: str | None):
        """Set character style of this `m:ctrlPr` element to `style`.

        If `style` is None, remove the style element.
        """
        rPr = self.get_or_add_rPr()
        rPr.style = style
    
    def _insert_rPr(self, rPr: CT_RPr) -> CT_RPr:
        self.insert(0, rPr)
        return rPr

class CT_mChar(BaseOxmlElement):
    """`m:chr` element, specifying the text."""
    val = RequiredAttribute("w:val", ST_String)
    
    
register_element_cls("m:ctrlPr", CT_ctrlPr)
register_element_cls("m:chr", CT_mChar)
