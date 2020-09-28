import requests
import pandas as pd
import pyCelsius as celsius
from datetime import datetime
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 15)

cel_credentials = r'/Users/oscartse/Desktop/my projects ;D/crypto_transactions/credentials.json'


def get_coin_list(desired_coin: str)-> list:
    pass


def get_ohlc(coin: str, currency: str,  day_range: int) -> pd.DataFrame:
    url = f'https://api.coingecko.com/api/v3/coins/{coin}/ohlc?vs_currency={currency}&days={day_range}'
    response = requests.get(url)
    df = pd.DataFrame(response, columns=['time', 'open', 'high', 'low', 'close'])
    df['date'] = df['time'].apply(lambda x: datetime.fromtimestamp(x / 1e3))
    df = df.drop(columns=['time'])[['date', 'open', 'high', 'low', 'close']]

    return df


def read_credentials(cred_path: str) -> dict:
    cred = celsius.readCreds(cred_path)
    return cred


def get_cel_historical_stat(token_balance: dict) -> pd.DataFrame:
    url = "https://raw.githubusercontent.com/Celsians/Google-Sheets/master/data.json"
    response = requests.request("GET", url)
    df = pd.DataFrame(response.json())
    df = df[["Date"]+list(token_balance.keys())][1:]
    df['date_obj'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
    df = df.query('date_obj > "2020-07-01"').drop(columns=['Date']).reset_index(drop=True)
    return df


def main():
    cel_cred = read_credentials(cel_credentials)
    celsius.getBalance(cel_cred)


if __name__ == '__main__':
    main()
