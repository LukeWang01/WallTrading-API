# Description: This file contains the settings for trading.


""" Step 1: !!! Important. Set up the broker name !!! """
TRADING_BROKER = 'LONGPORT'  # set up the broker name based on the broker class name
"""
'IBKR': IBKRBroker,
'WEBULL': WebullBroker,
'MooMoo': MooMooFutuBroker,
'Futu': MooMooFutuBroker,
'SCHWAB': SchwabBroker,
'TIGER': TigerBroker,
'LONGPORT': LongPortBroker
"""


""" Step 2: !!! Important. Please choose qty decision mode, revise qty setting for each stock !!! """
# Option 1: FUND_MODE, calculate the trading quantity based on the initial fund
FUND_MODE = True  # default to True, set to False if you want to use fixed qty
INITIAL_FUND_FOR_TQQQ = 1  # default to 1, set the initial trading fund for tqqq, it will be used for qty calculation
INITIAL_FUND_FOR_SOXL = 1  # default to 1, set the initial trading fund for soxl, it will be used for qty calculation
INITIAL_FUND_FOR_IBIT = 1  # default to 1, set the initial trading fund for ibit, it will be used for qty calculation

# Option 2: QTY_MODE, calculate the trading quantity based on the fixed qty
QTY_MODE = False  # default to False, set to True if you want to use fixed qty
ONE_PERCENT_TRADING_QTY_FOR_TQQQ = 1  # default to 1, set the trading quantity for 1% of the initial fund
ONE_PERCENT_TRADING_QTY_FOR_SOXL = 1  # default to 1, set the trading quantity for 1% of the initial fund
ONE_PERCENT_TRADING_QTY_FOR_IBIT = 1  # default to 1, set the trading quantity for 1% of the initial fund


""" Step 3: !!! Important. Please choose which level and which ticker you want to trade !!! """
TRADING_LIST = ['TQQQ', 'SOXL', 'IBIT']  # set the trading list, delete the stock if you don't want to trade
TRADING_LEVEL = ['L0', 'L1', 'L2', 'L3', 'L4']  # set the trading level, delete the level if you don't want to trade


""" Please don't change the code below, unless you know what you are doing """

""" (Optional): Account settings, don't change the default setting unless you know what you are doing """
TRADING_CONFIRMATION = True  # default to True, set to False if you want to stop trading
TRADING_CASH_THRESHOLD = 1  # set the minimum cash balance requirement after each trade
TRADING_CASH_MARGIN_CONTROL = True  # default to True, set to False if you want to use margin or bypass the cash check
TRADING_ALLOW_PRE_POST_MARKET_ORDER = True  # default to True, set to False if you don't want to trade in pre/post market



""" (Optional): 1. Specific trading direction control settings """
# buy side
ENABLE_BUY_TQQQ = True  # default to True, set to False if you don't want to buy TQQQ
ENABLE_BUY_SOXL = True  # default to True, set to False if you don't want to buy SOXL
ENABLE_BUY_IBIT = True  # default to True, set to False if you don't want to buy IBIT
# sell side
ENABLE_SELL_TQQQ = True  # default to True, set to False if you don't want to sell TQQQ
ENABLE_SELL_SOXL = True  # default to True, set to False if you don't want to sell SOXL
ENABLE_SELL_IBIT = True  # default to True, set to False if you don't want to sell IBIT

""" (Optional): 2. Specific Trading Control Settings: Level, Depth, CodeNum """
# this is the default setting, which corresponds to the trading strategy for WallTrading Bot
# please don't change the default setting, unless you know what you are doing
# please contact the dev team for any questions
# trading position control per stock ticker:

Bind_Depth_codeNum = False  # Default to False, set to True if you want to bind the depth and codeNum

