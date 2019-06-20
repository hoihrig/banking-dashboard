import json

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import sbanken_data as sb
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


def create_columns(df):
    col = []
    for i in df.columns:
        if i in [
            "accountingDate",
            "amount",
            "text",
            "transactionType"
        ]:
            col.append({"name": i, "id": i, "hidden": False})
        else:
            col.append({"name": i, "id": i, "hidden": True})
    return col


def sanitize_transactions(transactions, key):
    for entry in transactions:
        entry.pop(key, None)
    return transactions


def get_standard_account_id(session, cId):
    accounts = sb.get_accounts(session, cId)
    for res in accounts:
        if res["accountType"] == "Standard account":
            return res["accountId"]


def generate_pie(datasets, dataset):
    pielabels = []
    pievalues = []
    for key, value in datasets[dataset].items():
        pielabels.append(key)
        pievalues.append(value)
    figuredata = {
        "data": [{
            "labels": pielabels,
            "values": pievalues,
            "type": "pie"
        }],
        "layout": {
            'margin': {
                'l': 30,
                'r': 0,
                'b': 30,
                't': 50
            },
            'legend': {'x': 0, 'y': 1, "bgcolor": "transparent"}
        }
    }
    return figuredata


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1('Banking Dashboard'),

    dcc.DatePickerRange(
        id="transaction-range",
        min_date_allowed=dt(2012, 1, 1),
        max_date_allowed=dt.now().date(),
        start_date=dt(2019, 6, 1),
        end_date=dt.now().date()
    ),

    html.Button("Fetch Data", id="fd-button", style=
    {
        "margin-left": "30px"
    }
                ),

    html.Br(),
    html.Br(),

    # Hidden div inside the app that stores the intermediate value
    html.Div(id='bdata', style={'display': 'none'}),

    dcc.Tabs(
        id="tabs",
        value="overview",
        children=
        [
            dcc.Tab(label="Overview", value="overview", children=
            [
                html.Div(id="pie-overview", className="row", children=
                            [
                                html.Div(dcc.Graph(id="overview-incoming"),className="six columns"),
                                html.Div(dcc.Graph(id="overview-outgoing"),className="six columns"),
                            ]
                         )
            ]
                    ),
            dcc.Tab(label="Transactions", value="transactions", children=
            [
                dcc.Checklist(
                    id="switches",
                    options=[
                        {"label": "Enable Sorting", "value": "sort"},
                        {"label": "Enable Filtering", "value": "filter"},
                    ],
                    values=["sort"],
                    labelStyle={"display": "inline-block"}
                ),

                html.Br(),

                dash_table.DataTable(
                    id="table"
                ),
            ]
                    ),
        ]),

])


@app.callback(
    dash.dependencies.Output("bdata", "children"),
    [
        dash.dependencies.Input("fd-button", "n_clicks"),
    ],
    [
        dash.dependencies.State("transaction-range", "start_date"),
        dash.dependencies.State("transaction-range", "end_date"),
    ]
)
def fetch_process_data(n_clicks, start_date, end_date):
    if n_clicks is None:
        return

    transactions = sb.get_transactions(http_session, customerId, accountId, start_date, end_date, fake=False)
    transactions = sanitize_transactions(transactions, "cardDetails")

    df = pd.DataFrame.from_dict(transactions, orient="columns")
    categorized_transactions = sb.categorize_transactions(transactions)

    datasets = {
        "data_columns": create_columns(df),
        "data_records": df.to_dict("records"),
        "categorized_data_incoming": sb.sum_income_categories(categorized_transactions),
        "categorized_data_outgoing": sb.sum_expense_categories(categorized_transactions)
    }

    return json.dumps(datasets)


@app.callback(
    [
        dash.dependencies.Output("overview-incoming", "figure"),
        dash.dependencies.Output("overview-incoming", "style"),
        dash.dependencies.Output("overview-outgoing", "figure"),
        dash.dependencies.Output("overview-outgoing", "style"),
    ],
    [
        dash.dependencies.Input("bdata", "children"),
        dash.dependencies.Input("fd-button", "n_clicks"),
    ]
)
def update_overview(json_data, n_clicks):
    if n_clicks is None:
        return (
            {},
            {"display": "none"},
            {},
            {"display": "none"}
        )

    datasets = json.loads(json_data)

    figuredata_incoming = generate_pie(datasets, "categorized_data_incoming")
    figuredata_outgoing = generate_pie(datasets, "categorized_data_outgoing")

    return (
        figuredata_incoming,
        {"display": "block"},
        figuredata_outgoing,
        {"display": "block"}
    )


@app.callback(
    [
        dash.dependencies.Output("table", "columns"),
        dash.dependencies.Output("table", "data"),
    ],
    [
        dash.dependencies.Input("bdata", "children"),
        dash.dependencies.Input("fd-button", "n_clicks"),
    ]
)
def update_table(json_data, n_clicks):
    if n_clicks is None:
        return (
            [],
            []
        )

    datasets = json.loads(json_data)

    col = datasets["data_columns"]
    records = datasets["data_records"]

    return (
        col,
        records,
    )


@app.callback(
    [
        dash.dependencies.Output("table", "sorting"),
        dash.dependencies.Output("table", "filtering")
    ],
    [
        dash.dependencies.Input("switches", "values")
    ]
)
def update_table_capabilities(values):
    sorting = False
    filtering = False

    if "sort" in values:
        sorting = True

    if "filter" in values:
        filtering = True

    return (
        sorting,
        filtering
    )


if __name__ == '__main__':
    import app_settings

    http_session = sb.create_authenticated_http_session(app_settings.CLIENTID, app_settings.SECRET)

    customerId = app_settings.CUSTOMERID

    accountId = get_standard_account_id(http_session, customerId)

    app.run_server(host='0.0.0.0', debug=False)
