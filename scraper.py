import requests
import pandas as pd

class Scraper:
    def __init__(self):
        self.base_url = 'https://ftx.com/api/markets/'

    def scrape(self, asset, frequency, output_name):
        r = []
        url = f'{self.base_url}asset/candles?limit=5000&resolution={frequency}'
        temp = requests.get(url).json()['result']
        r.extend(temp)
        while len(temp) >= 4500:
            temp = requests.get(f'{url}&end_time={temp[0]["time"]/1000}').json()['result']
            r.extend(temp)
        df = pd.DataFrame(r)
        df['time'] = pd.to_datetime(df.time, unit='ms')
        df.drop('startTime', axis=1,inplace=True)
        df.sort_values('time',inplace=True)
        df.drop_duplicates(inplace=True)
        df = df[['time', 'close']]
        df.to_csv(output_name, index=False)
    
    def get_all_markets(self):
        resp = requests.get(self.base_url).json()['result']
        return [r['name'] for r in resp]
    
    def get_perp(self):
        markets = self.get_all_markets()
        perp = [m for m in markets if m.split('-')[1] == 'PERP']
        return perp
    
    