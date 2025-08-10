# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Desc: 东方财富-实时行情报价 
https://quote.eastmoney.com/sz000001.html
"""
import pandas as pd
import requests
from loguru import logger
import concurrent.futures
import warnings
from typing import List

warnings.filterwarnings('ignore', category=FutureWarning)
""""
频繁调用会封ip,可以加上代理ip

"""


def stock_bid_ask_em(symbol: str = "000001", proxies=None) -> pd.DataFrame:
    """
    东方财富-行情报价
    https://quote.eastmoney.com/sz000001.html
    :param proxies: 代理ip
    :param symbol: 股票代码
    :type symbol: str
    :return: 行情报价
    :rtype: pandas.DataFrame
    """
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    market_code = 1 if symbol.startswith("6") else 0
    params = {
        "fltt": "2",
        "invt": "2",
        "fields": "f120,f121,f122,f174,f175,f59,f163,f43,f57,f58,f169,f170,f46,f44,f51,"
                  "f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,"
                  "f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,"
                  "f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,"
                  "f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,"
                  "f268,f255,f256,f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,"
                  "f279,f288,f152,f250,f251,f252,f253,f254,f269,f270,f271,f272,f273,f274,f275,"
                  "f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295",
        "secid": f"{market_code}.{symbol}",
    }

    # 是否加代理
    if proxies is None:
        r = requests.get(url, params)
    else:
        r = requests.get(url, params, proxies=proxies)
    try:
        data_json = r.json()
        data_dict = data_json["data"]
        data_df = pd.DataFrame([data_dict])
        data_df = data_df.rename(
            columns={
                "f31": "sell_5",
                "f32": "sell_5_vol",
                "f33": "sell_4",
                "f34": "sell_4_vol",
                "f35": "sell_3",
                "f36": "sell_3_vol",
                "f37": "sell_2",
                "f38": "sell_2_vol",
                "f39": "sell_1",
                "f40": "sell_1_vol",
                "f19": "buy_1",
                "f20": "buy_1_vol",
                "f17": "buy_2",
                "f18": "buy_2_vol",
                "f15": "buy_3",
                "f16": "buy_3_vol",
                "f13": "buy_4",
                "f14": "buy_4_vol",
                "f11": "buy_5",
                "f12": "buy_5_vol",
                "f43": "now_price",
                "f71": "average_price",
                "f170": "chg",
                "f169": "change",
                "f47": "volume",
                "f48": "amount",
                "f168": "exchange",
                "f50": "quantity_ratio",
                "f44": "high",
                "f45": "low",
                "f46": "open",
                "f60": "yesterday_price",
                "f51": "zt_price",
                "f52": "df_price",
                "f49": "outer_disk",
                "f161": "inner_disk",
                "f116": "total_mv",
                "f117": "flow_mv",
                "f191": 'wei_bi',
                "f127": 'industry',
                "f128": 'area',
                "f137": 'today_main_net_inflow',
                "f140": 'super_large_order_net_inflow',
                "f143": 'large_order_net_inflow',
                "f57": 'symbol',
                "f58": 'name',
            })
        data_df = data_df[[
            "sell_5",
            "sell_5_vol",
            "sell_4",
            "sell_4_vol",
            "sell_3",
            "sell_3_vol",
            "sell_2",
            "sell_2_vol",
            "sell_1",
            "sell_1_vol",
            "buy_1",
            "buy_1_vol",
            "buy_2",
            "buy_2_vol",
            "buy_3",
            "buy_3_vol",
            "buy_4",
            "buy_4_vol",
            "buy_5",
            "buy_5_vol",
            "now_price",
            "average_price",
            "chg",
            "change",
            "volume",
            "amount",
            "exchange",
            "quantity_ratio",
            "high",
            "low",
            "open",
            "yesterday_price",
            "zt_price",
            "df_price",
            "outer_disk",
            "inner_disk",
            "total_mv",
            "flow_mv",
            'wei_bi',
            'industry',
            'area',
            'today_main_net_inflow',
            'super_large_order_net_inflow',
            'large_order_net_inflow',
            'symbol',
            'name',
        ]]
        data_df = data_df.replace('-', 0)
        return data_df
    except Exception as e:
        logger.error('获取实时行异常:{},{}', symbol, str(e))
        return pd.DataFrame()


def fetch_with_retry(symbol: str, timeout: int = 5, retries: int = 1, proxies=None) -> pd.DataFrame:
    for attempt in range(retries + 1):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as single_executor:
                future = single_executor.submit(stock_bid_ask_em, symbol, proxies)
                return future.result(timeout=timeout)
        except Exception as e:
            if attempt == retries:
                logger.error("失败:{},最终失败,错误:{}", symbol, str(e))
                return pd.DataFrame()
            logger.error("重试:{},第{}次失败,错误:{}", symbol, attempt + 1, str(e))


def fetch_all_symbols(symbols: List[str], max_workers: int = 20, timeout: int = 5, proxies=None) -> pd.DataFrame:
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_symbol = {
            executor.submit(fetch_with_retry, symbol, timeout, 1, proxies): symbol for symbol in symbols
        }
        for future in concurrent.futures.as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                df = future.result()
                if not df.empty:
                    results.append(df)
            except Exception as e:
                logger.error("错误:无法获取:{},", symbol, str(e))

        return pd.concat(results, ignore_index=True)


def get_company_info():
    company_info_df = mongodb_util_27017.find_all_data('company_info')
    company_info_df = company_info_df.iloc[0:100]
    symbol_list = list(company_info_df['symbol'])
    return symbol_list


from mns_common.db.MongodbUtil import MongodbUtil

mongodb_util_27017 = MongodbUtil('27017')
if __name__ == "__main__":
    test_df = stock_bid_ask_em("000001", None)
    test_df = test_df.iloc[0:100]

    symbol_list_test = get_company_info()
    number = 1
    logger.error("开始执行")
    while True:
        stock_bid_ask_em_df = fetch_all_symbols(symbol_list_test, max_workers=100, timeout=5,
                                                proxies=None)
        logger.error("执行次数:{}", number)
