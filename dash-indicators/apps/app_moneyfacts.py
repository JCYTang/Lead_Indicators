import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from waitress import serve
from paste.translogger import TransLogger

from app import app

# declare global variables
file_data = 'data\\moneyfacts.csv'


def serve_layout():

    # import mapping
    df_data = pd.read_csv(file_data)
    vuk_brands = ['Clydesdale Bank', 'Virgin Money', 'Yorkshire Bank']
    other_brands = df_data['Company'].value_counts()
    other_brands = other_brands[other_brands >= 12].index.to_list()
    for brand in vuk_brands:
        other_brands.remove(brand)
    other_brands.sort()

    layout = dbc.Container([

        # store initial data
        dcc.Store(id='moneyfacts_data', data=df_data.to_dict('records')),

        # Top Banner
        dbc.Navbar([
            html.Div(
                dbc.Row([
                    dbc.Col(html.H1('UK Mortgage Rates'))
                ])
            ),

            dbc.Row([
                dbc.Col(html.Img(src=app.get_asset_url('IML_Logo.png'), height="40px")),
            ],
                className="ml-auto flex-nowrap mt-3 mt-md-0",
            )
        ]),

        dcc.Link('Back to home', href='/'),

        # Radio items
        dbc.Row([
            dbc.FormGroup(
                [
                    dbc.Label("Choose tenure"),
                    dbc.RadioItems(
                        options=[
                            {"label": "2yr", "value": '2yr'},
                            {"label": "5yr", "value": '5yr'},
                        ],
                        id="tenure-input-moneyfacts",
                    ),
                ]
            )
        ]),

        # Drop Down Menus
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='vuk-dropdown',
                    options=[dict(label=str(s), value=str(s)) for s in vuk_brands],
                    placeholder="Select VUK lender",
                ),
                width={'size': 3}
            ),
            dbc.Col(
                dcc.Dropdown(
                    id='other-dropdown',
                    options=[dict(label=str(s), value=str(s)) for s in other_brands],
                    placeholder="Select comparison lender",
                ),
                width={'size': 3}
            ),
        ]),

        # table with links to indicators
        # create charts for indicators vs share price
        dbc.Row(
            dbc.Col(
                id='chart-layout-moneyfacts',
                width='auto'
            )
        ),

        dbc.Row(
            dbc.Col(
                id='table-content-moneyfacts',
                width='auto'
            )
        ),
    ],
        fluid=True
    )

    return layout


# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# app.layout = serve_layout


# callback to update chart
@app.callback(
    Output('chart-layout-moneyfacts', 'children'),
    Output('table-content-moneyfacts', 'children'),
    Input('tenure-input-moneyfacts', 'value'),
    Input('vuk-dropdown', 'value'),
    Input('other-dropdown', 'value'),
    State('moneyfacts_data', 'data'))
def update_chart(tenure, vuk_brand, lender, data):

    if any(i is None for i in [tenure, vuk_brand, lender, data]):
        return [], []

    # populate table content with indicator descriptions
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[df['Term'] == tenure]
    df1 = df[df['Company'] == vuk_brand]
    df1 = df1.set_index('Date')
    ser1 = pd.Series(data=df1['Rate'])

    df2 = df[df['Company'] == lender]
    df2 = df2.set_index('Date')
    ser2 = pd.Series(data=df2['Rate'])

    fig = px.line(
        ser1 - ser2,
        y='Rate',
        labels={'Rate': 'Mortgage Rate (%)'},
        title=vuk_brand + ' - ' + lender + ' relative rate'
    )

    ser1.name = vuk_brand
    ser2.name = lender
    df_rates = pd.concat([ser1, ser2], axis=1).reset_index()
    df_rates['Date'] = df_rates['Date'].dt.strftime('%b-%y')

    table = dbc.Table.from_dataframe(df_rates, striped=True, bordered=True, hover=True)

    return [dbc.Col(dcc.Graph(figure=fig))], table


if __name__ == '__main__':
    serve(TransLogger(app.server, logging_level=30), host='AUD0100CK4', port=8085)
    # app.run_server(debug=True, host='AUD0100CK4', port=8085)