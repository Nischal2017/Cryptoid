import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objects as go
import sqlalchemy
import pandas as pd
    
engine = sqlalchemy.create_engine("sqlite:///BTCUSDTstream.db")
df = pd.read_sql('BTCUSDT',engine)
plot = dash.Dash(__name__)
plot.layout = html.Div(
    [
        dcc.Graph(id = 'live-graph', animate = True),
        dcc.Interval(
            id = 'graph-update',
            interval = 1000,
            n_intervals = 0
        ),
    ]
)

@plot.callback(
    Output('live-graph','figure'),
    [ Input('graph-update', 'n_intervals')]
)

def update_graph_scatter(n):
    fig = go.Figure([go.Scatter(x=df['Time'], y = df['Price'])])
    fig.show()

if __name__ == '__main__':
    plot.run_server()


