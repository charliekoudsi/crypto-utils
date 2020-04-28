from scraper import Scraper

scrpr = Scraper()

# scrape all BTC-PERP data at 5 minute intervals and save it to a file
# called btc_5min.csv
scrpr.scrape('BTC-PERP', 300, 'btc_5min.csv')