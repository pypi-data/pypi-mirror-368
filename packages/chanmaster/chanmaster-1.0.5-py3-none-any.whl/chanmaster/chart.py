from K import *

import numpy as np

from ta import SMA, MACD

from pyecharts import options as opts
from pyecharts.charts import Kline,Grid,Line,Bar,Scatter
from pyecharts.globals import ThemeType

from pyecharts.commons.utils import JsCode


width='1500px'
height='750px'
color_up = '#F9293E'
color_down = '#00aa3b'


def draw(k: K):
    init_opts = opts.InitOpts(page_title='%s__%s__%s__%s' % (k.symbol,k.freq,k.rawBars[0].dt,k.rawBars[-1].dt), width=width, height=height, theme=ThemeType.DARK)
    chart = Grid(init_opts)

    kChart=makeKline(k)
    lChart=makeLline(k)
    kChart = kChart.overlap(lChart)
    sChart=makeSline(k)
    kChart = kChart.overlap(sChart)
    zChart=makeSzone(k)
    kChart = kChart.overlap(zChart)

    smaChart=makeSMA(k)
    kChart = kChart.overlap(smaChart)

    chart.add(kChart, grid_opts=opts.GridOpts(pos_left='3%', pos_right='0%', pos_top='5%', height='50%'))

    macdChart=makeMACD(k)
    chart.add(macdChart, grid_opts=opts.GridOpts(pos_left='3%', pos_right='0%', pos_top='60%', height='15%'))

    volChart=makeVOL(k)
    chart.add(volChart, grid_opts=opts.GridOpts(pos_left='3%', pos_right='0%', pos_top='77%', height='15%'))

    return chart


def makeKline(k: K):
    #data
    rawBars=k.rawBars

    js_code_str= """
                 function(data)
                 {
                     tips='';
                     for(i=0;i<data.length;i++)
                     {
                         item=data[i];
                         if (item.seriesName==='L' || item.seriesName==='S' || item.seriesName==='R')
                         {
                             if (item.value.length>2)
                             {
                                 tips+=item.marker+item.seriesName;

                                 tips+='<strong>';
                                 tips+='&nbsp;&nbsp;&nbsp;&nbsp;'+item.value[1];
                                 tips+='</strong>';
                                 tips+='<br/>'                  
                             }
                         }
                         /*
                         if (item.seriesName==='R')
                         {
                             tips+=item.marker+item.seriesName;
                             tips+='<strong>';
                             tips+='&nbsp;&nbsp;&nbsp;&nbsp;'+item.value[1];
                             tips+='</strong>';
                             tips+='<br/>'
                         }
                         */
                         if (item.seriesName==='K')
                         {
                             tips+=item.marker+item.seriesName;

                             tips+='<strong>';
                             tips+='&nbsp;&nbsp;&nbsp;&nbsp;o '+item.value[1];
                             tips+='&nbsp;&nbsp;&nbsp;&nbsp;c '+item.value[2];
                             tips+='&nbsp;&nbsp;&nbsp;&nbsp;l '+item.value[3];
                             tips+='&nbsp;&nbsp;&nbsp;&nbsp;h '+item.value[4];
                             tips+='</strong>';
                             tips+='<br/>'
                         }
                     }
                     if (tips!='')
                     {
                         tips=data[0].axisValue+'<br>'+tips;
                     }
                     return tips;
                 }
                 """

    #init
    init_opts = opts.InitOpts(animation_opts=opts.AnimationOpts(animation=False))
    chart=Kline(init_opts)
    chart.set_global_opts(
        xaxis_opts=opts.AxisOpts(is_scale=True),
        yaxis_opts=opts.AxisOpts(is_scale=True),
        legend_opts=opts.LegendOpts(selected_map={"K": False,"笔": True,"R": False,"E": False,"MA5": False,"MACD": False,"VOL": False}),
        tooltip_opts=opts.TooltipOpts(trigger='axis',axis_pointer_type='none',formatter=JsCode(js_code_str),position=['3%','3%']),
        toolbox_opts=opts.ToolboxOpts(feature= opts.ToolBoxFeatureOpts(magic_type=None)),
        datazoom_opts=opts.DataZoomOpts(type_='slider',range_start=0,range_end=100,xaxis_index=[0, 1, 2]),
        # 添加版权信息文本
        graphic_opts=[opts.GraphicText(
                        graphic_item=opts.GraphicItem(
                            right="0.5%",
                            top="1%",
                            z=100),
                        graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                            text='chan.thingswell.cn',
                            font="16px Microsoft YaHei",
                            graphic_basicstyle_opts=opts.GraphicBasicStyleOpts(fill="rgba(152, 147, 193, 1.0)")
                        )
                     )],
    )

    #x
    dts = [x.dt for x in rawBars]
    chart.add_xaxis(xaxis_data=dts)

    #y
    data = [opts.CandleStickItem(name=x.dt, value=[x.open, x.close, x.low, x.high]) for x in rawBars]
    style = opts.ItemStyleOpts(color=color_up, color0=color_down, border_color=color_up, border_color0=color_down)
    chart.add_yaxis(series_name='K', y_axis=data,itemstyle_opts=style)

    return chart


