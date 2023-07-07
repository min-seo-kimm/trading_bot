# encoding: utf-8

# Import needed libraries
from traderlib import *
from logger import *
import alpaca_trade_api as tradeapi
import sys
import gvars

# Check our trading account
def check_account(api):
    try:
        account = api.get_account()
        if account.status != 'ACTIVE':
            lg.error('The account is not ACTIVE, aborting...')
            sys.exit()
    except Exception as e:
        lg.error('Could not get account info, aborting...')
        lg.error(e)
        sys.exit()

# Close current orders
def clean_open_orders(api):
    lg.info('\nCancelling all orders')
    try:
        api.cancel_all_orders()    
        lg.info('All orders cancelled')
    except Exception as e:
        lg.error('Could not cancel all orders, aborting...')
        lg.error(e)
        sys.exit()

# Check whether asset is tradable
def check_asset(api, ticker):
    lg.info('Checking whether %s is tradable' % ticker)
    try:
        asset = api.get_asset(ticker)
        if asset.tradable:
            lg.info('%s exists and is tradable' % ticker)
            return True
        else:
            lg.info('%s exists but is not tradable, aborting...' % ticker)
            sys.exit()
    except Exception as e:
        lg.error('%s does not exist, aborting...' % ticker)
        lg.error(e)
        sys.exit()

# Execute our trading bot
def main():
    api = tradeapi.REST(gvars.API_KEY, gvars.API_SECRET_KEY, gvars.API_URL, api_version='v2')

    # Initialize the logger
    initialize_logger()

    # Check our trading account
    check_account(api)

    # Close current orders
    clean_open_orders(api)
    
    # Get ticker
    ticker = input('\nWrite the ticker you want to operate with: ')

    # Check whether asset is tradable
    check_asset(api, ticker)

    # Initialize trading bot
    trader = Trader(api, ticker)

    # Run trading bot
    while True:
        trading_success = trader.run()

        if not trading_success:
            lg.info('\nTrading was not successful, locking asset')
            time.sleep(gvars.sleep_time_me)
        else:
            lg.info('\nTrading was successful')
            time.sleep(gvars.sleep_time_me)

if __name__ == '__main__':
    main()
