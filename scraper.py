import requests
import pandas as pd

class Scraper:
    def __init__(self):
        self.base_url = 'https://ftx.com/api/markets/'

    def scrape(self, asset, frequency, output_name):
        '''
        Scrape FTX price data and store it in a file

        Inputs:
            asset (string): Name of asset to scrape.
            frequency (int): Window length in seconds. Options are:
                15, 60, 300, 900, 3600, 14400, 86400
            output_name (string): Name of output file. Must end in .csv
        
        Outputs:
            Outputs results to file.
        '''
        r = []
        url = f'{self.base_url}{asset}/candles?limit=5000&resolution={frequency}'
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
        '''
        Get list of all markets on FTX
        '''
        resp = requests.get(self.base_url[:-1]).json()['result']
        return [r['name'] for r in resp]
    
    def get_perp(self):
        '''
        Get list of all perpetual contracts on FTX
        '''
        markets = self.get_all_markets()
        perp = [m for m in markets if len(m.split('-')) == 2 and m.split('-')[1] == 'PERP']
        return perp
    
