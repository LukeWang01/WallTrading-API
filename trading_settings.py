# Description: This file contains the settings for trading.

"""
json_data = {
        "time": time_now,
        "ticker": stock,
        "price": price,
        "level": level,
        "direction": direction,
        "depth": depth,
        "codeNum": codeNum,
    }

'IBKR': IBKRBroker,
'WEBULL': WebullBroker,
'MooMoo': MooMooFutuBroker,
'Futu': MooMooFutuBroker,
'SCHWAB': SchwabBroker,

"""

TRADING_BROKER = 'MooMoo'

LEVEL_QTY = {
    # for testing purposes, revise based on the actual trading strategy
    'L0': 1,
    'L1': 2,
    'L2': 3,
    'L3': 4,
    'L4': 5,
}

TRADING_LIST = ['TQQQ', 'SOXL', 'IBIT']
TRADING_LEVEL = ['L0', 'L1', 'L2', 'L3', 'L4']
TRADING_CONFIRMATION = True     # default to True, set to False if you want to stop trading
TRADING_CASH_THRESHOLD = 1      # set the minimum cash balance after each trade
TRADING_CASH_CONTROL = False    # default to False, set to True if you need control the cash balance, eg: using margin


def decision_qty(json_data):
    # for testing purposes, revise based on the actual trading strategy
    if json_data["ticker"] not in TRADING_LIST:
        return 0
    if json_data["level"] not in TRADING_LEVEL:
        return 0
    return LEVEL_QTY[json_data["level"]]
