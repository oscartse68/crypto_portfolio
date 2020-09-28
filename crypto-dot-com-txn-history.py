import pandas as pd
from datetime import timedelta
import os
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 15)


def df_numeric_col_fillna(df, fill_val=0):
    numerical_col = [col for col in df.columns if df[col].dtype == ('float64' or 'int64')]
    for col in numerical_col:
        df[col] = df[col].fillna(fill_val)


filepath = r'/Users/oscartse/Desktop/crypto transaction'
crypto_transaction = [i for i in os.listdir(filepath) if "crypto" in i][0]

df = pd.read_csv(os.path.join(filepath, crypto_transaction))

try:
    df = df.drop(columns=['Unnamed: 0'])
except KeyError:
    pass

df['Timestamp (UTC)'] = pd.to_datetime(df['Timestamp (UTC)']).apply(lambda x: x + timedelta(hours=8))
df['Date'] = df['Timestamp (UTC)'].apply(lambda x: x.date())
date_range = pd.DataFrame([min(df['Date'])+timedelta(days=i) for i in range((max(df['Date'])-min(df['Date'])).days + 1)], columns=['Date_range'])

crypto_purchase = pd.merge(date_range, df[df['Transaction Kind'] == 'crypto_purchase'], how='left', left_on='Date_range', right_on='Date').drop(columns=['Date'])
df_numeric_col_fillna(crypto_purchase)
agg = 0
for idx, row in crypto_purchase.iterrows():
    if row['Transaction Kind'] == 'crypto_purchase':
        agg += row['Native Amount (in USD)']
    crypto_purchase['Native Amount (in USD)'][idx] = agg

crypto_purchase.to_csv()
# df = pd.merge(date_range, df, how='left', left_on='Date_range', right_on='Date').drop(columns=['Date'])

df.to_csv(os.path.join(filepath, r'crypto_purchase.csv'), index=False)
