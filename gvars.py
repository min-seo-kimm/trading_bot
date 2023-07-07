# encoding: utf-8

# REST API
API_KEY = "PKQZIS3VID0N34Y5YCGE"
API_SECRET_KEY = "ua4PLYNh3kZhC3qbjO5zadPRGYvAKcbS52kV3Zdm"
API_URL = "https://paper-api.alpaca.markets"

# Percentage margin section
stop_loss_margin = 0.01 # Stop loss (need modification)
take_profit_margin = 0.03 # Take profit (need modification)
max_var = 0.02 # Limit price (need modification)

# Max attempts section
max_attempts_cp = 5 # Check position
max_attempts_cpo = 5 # Cancel pending order
max_attempts_gcp = 5 # Get current price
max_attempts_gaep = 5 # Get average entry price
max_attempts_ggt = 10 # Get general trend (need modification)
max_attempts_git = 20 # Get instant trend (need modification)
max_attempts_rsi = 20 # Get rsi (need modification)
max_attempts_stc = 20 # Get stochastic (need modification)
max_attempts_epm = 360 # Enter position mode

# Sleep time section (seconds)
sleep_time_cp = 5 # Check position
sleep_time_cpo = 5 # Cancel pending order
sleep_time_gcp = 5 # Get current price
sleep_time_gaep = 5 # Get average entry price
sleep_time_ggt = 60 # Get general trend (need modification)
sleep_time_git = 30 # Get instant trend (need modification)
sleep_time_rsi = 30 # Get rsi (need modification)
sleep_time_stc = 30 # Get stochastic (need modification)
sleep_time_epm = 20 # Enter position mode
sleep_time_me = 3600 # Main execution

max_spent_equity = 5000 # Total equity to spend in a single operation
