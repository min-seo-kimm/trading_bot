# encoding: utf-8

from logger import *
import sys, time, gvars
import tulipy as ti
import yfinance as yf

class Trader:
    def __init__(self, api, ticker):
        lg.info('\nTrader initialized with ticker %s' % ticker)
        self.api = api
        self.ticker = ticker
        
    def set_stop_loss(self, entry_price, trend):
        # Take an entry price and set the stop loss (trend)
            # IN: entry price, trend (long / short)
            # OUT: stop loss ($)
        try: 
            if trend == 'long':
                stop_loss = entry_price - (entry_price * gvars.stop_loss_margin)
                lg.info('Stop loss set for long at %.2f' % stop_loss)
                return stop_loss
            elif trend == 'short':
                stop_loss = entry_price + (entry_price * gvars.stop_loss_margin)
                lg.info('Stop loss set for short at %.2f' % stop_loss)
                return stop_loss
            else:
                raise ValueError 
        except Exception as e:
            lg.error('Trend could not be understood, aborting...')
            sys.exit()

    def set_take_profit(self, entry_price, trend):
        # Take an entry price and set the take profit (trend)
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
            lg.error('Trend could not be understood, aborting...')
            sys.exit()

    def load_historical_data(self, ticker, interval, period):
        # Load historical data
            # IN: ticker, interval (window length), period
            # OUT: array with stock data (OHCL)
        try:
            ticker = yf.Ticker(ticker)
            data = ticker.history(interval=interval, period=period)
        except Exception as e:
            lg.error('Something went wrong while loading historical data, aborting...')
            lg.error(e)
            sys.exit()
        return data

    def submit_order(self, ticker, shares_qty, trend, type, exit=False):
        # Get our order through the API
            # IN: ticker, number of shares, trend, order type, boolean (True = market order, False = limit order)
            # OUt: boolean (True = order went through, False = order did not)
        if trend == 'long' and not exit:
            side = 'buy'
            limit_price = round(self.current_price + self.current_price * gvars.max_var, 2)
        elif trend == 'short' and not exit:
            side = 'sell'
            limit_price = round(self.current_price - self.current_price * gvars.max_var, 2)
        elif trend == 'long' and exit:
            side = 'sell'
        elif trend == 'short' and exit:
            side = 'buy'
        else:
            lg.error('Trend could not be understood, aborting...')
            sys.exit()
        
        lg.info('\nSubmitting %s order for %s' % (side, ticker))
        try:
            if type == 'limit':
                lg.info('Current price: %.2f / Limit price: %.2f' % (self.current_price, limit_price))
                order = self.api.submit_order(
                    symbol=ticker,
                    qty=shares_qty,
                    side=side,
                    type=type,
                    time_in_force='gtc',
                    limit_price=limit_price
                )
            elif type == 'market':
                lg.info('Current price: %.2f' % self.current_price)
                order = self.api.submit_order(
                    symbol=ticker,
                    qty=shares_qty,
                    side=side,
                    type=type,
                    time_in_force='gtc'
                )
            else:
                lg.error('Type of order could not be understood, aborting...')
                sys.exit()

            self.order_id = order.id
            lg.info('Order submitted correctly')
            lg.info('%d shares %s for %s' % (shares_qty, side, ticker))
            lg.info('Order ID: %s' % self.order_id)
            return True
        except Exception as e:
            lg.error('Something went wrong while submitting order, aborting...')
            lg.error(e)
            sys.exit()

    def cancel_pending_order(self, ticker):
        # Cancel our order (retry) through the API
            # IN: ticker
            # OUT: boolean (True = order cancelled, False = order not cancelled)
        lg.info('\nCancelling order %s for %s' % (self.order_id, ticker))
        attempt = 1
        while attempt <= gvars.max_attempts_cpo:
            try:
                self.api.cancel_order(self.order_id)
                lg.info('Order cancelled correctly')
                return True
            except:
                lg.info('Order could not be cancelled, retrying...')
                time.sleep(gvars.sleep_time_cpo)
                attempt += 1
        lg.error('Order could not be cancelled, cancelling all orders')
        self.api.cancel_all_orders()
        sys.exit()

    def check_position(self, ticker, do_not_find=False):
        # Check whether the position is exists or not
            # IN: ticker, boolean (True = position shouldn't exist, False = otherwise)
            # OUT: boolean (True = order is there, False = order not there)
        lg.info('\nChecking position for %s' % ticker)
        attempt = 1
        time.sleep(gvars.sleep_time_cp)
        while attempt <= gvars.max_attempts_cp:
            try:
                position = self.api.get_position(ticker)
                current_price = float(position.current_price)
                lg.info('Position was found for %s. Current price is %.2f' % (ticker, current_price))
                return True
            except:
                if do_not_find:
                    lg.info('Position not found for %s' % ticker)
                    return False
                lg.info('Position not found for %s, waiting for it...' % ticker)
                time.sleep(gvars.sleep_time_cp) # Wait 5 seconds and retry
                attempt += 1
        lg.info('Position not found for %s, not waiting anymore' % ticker)
        return False 

    def get_shares_amount(self, ticker, asset_price):
        # Work out the total number of shares to buy / sell
            # IN: asset price
            # OUT: number of shares
        lg.info('\nGetting shares amount for %s' % ticker)
        try:
            # Get the total cash available
            account = self.api.get_account()
            equity = float(account.equity)

            # Calcualte the number of shares
            shares_qty = int(gvars.max_spent_equity / asset_price)
            if equity > shares_qty * asset_price:
                lg.info('Total shares to operate with: %d' % shares_qty)
                return shares_qty
            else:
                lg.info('Cannot spend %.2f, remaining equity is %.2f, aborting...' % (shares_qty * asset_price, equity))
                sys.exit()
        except Exception as e:
            lg.error('Something went wrong while getting shares amount, aborting...')
            lg.error(e)
            sys.exit()

    def get_current_price(self, ticker):
        # Get the current price of a ticker with open position
            # IN: ticker
            # OUT: price ($)
        lg.info('\nGetting current price for %s' % ticker)
        attempt = 1
        while attempt <= gvars.max_attempts_gcp:
            try:
                position = self.api.get_position(ticker)
                current_price = float(position.current_price)
                lg.info('Position was checked for %s. Current price is %.2f' % (ticker, current_price))
                return current_price
            except:
                lg.info('Position not found for %s, waiting for it...' % ticker)
                time.sleep(gvars.sleep_time_gcp)
                attempt += 1
        lg.info('Position not found for %s, not waiting anymore' % ticker)
        return False
    
    def get_avg_entry_price(self, ticker):
        # Get the average entry price for a ticker with open position
            # IN: ticker
            # OUT: price ($)
        lg.info('\nGetting average entry price for %s' % ticker)
        attempt = 1
        while attempt <= gvars.max_attempts_gaep:
            try:
                position = self.api.get_position(ticker)
                avg_entry_price = float(position.avg_entry_price)
                lg.info('Position was checked for %s. Average entry price is %.2f' % (ticker, avg_entry_price))
                return avg_entry_price
            except:
                lg.info('Position not found for %s, waiting for it...' % ticker)
                time.sleep(gvars.sleep_time_gaep)
                attempt += 1
        lg.info('Position not found for %s, not waiting anymore' % ticker)
        return False

    def get_general_trend(self, ticker):
        # Detect interesting trend (UP / DOWN / FALSE if no trend)
            # IN: ticker
            # OUT: UP / DOWN / NO TREND (string)
        lg.info('\nGENERAL TREND ANALYSIS entered')
        attempt = 1
        try:
            while True:
                # Ask for 30 min candles
                data = self.load_historical_data(ticker, interval='30m', period='1mo')

                # Calculate the EMAs
                ema9 = ti.ema(data.Close.values, 9)[-1]
                ema26 = ti.ema(data.Close.values, 26)[-1]
                ema50 = ti.ema(data.Close.values, 50)[-1]

                lg.info('%s general trend EMAs = [EMA9: %.2f, EMA26: %.2f, EMA50: %.2f]' % (ticker, ema9, ema26, ema50))

                # Check EMAs relative position
                if (ema9 > ema26) and (ema26 > ema50):
                    lg.info('Long trend detected for %s' % ticker)
                    return 'long'
                elif (ema9 < ema26) and (ema26 < ema50):
                    lg.info('Short detected for %s' % ticker)
                    return 'short'
                elif attempt <= gvars.max_attempts_ggt:
                    lg.info('Trend not clear for %s, waiting...' % ticker)
                    time.sleep(gvars.sleep_time_ggt)
                    attempt += 1 
                else:
                    lg.info('Trend NOT detected and timeout reached for %s' % ticker)
                    return False
        except Exception as e:
            lg.error('Something went wrong while getting general trend, aborting...')
            lg.error(e)
            sys.exit()

    def get_instant_trend(self, ticker, trend):
        # Confirm the trend detected by GT analysis
            # IN: ticker, trend
            # OUT: True (confirmed) / False (not confirmed)
        lg.info('\nINSTANT TREND ANALYSIS entered')
        attempt = 1
        try:
            while True:
                # Ask for 5 min candles
                data = self.load_historical_data(ticker, interval='5m', period='5d')
                
                # Calculate the EMAs
                ema9 = ti.ema(data.Close.values, 9)[-1]
                ema26 = ti.ema(data.Close.values, 26)[-1]
                ema50 = ti.ema(data.Close.values, 50)[-1]

                lg.info('%s instant trend EMAs = [EMA9: %.2f, EMA26: %.2f, EMA50: %.2f]' % (ticker, ema9, ema26, ema50))

                # Check EMAs relative position
                if (trend == 'long') and (ema9 > ema26) and (ema26 > ema50):
                    lg.info('Long trend confirmed for %s' % ticker)
                    return True
                elif (trend == 'short') and (ema9 < ema26) and (ema26 < ema50):
                    lg.info('Short trend confirmed for %s' % ticker)
                    return True
                elif attempt <= gvars.max_attempts_git:
                    lg.info('Trend not clear for %s, waiting...' % ticker)
                    time.sleep(gvars.sleep_time_git)
                    attempt += 1
                else:
                    lg.info('Trend NOT detected and timeout reached for %s' % ticker)
                    return False
        except Exception as e:
            lg.error('Something went wrong while getting instant trend, aborting...')
            lg.error(e)
            sys.exit()      

    def get_rsi(self, ticker, trend):
        # Perform RSI analysis
            # IN: ticker, trend
            # OUT: True (confirmed) / False (not confirmed)
        lg.info('\nRSI ANALYSIS entered')
        attempt = 1
        try:
            while True:
                # Ask for 5 min candles
                data = self.load_historical_data(ticker, interval='5m', period='5d')

                # Calculate the RSI
                rsi = ti.rsi(data.Close.values, 14)[-1] # Uses 14-sample window
                lg.info('%s RSI = [%.2f]' % (ticker, rsi))
                
                if (trend == 'long') and (rsi > 50) and (rsi < 80):
                    lg.info('Long trend confirmed for %s' % ticker)
                    return True
                elif (trend == 'short') and (rsi < 50) and (rsi > 20):
                    lg.info('Short trend confirmed for %s' % ticker)
                    return True
                elif attempt <= gvars.max_attempts_rsi:
                    lg.info('Trend not clear for %s, waiting...' % ticker)
                    time.sleep(gvars.sleep_time_rsi)
                    attempt += 1
                else:
                    lg.info('Trend NOT detected and timeout reached for %s' % ticker)
                    return False
        except Exception as e:
            lg.error('Something went wrong while getting instant trend, aborting...')
            lg.error(e)
            sys.exit()
    
    def get_stochastic(self, ticker, trend):
        # Perform stochastic analysis
            # IN: ticker, trend
            # OUT: True (confirmed) / False (not confirmed)
        lg.info('\nSTOCHASTIC ANALYSIS entered')
        attempt = 1
        try:
            while True:
                # Ask for 5 min candles
                data = self.load_historical_data(ticker, interval='5m', period='5d')

                # Calculate the STOCHASTIC
                stoch_k, stoch_d = ti.stoch(data.High.values, data.Low.values, data.Close.values, 9, 6, 9)
                stoch_k = stoch_k[-1]
                stoch_d = stoch_d[-1]

                lg.info('%s stochastic = [K_FAST: %.2f, D_SLOW: %.2f]' % (ticker, stoch_k, stoch_d))

                if (trend == 'long') and (stoch_k > stoch_d) and (stoch_k < 80) and (stoch_d < 80):
                    lg.info('Long trend confirmed for %s' % ticker)
                    return True
                elif (trend == 'short') and (stoch_k < stoch_d) and (stoch_k > 20) and (stoch_d > 20):
                    lg.info('Short trend confirmed for %s' % ticker)
                    return True
                elif attempt <= gvars.max_attempts_stc:
                    lg.info('Trend not clear for %s, waiting...' % ticker)
                    time.sleep(gvars.sleep_time_stc)
                    attempt += 1
                else:
                    lg.info('Trend NOT detected and timeout reached for %s' % ticker)
                    return False
        except Exception as e:
            lg.error('Something went wrong while getting instant trend, aborting...')
            lg.error(e)
            sys.exit()
     
    def check_stochastic_crossing(self, ticker, trend):
        # Check whether the stochastic curves have crossed or not depending on the trned
            # IN: ticker, trend
            # OUT: True if crossed / False if not crossed
        lg.info('\nChecking stochastic crossing...')

        # Ask for 5 min candles
        data = self.load_historical_data(ticker, interval='5m', period='5d')

        # Calculate the STOCHASTIC
        stoch_k, stoch_d = ti.stoch(data.High.values, data.Low.values, data.Close.values, 9, 6, 9)
        stoch_k = stoch_k[-1]
        stoch_d = stoch_d[-1]

        lg.info('%s stochastic = [K_FAST: %.2f, D_SLOW: %.2f]' % (ticker, stoch_k, stoch_d))
        
        try:
            if (trend == 'long') and (stoch_k <= stoch_d):
                return True
            elif (trend == 'short') and (stoch_k >= stoch_d):
                return True
            else:
                lg.info('Stochastic curves have not crossed')
                return False
        except Exception as e:
            lg.error('Something went wrong while checking stochastic crossing')
            lg.error(e)
            return True

    def enter_position_mode(self, ticker, trend):
        # Check conditions in parallel once inside the position
        attempt = 1

        # Get average entry price
        entry_price = self.get_avg_entry_price(ticker)

        # Set take profit
        take_profit = self.set_take_profit(entry_price, trend)

        # Set stop loss
        stop_loss = self.set_stop_loss(entry_price, trend)

        try:
            while True:
                self.current_price = self.get_current_price(ticker)
                
                # Check if take profit met for long
                if (trend == 'long') and (self.current_price >= take_profit):
                    lg.info('\nTake profit met at %.2f. Current price is %.2f' % (take_profit, self.current_price))
                    return True
                
                # Check if take profit met for short
                elif (trend == 'short') and (self.current_price <= take_profit):
                    lg.info('\nTake profit met at %.2f. Current price is %.2f' % (take_profit, self.current_price))
                    return True
                
                # Check if stop loss met for long
                elif (trend == 'long') and (self.current_price <= stop_loss):
                    lg.info('\nStop loss met at %.2f. Current price is %.2f' % (stop_loss, self.current_price))
                    return False
                
                # Check if stop loss met for short
                elif (trend == 'short') and (self.current_price >= stop_loss):
                    lg.info('\nStop loss met at %.2f. Current price is %.2f' % (stop_loss, self.current_price))
                    return False
                
                # Check stoch crossing
                if self.check_stochastic_crossing(ticker, trend):
                    lg.info('Stochastic curves crossed for %s. Current price is %.2f' % (trend, self.current_price))
                    return True
                
                # We wait
                elif attempt <= gvars.max_attempts_epm:
                    lg.info('\nWaiting inside position, attempt #%d' % attempt)
                    lg.info('SL %.2f <-- %.2f --> %.2f TP' % (stop_loss, self.current_price, take_profit))
                    time.sleep(gvars.sleep_time_epm)
                    attempt += 1

                # Get out (timeout reached)
                else:
                    lg.info('\nTimeout reached at enter position, too late')
                    return False
        except Exception as e:
            lg.error('Something went wrong at enter position')
            lg.error(e)
            return False

    def run(self):
        # LOOP until timeout reached
        # POINT ECHO
        while True:
            # Ask if we already have an open position
            if self.check_position(self.ticker, do_not_find=True):
                lg.info('There is already an open position with %s, going out...' % self.ticker)
                return False # Aborting execution
            
            # POINT DELTA
            while True:
                # Find general trend
                trend = self.get_general_trend(self.ticker)
                if not trend:
                    lg.info('No general trend found for %s, going out...' % self.ticker)
                    return False # Aborting execution
                
                # Confirm instant trend
                if not self.get_instant_trend(self.ticker, trend):
                    lg.info('Instant trend is not confirmed, going back...')
                    continue # If failed, go back to POINT DELTA

                # Perform RSI analysis
                if not self.get_rsi(self.ticker, trend):
                    lg.info('RSI is not confirmed, going back...')
                    continue # If failed, go back to POINT DELTA
                
                # Perform stochastic analysis
                if not self.get_stochastic(self.ticker, trend):
                    lg.info('Stochastic is not confirmed, going back...')
                    continue # If failed, go back to POINT DELTA
                
                lg.info('\nAll filtering passed, carrying on with the order')
                break # Get out of the loop

            # Get current price
            lg.info('\nGetting current price for %s' % self.ticker)
            self.current_price = round(float(self.load_historical_data(self.ticker, interval='1m', period='1d').Close.values[-1]), 2)
            lg.info('Current price is %.2f' % self.current_price)

            # Get shares amount
            shares_qty = self.get_shares_amount(self.ticker, self.current_price)

            # Submit order (limit)
            self.submit_order(self.ticker, shares_qty, trend, 'limit')
            
            # Check position
            if not self.check_position(self.ticker):
                self.cancel_pending_order(self.ticker)
                continue # Go back to POINT ECHO

            # Enter position mode
            successful_operation = self.enter_position_mode(self.ticker, trend)

            # Submit order (market)
            self.submit_order(self.ticker, shares_qty, trend, 'market', exit=True)

            # Check if position is cleared
            while True:
                if not self.check_position(self.ticker, do_not_find=True):
                    break
                time.sleep(gvars.sleep_time_cp)
                
            # End of execution
            return successful_operation
