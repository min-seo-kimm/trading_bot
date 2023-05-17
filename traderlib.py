# Define asset (TSLA)
    # IN: keyboard
    # OUT: string

# LOOP until timeout reached (ex. 2 hr)
# POINT ECHO: INITIAL CHECK
# Check the position: ask the broker/API if we have an open position with "asset"
    # IN: asset (string)
    # OUT: True (exists) / False (does not exist)

# Check if tradable: ask the broker/API if "asset" is tradable
    # IN: asset (string)
    # OUT: True (exists) / False (does not exist)

# GENERAL TREND
# Load 30 min candles: demand the API for 30 min candles
    # IN: asset (or whatever the API needs), time range*, candle size*
    # OUT: 30 min candles (OHLC for every candle)

# Perform general trend analysis: detect interesting trned (UP / DOWN / NO TREND)
    # IN: 30 min candles data (Close data)
    # OUT: UP / DOWN / NO TREND (string)
    # If no trend detected, go back to POINT ECHO

    # LOOP until timeout reached (ex. 30 min) or go back to POINT ECHO
    # POINT DELTA
    # STEP 1: Load 5 min candles
        # IN: asset (or whatever the API needs), time range*, candle size*
        # OUT: 5 min candles (OHLC for every candle)
        # If failed, go back to POINT DELTA

    # STEP 2: Perform instant trend analysis: confirm the trend detected by GT analysis
        # IN: 5 min candles data (Close data), output of the GT analysis (UP / DOWN string)
        # OUT: True (confirmed) / False (not confirmed)
        # If failed, go back to POINT DELTA

    # STEP 3: Perform RSI analysis
        # IN: 5 min candles data (Close data), output of the GT analysis (UP / DOWN string)
        # OUT: True (confirmed) / False (not confirmed)
        # If failed, go back to POINT DELTA

    # STEP 4: Perform stochastic analysis
        # IN: 5 min candles data (OHLC data), output of the GT analysis (UP / DOWN string)
        # OUT: True (confirmed) / False (not confirmed)
        # If failed, go back to POINT DELTA

# SUBMIT ORDER
# Submit order (limit order): interact with the broker API
    # IN: number of shares to operate with, asset, desired price
    # OUT: True (confirmed) / False (not confirmed), position ID
    # If False, abort / go back to POINT ECHO

# Check position: see if the position exists
    # IN: position ID
    # OUT: True (confirmed) / False (not confirmed)
    # If False, abort / go back to POINT ECHO

# LOOP until timeout reached (ex. ~8 hr)
# ENTER POSITION MODE: check the conditions in parallel
# IF check take profit. If True -> close position
    # IN: current gains (earning $)
    # OUT: True / False

# ELIF check stop loss. If True -> close position
    # IN: current gains (losing $)
    # OUT: True / False

# ELIF check stoch crossing. Pull OHLC data. If True -> close position
    # STEP 1: pull 5 min OHLC data
        # IN: asset
        # OUT: OHLC data (5 min candles)

    # STEP 2: see whether the stochastic curves are crosisng
        # IN: OHLC data (5 min candles)
        # OUT: True / False

# GET OUT
# SUBMIT ORDER
# SUbmit order (market order): interact with the broker API
    # IN: number of shares to operate with, asset, position ID
    # OUT: True (confirmed) / False (not confirmed)
    # If False, retry until it works

# Check position: see if the position exists
    # IN: position ID
    # OUT: True (still exists) / False (does not exist)
    # If False, abort / go back to SUBMIT ORDER

# Wait 15 min
# End
