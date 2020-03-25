#!/usr/bin/env python3

import configparser
import exceptions
import output as op
import os

config_file = "config.ini"
if os.path.exists(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    SWING_API_KEY = config['keys']['swing_api_key']
    CURRENT_CAPITAL = float(config['account']['current_capital'])
    COMMISSION_COST = float(config['account']['commission_cost'])
    VERBOSITY = int(config['app']['verbosity'])
    WRITE_TO_FILE = True if config['app']['write_to_file'] == "true" else False
else:
    op.log_error(exceptions.DocumentError)