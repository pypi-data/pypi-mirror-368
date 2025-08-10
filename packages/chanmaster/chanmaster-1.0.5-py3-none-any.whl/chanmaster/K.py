from myEnum import *
from myObject import *


class K:
    def __init__(self,symbol: str,freq: Freq):
        self.symbol=symbol
        self.freq=freq
        self.count=0
        
        self.rawBars=[]

        self.lNodes=[]
        self.sNodes=[]

        self.sZones =[]

    def addRawBar(self,dt,open,close,high,low,vol,amount):
        rawBar=RawBar(id=self.count, dt=dt, 
                    open=open, close=close, high=high, low=low, 
                    vol=vol, amount=amount)
        self.rawBars.append(rawBar)
        self.count+=1
        self.update()

    def update(self):
        pass

    def calPower(self,node: Union[LNode,SNode], nodes: List[Union[LNode,SNode]]):
        return 0

    def calPower_R(self,node: Union[LNode,SNode], nodes: List[Union[LNode,SNode]]):
        return 0
