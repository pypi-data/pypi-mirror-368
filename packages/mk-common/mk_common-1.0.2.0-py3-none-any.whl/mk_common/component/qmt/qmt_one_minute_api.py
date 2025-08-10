from xtquant import xtdata
import time
from loguru import logger
import pandas as pd
from datetime import datetime, timedelta
import mk_common.util.date_handle_util as date_handle_util

'''
用于显示下载进度
'''
import string


def my_download(stock_list: list, period: str, start_date='', end_date=''):
    if [i for i in ["d", "w", "mon", "q", "y", ] if i in period]:
        period = "1d"
    elif "m" in period:
        numb = period.translate(str.maketrans("", "", string.ascii_letters))
        if int(numb) < 5:
            period = "1m"
        else:
            period = "5m"
    elif "tick" == period:
        pass
    else:
        raise KeyboardInterrupt("周期传入错误")
    n = 1
    for i in stock_list:
        xtdata.download_history_data(i, period, start_date, end_date)
        n += 1


def do_subscribe_quote(stock_list: list, period: str):
    for i in stock_list:
        xtdata.subscribe_quote(i, period=period)
    time.sleep(1)  # 等待订阅完成


def down_load_data_his(start_date, end_date, period, need_download, code_list):
    #
    if need_download:  # 判断要不要下载数据, gmd系列函数都是从本地读取历史数据,从服务器订阅获取最新数据
        my_download(code_list, period, start_date, end_date)
    ############ 仅获取历史行情 #####################
    data_one_minute_df = xtdata.get_market_data_ex([], code_list, period=period, start_time=start_date,
                                                   end_time=end_date)
    return data_one_minute_df


def get_one_minute_data(symbol, start_date, end_date, period, need_download):
    code_list = [symbol]
    data = down_load_data_his(start_date, end_date, period, need_download, code_list)
    data_df_init = data[symbol]
    if data_df_init.shape[0]:
        logger.warning("无分钟数据:{},{},{}", symbol, start_date, end_date)
        return None
    data_df = data_df_init.copy()

    # 本地化为 UTC 时区
    data_df['time'] = pd.to_datetime(data_df['time'], unit='ms')
    # 加上 8 小时
    data_df['time'] = data_df['time'] + pd.Timedelta(hours=8)

    data_df['time'] = data_df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    data_df = data_df[['time', 'open', 'high', 'low', 'close', 'volume', 'amount']]
    data_df['symbol'] = symbol
    data_df['_id'] = symbol + '_' + data_df['time']

    data_df.dropna(subset=['open'], axis=0, inplace=True)
    logger.info("同步分钟数据完成:,{}", symbol)
    return data_df


# 批量获取分钟数据
def get_one_minute_data_by_symbol_list(code_list, start_date, end_date, period, need_download):
    data = down_load_data_his(start_date, end_date, period, need_download, code_list)

    result_df = pd.concat(
        {k: df.assign(symbol=k) for k, df in data.items()},
        ignore_index=True
    )

    if result_df.shape[0] == 0:
        logger.warning("无分钟数据:{},{},{}", code_list, start_date, end_date)
        return None
    data_df = result_df.copy()

    # 本地化为 UTC 时区
    data_df['time'] = pd.to_datetime(data_df['time'], unit='ms')
    # 加上 8 小时
    data_df['time'] = data_df['time'] + pd.Timedelta(hours=8)

    data_df['time'] = data_df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    data_df = data_df[['symbol', 'time', 'open', 'high', 'low', 'close', 'volume', 'amount']]

    data_df['_id'] = data_df['symbol'] + '_' + data_df['time']

    data_df.dropna(subset=['open'], axis=0, inplace=True)
    logger.info("同步分钟数据完成:,{}", code_list)
    return data_df


if __name__ == '__main__':
    now_date = datetime.now()
    # Get the first day of the current month
    first_day_current = now_date.replace(day=1)
    # Subtract one day to get the last day of previous month
    last_day_previous = first_day_current - timedelta(days=1)
    # Get the first day of previous month
    first_day_previous = last_day_previous.replace(day=1)
    # Format the dates
    first_day_str = first_day_previous.strftime('%Y-%m-%d')
    last_day_str = last_day_previous.strftime('%Y-%m-%d')
    while True:
        test_df = get_one_minute_data_by_symbol_list(['300315.SZ', '000001.SZ'],
                                                     date_handle_util.no_slash_date('2025-08-06'),
                                                     date_handle_util.no_slash_date('2025-08-06'), '1m', True)
        logger.info('test')
