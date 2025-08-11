from string import Formatter
import sys
import re
from bdtool.share import color_map
def get_formatter_keys(ss: str):
    res = set()
    for t in Formatter().parse(ss):
        if t[1] is not None:
            res.add(t[1])
    return res

def touch():
    with open(sys.argv[1], 'a') as f:
        pass
    
def common_color_rgb(color) -> tuple | None:
    if isinstance(color, str):
        if color in color_map:
            return color_map[color]
        else:
            match = re.search(r"\(([^>]+)\)", color)
            if match:
                rgb = tuple(int(v) for v in match.group(1).split(','))
                if len(rgb) >= 3:
                    return rgb
            return None
    else:
        return tuple(int(v) for v in color)
    