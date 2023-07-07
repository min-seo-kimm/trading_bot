# encoding: utf-8

# REST API
API_KEY = ""
API_SECRET_KEY = ""
API_URL = "https://paper-api.alpaca.markets"

# Percentage margin section
stop_loss_margin = 0.01 # Stop loss
take_profit_margin = 0.03 # Take profit 
max_var = 0.02 # Limit price 

# Max attempts section
max_attempts_cp = 5 # Check position
max_attempts_cpo = 5 # Cancel pending order
max_attempts_gcp = 5 # Get current price
max_attempts_gaep = 5 # Get average entry price
max_attempts_ggt = 10 # Get general trend 
max_attempts_git = 20 # Get instant trend 
max_attempts_rsi = 20 # Get rsi 
max_attempts_stc = 20 # Get stochastic 
max_attempts_epm = 360 # Enter position mode

# Sleep time section (seconds)
sleep_time_cp = 5 # Check position
sleep_time_cpo = 5 # Cancel pending order
sleep_time_gcp = 5 # Get current price
sleep_time_gaep = 5 # Get average entry price
sleep_time_ggt = 60 # Get general trend 
sleep_time_git = 30 # Get instant trend 
sleep_time_rsi = 30 # Get rsi 
sleep_time_stc = 30 # Get stochastic 
sleep_time_epm = 20 # Enter position mode
sleep_time_me = 3600 # Main execution

max_spent_equity = 5000 # Total equity to spend in a single operation