def makeLline(k: K):
    #data
    lNodes=k.lNodes

    #init
    chart=Line()

    #x
    dts = [x.dt for x in lNodes]
    chart.add_xaxis(xaxis_data=dts)

    #y
    data = [x.value for x in lNodes]
    style = opts.ItemStyleOpts(color="rgba(152, 147, 193, 1.0)")
    chart.add_yaxis(series_name="笔", y_axis=data, symbol="circle", symbol_size=8,is_symbol_show=False,itemstyle_opts=style, label_opts=opts.LabelOpts(is_show=False))

    dotChart=Scatter()
    dotChart.add_xaxis(xaxis_data=dts)
    data = [[x.value,k.calPower(x,lNodes)] for x in lNodes]

    dotChart.add_yaxis(series_name="笔", y_axis=data, symbol="circle", symbol_size=8,itemstyle_opts=style, label_opts=opts.LabelOpts(is_show=False))

    return chart.overlap(dotChart)


def makeSline(k: K):
    #data
    sNodes=k.sNodes

    #init
    chart=Line()

    #x
    dts = [x.dt for x in sNodes]
    chart.add_xaxis(xaxis_data=dts)

    #R
    data = [x._value for x in sNodes]
    style = opts.ItemStyleOpts(color="rgba(255, 20, 147, 1.0)")
    chart.add_yaxis(series_name="R", y_axis=data, symbol="circle", symbol_size=8,is_symbol_show=False,itemstyle_opts=style, label_opts=opts.LabelOpts(is_show=False))

    dotChart=Scatter()
    dotChart.add_xaxis(xaxis_data=dts)
    data = [[x._value,k.calPower_R(x,sNodes)] for x in sNodes]

    dotChart.add_yaxis(series_name="R", y_axis=data, symbol="circle", symbol_size=8,itemstyle_opts=style, label_opts=opts.LabelOpts(is_show=False))

    chart=chart.overlap(dotChart)

    #y
    data = [x.value for x in sNodes]
    style = opts.ItemStyleOpts(color="rgba(255, 0, 0, 1.0)")
    chart.add_yaxis(series_name="线段", y_axis=data, symbol="circle", symbol_size=8,is_symbol_show=False,itemstyle_opts=style, label_opts=opts.LabelOpts(is_show=False))

    dotChart=Scatter()
    dotChart.add_xaxis(xaxis_data=dts)
    data = [[x.value,k.calPower(x,sNodes)] for x in sNodes]

    dotChart.add_yaxis(series_name="线段", y_axis=data, symbol="circle", symbol_size=8,itemstyle_opts=style, label_opts=opts.LabelOpts(is_show=False))

    return chart.overlap(dotChart)


def makeSzone(k: K):
    #init
    chart=Line()

    label_not_show_opts = opts.LabelOpts(is_show=False)
    for zone in k.sZones:
        if type(zone)==T and zone==k.sZones[-1]:
            continue
        rect=Line()
        rect.add_xaxis(xaxis_data=[zone.left.dt,zone.left.dt,zone.right.dt,zone.right.dt,zone.left.dt])
        rect.add_yaxis(series_name="Z", y_axis=[zone.zd,zone.zg,zone.zg,zone.zd,zone.zd], label_opts=label_not_show_opts, is_symbol_show=False,symbol='none',
                   linestyle_opts=opts.LineStyleOpts(opacity=1.0, width=1.0, color="#32CD32"))
        chart.overlap(rect)

        ggLine=Line()
        ggLine.add_xaxis(xaxis_data=[zone.left.dt,zone.right.dt])
        ggLine.add_yaxis(series_name="E", y_axis=[zone.gg,zone.gg], label_opts=label_not_show_opts, is_symbol_show=False,symbol='none',
                   linestyle_opts=opts.LineStyleOpts(type_='dashed',opacity=1.0, width=1.0, color="#FFD700"))
        chart.overlap(ggLine)

        ddLine=Line()
        ddLine.add_xaxis(xaxis_data=[zone.left.dt,zone.right.dt])
        ddLine.add_yaxis(series_name="E", y_axis=[zone.dd,zone.dd], label_opts=label_not_show_opts, is_symbol_show=False,symbol='none',
                   linestyle_opts=opts.LineStyleOpts(type_='dashed',opacity=1.0, width=1.0, color="#FFD700"))
        chart.overlap(ddLine)


        midLine=Line()

        midLine.add_xaxis(xaxis_data=[zone.left.dt,zone.right.dt])
        midLine.add_yaxis(series_name="E", y_axis=[zone.zz,zone.zz], label_opts=label_not_show_opts, is_symbol_show=False,symbol='none',
                   linestyle_opts=opts.LineStyleOpts(type_='dashed',opacity=1.0, width=1.0, color="white"))

        mids=k.getZoneMids(zone)
        for i in range(len(mids)-1):
            a=mids[i]
            b=mids[i+1]
            midLine.add_xaxis(xaxis_data=[a['dt'],b['dt']])
            midLine.add_yaxis(series_name="E", y_axis=[a['value'],b['value']], label_opts=label_not_show_opts, is_symbol_show=False,symbol='none',
                   linestyle_opts=opts.LineStyleOpts(opacity=1.0, width=2.0, color="rgba(255, 20, 147, 1.0)" if b['value']>=a['value'] else "#1E90FF"))

        chart.overlap(midLine)

    return chart


