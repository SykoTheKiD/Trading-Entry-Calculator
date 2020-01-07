#!/usr/bin/env python3

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

SWING_API_KEY = config['keys']['swing_api_key']
CURRENT_CAPITAL = config['account']['current_capital']
COMMISSION_COST = config['account']['commission_cost']
VERBOSITY = config['app']['verbosity']
