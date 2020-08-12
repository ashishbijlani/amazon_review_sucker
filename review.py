# coding=utf-8
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import time


def get_asin(keyword, page):
    """
    获取关键词搜索结果的asin
    :param keyword:关键词
    :param page:搜索结果翻页 1 - ∞
    :return: ['B0861BK9LQ', 'B07YX6WCLH']
    """
    url = f'https://www.amazon.com/s/query?k={keyword}&page={page}'
    header = {
        'sec-fetch-mode': 'cors',
        'x-amazon-s-swrs-version': 'EE47A80B3E983526E0C6E49FEFA99624',
        'x-amazon-s-fallback-url': '',
        'rtt': '0',
        'x-amazon-rush-fingerprints': '',
        'user-agent': 'Amazon.com/20.15.0.100 (Android/9/ONEPLUS A5000)',
        'accept': 'text/html,*/*',
        'x-amazon-s-mismatch-behavior': 'ALLOW',
        'x-requested-with': 'XMLHttpRequest',
        'downlink': '9.2',
        'ect': '4g',
        'sec-fetch-site': 'same-origin',
        'referer': f'https://www.amazon.com/s?k={keyword}&__mk_zh_CN=%E4%BA%9A%E9%A9%AC%E9%80%8A%E7%BD%91%E7%AB%99&buildFingerprint=OnePlus%2FOnePlus5%2FOnePlus5%3A9%2FPKQ1.180716.001%2F1912311102%3Auser%2Frelease-keys&buildProduct=OnePlus5&cri=bYpzQViSpd535jeJ&deviceDensityClassification=420&deviceScreenLayout=SCREENLAYOUT_SIZE_NORMAL&deviceType=A1MPSLFC7L5AFK&imgCrop=true&imgRes=0&manufacturer=OnePlus&model=ONEPLUS+A5000&osVersion=28&phoneType=PHONE_TYPE_GSM&ref=nb_sb_noss',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    resp = requests.get(url, headers=header).text

    def not_empty(s):
        return s and s.strip()

    asin_list = list(filter(not_empty, re.findall('"asin" : "(.*)",', resp)))
    return asin_list


def get_reviews(asin, star):
    """
    review获取,pageSize指定返回50个结果
    :param asin:
    :param star:
    :return: dict type review data
    """
    url = 'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/ref=cm_cr_unknown'

    data = f'sortBy=&reviewerType=&formatType=&mediaType=&filterByStar={star}&pageNumber=1&filterByLanguage=&filterByKeyword=&shouldAppend=undefined&deviceType=mobile&canShowIntHeader=undefined&reftag=cm_cr_unknown' \
           f'&pageSize=50' \
           f'&asin={asin}&scope=reviewsAjax0'

    header = {
        'sec-fetch-mode': 'cors',
        'origin': 'https://www.amazon.com',
        'rtt': '450',
        'user-agent': 'Mozilla/5.0 (Linux; Android 9; ONEPLUS A5000) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.92 Mobile Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'accept': 'text/html,*/*',
        'x-requested-with': 'XMLHttpRequest',
        'downlink': '0.7',
        'ect': '3g',
        'sec-fetch-site': 'same-origin',
        'referer': f'https://www.amazon.com/gp/aw/reviews/{asin}/ref=cm_cr_dp_mb_top?ie=UTF8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'Content-Length': str(len(data))
    }

    resp = requests.post(url, headers=header, data=data).text
    return html_parse(resp, star, asin)


def html_parse(html, star, asin):
    html = html.strip().split('&&&')
    reviews = []
    for i in html:
        cache = i.replace('"]', '').replace('["', '').replace('\\n', '').replace('\\', '').strip()    # append","#cm_cr-review_list","<div id=\"R260ZOOG3HNFZW\" data-hook=\"review-content\"
        data = cache.split(',', 2)                                                                    # ['append"', '"#cm_cr-review_list"', '"<div id="R260ZOOG3HNFZW" data-hook="review-content"
        try:
            if data[1] == '"#cm_cr-review_list"':
                soup = BeautifulSoup(data[2], 'lxml')
                review = {
                    'asin': asin,
                    'star': star,
                    'buyer': soup.find(attrs={'class': 'a-profile-name'}).text,
                    'title': soup.find(attrs={'data-hook': 'review-title'}).span.text.lstrip(' '),
                    'time':  soup.find(attrs={'data-hook': 'review-date'}).text,
                    'review':  soup.find(attrs={'data-hook': 'review-body'}).div.span.text,
                    'helpful': soup.find(attrs={'data-hook': 'helpful-vote-statement'}).text.strip()
                }
                # print(review)
                reviews.append(review)
        except Exception as e:
            print(e)
            pass

    return reviews


if __name__ == '__main__':
    # 设置所需的评价类型one_star - five_star
    review_type = ['one_star', 'two_star', 'three_star']
    keyword = 'uv+sterilizer'  # 关键词空格用+替换

    # main
    asin_list = get_asin(keyword, 3)
    for _asin in asin_list:
        for star in review_type:
            data = get_reviews(_asin, star)
            pd.DataFrame(data).to_csv('review.csv', mode='a', header=False)
            print(data)
            time.sleep(25)   # 使用休眠时间来防止风控，也可以采用proxy提速
