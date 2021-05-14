import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
from waitress import serve
from paste.translogger import TransLogger

from app import app

# declare global variables
file_returns = 'data\\returns.xlsm'
file_map = 'data\\maps.xlsx'
file_data = 'data\\data.csv'

# import mapping
df_stocks = pd.read_excel(file_map, sheet_name='stocks')
df_sectors = pd.read_excel(file_map, sheet_name='sectors')
df_indicators = pd.read_excel(file_map, sheet_name='indicators')
sectors = df_sectors['Sector'].unique()
sector_options = [dict(label=str(s), value=str(s)) for s in sectors]
df_map = df_stocks.join(df_sectors.set_index('Stock'), 'Stock').join(df_indicators.set_index('Indicator'), 'Indicator')


def serve_layout():

    # import stock returns
    df_returns = pd.read_excel(file_returns, sheet_name='Sheet1')
    tickers = df_returns['Code']
    df_returns = df_returns.iloc[:, 2:].T
    df_returns.columns = tickers
    df_returns.columns.name = ''
    df_returns.index.name = 'Date'
    df_returns.dropna(inplace=True)
    df_returns.index = pd.to_datetime(df_returns.index)

    # import indicator data
    df_data = pd.read_csv(file_data, index_col='Date')
    df_data.index = pd.to_datetime(df_data.index)

    layout = dbc.Container([

        # store initial data
        dcc.Store(id='initial_returns_data', data=df_returns.reset_index().to_dict('records')),
        dcc.Store(id='initial_indicators_data', data=df_data.reset_index().to_dict('records')),

        # indicator descriptions based on user stock selection
        dcc.Store(id='indicators_desc'),

        # filtered returns data based on user stock selection
        dcc.Store(id='returns_data'),

        # filtered indicator data based on user stock selection
        dcc.Store(id='indicators_data'),

        # Top Banner
        dbc.Navbar([
            html.Div(
                dbc.Row([
                    dbc.Col(html.H1('Leading Indicators'))
                ])
            ),

            dbc.Row([
                dbc.Col(html.Img(src=app.get_asset_url('IML_Logo.png'), height="40px")),
            ],
                className="ml-auto flex-nowrap mt-3 mt-md-0",
            )
        ]),

        # Drop Down Menus
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='sect-dropdown',
                    options=sector_options,
                    placeholder="Select a sector",
                ),
                width={'size': 3}
            ),
            dbc.Col(
                dcc.Dropdown(
                    id='stock-dropdown',
                    placeholder="Select a stock",
                ),
                width={'size': 2}
            ),
        ]),

        # table with links to indicators
        dbc.Row([
            dbc.Col(
                id='table-content',
            )
        ]),

        # create charts for indicators vs share price
        dbc.Row(
            id='chart-layout',
        )
    ],
        fluid=True
    )

    return layout


# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# app.layout = serve_layout


# callback to update the following output when user selects a stock:
# 1. indicators description dataframe
# 2. returns data dataframe
# 3. indicators data dataframe
@app.callback(
    Output('indicators_desc', 'data'),
    Output('indicators_data', 'data'),
    Output('returns_data', 'data'),
    Input('stock-dropdown', 'value'),
    State('initial_indicators_data', 'data'),
    State('initial_returns_data', 'data'))
def filter_data(stock, initial_indicators_data, initial_returns_data):
    if stock is None:
        return None, None, None

    # indicators = df_map[df_map['Stock'] == stock]['Indicator'].tolist()
    indicators = df_map[(df_map['Stock'] == stock) & (df_map['Chart'] == True)]['Indicator'].tolist()
    df_data = pd.DataFrame(initial_indicators_data)
    df_returns = pd.DataFrame(initial_returns_data)
    df_data.set_index('Date', inplace=True)
    df_returns.set_index('Date', inplace=True)

    return df_map[df_map['Stock'] == stock].to_dict('records'), \
           df_data[indicators].reset_index().to_dict('records'), \
           df_returns[stock].reset_index().to_dict('records')


# callback to update table with indicator decriptions when user selects a stock
@app.callback(
    Output('stock-dropdown', 'options'),
    Output('table-content', 'children'),
    Output('chart-layout', 'children'),
    Input('sect-dropdown', 'value'),
    Input('indicators_desc', 'data'),
    Input('indicators_data', 'data'),
    Input('returns_data', 'data'),
    State('stock-dropdown', 'options'))
def update_table(sector, indicators_desc_data, indicators_data, returns_data, stock_options):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger == 'sect-dropdown':
        if sector is None:
            return [], None, None

        return [{'label': i, 'value': i} for i in df_sectors[df_sectors['Sector'] == sector]['Stock']], None, None

    if any(i is None for i in [indicators_desc_data, indicators_data, returns_data]):
        raise PreventUpdate

    # populate table content with indicator descriptions
    df = pd.DataFrame(indicators_desc_data)
    indicators = df[df['Chart']==True]['Indicator'].tolist()
    df = df[['Indicator', 'Description', 'Source']]
    df_dict = df.to_dict('list')
    df_dict['Source'] = [html.A(link, href=link, target='_blank') for link in df_dict['Source']]
    df = pd.DataFrame(df_dict)
    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

    # populate chart data for each indicator
    charts = []
    df_ind = pd.DataFrame(indicators_data)
    df_ind.set_index('Date', inplace=True)
    df_stock_ret = pd.DataFrame(returns_data)
    df_stock_ret.set_index('Date', inplace=True)

    for indicator in indicators:
        # rebase indicator series to 100
        ser_ind = df_ind[indicator].dropna()
        ser_ind = ser_ind / ser_ind[0] * 100

        # rebase stock returns to 100
        start_date = ser_ind.index[0]
        ser_stock = df_stock_ret[start_date:]
        ser_stock = (1 + ser_stock / 100).cumprod()
        ser_stock = ser_stock / ser_stock.loc[start_date] * 100

        # set dataframe which contains indicator and stock return series
        df_chart = pd.concat([ser_ind, ser_stock], axis=1)
        df_chart.dropna(inplace=True)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=df_chart.index, y=df_chart[indicator], name=indicator + ' (LHS)'),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=df_chart.index, y=df_chart.iloc[:, 1], name=df_chart.columns[1] + ' (RHS)'),
            secondary_y=True,
        )

        fig.update_layout(
            legend=dict(
                orientation="h",
            )
        )

        charts.append(dbc.Col(dcc.Graph(figure=fig), width={'size': 6}))

    return stock_options, table, charts


# if __name__ == '__main__':
#     serve(TransLogger(app.server, logging_level=30), host='AUD0100CK4', port=8084)
#     # app.run_server(debug=True, host='AUD0100CK4', port=8084)