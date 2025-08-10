from myEnum import *
from myObject import *
from K import *

import requests

from flask import request


def updateK(k: K):
    token=request.args.get('token')

    items=[]
    for bar in k.rawBars:
        item=[bar.dt,bar.high,bar.low]
        items.append(item)
    data={'token':token, 'items':items}
    
    #result=requests.post('http://127.0.0.1:6000/k',json=data)
    result=requests.post('https://chan-api.thingswell.cn/',json=data)

    if result.status_code in [401,405]:
        raise Exception(result.text)
    
    result=result.json()

    lNodes=result['lNodes']
    sNodes=result['sNodes']

    for item in lNodes:
        node=LNode(T.Bottom if item['t']=='Bottom' else T.Top,0,item['id'],item['dt'],item['value'],[])
        k.lNodes.append(node)

    for item in sNodes:
        node=SNode(T.Bottom if item['t']=='Bottom' else T.Top,0,item['id'],item['dt'],item['value'],[],item['_value'])
        k.sNodes.append(node)
