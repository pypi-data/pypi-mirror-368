from __future__ import annotations

import re as _re

        
def parse_kind_pattern(text: str, pattern: str | _re.Pattern):
    # pattern = fr"""
    # {prefix}(?:
    #     (?P<kind>{pattern})  |   # pattern sequence of kind
    #     (?P<invalid>)             # Other ill-formed exprs
    # )
    # """
    if isinstance(pattern, str):
        pattern = _re.compile(pattern, _re.IGNORECASE | _re.VERBOSE)
    if not isinstance(pattern, _re.Pattern):
        raise ValueError("pattern must be a string or compiled regex pattern.")
    tokens = []
    for match in pattern.finditer(text):
        kind = match.lastgroup  # 确定 token 类型
        value = match.group()   # 匹配的字符串
        tokens.append((kind, value))
    return tokens

def parse_nested_blocks(text, delimiters: str = "{}") -> list[tuple]:
    """Use the stack to track delimiters and parse nested delimiters"""
    if not isinstance(delimiters, str) or len(delimiters) != 2 or delimiters[0] == delimiters[1]:
        raise ValueError("Delimiter tuple must have exactly two different char.")
    left, right = delimiters
    nested_blocks = []
    stack = []
    flag = 1
    literal_text, field= ([], [])
    for char in text:
        if char == left:
            if not stack:  # 栈为空时，标记新嵌套块的开始
                flag = 2
            else:
                field.append(char)
            stack.append(char)  # 入栈，增加层级
        elif char == right:
            if stack:  # 栈不为空时，出栈减少层级
                stack.pop()
                if not stack:  # 栈为空时，说明当前嵌套块结束
                    nested_blocks.append(("".join(literal_text), "".join(field)))
                    flag = 1
                    literal_text, field= ([], [])
                else:
                    field.append(char)
        elif flag == 1:
            literal_text.append(char)
        elif flag == 2:
            field.append(char)
    
    return nested_blocks

def first_nested_blocks(text, delimiters: str = "{}") -> list[tuple]:
    if not isinstance(delimiters, str) or len(delimiters) != 2 or delimiters[0] == delimiters[1]:
        raise ValueError("Delimiter tuple must have exactly two different char.")
    left, right = delimiters
    stack = []
    flag = 1
    literal_text, field= ([], [])
    for char in text:
        if char == left:
            if not stack:  # 栈为空时，标记新嵌套块的开始
                flag = 2
            else:
                field.append(char)
            stack.append(char)  # 入栈，增加层级
        elif char == right:
            if stack:  # 栈不为空时，出栈减少层级
                stack.pop()
                if not stack:  # 栈为空时，说明当前嵌套块结束
                    break 
                else:
                    field.append(char)
        elif flag == 1:
            literal_text.append(char)
        elif flag == 2:
            field.append(char)
    if stack:
        raise ValueError("The block is not closed.")
    
    return ("".join(literal_text), "".join(field))