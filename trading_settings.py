# Description: This file contains the settings for trading.


TRADING_BROKER = 'MooMoo'  # set up the broker name based on the broker class name
"""
'IBKR': IBKRBroker,
'WEBULL': WebullBroker,
'MooMoo': MooMooFutuBroker,
'Futu': MooMooFutuBroker,
'SCHWAB': SchwabBroker,
"""

level_positions = {
    # this is the default setting, which corresponds to the trading strategy for WallTrading Bot
    # please don't change the default setting, unless you know what you are doing
    # please contact the dev team for any questions
    0: {  # L0
        'depth': {0: 0.01, 1: 0.01, 2: 0.01, 3: 0.00, 4: 0.00, 5: 0.02, 6: 0.02, 7: 0.03, 8: 0.04, 9: 0.04, 10: 0.05},
        'code': {3: 0.02}
    },
    1: {  # L1
        'depth': {0: 0.01, 1: 0.01, 2: 0.01, 3: 0.00, 4: 0.00, 5: 0.02, 6: 0.02, 7: 0.03, 8: 0.04, 9: 0.04, 10: 0.05},
        'code': {3: 0.03}
    },
    2: {  # L2
        'depth': {0: 0.02, 1: 0.02, 2: 0.02, 3: 0.00, 4: 0.00, 5: 0.00, 6: 0.04, 7: 0.04, 8: 0.05, 9: 0.06, 10: 0.07},
        'code': {3: 0.04}
    },
    3: {  # L3
        'depth': {0: 0.03, 1: 0.03, 2: 0.03, 3: 0.04, 4: 0.08, 5: 0.00, 6: 0.00, 7: 0.00, 8: 0.00, 9: 0.00, 10: 0.00},
        'code': {3: 0.08}
    },
    4: {  # L4
        'depth': {0: 0.15, 1: 0.22, 2: 0.22, 3: 0.25, 4: 0.25, 5: 0.00, 6: 0.00, 7: 0.00, 8: 0.00, 9: 0.00, 10: 0.00},
        'code': {3: 0.22}
    }
}

""" ‼️ Important, please revise fund, you want to trade for each stock ‼️ """
INITIAL_FUND_FOR_TQQQ = 100000  # set the initial trading fund for tqqq, it will be used for qty calculation
INITIAL_FUND_FOR_SOXL = 100000  # set the initial trading fund for soxl, it will be used for qty calculation
INITIAL_FUND_FOR_IBIT = 100000  # set the initial trading fund for ibit, it will be used for qty calculation

TRADING_LIST = ['TQQQ', 'SOXL', 'IBIT']  # set the trading list, delete the stock if you don't want to trade
TRADING_LEVEL = ['L0', 'L1', 'L2', 'L3', 'L4']  # set the trading level, delete the level if you don't want to trade

TRADING_CONFIRMATION = True  # default to True, set to False if you want to stop trading
TRADING_CASH_THRESHOLD = 1  # set the minimum cash balance requirement after each trade
TRADING_CASH_MARGIN_CONTROL = True  # default to True, set to False if you want to use margin
TRADING_ALLOW_PRE_POST_MARKET_ORDER = True  # default to True, set to False if you don't want to trade in pre/post market


def decision_qty(json_data):
    """
    :param json_data:
    :return: trading quantity
    """
    # check if the trading data is in the trading list and trading level
    if json_data["ticker"] not in TRADING_LIST:
        return 0
    if json_data["level"] not in TRADING_LEVEL:
        return 0

    initial_fund = 0

    if json_data["ticker"] == "TQQQ":
        initial_fund = INITIAL_FUND_FOR_TQQQ
    elif json_data["ticker"] == "SOXL":
        initial_fund = INITIAL_FUND_FOR_SOXL
    elif json_data["ticker"] == "IBIT":
        initial_fund = INITIAL_FUND_FOR_IBIT

    level = int(json_data["level"][1:])
    depth = int(json_data["depth"])
    codeNum = int(json_data["codeNum"])
    price = float(json_data["price"])

    position_pct = 0

    if level in level_positions:
        if depth in level_positions[level]['depth']:
            position_pct += level_positions[level]['depth'][depth]
        if codeNum in level_positions[level]['code']:
            position_pct += level_positions[level]['code'][codeNum]

    qty = int((position_pct * initial_fund) / price)

    return qty
