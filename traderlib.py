# encoding: utf-8

# import alpaca_trade_api as tradeapi

import sys, os, time, pytz, gvars
import logging as lg
import tulipy as ti
import pandas as pd

from datetime import datetime
from math import ceil

class Trader:
    def __init__(self, ticker):
        lg.info('Trader initialized with ticker %s' % ticker)
        self.ticker = ticker

    def is_tradable(self, ticker):
        # Ask the broker/API if "asset" is tradable
            # IN: asset (string)
            # OUT: True (tradable) / False (not tradable)
        try: 
            # asset = get asset from alpaca wrapper (.tradable)
            if not asset.tradable:
                lg.info('The asset %s is not tradable' % ticker)
                return False
            else:
                lg.info('The asset %s is tradable' % ticker)
                return True
        except:
            lg.error('The asset %s is not answering well' % ticker)
            return False
        
    def set_stop_loss(self, entry_price, trend):
        # Takes an entry price and sets the stop loss (trend)
            # IN: entry price, trend (long / short)
            # OUT: stop loss ($)
        try: 
            if trend == 'long':
                stop_loss = entry_price - (entry_price * gvars.stop_loss_margin)
                return stop_loss
            elif trend == 'short':
                stop_loss = entry_price + (entry_price * gvars.stop_loss_margin)
                return stop_loss
            else:
                raise ValueError 
        except Exception as e:
            lg.error('The trend value cannot be understood: %s' % str(trend))
            sys.exit()

    def set_take_profit(self, entry_price, trend):
        # Takes an entry price and sets the take profit (trend)
            # IN: entry price, trend (long / short)
            # OUT: take profit ($)
        try:
            if trend == 'long':
                take_profit = entry_price + (entry_price * gvars.take_profit_margin)
                lg.info('Take profit set for long at %.2f' % take_profit)
                return take_profit
            elif trend == 'short':
                take_profit = entry_price - (entry_price * gvars.take_profit_margin)
                lg.info('Take profit set for short at %.2f' % take_profit)
                return take_profit
            else:
                raise ValueError
        except Exception as e:
            lg.error('The trend value cannot be understood: %s' % str(trend))
            sys.exit()

    # load historical data
        # IN: ticker, interval, entries limit
        # OUT: array with stock data (OHCL)

    def get_open_positions(self, asset_id):
        # Get open positions
            # IN: asset ID (unique identifier)
            # OUT: boolean (True = already open, False = not open)
        # positions = ask alpaca wrapper for the list of open positions
        for position in positions:
            if position.symbol == asset_id:
                return True
            else:
                return False

    # submit order: gets our order through the API (loop / retry)
        # IN: order data, order type
        # OUt: boolean (True = order went through, False = order did not)
    
    # cancel order: cancels our order (retry)
        # IN: order ID
        # OUT: boolean (True = order cancelled, False = order not cancelled)
    
    def check_position(self, ticker, do_not_find=False):
        # Check whether the position is exists or not
            # IN: ticker, do not find
            # OUT: boolean (True = order is there, False = order not there)
        attempt = 1
        while attempt <= gvars.max_attempts_cp:
            try:
                # position = ask the alpaca wrapper for a position
                current_price = position.current_price
                lg.info('The position was found. Current price is %.2f' % current_price)
                return True
            except:
                if do_not_find:
                    lg.info('Position not found, this is good')
                    return False
                lg.info('Position not found, waiting for it...')
                time.sleep(gvars.sleep_time_cp) # Wait and retry
                attempt += 1
        lg.info('Position not found for %s, not waiting anymore' % ticker)
        return False 

    def get_shares_amount(self, asset_price):
        # Works out the total number of shares to buy / sell
            # IN: asset price
            # OUT: number of shares
        lg.info('Getting shares amount')
        try:
            # Get the total equity available
            # total_equity = ask Alpaca wrapper for available equity
            # Calcualte the number of shares
            shares_quantity = int(gvars.max_spent_equity / asset_price)
            lg.info('Total shares to operate with: %d' % shares_quantity)
            return shares_quantity
        except Exception as e:
            lg.error('Something went wrong while getting shares amount')
            lg.error(e)
            sys.exit()

    def get_current_price(self, ticker):
        # Get the current price of an asset with an open position
            # IN: ticker
            # OUT: price ($)
        attempt = 1
        while attempt <= gvars.max_attempts_gcp:
            try:
                # position = ask the alpaca wrapper for a position
                current_price = position.current_price
                lg.info('The position has been checked. Current price is %.2f' % current_price)
                return current_price
            except:
                lg.info('Position not found, waiting for it...')
                time.sleep(gvars.sleep_time_gcp) # Wait and retry
                attempt += 1
        lg.error('Position not found for %s, not waiting anymore' % ticker)
        return False 

    def get_general_trend(self, ticker):
        # Detect interesting trend (UP / DOWN / FALSE if no trend)
            # IN: ticker
            # OUT: UP / DOWN / NO TREND (string)
            # If no trend detected, go back to POINT ECHO
        lg.info('GENERAL TREND ANALYSIS entered')
        attempt = 1
        max_attempts = 10 # total time = max attempts * 60 sec (as implemented)
        try:
            while True:
                # data = ask Alpaca wrapper for 30 min candles
                # Calculate the EMAs
                ema9 = ti.ema(data, 9)
                ema26 = ti.ema(data, 26)
                ema50 = ti.ema(data, 50)
                lg.info('%s instant trend EMAs = [%.2f, %.2f, %.2f]' % (ticker, ema9, ema26, ema50))
                # Check EMAs relative position
                if (ema9 > ema26) and (ema26 > ema50):
                    lg.info('Trend detected for %s: long' % ticker)
                    return 'long'
                elif (ema9 < ema26) and (ema26 < ema50):
                    lg.info('Trend detected for %s: short' % ticker)
                    return 'short'
                elif attempt <= max_attempts:
                    lg.info('Trend not clear for %s, waiting...' % ticker)
                    time.sleep(60*10)
                    attempt += 1 
                else:
                    lg.info('Trend NOT detected and timeout reached for %s' % ticker)
                    return False
        except Exception as e:
            lg.error('Something went wrong while getting general trend')
            lg.error(e)
            sys.exit()

    def get_instand_trend(self, ticker, trend):
        # Confirm the trend detected by GT analysis
            # IN: ticker, trend
            # OUT: True (confirmed) / False (not confirmed)
        lg.info('INSTAND TREND ANALYSIS entered')
        attempt = 1
        max_attempts = 10 # total time = max attempts * 30 sec (as implemented)
        try:
            while True:
                # data = ask Alpaca wrapper for 5 min candles
                # Calculate the EMAs
                ema9 = ti.ema(data, 9)
                ema26 = ti.ema(data, 26)
                ema50 = ti.ema(data, 50)
                lg.info('%s instant trend EMAs = [%.2f, %.2f, %.2f]' % (ticker, ema9, ema26, ema50))
                # Check EMAs relative position
                if (trend == 'long') and (ema9 > ema26) and (ema26 > ema50):
                    lg.info('Long trend confirmed for %s' % ticker)
                    return True
                elif (trend == 'short') and (ema9 < ema26) and (ema26 < ema50):
                    lg.info('Short trend confirmed for %s' % ticker)
                    return True
                elif attempt <= max_attempts:
                    lg.info('Trend not clear for %s, waiting...' % ticker)
                    time.sleep(30)
                    attempt += 1
                else:
                    lg.info('Trend NOT detected and timeout reached for %s' % ticker)
                    return False
        except Exception as e:
            lg.error('Something went wrong while getting instant trend')
            lg.error(e)
            sys.exit()      

    def get_rsi(self, ticker, trend):
        # Perform RSI analysis
            # IN: ticker, trend
            # OUT: True (confirmed) / False (not confirmed)
        lg.info('RSI ANALYSIS entered')
        attempt = 1
        max_attempts = 10 # total time = max attempts * 20 sec (as implemented)
        try:
            while True:
                # data = ask Alpaca wrapper for 5 min candles
                # Calculate the RSI
                rsi = ti.rsi(data, 14) # Uses 14-sample window
                lg.info('%s RSI = [%.2f]' % (ticker, rsi))
                if (trend == 'long') and (rsi > 50) and (rsi < 80):
                    lg.info('Long trend confirmed for %s' % ticker)
                    return True
                elif (trend == 'short') and (rsi < 50) and (rsi > 20):
                    lg.info('Short trend confirmed for %s' % ticker)
                    return True
                elif attempt <= max_attempts:
                    lg.info('Trend not clear for %s, waiting...' % ticker)
                    time.sleep(20)
                    attempt += 1
                else:
                    lg.info('Trend NOT detected and timeout reached for %s' % ticker)
                    return False
        except Exception as e:
            lg.error('Something went wrong while getting instant trend')
            lg.error(e)
            sys.exit()
    
    def get_stochastic(self, ticker, trend):
        # Perform stochastic analysis
            # IN: ticker, trend
            # OUT: True (confirmed) / False (not confirmed)
        lg.info('STOCHASTIC ANALYSIS entered')
        attempt = 1
        max_attempts = 10 # total time = max attempts * 10 sec (as implemented)
        try:
            while True:
                # data = ask Alpaca wrapper for 5 min candles
                # Calculate the STOCHASTIC
                stoch_k, stoch_d = ti.stoch(high, low, close, 9, 6, 9)
                lg.info('%s STOCHASTIC = [%.2f, %.2f]' % (ticker, stoch_k, stoch_d))
                if (trend == 'long') and (stoch_k > stoch_d) and (stoch_k < 80) and (stoch_d < 80):
                    lg.info('Long trend confirmed for %s' % ticker)
                    return True
                elif (trend == 'short') and (stoch_k < stoch_d) and (stoch_k > 20) and (stoch_d > 20):
                    lg.info('Short trend confirmed for %s' % ticker)
                    return True
                elif attempt <= max_attempts:
                    lg.info('Trend not clear for %s, waiting...' % ticker)
                    time.sleep(10)
                    attempt += 1
                else:
                    lg.info('Trend NOT detected and timeout reached for %s' % ticker)
                    return False
        except Exception as e:
            lg.error('Something went wrong while getting instant trend')
            lg.error(e)
            sys.exit()
     
    def check_stochastic_crossing(self, ticker, trend):
        # Check whether the stochastic curves have crossed or not depending on the trned
            # IN: ticker, trend
            # OUT: True if crossed / False if not crossed
        lg.info('Checking stochastic crossing...')
        # data = ask Alpaca wrapper for 5 min candles
        # Calculate the STOCHASTIC
        stoch_k, stoch_d = ti.stoch(high, low, close, 9, 6, 9)
        lg.info('%s STOCHASTIC = [%.2f, %.2f]' % (ticker, stoch_k, stoch_d))
        try:
            if (trend == 'long') and (stoch_k <= stoch_d):
                lg.info('Stochastic curves crossed: long, k=%.2f, d=%.2f' % (stoch_k, stoch_d))
                return True
            elif (trend == 'short') and (stoch_k >= stoch_d):
                lg.info('Stochastic curves crossed: short, k=%.2f, d=%.2f' % (stoch_k, stoch_d))
                return True
            else:
                lg.info('Stochastic curves have not crossed')
                return False
        except Exception as e:
            lg.error('Something went wrong while checking stochastic crossing')
            lg.error(e)
            return True

    def enter_position_mode(self, ticker, trend):
        # Check the conditions in parallel once inside the position
        attempt = 1
        max_attempts = 1260 # Calculate 7 hr total: 7*60*60/20
        # entry_price = ask the Alpaca wrapper for the entry price
        # Set the take profit
        take_profit = set_take_profit(entry_price, trend)
        # Set the stop loss
        stop_loss = set_stop_loss(entry_price, trend)
        try:
            while True:
                current_price = get_current_price(ticker)
                # Check if take profit met
                # LONG version
                if (trend == 'long') and (current_price >= take_profit):
                    lg.info('Take profit met at %.2f. Current price is %.2f' % (take_profit, current_price))
                    return True
                # Check if take profit met
                # SHORT version
                elif (trend == 'short') and (current_price <= take_profit):
                    lg.info('Take profit met at %.2f. Current price is %.2f' % (take_profit, current_price))
                    return True
                # Check if stop loss met
                # LONG version
                elif (trend == 'long') and (current_price <= stop_loss):
                    lg.info('Stop loss met at %.2f. Current price is %.2f' % (stop_loss, current_price))
                    return False
                # Check if stop loss met
                # LONG version
                elif (trend == 'short') and (current_price >= stop_loss):
                    lg.info('Stop loss met at %.2f. Current price is %.2f' % (stop_loss, current_price))
                    return False
                # Check stoch crossing
                elif check_stochastic_crossing(ticker, trend):
                    lg.info('Stochastic curves crossed. Current price is %.2f' % current_price)
                    return True
                # We wait
                elif attempt <= max_attempts:
                    lg.info('Waiting inside position, attempt #%d' % attempt)
                    lg.info('%.2f <-- %.2f --> %.2f' % (stop_loss, current_price, take_profit))
                    time.sleep(20)
                # Get out, time is out
                else:
                    lg.info('Timeout reached at enter position, too late')
                    return False
        except Exception as e:
            lg.error('Something went wrong at enter position position')
            lg.error(e)
            return True

    def run():
        # LOOP until timeout reached (ex. 2 hr)
        # POINT ECHO
        while True:
            # Ask the broker/API if we have an open position with "asset"
            if check_position(self.ticker, do_not_find=True):
                lg.info('There is already an open position with %s, aborting...' % self.ticker)
                return False # Aborting execution
            # POINT DELTA
            while True:
                # Find a general trend
                trend = get_general_trend(self.ticker)
                if not trend:
                    lg.info('No general trend found for %s, going out...' % self.ticker)
                    return False # Aborting execution
                # Confirm instand trend
                if not get_instant_trend(self.ticker, trend):
                    lg.info('The instant trend is not confirmed, going back...')
                    continue # If failed, go back to POINT DELTA
                # Perform RSI analysis
                if not get_rsi(self.ticker, trend):
                    lg.info('The rsi is not confirmed, going back...')
                    continue # If failed, go back to POINT DELTA
                # Perform stochastic analysis
                if not get_stochastic(self.ticker, trend):
                    lg.info('The stochastic is not confirmed, going back...')
                    continue # If failed, go back to POINT DELTA
                lg.info('All filtering passed, carrying on with the order')
                break # Get out of the loop
            # Get current price
            self.current_price = get_current_price(self.ticker)
            # Get shares amount
            shares_quantity = get_shares_amount(self.ticker, self.current_price)
            # submit order (limit)
                # If False, abort / go back to POINT ECHO
            # Check position
            if not check_position(self.ticker):
                # cancel pending order
                continue # If False, go back to POINT ECHO
            # enter position mode
            successful_operation = enter_position_mode(self.ticker, trend)
            # GET OUT
            while True:
                # submit order (market)
                if not check_position(self.ticker, do_not_find=True):
                    break
                time.sleep(10) # Wait 10 seconds
            # End of execution
            return successful_operation
