# encoding: utf-8

from datetime import datetime
import logging as lg
import os

def initialize_logger():
    # Create a folder for all the logs
    logs_path = './logs/' # Define the path
    try:
        os.mkdir(logs_path)
    except OSError:
        print('Creation of directory %s failed - the directory already exists' % logs_path)
    else:
        print('Successfully created log directory')

    # Rename each log depending on the time
    date = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_name = date + '.log'
    current_log_path = logs_path + log_name
    
    # Log parameters
    lg.basicConfig(filename=current_log_path, format='%(asctime)s - %(levelname)s: %(message)s', level=lg.INFO)
    lg.getLogger().addHandler(lg.StreamHandler())

    # Init message
    lg.info('Log initialized')
