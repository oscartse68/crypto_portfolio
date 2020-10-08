from .celsius_wallet import CelsiusNetworkAPI
import os
import json

cel_credentials_path = [os.path.join(os.getcwd(), x) for x in os.listdir(os.getcwd()) if "credentials" in x][0]
cel_credentials = json.load(open(cel_credentials_path))
cel = CelsiusNetworkAPI(partner_token=cel_credentials['partner_token'], user_token=cel_credentials['user_token'])
