import scraper
import cointegration
import process
import backtest
import pandas as pd
import numpy as np

scrpr = scraper.Scraper()
tester = cointegration.Tester()

# scrape all BTC-PERP data at 5 minute intervals and save it to a file called btc_5min.csv
scrpr.scrape('BTC-PERP', 300, 'btc_5min.csv')

#same thing with ETH-PERP
scrpr.scrape('ETH-PERP', 300, 'eth_5min.csv')

# scrape all 5-min perpetual contract data and save it to disk
markets = scrpr.get_perp()
for market in markets:
    scrpr.scrape(market, 300, f'{market.split("-")[0].lower()}_5min.csv')
    print(f'Finished: {market}')


# example of non cointegrated pair
tester.test('btc_5min.csv','eth_5min.csv', mode='kalman')

#test normal pairs trading
quotes_normal = process.process('eth', 'btc', 'eth_5min.csv', 'btc_5min.csv')
bt1 = backtest.Backtester(quotes_normal, threshold=0.3, fee= 0.0007, t_pen=500)

#test kalman filter
quotes_kalman = process.process('eth', 'btc', 'eth_5min.csv', 'btc_5min.csv', mode='kalman')
bt2 = backtest.Backtester(quotes_kalman, threshold=0.75, fee= 0.0007, t_pen=np.inf)

# from these results, we can see that eth-btc is not a good pair to trade
# if you want more detailed backtest information, you can access each trade with:
trades = pd.DataFrame(bt1.trades)



# find all cointegrated pairs
# assumes you have downloaded all data as shown above
for i in range(len(markets) - 1):
    for n in range(i, len(markets)):
        asset1 = markets[i]
        asset1_name = asset1.split("-")[0].lower()
        asset2 = markets[n]
        asset2_name = asset2.split("-")[0].lower()
        p_value = tester.test(f'{asset1_name}_5min.csv', f'{asset2_name}_5min.csv')
        if p_value < 0.01:
            print(f'{asset1_name}-{asset2_name} are likely cointegreated')
        elif p_value < 0.05:
            print(f'{asset1_name}-{asset2_name} may be cointegreated')
        else:
            print(f'{asset1_name}-{asset2_name} are not cointegreated')


