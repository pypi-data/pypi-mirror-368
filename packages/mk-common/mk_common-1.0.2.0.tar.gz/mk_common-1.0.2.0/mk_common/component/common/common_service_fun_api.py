# 股票分类
def classify_symbol(real_time_quotes_now_df):
    real_time_quotes_now_df['classification'] = real_time_quotes_now_df['symbol'].apply(
        lambda symbol: classify_symbol_one(symbol))
    return real_time_quotes_now_df


# 增加前缀
def add_pre_prefix(real_time_quotes_now_df):
    real_time_quotes_now_df['symbol_prefix'] = real_time_quotes_now_df['symbol'].apply(
        lambda symbol: add_pre_prefix_one(symbol))
    return real_time_quotes_now_df


# 增加后缀
def add_after_prefix(real_time_quotes_now_df):
    real_time_quotes_now_df['symbol_prefix'] = real_time_quotes_now_df['symbol'].apply(
        lambda symbol: add_after_prefix_one(symbol))
    return real_time_quotes_now_df


# 单个股票分类
def classify_symbol_one(symbol):
    if symbol.startswith('3'):
        return 'C'
    elif symbol.startswith('6'):
        if symbol.startswith('68'):
            return 'K'
        else:
            return 'H'
    elif symbol.startswith('0'):
        return 'S'
    else:
        return 'X'


# 添加前缀
def add_pre_prefix_one(symbol):
    symbol_simple = symbol[0:6]
    if bool(1 - is_valid_symbol(symbol_simple)):
        return symbol
    if symbol_simple.startswith('6'):
        return 'SH' + symbol_simple
    elif symbol_simple.startswith('0') or symbol_simple.startswith('3'):
        return 'SZ' + symbol_simple
    else:
        return 'BJ' + symbol_simple


# 添加后缀
def add_after_prefix_one(symbol):
    symbol_simple = symbol[0:6]
    if bool(1 - is_valid_symbol(symbol_simple)):
        return symbol
    if symbol_simple.startswith('6'):
        return symbol_simple + '.SH'
    elif symbol_simple.startswith('0') or symbol_simple.startswith('3'):
        return symbol_simple + '.SZ'
    else:
        return symbol_simple + '.BJ'


# 排除 新股
def exclude_new_stock(real_time_quotes_now_df):
    return real_time_quotes_now_df.loc[~(real_time_quotes_now_df['name'].str.contains('N'))]


# 排除 包含名字中包含特定字母的数据
def exclude_str_name_stock(real_time_quotes_now_df, str_name):
    return real_time_quotes_now_df.loc[~(real_time_quotes_now_df['name'].str.contains(str_name))]


# 排除st
def exclude_st_symbol(real_time_quotes_now_df):
    exclude_st_symbol_list = list(
        real_time_quotes_now_df.loc[(real_time_quotes_now_df['name'].str.contains('ST'))
                                    | (real_time_quotes_now_df['name'].str.contains('退'))]['symbol'])
    return real_time_quotes_now_df.loc[
        ~(real_time_quotes_now_df['symbol'].isin(
            exclude_st_symbol_list))]


# 排除带星的ST 容易退市
def exclude_star_st_symbol(df):
    exclude_st_symbol_list = list(
        df.loc[(df['name'].str.contains('\*'))
               | (df['name'].str.contains('退'))]['symbol'])
    return df.loc[
        ~(df['symbol'].isin(
            exclude_st_symbol_list))]


# 排除b股数据
def exclude_b_symbol(real_time_quotes_now_df):
    return real_time_quotes_now_df.loc[(real_time_quotes_now_df.symbol.str.startswith('3'))
                                       | (real_time_quotes_now_df.symbol.str.startswith('0'))
                                       | (real_time_quotes_now_df.symbol.str.startswith('6'))
                                       | (real_time_quotes_now_df.symbol.str.startswith('4'))
                                       | (real_time_quotes_now_df.symbol.str.startswith('9'))
                                       | (real_time_quotes_now_df.symbol.str.startswith('8'))]


def exclude_ts_symbol(real_time_quotes_now_df):
    return real_time_quotes_now_df.loc[~(real_time_quotes_now_df['name'].str.contains('退'))]


# 排除成交量为0 停牌的股票
def exclude_amount_zero_stock(real_time_quotes_now_df):
    return real_time_quotes_now_df.loc[~(real_time_quotes_now_df['amount'] == 0)]


# 获取当天 new stock
def get_new_stock(real_time_quotes_now_df):
    return real_time_quotes_now_df.loc[(real_time_quotes_now_df['name'].str.contains('N'))]


# 增加东财股票前缀
def symbol_add_em_prefix(symbol):
    symbol_simple = symbol[0:6]
    if bool(1 - is_valid_symbol(symbol_simple)):
        return symbol
    if symbol_simple.startswith('6'):
        return '1.' + symbol_simple
    elif symbol_simple.startswith('0') or symbol_simple.startswith('3'):
        return '0.' + symbol_simple
    else:
        return '0.' + symbol_simple



def is_valid_symbol(symbol):
    # 确保输入是字符串（避免数字或其他类型）
    if not isinstance(symbol, str):
        return False
    # 检查长度是否为6且所有字符都是数字
    return len(symbol) == 6 and symbol.isdigit()