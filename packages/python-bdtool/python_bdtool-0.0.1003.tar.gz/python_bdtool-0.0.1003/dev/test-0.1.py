import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

class LaTeXToOMathConverter:
    def __init__(self):
        # 定义命名空间
        self.ns = {
            'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
        }
        ET.register_namespace('m', self.ns['m'])
        
        # 希腊字母映射表（LaTeX → Unicode）
        self.greek_letters = {
            r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ',
            r'\epsilon': 'ε', r'\zeta': 'ζ', r'\eta': 'η', r'\theta': 'θ',
            r'\iota': 'ι', r'\kappa': 'κ', r'\lambda': 'λ', r'\mu': 'μ',
            r'\nu': 'ν', r'\xi': 'ξ', r'\omicron': 'ο', r'\pi': 'π',
            r'\rho': 'ρ', r'\sigma': 'σ', r'\tau': 'τ', r'\upsilon': 'υ',
            r'\phi': 'φ', r'\chi': 'χ', r'\psi': 'ψ', r'\omega': 'ω',
            # 大写希腊字母
            r'\Gamma': 'Γ', r'\Delta': 'Δ', r'\Theta': 'Θ',
            r'\Lambda': 'Λ', r'\Xi': 'Ξ', r'\Pi': 'Π',
            r'\Sigma': 'Σ', r'\Upsilon': 'Υ', r'\Phi': 'Φ',
            r'\Psi': 'Ψ', r'\Omega': 'Ω'
        }
    
    def convert(self, latex_formula):
        """将LaTeX数学公式转换为m:oMathPara XML"""
        # 创建根节点 m:oMathPara
        omath_para = ET.Element('{%s}oMathPara' % self.ns['m'])
        
        # 创建m:oMath节点
        omath = ET.SubElement(omath_para, '{%s}oMath' % self.ns['m'])
        
        # 解析LaTeX并构建XML结构
        self._parse_latex(latex_formula, omath)
        
        # 美化XML输出
        xml_string = ET.tostring(omath_para, 'utf-8')
        parsed = minidom.parseString(xml_string)
        return parsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')
    
    def _parse_latex(self, latex, parent_node):
        """递归解析LaTeX公式并构建OMath节点"""
        # 处理括号
        latex = self._process_parentheses(latex)
        
        # 处理希腊字母
        latex = self._process_greek_letters(latex)
        
        # 处理分数 \frac{a}{b}
        if r'\frac' in latex:
            self._process_fractions(latex, parent_node)
            return
        
        # 处理根号 \sqrt[n]{...}
        if r'\sqrt' in latex:
            self._process_sqrt(latex, parent_node)
            return
        
        # 处理上下标 x^{2} 或 x_{i}
        if '^' in latex or '_' in latex:
            self._process_sup_sub(latex, parent_node)
            return
        
        # 处理积分 \int_{a}^{b}
        if r'\int' in latex:
            self._process_integral(latex, parent_node)
            return
        
        # 处理求和 \sum_{i=1}^{n}
        if r'\sum' in latex:
            self._process_sum(latex, parent_node)
            return
        
        # 处理普通文本
        self._add_text(latex, parent_node)
    
    def _process_parentheses(self, latex):
        """处理括号，替换为OMath中的适当表示"""
        # 替换\left(和\right)为普通括号，但保留大小信息
        latex = re.sub(r'\\left\(', '(', latex)
        latex = re.sub(r'\\right\)', ')', latex)
        return latex
    
    def _process_greek_letters(self, latex):
        """将LaTeX希腊字母替换为Unicode字符"""
        for latex_char, unicode_char in self.greek_letters.items():
            latex = re.sub(rf'\{latex_char}\b', unicode_char, latex)
        return latex
    
    def _process_fractions(self, latex, parent_node):
        """处理分数结构"""
        # 匹配所有分数
        frac_pattern = r'\\frac\{([^}]+)\}\{([^}]+)\}'
        while True:
            match = re.search(frac_pattern, latex)
            if not match:
                break
                
            # 创建分数节点
            f = ET.SubElement(parent_node, '{%s}f' % self.ns['m'])
            
            # 分子
            num = ET.SubElement(f, '{%s}num' % self.ns['m'])
            numerator = match.group(1)
            self._parse_latex(numerator, num)
            
            # 分母
            den = ET.SubElement(f, '{%s}den' % self.ns['m'])
            denominator = match.group(2)
            self._parse_latex(denominator, den)
            
            # 处理剩余部分
            latex_before = latex[:match.start()]
            latex_after = latex[match.end():]
            
            if latex_before:
                self._parse_latex(latex_before, parent_node)
            
            if latex_after:
                self._parse_latex(latex_after, parent_node)
            
            return
    
    def _process_sqrt(self, latex, parent_node):
        """处理根号结构"""
        # 匹配根号 \sqrt[n]{...}
        sqrt_pattern = r'\\sqrt(\[([^\]]+)\])?\{([^}]+)\}'
        match = re.search(sqrt_pattern, latex)
        
        if match:
            # 创建根号节点
            rad = ET.SubElement(parent_node, '{%s}rad' % self.ns['m'])
            
            # 指数（如果有）
            index = match.group(2)
            if index:
                deg = ET.SubElement(rad, '{%s}deg' % self.ns['m'])
                self._parse_latex(index, deg)
            
            # 被开方数
            e = ET.SubElement(rad, '{%s}e' % self.ns['m'])
            content = match.group(3)
            self._parse_latex(content, e)
            
            # 处理剩余部分
            latex_before = latex[:match.start()]
            latex_after = latex[match.end():]
            
            if latex_before:
                self._parse_latex(latex_before, parent_node)
            
            if latex_after:
                self._parse_latex(latex_after, parent_node)
            
            return
    
    def _process_sup_sub(self, latex, parent_node):
        """处理上下标结构"""
        # 先处理上标 ^
        sup_pattern = r'\^\{([^}]+)\}'
        sup_match = re.search(sup_pattern, latex)
        
        if sup_match:
            # 创建上标节点
            sSup = ET.SubElement(parent_node, '{%s}sSup' % self.ns['m'])
            
            # 底数
            e = ET.SubElement(sSup, '{%s}e' % self.ns['m'])
            base = latex[:sup_match.start()]
            self._parse_latex(base, e)
            
            # 指数
            sup = ET.SubElement(sSup, '{%s}sup' % self.ns['m'])
            exponent = sup_match.group(1)
            self._parse_latex(exponent, sup)
            
            # 处理剩余部分
            remaining = latex[sup_match.end():]
            if remaining:
                self._parse_latex(remaining, parent_node)
            
            return
        
        # 再处理下标 _
        sub_pattern = r'\_\{([^}]+)\}'
        sub_match = re.search(sub_pattern, latex)
        
        if sub_match:
            # 创建下标节点
            sSub = ET.SubElement(parent_node, '{%s}sSub' % self.ns['m'])
            
            # 底数
            e = ET.SubElement(sSub, '{%s}e' % self.ns['m'])
            base = latex[:sub_match.start()]
            self._parse_latex(base, e)
            
            # 下标
            sub = ET.SubElement(sSub, '{%s}sub' % self.ns['m'])
            subscript = sub_match.group(1)
            self._parse_latex(subscript, sub)
            
            # 处理剩余部分
            remaining = latex[sub_match.end():]
            if remaining:
                self._parse_latex(remaining, parent_node)
            
            return
    
    def _process_integral(self, latex, parent_node):
        """处理积分结构"""
        # 匹配积分 \int_{a}^{b}
        integral_pattern = r'\\int(_{([^}]*)})?(\^{([^}]*)})?'
        match = re.search(integral_pattern, latex)
        
        if match:
            # 创建积分节点
            inte = ET.SubElement(parent_node, '{%s}inte' % self.ns['m'])
            
            # 积分符号
            e = ET.SubElement(inte, '{%s}e' % self.ns['m'])
            self._add_text('∫', e)
            
            # 下限（如果有）
            if match.group(2):
                limLow = ET.SubElement(inte, '{%s}limLow' % self.ns['m'])
                e_low = ET.SubElement(limLow, '{%s}e' % self.ns['m'])
                self._parse_latex(match.group(2), e_low)
            
            # 上限（如果有）
            if match.group(4):
                limUpp = ET.SubElement(inte, '{%s}limUpp' % self.ns['m'])
                e_upp = ET.SubElement(limUpp, '{%s}e' % self.ns['m'])
                self._parse_latex(match.group(4), e_upp)
            
            # 处理剩余部分
            latex_after = latex[match.end():]
            if latex_after:
                self._parse_latex(latex_after, parent_node)
            
            return
    
    def _process_sum(self, latex, parent_node):
        """处理求和结构"""
        # 匹配求和 \sum_{i=1}^{n}
        sum_pattern = r'\\sum(_{([^}]*)})?(\^{([^}]*)})?'
        match = re.search(sum_pattern, latex)
        
        if match:
            # 创建求和节点
            sum_elem = ET.SubElement(parent_node, '{%s}sum' % self.ns['m'])
            
            # 求和符号
            e = ET.SubElement(sum_elem, '{%s}e' % self.ns['m'])
            self._add_text('∑', e)
            
            # 下限（如果有）
            if match.group(2):
                limLow = ET.SubElement(sum_elem, '{%s}limLow' % self.ns['m'])
                e_low = ET.SubElement(limLow, '{%s}e' % self.ns['m'])
                self._parse_latex(match.group(2), e_low)
            
            # 上限（如果有）
            if match.group(4):
                limUpp = ET.SubElement(sum_elem, '{%s}limUpp' % self.ns['m'])
                e_upp = ET.SubElement(limUpp, '{%s}e' % self.ns['m'])
                self._parse_latex(match.group(4), e_upp)
            
            # 处理剩余部分
            latex_after = latex[match.end():]
            if latex_after:
                self._parse_latex(latex_after, parent_node)
            
            return
    
    def _add_text(self, text, parent_node):
        """添加文本内容到节点"""
        if not text.strip():
            return
            
        # 创建运行节点
        r = ET.SubElement(parent_node, '{%s}r' % self.ns['m'])
        
        # 创建文本节点
        t = ET.SubElement(r, '{%s}t' % self.ns['m'])
        t.text = text

# 使用示例
if __name__ == "__main__":
    converter = LaTeXToOMathConverter()
    
    # 测试LaTeX公式
    latex_formula = r"\frac{x^2 + 1}{2y} + \sqrt{5x} + \int_{0}^{1} x^2 dx + \sum_{i=1}^{n} i^2"
    
    # 转换为Office MathML
    omath_xml = converter.convert(latex_formula)
    
    # 打印结果
    print(omath_xml)
    
    # 保存到文件
    with open('formula.xml', 'w', encoding='utf-8') as f:
        f.write(omath_xml)