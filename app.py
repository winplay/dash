# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_daq as daq
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import numpy as np
from datetime import datetime


# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)

###----------------生成左边栏----------------###
def Generate_input_ip_address(id='input_ip_address'):
    """
    生成输入 IP地址栏
    """
    return html.Div(children=[
        dbc.Label("Input Ip Address and port:"),
        dbc.Input(placeholder="Input Ip here...", value='192.168.1.10',type="text",id=id),
        dbc.FormText("time tagger IP 地址"),
    ])

def Generate_input_time_intergration(id='input_time_intergration'):
    """
    时间积分
    """
    return html.Div(children=[
        dbc.Label("输入时间积分窗口[us]:"),
        dbc.Input(placeholder="Input us here...", value='10',type="number",id=id),
        dbc.FormText("在时间窗口内计数"),
    ])


###----------------生成右边栏----------------###
#####--------------生成第一栏--------------#####
intersting_Value=['date','SR[KHz]','cps','shot noise','contrast','std','allan']

def Genrate_intersting_table(table_header_name=intersting_Value,table_id='intersting_table',row_id='intersting_table_vlaue'):
    """
    生成感兴趣值的表格
    """
    table_header = [
    html.Thead(html.Tr([html.Th(name) for name in table_header_name]))
    ]
    init_value=np.zeros(len(table_header_name)).tolist()
    init_value[0]=datetime.now().strftime('%Y-%m-%d %H:%M:%S')    
    row1 = html.Tr(children=Generate_intersting_table_vlaue(init_value),id=row_id)
    table_body = [html.Tbody([row1])]
    table = dbc.Table(table_header + table_body,id=table_id,bordered=True)
    return table
def Generate_intersting_table_vlaue(value_list):
    """
    生成感兴趣值的表格的值
    """
    return [html.Td(value_list[0])]+[html.Td("{:.2f}".format(value)) for value in value_list[1:]]
def Generate_r_c_row1():
    '''
    生成右边第一栏
    包含我们所感兴趣的结果
    '''
    return dbc.Row(id='r_c_row1',children=[Genrate_intersting_table()]
    )

#####--------------生成第二栏--------------#####

def Generate_time_phi_graph():
    """
    生成图表
    """
    fig_time_phi = make_subplots(rows=1, cols=2)

    fig_time_phi.add_trace(
        go.Scatter(x=[1, 2, 3], y=[4, 5, 6],mode='lines', name='$\Delta$'),
        row=1, col=1
    )

    fig_time_phi.add_trace(
        go.Scatter(x=[20, 30, 40], y=[50, 60, 70]),
        row=1, col=2
    )
    
    return fig_time_phi

def Generate_r_c_row2():
    """
    生成右边第二栏
    包含图表
    """
    return dbc.Row(id='r_c_row2',children=[
        dcc.Graph(figure=Generate_time_phi_graph(), id='time_phi_graph',mathjax=True),
        dcc.Graph(figure=px.line(x=[0],y=[0]), id='frequency_phi_graph') 
        ])

#####--------------生成第三栏--------------#####
def Generate_cps_phi_graph():
    """
    生成图表
    """
    fig_cps_phi = go.Figure()
    fig_cps_phi.add_trace(go.Scatter(
        x=[],
        y=[]))
    return fig_cps_phi


def Generate_r_c_row3():
    """
    生成右边第三栏
    包含结果随时间变化的趋势
    """
    return dbc.Row(id='r_c_row3',children=[
        daq.BooleanSwitch(id='flag_cps_std', on=False,label="开启统计",labelPosition="top"),
        dcc.Graph(figure=Generate_cps_phi_graph(), id='cps_phi_graph')
    ])

# App layout
app.layout = dbc.Container([
    
    dcc.Interval(id='interval_component', interval=2*1000, n_intervals=0),
    
    dbc.Row(id='Title_app_name',children=[
        html.Div('General Application for real-time data visualization and DAQ',className='ten columns offset-by-one')
    ]),

    dbc.Row(id='main windows',children=[
        dbc.Col(id='left columns',width='auto',children=[
            Generate_input_ip_address(),
            Generate_input_time_intergration(),
        ]),

        dbc.Col(id='right columns',width='auto',children=[
            Generate_r_c_row1(),
            Generate_r_c_row2(),
            Generate_r_c_row3()
        ]),
    ]),

], fluid=True)


# Add controls to build the interaction
@callback(
    [Output(component_id='time_phi_graph', component_property='extendData'),
    Output(component_id='frequency_phi_graph', component_property='extendData'),
    Output(component_id='intersting_table_vlaue', component_property='children')],
    Input(component_id='interval_component', component_property='n_intervals'),
    Input(component_id='input_time_intergration', component_property='value')
)
def update_graph(n,time_intergration):
    time_intergration=float(time_intergration)
    data=np.random.random(20)
    data_time=np.arange(data.size)
    freq_data=np.abs(np.fft.rfft(data))
    freq=np.fft.rfftfreq(data.size,d=1/data.size)
    time_fig = [dict( x=[data_time],y=[data]), [0], data.size]
    freq_fig = [dict( x=[freq],y=[freq_data]), [0], freq.size]
    out_data=np.random.rand(len(intersting_Value)).tolist()
    out_data[0]=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    out_data[1]=1/time_intergration*1e3
    return [time_fig, freq_fig,Generate_intersting_table_vlaue(out_data)]

@callback(
    [Output(component_id='cps_phi_graph', component_property='extendData')],
    Input(component_id='interval_component', component_property='n_intervals'),
    Input(component_id='flag_cps_std', component_property='on')
)
def update_graph(n,flag_cps_std):
    if flag_cps_std:
        cps_fig=[dict( x=[[n]],y=[[1+n]]), [0], 100]
    else:
        cps_fig=[dict(x=[[]], y=[[]]), [0], 100]
    return [cps_fig]

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