def makeMACD(k: K):
    label_not_show_opts = opts.LabelOpts(is_show=False)
    green_item_style = opts.ItemStyleOpts(color=color_down)
    red_item_style = opts.ItemStyleOpts(color=color_up)

    close = np.array([x.close for x in k.rawBars], dtype=np.double)
    diff, dea, macd = MACD(close)
    macd_bar = []
    for i, v in enumerate(macd.tolist()):
        item_style = red_item_style if v > 0 else green_item_style
        bar = opts.BarItem(name=i, value=round(v, 4), itemstyle_opts=item_style,
                           label_opts=label_not_show_opts)
        macd_bar.append(bar)

    diff = diff.round(4)
    dea = dea.round(4)


    dts = [x.dt for x in k.rawBars]
    chart_macd = Bar()
    chart_macd.add_xaxis(dts)
    chart_macd.add_yaxis(series_name="MACD", y_axis=macd_bar)
    chart_macd.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            type_="category",
            grid_index=2,
            axislabel_opts=opts.LabelOpts(is_show=False),
            splitline_opts=opts.SplitLineOpts(is_show=False),
        ),
        yaxis_opts=opts.AxisOpts(
            grid_index=2,
            split_number=4,
            axisline_opts=opts.AxisLineOpts(is_on_zero=False),
            axistick_opts=opts.AxisTickOpts(is_show=False),
            splitline_opts=opts.SplitLineOpts(is_show=False),
            axislabel_opts=opts.LabelOpts(is_show=True, color="#c7c7c7"),
        ),
        legend_opts=opts.LegendOpts(pos_left='3%'),
    )

    line = Line()
    line.add_xaxis(dts)
    line.add_yaxis(series_name="MACD", y_axis=diff, label_opts=label_not_show_opts, is_symbol_show=False,symbol='none',
                   linestyle_opts=opts.LineStyleOpts(opacity=0.8, width=1.0, color="#39afe6"))
    line.add_yaxis(series_name="MACD", y_axis=dea, label_opts=label_not_show_opts, is_symbol_show=False,symbol='none',
                   linestyle_opts=opts.LineStyleOpts(opacity=0.8, width=1.0, color="#FFFFFF"))

    chart_macd = chart_macd.overlap(line)

    return chart_macd


def makeVOL(k: K):
    label_not_show_opts = opts.LabelOpts(is_show=False)
    green_item_style = opts.ItemStyleOpts(color=color_down)
    red_item_style = opts.ItemStyleOpts(color=color_up)

    dts = [x.dt for x in k.rawBars]

    vol = []
    for item in k.rawBars:
        item_style = red_item_style if item.close > item.open else green_item_style
        bar = opts.BarItem(name=item.id, value=item.vol, itemstyle_opts=item_style, label_opts=label_not_show_opts)
        vol.append(bar)

    chart_vol = Bar()
    chart_vol.add_xaxis(dts)
    chart_vol.add_yaxis(series_name="VOL", y_axis=vol, bar_width='60%')
    chart_vol.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            type_="category",
            grid_index=2,
            axislabel_opts=opts.LabelOpts(is_show=False),
            splitline_opts=opts.SplitLineOpts(is_show=False),
        ),
        yaxis_opts=opts.AxisOpts(
            grid_index=2,
            split_number=4,
            axisline_opts=opts.AxisLineOpts(is_on_zero=False),
            axistick_opts=opts.AxisTickOpts(is_show=False),
            splitline_opts=opts.SplitLineOpts(is_show=False),
            axislabel_opts=opts.LabelOpts(is_show=True, color="#c7c7c7"),
        ),
        legend_opts=opts.LegendOpts(pos_left='10%'),
    )

    return chart_vol


def makeSMA(k: K):
    label_not_show_opts = opts.LabelOpts(is_show=False)

    dts = [x.dt for x in k.rawBars]
    close = np.array([x.close for x in k.rawBars], dtype=np.double)

    chart_ma = Line()
    chart_ma.add_xaxis(xaxis_data=dts)
    
    ma5=SMA(close, timeperiod=5)

    chart_ma.add_yaxis(series_name='MA5', y_axis=ma5, is_smooth=True,
                           is_symbol_show=False,symbol='none', label_opts=label_not_show_opts,
                           linestyle_opts=opts.LineStyleOpts(opacity=0.8, width=1, color="#39afe6"))

    return chart_ma
