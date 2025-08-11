from __future__ import annotations

from docx.oxml.text.paragraph import CT_P
from bdtool.docxext.oxml.math import OxmlElement, CT_oMath, CT_mBlock
from lxml import etree
import re

def add_math(ct_p: CT_P, latex: str = None) -> CT_oMath:
    if ct_p.text:
        ct_math = OxmlElement("m:oMath")
        ct_p.append(ct_math)
    else:
        ct_math = OxmlElement("m:oMathPara")
        ct_p.append(ct_math)
        ct_math = ct_math.add_m()
    if latex:
        parse_math(ct_math, latex)
    return ct_math

def parse_math(ct_math: CT_mBlock, latex: str) -> CT_oMath: 
    """parse latex math fomula to oxml"""
    idpattern = r'(?a:[a-z][a-z0-9]*)'
    pattern = fr"""(?:
        \\(?P<function>{idpattern}) |
        (?P<subscript>_) |
        (?P<superscript>\^) |
        (?P<block>{{) |
        (?P<endblock>}})
    )"""
    pattern = re.compile(pattern, re.IGNORECASE | re.VERBOSE)
    obj = ct_math
    stack = [(obj, {"op": 0})]
    while stack:
        obj, status = stack.pop()
        match = pattern.search(latex)
        if match is None:
            obj.add_r(latex)
            break
        else:
            kind = match.lastgroup
            span=match.span()
            text = latex[:span[0]]
            if text:
                obj.add_r(text)
            stack.append((obj, status))
            if kind == "endblock":
                stack.pop()
                obj, status = stack.pop()
                op = status.get("op", 0)
                if op:
                    stack.append((obj, status))
            elif kind == 'function':
                func = match.group(kind)
                if func == "ssub":
                    new_obj = obj._add_ssub()
                    stack.append((new_obj, {"op": 1}))
                elif func == "ssup":
                    new_obj = obj._add_ssup()
                    stack.append((new_obj, {"op": 1}))
                elif func == "ssubsup":
                    new_obj = obj._add_ssubsup()
                    stack.append((new_obj, {"op": 1}))
                else:
                    new_obj = obj.add_nary(char=latex_to_symbol.get(func, func))
                    new_obj.set_supHide("1")
                    new_obj.set_subHide("1")
                    stack.append((new_obj, {"op": 1}))
            elif kind == 'subscript':
                if hasattr(obj, 'set_subHide'):
                    obj.set_subHide("0")
                new_obj = obj.get_or_add_sub()
                stack.append((new_obj, {"op": 0}))
            elif kind == 'superscript':
                if hasattr(obj, 'set_supHide'):
                    obj.set_supHide("0")
                new_obj = obj.get_or_add_sup()
                stack.append((new_obj, {"op": 0}))
            elif kind == 'block':
                if text:
                    new_obj = obj._add_e()
                    stack.append((new_obj, {"op": 0}))
                else:
                    op = status.get("op", 0)
                    if op:
                        status["op"] = op - 1
                        new_obj = obj._add_e()
                        stack.append((new_obj, {"op": 0}))
                
            latex = latex[span[1]:]
    xml_str = etree.tostring(
        ct_math,
        encoding='unicode',
        pretty_print=True,
        xml_declaration=False  # 不包含XML声明头
    )
    print(xml_str)
    return ct_math


latex_to_symbol = {
    # 希腊字母（小写）
    'alpha': 'α',
    'beta': 'β',
    'gamma': 'γ',
    'delta': 'δ',
    'epsilon': 'ε',
    'zeta': 'ζ',
    'eta': 'η',
    'theta': 'θ',
    'iota': 'ι',
    'kappa': 'κ',
    'lambda': 'λ',
    'mu': 'μ',
    'nu': 'ν',
    'xi': 'ξ',
    'omicron': 'ο',
    'pi': 'π',
    'rho': 'ρ',
    'sigma': 'σ',
    'tau': 'τ',
    'upsilon': 'υ',
    'phi': 'φ',
    'chi': 'χ',
    'psi': 'ψ',
    'omega': 'ω',

    # 希腊字母（大写）
    'Gamma': 'Γ',
    'Delta': 'Δ',
    'Theta': 'Θ',
    'Lambda': 'Λ',
    'Xi': 'Ξ',
    'Pi': 'Π',
    'Sigma': 'Σ',
    'Phi': 'Φ',
    'Psi': 'Ψ',
    'Omega': 'Ω',

    # 运算符
    'pm': '±',
    'mp': '∓',
    'times': '×',
    'div': '÷',
    'cdot': '⋅',
    'ast': '∗',
    'circ': '∘',
    'otimes': '⊗',
    'oplus': '⊕',
    'leq': '≤',
    'geq': '≥',
    'leqq': '≦',
    'geqq': '≧',
    'neq': '≠',
    'approx': '≈',
    'equiv': '≡',
    'propto': '∝',
    'in': '∈',
    'notin': '∉',
    'subset': '⊂',
    'supset': '⊃',
    'subseteq': '⊆',
    'supseteq': '⊇',
    'cap': '∩',
    'cup': '∪',
    'emptyset': '∅',
    'forall': '∀',
    'exists': '∃',
    'nexists': '∄',
    'implies': '⇒',
    'iff': '⇔',
    'neg': '¬',
    'land': '∧',
    'lor': '∨',
    'nabla': '∇',
    'Delta': '∆',
    'prod': '∏',
    'sum': '∑',
    'int': '∫',
    'iint': '∬',
    'iiint': '∭',
    'oint': '∮',
    'infty': '∞',
    'sqrt': '√',
    'sqrt[3]': '∛',
    'sqrt[4]': '∜',

    # 数学函数
    'sin': 'sin',
    'cos': 'cos',
    'tan': 'tan',
    'cot': 'cot',
    'sec': 'sec',
    'csc': 'csc',
    'arcsin': 'arcsin',
    'arccos': 'arccos',
    'arctan': 'arctan',
    'sinh': 'sinh',
    'cosh': 'cosh',
    'tanh': 'tanh',
    'ln': 'ln',
    'log': 'log',
    'exp': 'exp',
    'lim': 'lim',
    'max': 'max',
    'min': 'min',
    'det': 'det',
    'dim': 'dim',
    'arg': 'arg',
    'deg': 'deg',
    'gcd': 'gcd',
    'lcm': 'lcm',
}
