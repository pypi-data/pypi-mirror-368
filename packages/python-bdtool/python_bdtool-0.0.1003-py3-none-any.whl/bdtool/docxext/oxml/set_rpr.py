from __future__ import annotations
from docx.oxml.text.run import CT_R
from docx.oxml.text.font import CT_RPr
from docx.shared import RGBColor
from docx.oxml.ns import qn
from bdtool.tool import common_color_rgb
from bdtool.docxext.oxml import OxmlElement


def set_rpr(r: CT_R, 
            color = None, 
            themeColor=None,
            ascii = None,
            hAnsi = None,
            szCs = None,
            sz = None,
    ) -> CT_RPr:
    """
    Set the ``<m:rPr>`` child element of a ``<m:r>`` element.
    """
    rp = r.get_or_add_rPr()
    rp_color = rp.get_or_add_color()
    if color is not None:
        if isinstance(color, RGBColor):
            rp_color.val = color
        else:
            rgb = common_color_rgb(color)
            rp_color.val = RGBColor(*rgb)
    if themeColor is not None:
        rp_color.themeColor=themeColor
    rp_font = rp.get_or_add_rFonts()
    if ascii is not None:
        rp_font.ascii = ascii
    if hAnsi is not None:
        rp_font.hAnsi = hAnsi
    if sz is not None:
        sz = OxmlElement('w:sz')
        sz.set(qn('w:val'), sz)
        rp.append(sz)
    if szCs is not None:
        sz = OxmlElement('w:szCs')
        sz.set(qn('w:val'), szCs)
        rp.append(sz)  
    return rp