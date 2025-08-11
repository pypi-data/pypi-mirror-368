"""Custom element classes related to text runs (CT_mR)."""

from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Iterator, List

from docx.oxml.parser import OxmlElement, register_element_cls
from docx.oxml.ns import qn
from docx.oxml.drawing import CT_Drawing
from docx.oxml.simpletypes import ST_BrClear, ST_BrType
from docx.oxml.text.font import CT_RPr
from docx.oxml.xmlchemy import BaseOxmlElement, OptionalAttribute, ZeroOrMore, ZeroOrOne
from docx.shared import TextAccumulator
from docx.oxml.text.run import CT_Cr, CT_Br, CT_Text, _RunContentAppender, CT_R
if TYPE_CHECKING:
    from docx.oxml.shape import CT_Anchor, CT_Inline
    from docx.oxml.text.pagebreak import CT_LastRenderedPageBreak
    from docx.oxml.text.parfmt import CT_TabStop

class CT_mR(BaseOxmlElement):
    """`<m:r>` element, containing the properties and text for a run."""

    add_br: Callable[[], CT_Br]
    add_tab: Callable[[], CT_TabStop]
    get_or_add_rPr: Callable[[], CT_RPr]
    _add_t: Callable[..., CT_Text]

    rPr: CT_RPr | None = ZeroOrOne("w:rPr")  # pyright: ignore[reportAssignmentType]
    br = ZeroOrMore("w:br")
    cr = ZeroOrMore("w:cr")
    drawing = ZeroOrMore("w:drawing")
    t = ZeroOrMore("m:t")
    tab = ZeroOrMore("w:tab")

    def add_t(self, text: str) -> CT_Text:
        """Return a newly added `<m:t>` element containing `text`."""
        t = self._add_t(text=text)
        if len(text.strip()) < len(text):
            t.set(qn("xml:space"), "preserve")
        return t

    def clear_content(self) -> None:
        """Remove all child elements except a `w:rPr` element if present."""
        # -- remove all run inner-content except a `w:rPr` when present. --
        for e in self.xpath("./*[not(self::w:rPr)]"):
            self.remove(e)

    @property
    def inner_content_items(self) -> List[str | CT_Drawing | CT_LastRenderedPageBreak]:
        """Text of run, possibly punctuated by `w:lastRenderedPageBreak` elements."""
        from docx.oxml.text.pagebreak import CT_LastRenderedPageBreak

        accum = TextAccumulator()

        def iter_items() -> Iterator[str | CT_Drawing | CT_LastRenderedPageBreak]:
            for e in self.xpath(
                "w:br"
                " | w:cr"
                " | w:drawing"
                " | w:lastRenderedPageBreak"
                " | w:noBreakHyphen"
                " | w:ptab"
                " | w:t"
                " | w:tab"
            ):
                if isinstance(e, (CT_Drawing, CT_LastRenderedPageBreak)):
                    yield from accum.pop()
                    yield e
                else:
                    accum.push(str(e))

            # -- don't forget the "tail" string --
            yield from accum.pop()

        return list(iter_items())

    @property
    def lastRenderedPageBreaks(self) -> List[CT_LastRenderedPageBreak]:
        """All `w:lastRenderedPageBreaks` descendants of this run."""
        return self.xpath("./w:lastRenderedPageBreak")

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
        """Set character style of this `w:r` element to `style`.

        If `style` is None, remove the style element.
        """
        rPr = self.get_or_add_rPr()
        rPr.style = style

    @property
    def text(self) -> str:
        """The textual content of this run.

        Inner-content child elements like `w:tab` are translated to their text
        equivalent.
        """
        return "".join(
            str(e) for e in self.xpath("w:br | w:cr | w:noBreakHyphen | w:ptab | w:t | w:tab")
        )

    @text.setter
    def text(self, text: str):  # pyright: ignore[reportIncompatibleMethodOverride]
        self.clear_content()
        _RunContentAppender.append_to_run_from_text(self, text)

    def _insert_rPr(self, rPr: CT_RPr) -> CT_RPr:
        self.insert(0, rPr)
        return rPr

register_element_cls("m:r", CT_mR)

