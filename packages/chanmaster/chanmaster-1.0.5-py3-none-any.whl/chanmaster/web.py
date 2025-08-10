from flask import Flask
from flask import request

app = Flask(__name__ ,static_url_path='')

import render


@app.route('/',methods=['get'])
def home():
    return app.send_static_file('index.html')

@app.route('/adjust',methods=['get'])
def get_adjust():
    symbol=request.args.get('symbol')
    return adjust.getAdjust(symbol)
    

@app.route('/chart',methods=['get'])
def get_chart():
    try:
        symbol=request.args.get('symbol')
        freq=request.args.get('freq')
        isIndex=request.args.get('isIndex')=='true'
        isEnding=request.args.get('isEnding')=='true'
        isAdjust=request.args.get('isAdjust')=='true'

        kSet=render.getData(symbol,freq,isIndex,isAdjust)
        result=render.render_embed(kSet,freq,isEnding)
    except Exception as e:
        return '<h2>%s</h2>' % str(e)

    return result

def start(host,port):
    print('\n'*1)
    print('****** ChanMaster ******')
    print('请勿关此窗口')
    print('用浏览器打开  http://%s:%d  开始使用' % (host,port))
    print('\n'*2)
    app.run(host=host,port=port)


if __name__ == '__main__':
    start(host='127.0.0.1',port=51168)
