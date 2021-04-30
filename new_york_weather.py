import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# prepare data
df = pd.read_csv('data.csv')
# convert timestamp to datetime
df['t_stamp'] = pd.to_datetime(df['t_stamp'], unit='s')
# set index
df = df.set_index('t_stamp')

stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=stylesheet)

app.layout = html.Div([
    html.H1('History weather of New York', style={'textAlign': 'center'}),
    html.Div([
        dcc.Markdown("""
        This dataset comes from https://www.timeanddate.com/weather/usa/new-york/historic including almost everyday of 2019 and 2020.
        
        You can browser the temperature graph of every month. 
        """),
    ]),
    html.Div([
        dcc.Dropdown(options=[
            {'label': '2019', 'value': 2019},
            {'label': '2020', 'value': 2020},
        ], value=2019, id='year'),
        dcc.Dropdown(options=[{'label': i, 'value': i} for i in range(1, 13)],
                     id='month', value=1),
        dcc.Checklist(
            options=[
                {'label': '06:00', 'value': 6},
                {'label': '12:00', 'value': 12},
                {'label': '18:00', 'value': 18},
            ], value=[6, 12, 18], id='clock'),
    ], style={"width": "20%"}, ),
    dcc.Graph(
        id='line_chart',
    ),
    dcc.Graph(
        id='bar_graph',
    ),
])

server = app.server


@app.callback(
    Output(component_id="line_chart", component_property="figure"),
    Input(component_id="year", component_property="value"),
    Input(component_id="month", component_property="value"),
    Input(component_id="clock", component_property="value")
)
def update_line(year, month, clock):
    chart_df = search(year, month, clock)
    x = chart_df.index
    y1 = chart_df.temp_low
    y2 = chart_df.temp_hi
    s1 = go.Scatter(x=x, y=y1, name='temperature low')
    s2 = go.Scatter(x=x, y=y2, name='temperature high')
    return go.Figure(data=[s1, s2])


@app.callback(
    Output(component_id="bar_graph", component_property="figure"),
    Input(component_id="year", component_property="value"),
    Input(component_id="month", component_property="value"),
    Input(component_id="clock", component_property="value")
)
def update_bar(year, month, clock):
    chart_df = search(year, month, clock)
    weather_count = chart_df.groupby('weather').count()['temp_hi']
    x = weather_count.index
    y = weather_count.values
    bar = go.Bar(
        x=x,
        y=y,
        name='Count of weather'
    )
    return go.Figure(data=[bar])


def search(year, month, clock):
    chart_df = df.loc['%d-%d' % (year, month)]
    if clock is None or len(clock) == 0:
        clock = [6, 12, 18]
    idx = None
    for c in clock:
        if idx is None:
            idx = chart_df.clock == c
        else:
            idx |= chart_df.clock == c
    chart_df = chart_df[idx]
    return chart_df


if __name__ == '__main__':
    app.run_server(debug=True)
