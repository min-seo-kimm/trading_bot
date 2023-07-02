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
    lg.info('Cancelling all orders...')
    try:
        api.cancel_all_orders()    
        lg.info('All orders cancelled')
    except Exception as e:
        lg.error('Could not cancel all orders')
        lg.error(e)
        sys.exit()

# Execute trading bot
def main():

    api = tradeapi.REST(gvars.API_KEY, gvars.API_SECRET_KEY, gvars.API_URL)

    # Initialize the logger
    initialize_logger()

    # Check our trading account
    check_account(api)

    # Close current orders
    clean_open_orders(api)
    import pdb; pdb.set_trace()

    # Get ticker
    ticker = input('Write the ticker you want to operate with: ')

    trader = Trader(ticker) # Initialize trading bot
    trading_success = trader.run(ticker) # Run trading bot library

    if not trading_success:
        lg.info('Trading was not successful, locking asset')
        # Wait 15 min 

if __name__ == '__main__':
    main()
