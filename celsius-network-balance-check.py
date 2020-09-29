import requests
import pandas as pd
import os
from datetime import datetime

pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 15)


class CelsiusNetworkAPI:
    _base_url = "https://wallet-api.celsius.network"

    def __init__(self, partner_token, user_token):
        self.partner_token = partner_token
        self.user_token = user_token
        self.actions = {
            "balance_summary": {
                "description": "Check Wallet Balance Summary (USD)",
                "param": "No parameters needed",
                "url": "/wallet/interest"
            },
            "balance_summary_coin": {
                "description": "Check Wallet Balance Summary (in Kind)",
                "param": "coin short form (e.g. BTC, ETH)",
                "url": "/wallet/{}/balance"
            },
            "transaction_summary": {
                "description": "Check Transaction Summary",
                "param": "page, per_page",
                "url": "/wallet/transactions"
            },
            "transaction_summary_coin": {
                "description": "Check Transaction Summary",
                "param": "page, per_page",
                "url": "/wallet/transactions"
            },
            "interest_summary": {
                "description": "Check Interest Earned",
                "param": "No parameters needed",
                "url": "/wallet/interest"
            },
            "wallet_status": {
                "description": "Check Wallet Status",
                "url": "/util/statistics?timestamp="
            },
        }

    def get_credentials(self):
        return {
            "X-Cel-Api-Key": self.user_token,
            "X-Cel-Partner-Token": self.partner_token
        }

    def show_wallet_action(self):
        print("Action -> Command")
        for key, val in self.actions.items():
            print(val['description'], " -> ", key)

    def celsius_request(self, command):
        if command not in self.actions.keys():
            return "Error please input valid command"
        else:
            requests.get(self._base_url+self.actions[command]['url'], headers=self.get_credentials())


class CoinGecko:

    def get_coin_list(desired_coin: list) -> pd.DataFrame:
        url = r'https://api.coingecko.com/api/v3/coins/list'
        df = pd.DataFrame(requests.get(url).json())

        return df.query(f"symbol in {str(desired_coin)}")

    def get_ohlc(coin: str, currency: str, day_range: int) -> pd.DataFrame:
        url = f'https://api.coingecko.com/api/v3/coins/{coin}/ohlc?vs_currency={currency}&days={day_range}'
        response = requests.get(url)
        df = pd.DataFrame(response, columns=['time', 'open', 'high', 'low', 'close'])
        df['date'] = df['time'].apply(lambda x: datetime.fromtimestamp(x / 1e3))
        df = df.drop(columns=['time'])[['date', 'open', 'high', 'low', 'close']]

        return df


def get_cel_historical_interest(token_balance: dict) -> pd.DataFrame:
    url = "https://raw.githubusercontent.com/Celsians/Google-Sheets/master/data.json"
    response = requests.request("GET", url)
    df = pd.DataFrame(response.json())
    df = df[["Date"] + list(token_balance.keys())][1:]
    df['date_obj'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
    df = df.query('date_obj > "2020-07-01"').drop(columns=['Date']).reset_index(drop=True)
    return df


def main():
    cel_credentials = [os.path.join(os.getcwd(), x) for x in os.listdir(os.getcwd()) if "credentials" in x][0]


if __name__ == '__main__':
    main()