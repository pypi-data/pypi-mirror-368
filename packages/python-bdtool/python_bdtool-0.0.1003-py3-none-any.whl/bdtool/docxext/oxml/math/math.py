"""Custom element classes related to oMathPara (CT_oMathPara) and oMath (CT_OMath)."""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, cast
from docx.oxml.parser import OxmlElement, register_element_cls
from docx.oxml.xmlchemy import BaseOxmlElement, ZeroOrMore, ZeroOrOne
from bdtool.docxext.oxml.math.block import CT_mBlock

class CT_oMathPara(BaseOxmlElement):
    """`<m:oMathPara>` element, containing the properties and text for a oMathPara."""

    add_m: Callable[[], CT_oMath]
    m_lst: List[CT_oMath]
    m = ZeroOrMore("m:oMath")

    def clear_content(self):
        """Remove all child elements"""
        for child in self.xpath("./*"):
            self.remove(child)

    @property
    def text(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """The textual content of this oMathPara.

        Inner-content child elements like `m:r` and `w:hyperlink` are translated to
        their text equivalent.
        """
        return "".join(e.text for e in self.xpath("m:r | w:hyperlink"))

register_element_cls("m:oMathPara", CT_oMathPara)
    
class CT_oMath(CT_mBlock):
    """`<m:oMath>` element, containing the properties and text for a paragraph."""
    
    def add_m_before(self) -> CT_oMath:
        """Return a new `<m:oMath>` element inserted directly prior to this one."""
        new_p = cast(CT_oMath, OxmlElement("m:oMath"))
        self.addprevious(new_p)
        return new_p
    
register_element_cls("m:e", CT_mBlock)
register_element_cls("m:oMath", CT_oMath)