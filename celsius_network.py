import requests
import pandas as pd
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 15)


def get_historical_stat(token_balance: dict) -> pd.DataFrame:
    url = "https://raw.githubusercontent.com/Celsians/Google-Sheets/master/data.json"
    response = requests.request("GET", url)
    df = pd.DataFrame(response.json())
    df = df[["Date"]+list(token_balance.keys())][1:]
    df['date_obj'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
    df = df.query('date_obj > "2020-07-01"').drop(columns=['Date']).reset_index(drop=True)
    return df


monthly_token_deposit = 1000
init_token = {"USDC": 3000.00, "CEL": 404.3872}
