import requests
import json
import pandas as pd
# import numpy as np

# url = 'https://solana.drpc.org'

class Solana:
    def __init__(self, dkey:str, network:str):
        self.url = f"https://lb.drpc.org/ogrpc?network={network}&dkey={dkey}"
        self.headers = {
            'Content-Type': 'application/json'
        }

    def extractTransactions(self, wallet: str):

        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [wallet, {"limit": 500}]
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))

        transactions = dict()

        # print(response.json())

        if 'result' in response.json().keys():
            results = response.json()['result']
        else:
            print("Couldn't make successfull request")
            return None
        
        if len(results)==0:
            print("No transactions")
            return None

        for item in results:
            transactions[item['signature']] = dict()
            transactions[item['signature']]['blockTime'] = item['blockTime']

        for key, _ in transactions.items():
            dd = self.extractTransaction(key)
            if 'result' in dd.keys():
                transactions[key]['value'] = sum(dd['result']['meta']['postBalances']) - sum(dd['result']['meta']['preBalances'])
                transactions[key]['fee'] = dd['result']['meta']['fee']
                transactions[key]['amount'] = float(0)
                for token in dd['result']['meta']['postTokenBalances']:
                    if token['uiTokenAmount']['uiAmount'] is None:
                        continue
                    else:
                        transactions[key]['amount'] += token['uiTokenAmount']['uiAmount']
                for token in dd['result']['meta']['preTokenBalances']:
                    if token['uiTokenAmount']['uiAmount'] is None:
                        continue
                    else:
                        transactions[key]['amount'] -= token['uiTokenAmount']['uiAmount']
                transfers = 0
                for item in dd['result']['transaction']['message']['instructions']:
                    if 'parsed' in item.keys():
                        if type(item['parsed']) is dict:
                            if 'type' in item['parsed'].keys():
                                if item['parsed']['type'] == 'transfer':
                                    transfers += 1
                                if item['parsed']['type'] == 'transferChecked':
                                    transfers += 1
                for item in dd['result']['meta']['innerInstructions']:
                    if 'parsed' in item.keys():
                        if type(item['parsed']) is dict:
                            if 'type' in item['parsed'].keys():
                                if item['parsed']['type'] == 'transfer':
                                    transfers += 1
                                if item['parsed']['type'] == 'transferChecked':
                                    transfers += 1
                transactions[key]['transfers'] = transfers

        df = pd.DataFrame(transactions).T
        df = df[df.transfers > 1]
        df.fillna(0, inplace=True)

        value_mean = df['value'].mean()
        value_std = df['value'].std()
        fee_mean = df['fee'].mean()
        fee_std = df['fee'].std()
        transfers_mean = df['transfers'].mean()
        transfers_std = df['transfers'].std()
        amount_std = df['amount'].std()
        amount_mean = df['amount'].mean()
        total_transactions = len(df) 

        return pd.DataFrame([{
                                'value_mean': value_mean, 
                                'fee_mean': fee_mean, 
                                'transfers_mean':transfers_mean, 
                                'amount_mean': amount_mean,
                                'total_transactions':total_transactions, 
                                'value_std': value_std, 
                                'fee_std': fee_std, 
                                'transfers_std': transfers_std,
                                'amount_std': amount_std,
                            }]).fillna(0)
    #.reshape(1, -1)

    def extractTransaction(self, signature: str):
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                signature,
                {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}
            ]
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        return response.json()