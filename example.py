import scraper
import cointegration

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
tester.test('btc_5min.csv','eth_5min.csv')

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
            print(f'{asset1_name}-{asset2_name} are cointegreated')
        elif p_value < 0.05:
            print(f'{asset1_name}-{asset2_name} may be cointegreated')
        else:
            print(f'{asset1_name}-{asset2_name} are not cointegreated')