LEVEL_POSITIONS_TQQQ = {
    0: {  # L0
        'depth': {0: 0.01, 1: 0.01, 2: 0.01, 3: 0.00, 4: 0.00, 5: 0.02, 6: 0.02, 7: 0.03, 8: 0.04, 9: 0.04, 10: 0.05},
        'code': {3: 0.02},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    1: {  # L1
        'depth': {0: 0.01, 1: 0.01, 2: 0.01, 3: 0.00, 4: 0.00, 5: 0.02, 6: 0.02, 7: 0.03, 8: 0.04, 9: 0.04, 10: 0.05},
        'code': {3: 0.03},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    2: {  # L2
        'depth': {0: 0.02, 1: 0.02, 2: 0.02, 3: 0.00, 4: 0.00, 5: 0.00, 6: 0.04, 7: 0.04, 8: 0.05, 9: 0.06, 10: 0.07},
        'code': {3: 0.04},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    3: {  # L3
        'depth': {0: 0.03, 1: 0.03, 2: 0.03, 3: 0.04, 4: 0.08, 5: 0.00, 6: 0.00, 7: 0.00, 8: 0.00, 9: 0.00, 10: 0.00},
        'code': {3: 0.08},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    4: {  # L4
        'depth': {0: 0.15, 1: 0.22, 2: 0.22, 3: 0.25, 4: 0.25, 5: 0.00, 6: 0.00, 7: 0.00, 8: 0.00, 9: 0.00, 10: 0.00},
        'code': {3: 0.22},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    }
}


LEVEL_POSITIONS_SOXL = {
    0: {  # L0
        'depth': {0: 0.01, 1: 0.01, 2: 0.01, 3: 0.00, 4: 0.00, 5: 0.02, 6: 0.02, 7: 0.03, 8: 0.04, 9: 0.04, 10: 0.05},
        'code': {3: 0.02},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    1: {  # L1
        'depth': {0: 0.01, 1: 0.01, 2: 0.01, 3: 0.00, 4: 0.00, 5: 0.02, 6: 0.02, 7: 0.03, 8: 0.04, 9: 0.04, 10: 0.05},
        'code': {3: 0.03},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    2: {  # L2
        'depth': {0: 0.02, 1: 0.02, 2: 0.02, 3: 0.00, 4: 0.00, 5: 0.00, 6: 0.04, 7: 0.04, 8: 0.05, 9: 0.06, 10: 0.07},
        'code': {3: 0.04},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    3: {  # L3
        'depth': {0: 0.03, 1: 0.03, 2: 0.03, 3: 0.04, 4: 0.08, 5: 0.00, 6: 0.00, 7: 0.00, 8: 0.00, 9: 0.00, 10: 0.00},
        'code': {3: 0.08},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    4: {  # L4
        'depth': {0: 0.15, 1: 0.22, 2: 0.22, 3: 0.25, 4: 0.25, 5: 0.00, 6: 0.00, 7: 0.00, 8: 0.00, 9: 0.00, 10: 0.00},
        'code': {3: 0.22},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    }
}


LEVEL_POSITIONS_IBIT = {
    0: {  # L0
        'depth': {0: 0.01, 1: 0.01, 2: 0.01, 3: 0.00, 4: 0.00, 5: 0.02, 6: 0.02, 7: 0.03, 8: 0.04, 9: 0.04, 10: 0.05},
        'code': {3: 0.02},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    1: {  # L1
        'depth': {0: 0.01, 1: 0.01, 2: 0.01, 3: 0.00, 4: 0.00, 5: 0.02, 6: 0.02, 7: 0.03, 8: 0.04, 9: 0.04, 10: 0.05},
        'code': {3: 0.03},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    2: {  # L2
        'depth': {0: 0.02, 1: 0.02, 2: 0.02, 3: 0.00, 4: 0.00, 5: 0.00, 6: 0.04, 7: 0.04, 8: 0.05, 9: 0.06, 10: 0.07},
        'code': {3: 0.04},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    3: {  # L3
        'depth': {0: 0.03, 1: 0.03, 2: 0.03, 3: 0.04, 4: 0.08, 5: 0.00, 6: 0.00, 7: 0.00, 8: 0.00, 9: 0.00, 10: 0.00},
        'code': {3: 0.08},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    4: {  # L4
        'depth': {0: 0.15, 1: 0.22, 2: 0.22, 3: 0.25, 4: 0.25, 5: 0.00, 6: 0.00, 7: 0.00, 8: 0.00, 9: 0.00, 10: 0.00},
        'code': {3: 0.22},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    }
}


LEVEL_POSITIONS_DEFAULT = {
    0: {  # L0
        'depth': {0: 0.01, 1: 0.01, 2: 0.01, 3: 0.00, 4: 0.00, 5: 0.02, 6: 0.02, 7: 0.03, 8: 0.04, 9: 0.04, 10: 0.05},
        'code': {3: 0.02},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    1: {  # L1
        'depth': {0: 0.01, 1: 0.01, 2: 0.01, 3: 0.00, 4: 0.00, 5: 0.02, 6: 0.02, 7: 0.03, 8: 0.04, 9: 0.04, 10: 0.05},
        'code': {3: 0.03},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    2: {  # L2
        'depth': {0: 0.02, 1: 0.02, 2: 0.02, 3: 0.00, 4: 0.00, 5: 0.00, 6: 0.04, 7: 0.04, 8: 0.05, 9: 0.06, 10: 0.07},
        'code': {3: 0.04},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    3: {  # L3
        'depth': {0: 0.03, 1: 0.03, 2: 0.03, 3: 0.04, 4: 0.08, 5: 0.00, 6: 0.00, 7: 0.00, 8: 0.00, 9: 0.00, 10: 0.00},
        'code': {3: 0.08},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    },
    4: {  # L4
        'depth': {0: 0.15, 1: 0.22, 2: 0.22, 3: 0.25, 4: 0.25, 5: 0.00, 6: 0.00, 7: 0.00, 8: 0.00, 9: 0.00, 10: 0.00},
        'code': {3: 0.22},
        'enable': True  # default to True, set to False if you don't want to trade at this level
    }
}
