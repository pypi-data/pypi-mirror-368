import time, datetime, sys
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant
from loguru import logger
import pandas as pd
from functools import lru_cache


# 回调信息
class MyXtQuantTraderCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        """
        连接断开
        :return:
        """
        logger.error("连接断开回调:{}", datetime.datetime.now())

    def on_stock_order(self, order):
        """
        委托回报推送
        :param order: XtOrder对象
        :return:
        """
        logger.info("委托回调 投资备注:｛｝,{}", datetime.datetime.now(), order.order_remark)

    def on_stock_trade(self, trade):
        """
        成交变动推送
        :param trade: XtTrade对象
        :return:
        """
        logger.info("时间:{},成交回调:｛｝,委托方向(48买 49卖):{},成交价格:{},成交数量:{}",
                    datetime.datetime.now(),
                    trade.order_remark,
                    trade.offset_flag,
                    trade.traded_price,
                    trade.traded_volume
                    )

    def on_order_error(self, order_error):
        """
        委托失败推送
        :param order_error:XtOrderError 对象
        :return:
        """
        msg = order_error.order_remark + order_error.error_msg
        logger.error("委托报错回调:{}", msg)

    def on_cancel_error(self, cancel_error):
        """
        撤单失败推送
        :param cancel_error: XtCancelError 对象
        :return:
        """
        logger.error("撤单失败推送:{},{}", datetime.datetime.now(),
                     sys._getframe().f_code.co_name)

    def on_order_stock_async_response(self, response):
        """
        异步下单回报推送
        :param response: XtOrderResponse 对象
        :return:
        """
        print(f"异步委托回调 投资备注: {response.order_remark}")

    def on_cancel_order_stock_async_response(self, response):
        """
        :param response: XtCancelOrderResponse 对象
        :return:
        """
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)

    def on_account_status(self, status):
        """
        :param response: XtAccountStatus 对象
        :return:
        """
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)


# 委托下单 不一定成交
def order_buy(symbol, buy_price, buy_volume, account_no, qmt_data_path):
    logger.warning("委托买入代码:{},买入价格:{},买入数量:{}", symbol, buy_price, buy_volume)
    xt_trader = get_xt_trader(qmt_data_path)
    acc = get_trade_acc(account_no)
    seq = xt_trader.order_stock(acc,
                                symbol,
                                xtconstant.STOCK_BUY,
                                buy_volume,
                                xtconstant.FIX_PRICE,
                                buy_price,
                                "STOCK_BUY",
                                symbol)
    result_dict = {"entrust_no": str(seq)}
    return result_dict


# 委托卖出
def order_sell(symbol, sell_price, sell_volume, qmt_data_path, account_no):
    logger.warning("委托卖出代码:{},卖出价格:{},卖出数量:{}", symbol, sell_price, sell_volume)
    xt_trader = get_xt_trader(qmt_data_path)
    acc = get_trade_acc(account_no)
    seq = xt_trader.order_stock(acc,
                                symbol,
                                xtconstant.STOCK_SELL,
                                sell_volume,
                                xtconstant.FIX_PRICE,
                                sell_price,
                                "STOCK_SELL",
                                symbol)
    result_dict = {"entrust_no": str(seq)}
    return result_dict


# 成交查询 返回列表
# https://dict.thinktrader.net/nativeApi/xttrader.html#%E6%8C%81%E4%BB%93xtposition
def query_stock_trades(account_no, qmt_data_path):
    xt_trader = get_xt_trader(qmt_data_path)
    acc = get_trade_acc(account_no)
    trades = xt_trader.query_stock_trades(acc)

    return trades


# 取消委托
def order_cancel(entrust_no, symbol, qmt_data_path, account_no):
    xt_trader = get_xt_trader(qmt_data_path)
    acc = get_trade_acc(account_no)
    if symbol[-2:] == 'SZ':
        market = xtconstant.SZ_MARKET
    elif symbol[-2:] == 'SH':
        market = xtconstant.SH_MARKET
    else:
        # 北交所 todo
        market = xtconstant.SH_MARKET

    # xt_trader为XtQuant API实例对象
    cancel_result = xt_trader.cancel_order_stock_sysid(acc, market, str(entrust_no))
    return cancel_result


# account_id	str	资金账号
# stock_code	str	证券代码
# volume	int	持仓数量
# can_use_volume	int	可用数量
# open_price	float	开仓价
# market_value	float	市值
# frozen_volume	int	冻结数量
# on_road_volume	int	在途股份
# yesterday_volume	int	昨夜拥股
# avg_price	float	成本价
# 查询持仓 https://dict.thinktrader.net/nativeApi/xttrader.html#%E6%8C%81%E4%BB%93xtposition
def get_position(qmt_data_path, account_no):
    xt_trader = get_xt_trader(qmt_data_path)
    acc = get_trade_acc(account_no)
    position_list = xt_trader.query_stock_positions(acc)
    position_df = pd.DataFrame()
    for i in position_list:
        try:
            position_total_dict = {
                "account_type": i.account_type,
                "account_id": i.account_id,
                "stock_code": i.stock_code,
                "can_use_volume": i.can_use_volume,
                "open_price": i.open_price,
                "market_value": i.market_value,
                "frozen_volume": i.frozen_volume,
                "on_road_volume": i.on_road_volume,
                "yesterday_volume": i.yesterday_volume,
                "avg_price": i.avg_price
            }
            position_total_df = pd.DataFrame(position_total_dict, index=[1])
            if position_df is None:
                position_df = position_total_df
            else:
                position_df = pd.concat([position_total_df, position_df])
        except BaseException as e:
            logger.error("获取持仓信息异常:{}", e)
    return position_df


# 查询资产 https://dict.thinktrader.net/nativeApi/xttrader.html#%E8%B5%84%E4%BA%A7xtasset
def get_asset(account_no, qmt_data_path):
    account = StockAccount(account_no)
    # xt_trader为XtQuant API实例对象
    xt_trader = get_xt_trader(qmt_data_path)
    asset = xt_trader.query_stock_asset(account)
    result = {
        'account_type': asset.account_type,
        'account_id': asset.account_id,
        'cash': asset.cash,
        'frozen_cash': asset.frozen_cash,
        'market_value': asset.market_value,
        'total_asset': asset.total_asset,
    }
    return result


# 获取账号信息
@lru_cache(maxsize=None)
def get_trade_acc(account_no):
    # 创建资金账号为 account_no 的证券账号对象 股票账号为STOCK 信用CREDIT 期货FUTURE
    acc = StockAccount(account_no, 'STOCK')
    return acc


# 获取连接对象
@lru_cache(maxsize=None)
def get_xt_trader(qmt_data_path):
    session_id = int(time.time())
    xt_trader = XtQuantTrader(qmt_data_path, session_id)
    # 创建交易回调类对象，并声明接收回调
    callback = MyXtQuantTraderCallback()
    xt_trader.register_callback(callback)
    # 启动交易线程
    xt_trader.start()
    # 建立交易连接，返回0表示连接成功
    connect_result = xt_trader.connect()
    if connect_result == 0:
        logger.info("建立交易连接成功")
    else:
        logger.error("建立交易连接失败")
    return xt_trader


if __name__ == '__main__':
    get_asset('your_account', 'D:\\Program Files\\qmt\\国金证券QMT交易端\\userdata_mini')
