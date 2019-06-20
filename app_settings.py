from os import environ

"""
To promote good security practice, this sample application gets credentials from
environment variables.

For convenience during development, it is sometimes preferrable to use a `.env`
file. To do so, copy the distributed file (`cp .env.dist .env`) and add your
credentials. If you use [Pipenv](https://docs.pipenv.org/), the .env file will
be loaded automatically. If not, you can use 
[python-dotenv](https://github.com/theskumar/python-dotenv):

1. Install the package by running `pip install python-dotenv`.
2. Uncomment the two lines below to load the environment variables in `.env`.
"""

# from dotenv import load_dotenv, find_dotenv
# load_dotenv(find_dotenv())

# This is your social security number. The same Id which is used when you log in with BankID.
CUSTOMERID = environ['CUSTOMERID']

# Get CLIENTID ('Applikasjonsnøkkel') and SECRET ('Passord') from https://secure.sbanken.no/Personal/ApiBeta/Info
CLIENTID = environ['CLIENTID']
SECRET = environ['SECRET']
