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


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config['suppress_callback_exceptions'] = True

app.layout = html.Div(children=[
    html.H1('Sbanken Dashboard'),

    dcc.DatePickerRange(
        id="transaction-range",
        min_date_allowed=dt(2012, 1, 1),
        max_date_allowed=dt.now().date(),
        start_date=dt(2019, 6, 1),
        end_date=dt.now().date()
    ),

    html.Br(),

    dcc.Tabs(
        id="tabs",
        value="overview",
        children=
        [
            dcc.Tab(label="Overview", value="overview", children=
                    [
                        html.H5("Nothing to see yet!")
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
    [
        dash.dependencies.Output("table", "columns"),
        dash.dependencies.Output("table", "data"),
    ],
    [
        dash.dependencies.Input("transaction-range", "start_date"),
        dash.dependencies.Input("transaction-range", "end_date")
    ]
    )
def update_table(start_date, end_date):
    transactions = sb.get_transactions(http_session, customerId, accountId, start_date, end_date, fake=True)
    transactions = sanitize_transactions(transactions, "cardDetails")

    df = pd.DataFrame.from_dict(transactions, orient="columns")
    col = create_columns(df)
    return (
        col,
        df.to_dict("records"),
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
    import api_settings

    http_session = sb.create_authenticated_http_session(api_settings.CLIENTID, api_settings.SECRET)

    customerId = api_settings.CUSTOMERID

    accountId = get_standard_account_id(http_session, customerId)

    app.run_server(debug=True)
