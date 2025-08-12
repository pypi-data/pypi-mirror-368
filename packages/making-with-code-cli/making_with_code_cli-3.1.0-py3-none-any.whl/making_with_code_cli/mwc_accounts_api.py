import requests
import json
import os
from pathlib import Path
from urllib.parse import urljoin
from getpass import getpass

LOCALHOST = "http://localhost:8000"
MWC_ACCOUNTS_SERVER = "https://accounts.makingwithcode.org"

class MWCAccountsAPI:
    def __init__(self, mwc_accounts_server=MWC_ACCOUNTS_SERVER):
        self.mwc_accounts_server = mwc_accounts_server

    def login(self, username, password):
        "Authenticates with a username and password, returning an auth token"
        url = self.mwc_accounts_server + "/login"
        data = {"username": username, "password": password}
        response = requests.post(url, data=data)
        return self.handle_response(response)

    def logout(self, token):
        url = self.mwc_accounts_server + "/logout"
        headers = {"Authorization": f"Token {token}"}
        response = requests.post(url, headers=headers)
        return self.handle_response(response)

    def get_status(self, token):
        url = self.mwc_accounts_server + "/status"
        headers = {"Authorization": f"Token {token}"}
        response = requests.get(url, headers=headers)
        return self.handle_response(response)

    def get_roster(self, token):
        url = self.mwc_accounts_server + "/roster"
        headers = {"Authorization": f"Token {token}"}
        response = requests.get(url, headers=headers)
        return self.handle_response(response)

    def handle_response(self, response):
        if response.ok:
            return response.json()
        elif response.status_code == 500:
            raise self.ServerError("Error 500")
        else:
            try:
                rj = response.json()
                raise self.RequestFailed(rj)
            except requests.exceptions.JSONDecodeError:
                raise self.RequestFailed(response)

    class RequestFailed(Exception):
        pass

    class ServerError(Exception):
        pass





