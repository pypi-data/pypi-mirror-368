from typing import List,Union
from datetime import datetime
from dataclasses import dataclass

from myEnum import T,Direction


@dataclass
class RawBar:
    id: int  # id 必须是升序
    dt: datetime
    ###
    open: [float, int]
    close: [float, int]
    high: [float, int]
    low: [float, int]
    ###
    vol: [float, int]
    amount: [float, int]


@dataclass
class NewBar(RawBar):
    elements: List[RawBar]  # 存入具有包含关系的原始K线

    @property
    def rawBars(self):
        return self.elements


@dataclass
class TNode():
    t: T  # 顶底类型
    srcIndex: int
    id: int
    dt: datetime
    value: [float, int]

    elements: List[NewBar]  # 存入组成分型的三根K线

    @property
    def newBars(self):
        return self.elements


@dataclass
class LNode():
    t: T  # 顶底类型
    srcIndex: int
    id: int
    dt: datetime
    value: [float, int]

    elements: List[TNode]  # 存入具有扩展关系的原始分型

    @property
    def extendTNodes(self):
        return self.elements


@dataclass
class SNode():
    t: T  # 顶底类型
    srcIndex: int
    id: int
    dt: datetime
    value: [float, int]

    elements: List[LNode]  # 存入具有扩展关系的原始分型

    _value: [float, int]=None

    @property
    def extendLNodes(self):
        return self.elements


@dataclass
class X():
    id: int
    dt: datetime
    

@dataclass
class Zone():
    zz: [float, int]
    zg: [float, int]
    zd: [float, int]
    gg: [float, int]
    dd: [float, int]
    left: X
    right: X
    direction: Direction
    sCount=3
    elements: List[SNode]  # 存入中枢线段
