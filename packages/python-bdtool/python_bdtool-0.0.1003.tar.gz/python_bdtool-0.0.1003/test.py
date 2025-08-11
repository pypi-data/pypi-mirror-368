#!/bin/env python3

import docx
from bdtool.docxext.math import parse_math, add_math

doc=docx.Document()
p2=doc.add_paragraph()
ct_math=add_math(p2._element)
parse_math(ct_math, r"w=dasd+22132_323 + dasd^dasd_sadsa + \sum_{dsad}^{dsa} s+1")