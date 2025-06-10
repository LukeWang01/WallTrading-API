""" Please don't change the code below, unless you know what you are doing """

from trading_settings import TRADING_LIST, TRADING_LEVEL, ENABLE_BUY_TQQQ, ENABLE_BUY_SOXL, \
    ENABLE_BUY_IBIT, ENABLE_SELL_TQQQ, ENABLE_SELL_SOXL, ENABLE_SELL_IBIT, FUND_MODE, INITIAL_FUND_FOR_TQQQ, \
    INITIAL_FUND_FOR_SOXL, INITIAL_FUND_FOR_IBIT, QTY_MODE, ONE_PERCENT_TRADING_QTY_FOR_TQQQ, \
    ONE_PERCENT_TRADING_QTY_FOR_SOXL, ONE_PERCENT_TRADING_QTY_FOR_IBIT, LEVEL_POSITIONS_TQQQ, LEVEL_POSITIONS_SOXL, \
    LEVEL_POSITIONS_IBIT, LEVEL_POSITIONS_DEFAULT, Bind_Depth_codeNum
from utils.wall_api_client import print_status

"""
Local decision handler for the trade
"""

""" Please do NOT change the code below, unless you KNOW what you are doing """


def decision_qty(json_data) -> tuple[int, float]:
    """
    :param json_data:
    :return: qty, position_pct
    """

    level = int(json_data["level"][1:])
    depth = int(json_data["depth"])
    codeNum = int(json_data["codeNum"])
    price = float(json_data["price"])
    stock = json_data["ticker"]
    direction = json_data["direction"]

    bind_Depth_codeNum_local = Bind_Depth_codeNum  # use the global setting

    if level == 4:
        # if level is 4, set the Bind_Depth_codeNum to False
        bind_Depth_codeNum_local = False

    position_pct = 0

    # 0. # calculate the position percentage and check level
    LEVEL_POSITIONS_MAP = {
        "TQQQ": LEVEL_POSITIONS_TQQQ,
        "SOXL": LEVEL_POSITIONS_SOXL,
        "IBIT": LEVEL_POSITIONS_IBIT
    }
    LEVEL_POSITIONS = LEVEL_POSITIONS_MAP.get(stock, LEVEL_POSITIONS_DEFAULT)

    # 0. Mapping the position percentage
    if level in LEVEL_POSITIONS:
        depth_position = 0
        code_position = 0

        if depth in LEVEL_POSITIONS[level]['depth']:
            depth_position = LEVEL_POSITIONS[level]['depth'][depth]
        if codeNum in LEVEL_POSITIONS[level]['code']:
            if bind_Depth_codeNum_local:
                if depth_position > 0:
                    code_position = LEVEL_POSITIONS[level]['code'][codeNum]
                else:
                    code_position = 0
            else:
                code_position = LEVEL_POSITIONS[level]['code'][codeNum]

        position_pct = depth_position + code_position

        # check if the current level is enabled
        if not LEVEL_POSITIONS[level]['enable']:
            print_status("Decision QTY Handler",
                         f"Decision, level: {level}, not enabled, qty is 0, please check the trading settings",
                         "WARNING")
            return 0, position_pct
    else:
        print_status("Decision QTY Handler",
                     f"Warning, level issues, qty is 0, please check the trading settings",
                     "WARNING")
        return 0, position_pct

    # 1. check if the trading data is in the trading list and trading level
    if stock not in TRADING_LIST:
        print_status("Decision QTY Handler",
                     f"Warning, ticker not in the trading list, qty is 0, please check the trading settings",
                     "WARNING")
        return 0, position_pct
    if json_data["level"] not in TRADING_LEVEL:
        print_status("Decision QTY Handler",
                     f"Warning, level not in the trading level, qty is 0, please check the trading settings",
                     "WARNING")
        return 0, position_pct

    # 2. check if the trading direction is enabled
    if direction == "Bull":
        if stock == "TQQQ" and not ENABLE_BUY_TQQQ:
            print_status("Decision QTY Handler",
                         f"Warning, {stock} buy is not enabled, qty is 0, please check the trading settings",
                         "WARNING")
            return 0, position_pct
        if stock == "SOXL" and not ENABLE_BUY_SOXL:
            print_status("Decision QTY Handler",
                         f"Warning, {stock} buy is not enabled, qty is 0, please check the trading settings",
                         "WARNING")
            return 0, position_pct
        if stock == "IBIT" and not ENABLE_BUY_IBIT:
            print_status("Decision QTY Handler",
                         f"Warning, {stock} buy is not enabled, qty is 0, please check the trading settings",
                         "WARNING")
            return 0, position_pct
    elif direction == "Bear":
        if stock == "TQQQ" and not ENABLE_SELL_TQQQ:
            print_status("Decision QTY Handler",
                         f"Warning, {stock} sell is not enabled, qty is 0, please check the trading settings",
                         "WARNING")
            return 0, position_pct
        if stock == "SOXL" and not ENABLE_SELL_SOXL:
            print_status("Decision QTY Handler",
                         f"Warning, {stock} sell is not enabled, qty is 0, please check the trading settings",
                         "WARNING")
            return 0, position_pct
        if stock == "IBIT" and not ENABLE_SELL_IBIT:
            print_status("Decision QTY Handler",
                         f"Warning, {stock} sell is not enabled, qty is 0, please check the trading settings",
                         "WARNING")
            return 0, position_pct

    # 3. calculate the trading quantity
    # 3.1 calculate the trading quantity, FUND_MODE
    if FUND_MODE:
        initial_fund_map = {
            "TQQQ": INITIAL_FUND_FOR_TQQQ,
            "SOXL": INITIAL_FUND_FOR_SOXL,
            "IBIT": INITIAL_FUND_FOR_IBIT
        }

        initial_fund = initial_fund_map.get(stock, 1)

        qty = int((position_pct * initial_fund) / price)
        # if qty < 1:
        #     qty = 1
        #     print_status("Decision QTY Handler - FUND MODE", f"Warning, qty reset to: {qty}, please check the trading settings", "WARNING")
        # delete, choose to strictly follow the position percentage
        print_status("Decision QTY Handler - FUND MODE",
                     f"Decision, qty is {qty}, please check the trading settings",
                     "INFO")
        return qty, position_pct

    # 3.2calculate the trading quantity, QTY_MODE
    elif QTY_MODE:
        qty_one_percent_map = {
            "TQQQ": ONE_PERCENT_TRADING_QTY_FOR_TQQQ,
            "SOXL": ONE_PERCENT_TRADING_QTY_FOR_SOXL,
            "IBIT": ONE_PERCENT_TRADING_QTY_FOR_IBIT
        }

        qty_one_percent = qty_one_percent_map.get(stock, 1)

        qty = int(position_pct * 100) * qty_one_percent
        # if qty < 1:
        #     qty = 1
        #     print_status("Decision QTY Handler - QTY MODE", f"Warning, qty reset to: {qty}, please check the trading settings", "WARNING")
        # qty reset deleted, choose to strictly follow the position percentage
        print_status("Decision QTY Handler - QTY MODE",
                     f"Decision, qty is {qty}, please check the trading settings",
                     "INFO")
        return qty, position_pct

    else:
        print_status("Decision QTY Handler",
                     f"Warning, wrong decision mode, qty is 0, please check the trading settings",
                     "WARNING")
        return 0, position_pct
