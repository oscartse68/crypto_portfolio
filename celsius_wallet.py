import requests
import pandas as pd
import os
import json
from datetime import datetime


class CelsiusNetworkAPI:
    __base_url = "https://wallet-api.celsius.network"
    __openapi_documentation_url = r'https://wallet-api.staging.celsius.network/api-doc'

    def __init__(self, partner_token, user_token):
        self.headers = {
            "X-Cel-Api-Key": user_token,
            "X-Cel-Partner-Token": partner_token
        }
        self.actions = self.__get_actions()

    def __get_actions(self) -> list:
        response = requests.get(self.__openapi_documentation_url).json()

        # kyc, institutional, statistics are not capable to call
        action_list = [{
            "action": "-".join([z.replace(":", "") for z in [y for y in x.split("/")]])[1:],
            "path": "/".join([z if ":" not in z else f"{{{z.replace(':', '')}}}" for z in [y for y in x.split("/")]]),
            "param": [z.replace(':', '') for z in [y for y in x.split("/")]
                      if ":" in z] if [z.replace(':', '') for z in [y for y in x.split("/")] if ":" in z] else None,
            "param_description": [z.replace(':', '') for z in [y for y in x.split("/")] if ":" in z][0]
            if [z.replace(':', '') for z in [y for y in x.split("/")] if ":" in z] else "No Parameters needed",
        } for x in response['paths'].keys() if not any(s in x for s in ("kyc", "institutional", "util-statistics"))]

        # These two action are not listed in openAPI but Postman...
        action_list.append({
            "action": "wallet-transaction",
            "path": '/wallet/transactions?page={page}&per_page={per_page}',
            "param": ['page', 'per_page'],
            "param_description": "page, per_page"
        })
        action_list.append({
            "action": "wallet-coin-transaction",
            "path": '/wallet/{coin}/transactions?page={page}&per_page={per_page}',
            "param": ['coin', 'page', 'per_page'],
            "param_description": 'coin, page, per_page'
        })

        return action_list

    def show_wallet_action(self):
        print(pd.DataFrame(pd.DataFrame(self.actions).drop(columns=['path', 'param'])))

    def get(self, action: str, **kwargs) -> dict:
        if action not in [item['action'] for item in self.actions]:
            return {"Error": "Please input correct action"}
        for item in self.actions:
            if item['action'] == action:
                if item['param'] is None:
                    path = item['path']
                else:
                    if item['param'] == list(kwargs.keys()):
                        path = item['path'].format(**kwargs)
                    else:
                        return {"Error": "Please input valid param"}
                return requests.get(self.__base_url + path, headers=self.headers).json()


class CelsianStatistics:
    __celcian_stat_url = "https://raw.githubusercontent.com/Celsians/Google-Sheets/master/data.json"

    def __init__(self):
        self.celsian_stat = requests.request("GET", self.__celcian_stat_url).json()

    def show_historical_rate_available_coin(self) -> list:
        return list(self.celsian_stat[0].keys())[2:len(list(self.celsian_stat[0].keys()))-7]

    def get_historical_rate(self, coin_list: list, start_date: str) -> dict:
        df = pd.DataFrame(self.celsian_stat[1:])
        coin_list = [{coin: True} if coin in df.columns else {coin: False} for coin in coin_list]
        df = df[["Date"] + [list(i.keys())[0] for i in coin_list if list(i.values())[0] is True]]
        df['date_obj'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
        df['date'] = df.date_obj.dt.date
        df = df.query(f'date_obj > "{start_date}"').drop(columns=['Date']).reset_index(drop=True)
        df = df[['date']+[x for x in df.columns if x != "date_obj" and x != 'Date']]
        return df.to_dict("records")


class CoinGecko:

    def __init__(self, coins_in_cel_wallet):
        self.coin_list = self.get_coin_list(coins_in_cel_wallet)

    # default fetch in coins that you have in your celsius wallet
    def get_coin_list(self, desired_coin: list) -> pd.DataFrame:
        url = r'https://api.coingecko.com/api/v3/coins/list'
        df = pd.DataFrame(requests.get(url).json())
        return df.query(f"symbol in {str(desired_coin)}")

    def get_ohlc(self, coin: str, currency: str, day_range: int) -> pd.DataFrame:
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

    # Use Case 1
    # get balance in kind for balance > 0
    balance = []
    for key in {k: v for k, v in cel.get('wallet-balance')['balance'].items() if float(v) != float(0)}.keys():
        data = cel.get('wallet-coin-balance', coin=key)
        data.update({"coin": key})
        balance.append(data)
    print(balance)

    # Use Case 2
    # retrieve previous interest rates
    celsians_stat = CelsianStatistics()
    df_prev_ir = pd.DataFrame(celsians_stat.get_historical_rate([i['coin'].upper() for i in balance], start_date='20200101'))

    # df_balance_summary = pd.DataFrame(
    #     cel.get("balance_summary")['balance'].items(),
    #     columns=['coin', 'balance_in_kind']
    # ).astype({"balance_in_kind": "float"}).query("balance_in_kind != 0")


if __name__ == '__main__':
    main()
