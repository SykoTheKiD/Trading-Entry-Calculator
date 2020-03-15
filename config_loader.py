#!/usr/bin/env python3

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

SWING_API_KEY = config['keys']['swing_api_key']
CURRENT_CAPITAL = float(config['account']['current_capital'])
COMMISSION_COST = float(config['account']['commission_cost'])
VERBOSITY = int(config['app']['verbosity'])
WRITE_TO_FILE = True if config['app']['write_to_file'] == "true" else False
