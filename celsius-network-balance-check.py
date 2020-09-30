import requests
import pandas as pd
import os
import json
from datetime import datetime

pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 15)


class CelsiusNetworkAPI:
    __base_url = "https://wallet-api.celsius.network"
    __celsian_stat_url = "https://raw.githubusercontent.com/Celsians/Google-Sheets/master/data.json"

    def __init__(self, partner_token, user_token):
        self.partner_token = partner_token
        self.user_token = user_token
        self.coin_list = []
        self.headers = {
            "X-Cel-Api-Key": self.user_token,
            "X-Cel-Partner-Token": self.partner_token
        }
        self.__actions = {
            "balance_summary": {
                "description": "Check Wallet Balance Summary (USD)",
                "param": "No parameters needed",
                "url": "/wallet/balance"
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

    def show_wallet_action(self):
        print("Action -> Command")
        for key, val in self.__actions.items():
            print(val['description'], " -> ", key)

    def request(self, command: str, **kwargs):
        if command not in self.__actions.keys():
            return "Error please input valid command"
        else:
            return requests.get(self.__base_url+self.__actions[command]['url'], headers=self.headers).json()

    def get_cel_historical_interest(self, coin_list: list, start_date: str) -> pd.DataFrame:
        response = requests.request("GET", self.__celsian_stat_url)
        df = pd.DataFrame(response.json())
        df = df[["Date"] + coin_list][1:]
        df['date_obj'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
        df = df.query(f'date_obj > "{start_date}"').drop(columns=['Date']).reset_index(drop=True)
        df = df[['date_obj']+[x for x in df.columns if x != "date_obj"]]
        return df


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


def main():
    cel_credentials_path = [os.path.join(os.getcwd(), x) for x in os.listdir(os.getcwd()) if "credentials" in x][0]
    cel_credentials = json.load(open(cel_credentials_path))
    cel = CelsiusNetworkAPI(partner_token=cel_credentials['partner_token'], user_token=cel_credentials['user_token'])
    df_balance_summary = pd.DataFrame(
        cel.request("balance_summary").json()['balance'].items(),
        columns=['coin', 'balance_in_kind']
    ).astype({"balance_in_kind": "float"}).query("balance_in_kind != 0")


if __name__ == '__main__':
    main()
