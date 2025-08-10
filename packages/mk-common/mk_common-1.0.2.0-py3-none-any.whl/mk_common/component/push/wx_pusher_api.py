import json
import pandas as pd
import requests
from loguru import logger

'''
https://wxpusher.zjiecode.com/docs/#/

title : 推送标题
msg：推送主题
'''


def push_msg_to_wechat(title, msg, token_df):
    for token_one in token_df.itertuples():
        app_token = token_one.token
        uid = token_one.uids
        try:
            url = 'http://wxpusher.zjiecode.com/api/send/message'
            s = json.dumps({'appToken': app_token,
                            'content': msg,
                            'summary': title,
                            'contentType': 1,
                            'uids': [uid]
                            })
            headers = {
                "Content-Type": "application/json"
            }
            r = requests.post(url, data=s, headers=headers)
        except BaseException as e:
            logger.error("推送异常:{},{}", str(e), app_token)
        print(r)


if __name__ == '__main__':
    token_df_test = pd.DataFrame([
        ['test001', 'test004'],
        ['test002', 'test003']
    ], columns=['token', 'uids'])
    push_msg_to_wechat('test', 'big win', token_df_test)
