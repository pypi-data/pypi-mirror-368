from docx.oxml.xmlchemy import BaseOxmlElement
from docx.oxml import parse_xml

xmlns = {
    # Word文档核心命名空间
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',  # Word 2013+扩展
    'w16cid': 'http://schemas.microsoft.com/office/word/2016/wordml/cid',  # 内容标识
    'w16se': 'http://schemas.microsoft.com/office/word/2015/wordml/symex',  # 符号扩展

    # 文档关系与包结构
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',  # 关系定义
    'pkg': 'http://schemas.microsoft.com/office/2006/xmlPackage',  # 包内文件结构
    'md': 'http://schemas.openxmlformats.org/markup-compatibility/2006',  # 兼容性标记

    # 绘图与图形
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',  # 基础绘图
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',  # 文档内绘图
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',  # 图片
    'dgm': 'http://schemas.openxmlformats.org/drawingml/2006/diagram',  # 图表
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',  # Word形状

    # 数学公式
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',  # 基础数学公式
    'mml': 'http://www.w3.org/1998/Math/MathML',  # MathML兼容

    # 表格与列表
    'tbl': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',  # 表格（常复用w命名空间）
    'aml': 'http://schemas.microsoft.com/aml/2001/core',  # 标注语言
    'wne': 'http://schemas.microsoft.com/office/word/2006/wordml',  # 编号扩展

    # 文档属性与元数据
    'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',  # 核心属性
    'dc': 'http://purl.org/dc/elements/1.1/',  # Dublin Core元数据
    'dcterms': 'http://purl.org/dc/terms/',  # Dublin Core术语
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',  # XML Schema实例
}

def parse_word_xml(xml: str) -> BaseOxmlElement:
    ss = "<root"
    for key in xmlns:
        ss += " xmlns:" + key + "=\"" + xmlns[key] + "\""
    ss += ">" + xml + "</root>"
    root = parse_xml(ss)
    children = root.getchildren()
    if len(children):
        return children[0]
    else:
        return root
