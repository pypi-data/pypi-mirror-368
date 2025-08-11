"""Custom element classes related to paragraphs (CT_P)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, cast
from docx.oxml.ns import qn
from docx.oxml.parser import OxmlElement, register_element_cls
from docx.oxml.xmlchemy import BaseOxmlElement, ZeroOrMore, ZeroOrOne

if TYPE_CHECKING:
    from bdtool.docxext.oxml.math.run import CT_mR
    from bdtool.docxext.oxml.math.nary import CT_mNary
    from bdtool.docxext.oxml.math.share import CT_ctrlPr
    from bdtool.docxext.oxml.math.subsup import CT_mSub, CT_mSup, CT_msSub, CT_msSubSup, CT_msSup

class CT_mBlock(BaseOxmlElement):
    """`<m:e>` element, containing the properties and text for a math element block."""
    add_r: Callable[[], CT_mR]
    r_lst: List[CT_mR]

    add_nary: Callable[[], CT_mNary]
    get_or_add_ctrlPr: Callable[[], CT_ctrlPr]
    get_or_add_sub: Callable[[], CT_mSub]
    get_or_add_sup: Callable[[], CT_mSup]
    _add_ssub: Callable[[], CT_msSub]
    _add_ssup: Callable[[], CT_msSup]
    _add_ssubsup: Callable[[], CT_msSubSup]
    _add_e: Callable[[], CT_mBlock]
    
    ctrlPr: CT_ctrlPr = ZeroOrOne("m:ctrlPr")
    sub: CT_mSub = ZeroOrOne("m:sub")
    sup: CT_mSup = ZeroOrOne("m:sup")
    ssub: CT_msSub = ZeroOrMore("m:sSub")
    ssup: CT_msSup = ZeroOrMore("m:sSup")
    ssubsup: CT_msSubSup = ZeroOrMore("m:sSubSup")
    r: CT_mR = ZeroOrMore("m:r")
    nary: CT_mNary = ZeroOrMore("m:nary")
    e: CT_mBlock = ZeroOrMore("m:e")
    
    
    def add_r(self, text: str) -> CT_mR:
        """Return a newly added `<m:t>` element containing `text`."""
        t = self._add_r(text=text)
        if len(text.strip()) < len(text):
            t.set(qn("xml:space"), "preserve")
        return t

    def add_nary(self, char: str) -> CT_mNary:
        """Return a newly added `<m:nary>` element containing `char`."""
        nary: CT_mNary = self._add_nary()
        nary.add_naryPr(char)
        return nary
    
    def add_e_before(self) -> CT_mBlock:
        """Return a new `<m:e>` element inserted directly prior to this one."""
        new_p = cast(CT_mBlock, OxmlElement("m:e"))
        self.addprevious(new_p)
        return new_p
    
    def clear_content(self):
        """Remove all child elements."""
        for child in self.xpath("./*"):
            self.remove(child)

    @property
    def inner_content_elements(self) -> List[BaseOxmlElement]:
        """Run and hyperlink children of the `w:oMath` element, in document order."""
        return self.xpath("./*[not(self::m:ctrlPr)]")

    @property
    def text(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """The textual content of this e.

        Inner-content child elements like `m:r` are translated to
        their text equivalent.
        """
        return "".join(e.text for e in self.xpath("m:r"))
    
register_element_cls("m:e", CT_mBlock)