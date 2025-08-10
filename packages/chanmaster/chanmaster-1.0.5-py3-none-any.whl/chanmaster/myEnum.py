from enum import Enum


class Direction(Enum):
    Up = "向上"
    Down = "向下"

class Freq(Enum):
    F1 = "1分钟"
    F5 = "5分钟"
    F15 = "15分钟"
    F30 = "30分钟"
    F60 = "60分钟"
    D = "日线"
    W = "周线"
    M = "月线"
    S = "季线"
    Y = "年线"

class T(Enum):
    Top = "顶"
    Bottom = "底"
