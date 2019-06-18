from oauthlib.oauth2 import BackendApplicationClient
import requests
from requests_oauthlib import OAuth2Session
import urllib.parse
import json


def create_authenticated_http_session(client_id, client_secret) -> requests.Session:
    oauth2_client = BackendApplicationClient(client_id=urllib.parse.quote(client_id))
    session = OAuth2Session(client=oauth2_client)
    session.fetch_token(
        token_url='https://auth.sbanken.no/identityserver/connect/token',
        client_id=urllib.parse.quote(client_id),
        client_secret=urllib.parse.quote(client_secret)
    )
    return session


def get_customer_information(http_session: requests.Session, customerid):
    response_object = http_session.get(
        "https://api.sbanken.no/exec.customers/api/v1/Customers",
        headers={'customerId': customerid}
    )
    print(response_object)
    print(response_object.text)
    response = response_object.json()

    if not response["isError"]:
        return response["item"]
    else:
        raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))


def get_accounts(http_session: requests.Session, customerid):
    response = http_session.get(
        "https://api.sbanken.no/exec.bank/api/v1/Accounts",
        headers={'customerId': customerid}
    ).json()

    if not response["isError"]:
        return response["items"]
    else:
        raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))


def get_transactions(http_session: requests.Session, customerid, accountid, startDate, endDate, fake=False):
    if fake:
        with open('mytransactions.json') as json_file:
            data = json.load(json_file)
        return data

    rqbase = "https://api.sbanken.no/exec.bank/api/v1/Transactions/" + accountid
    qstring = "?startDate=" + startDate + "&endDate=" + endDate

    response = http_session.get(
        rqbase + qstring,
        headers={'customerId': customerid}
    ).json()

    if not response["isError"]:
        return response["items"]
    else:
        raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))


def categorize_transactions(transactions):
    stransactions = {}
    for t in transactions:
        if t["transactionType"] not in stransactions:
            stransactions[t["transactionType"]] = []
        stransactions[t["transactionType"]].append(t)
    return stransactions


def sum_income_categories(stransactions):
    sums = {}
    for category, entry in stransactions.items():
        for item in entry:
            if item["amount"] > 0:
                sums[category] = 0
                sums[category] = sums[category] + item["amount"]
    return sums


def sum_expense_categories(stransactions):
    sums = {}
    for category, entry in stransactions.items():
        for item in entry:
            if item["amount"] < 0:
                sums[category] = 0
                sums[category] = sums[category] + abs(item["amount"])
    return sums


def balance_total(csums):
    balance = 0
    for key, value in csums.items():
        balance = balance + value
    return balance