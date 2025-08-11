from docx.oxml.parser import OxmlElement, parse_xml, register_element_cls

from bdtool.docxext.oxml.math.run import CT_mR
from bdtool.docxext.oxml.math.nary import CT_mNary
from bdtool.docxext.oxml.math.share import CT_ctrlPr
from bdtool.docxext.oxml.math.subsup import CT_mSub, CT_mSup, CT_msSub, CT_msSubSup, CT_msSup
from bdtool.docxext.oxml.math.block import CT_mBlock
from bdtool.docxext.oxml.math.math import CT_oMath, CT_oMathPara



