# coding=utf-8
import http.client
import hashlib
import urllib
import random
import json
import pandas as pd
import time

appid = ''
secretKey = ''
httpClient = None
fromLang = 'auto'   # 原文语种
toLang = 'zh'       # 译文语种


def trans_api(lang):
    q = lang
    myurl = '/api/trans/vip/translate'
    salt = random.randint(32768, 65536)
    sign = hashlib.md5((appid + q + str(salt) + secretKey).encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)
        return result['trans_result'][0]['dst']

    except Exception as e:
        print(e)
        pass

    finally:
        if httpClient:
            httpClient.close()


if __name__ == '__main__':
    csv_data = pd.read_csv('./review.csv').T.to_dict()
    for i in csv_data.values():
        trans_title = trans_api(i['title'])
        time.sleep(5)
        trans_review = trans_api(i['review'])
        time.sleep(5)

        i['title'] = trans_title
        i['review'] = trans_review
        print(i)
        pd.DataFrame(i, index=[0]).to_csv('trans_review.csv', encoding="utf_8_sig", mode='a', header=False)



