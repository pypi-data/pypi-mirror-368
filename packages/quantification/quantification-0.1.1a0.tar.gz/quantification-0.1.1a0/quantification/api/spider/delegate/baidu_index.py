import json
from time import sleep
from tqdm import tqdm
from base64 import b64encode
from datetime import date, datetime, time, timedelta
from urllib.parse import urlencode, quote

import pandas as pd
import requests
from Crypto.Cipher import AES

from quantification.core import (
    Field,
    cache_query,
    BaseDelegate,
)

from ..setting import SpiderSetting


def get_cipher_text(keyword: str, headers) -> str:
    byte_list = [
        b"\x00", b"\x01", b"\x02", b"\x03", b"\x04", b"\x05", b"\x06", b"\x07",
        b"\x08", b"\x09", b"\x0a", b"\x0b", b"\x0c", b"\x0d", b"\x0e", b"\x0f",
        b"\x10"
    ]
    # 这个数是从acs-2057.js里写死的，但这个脚本请求时代时间戳，不确定是不是一个动态变化的脚本
    start_time = 1652338834776
    end_time = int(datetime.now().timestamp() * 1000)

    wait_encrypted_data = {
        "ua": headers["User-Agent"],
        "url": quote(f"https://index.baidu.com/v2/main/index.html#/trend/{keyword}?words={keyword}"),
        "platform": "MacIntel",
        "clientTs": end_time,
        "version": "2.1.0"
    }
    password = b"yyqmyasygcwaiyaa"
    iv = b"1234567887654321"
    aes = AES.new(password, AES.MODE_CBC, iv)
    wait_encrypted_str = json.dumps(wait_encrypted_data).encode()
    filled_count = 16 - len(wait_encrypted_str) % 16
    wait_encrypted_str += byte_list[filled_count] * filled_count
    encrypted_str = aes.encrypt(wait_encrypted_str)
    cipher_text = f"{start_time}_{end_time}_{b64encode(encrypted_str).decode()}"
    return cipher_text


def get_key(uniqid: str, cookies: str) -> str:
    headers = {
        'Host': 'index.baidu.com',
        'Connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
        'Cookie': cookies,
    }

    url = 'https://index.baidu.com/Interface/api/ptbk?uniqid=%s' % uniqid
    datas = json.loads(requests.get(url, headers=headers, timeout=30).text)
    return datas['data']


def decrypt_func(key: str, data: str) -> list[str]:
    """
        数据解密方法
    """
    a = key
    i = data
    n = {}
    s = []
    for o in range(len(a) // 2):
        n[a[o]] = a[len(a) // 2 + o]
    for r in range(len(data)):
        s.append(n[i[r]])
    return ''.join(s).split(',')


@cache_query(update=False)
def get_encrypt_json(
        *,
        start_date: date,
        end_date: date,
        keywords: list[list[str]],
        category: str,
        area: int,
        cookies: str
) -> dict:
    sleep(3)
    headers = {
        'Host': 'index.baidu.com',
        'Connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
        'Cookie': cookies,
    }
    headers["Cipher-Text"] = get_cipher_text(keywords[0][0], headers)

    word_list = [[{'name': keyword, 'wordType': 1} for keyword in keyword_list] for keyword_list in keywords]

    pre_urls = {
        'search': 'https://index.baidu.com/api/SearchApi/index?',
        'feed': 'https://index.baidu.com/api/FeedSearchApi/getFeedIndex?'
    }

    url = pre_urls[category] + urlencode({
        'word': json.dumps(word_list),
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d'),
        'area': area
    })

    encrypt_json = json.loads(requests.get(url, headers=headers, timeout=30).text)
    if category == "search":
        encrypt_datas = encrypt_json['data']['userIndexes']
    else:
        encrypt_datas = encrypt_json['data']['index']

    uniqid = encrypt_json['data']['uniqid']
    key = get_key(uniqid, cookies)

    for encrypt_data in encrypt_datas:
        if category == "search":
            for kind in ['all', 'pc', 'wise']:
                encrypt_data[kind]['data'] = decrypt_func(key, encrypt_data[kind]['data'])
        else:
            encrypt_data['data'] = decrypt_func(key, encrypt_data['data'])

    return encrypt_datas


@cache_query(update=False)
def check_keywords_exists(keywords: list[str], cookies: str):
    params = {"word": ",".join(keywords)}

    headers = {
        'Host': 'index.baidu.com',
        'Connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
        'Cookie': cookies,
    }

    url = "https://index.baidu.com/api/AddWordApi/checkWordsExists?" + urlencode(params)
    json_data = json.loads(requests.get(url, headers=headers, timeout=30).text)
    not_exists_keywords = []
    for item in json_data["data"]["result"]:
        if item["status"] == 10003:
            not_exists_keywords.extend(item["word"].split(","))

    return not_exists_keywords


def get_time_range_list(start_date: date, end_date: date) -> list[tuple[date, date]]:
    """
        切分时间段
    """
    date_range_list = []
    while 1:
        temp_date = start_date + timedelta(days=300)
        if temp_date > end_date:
            date_range_list.append((start_date, end_date))
            break
        date_range_list.append((start_date, temp_date))
        start_date = temp_date + timedelta(days=1)
    return date_range_list


class BaiduIndexDelegate(BaseDelegate[SpiderSetting]):
    pair = [
        (Field.BAIN_搜索指数, "search"),
        (Field.BAIN_资讯指数, "feed")
    ]

    def has_field(self, field: Field, **kwargs):
        if self.field2str.get(field) is None:
            return False

        keywords = kwargs.get("keywords")
        assert keywords is not None, "请传入keywords参数, 如keywords=['原神', 'Genshin']"
        for keyword in keywords:
            assert isinstance(keyword, str), "keyword必须都是str"
        assert len(keywords) <= 3, "keywords参数最多填入3个同义词"

        if not_exists := check_keywords_exists(keywords=keywords, cookies=f"BDUSS={self.setting.bduss}"):
            raise ValueError(f"词条不存在: {not_exists}")

        return True

    def query(self, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        keywords: list[str] = kwargs.get("keywords")

        df_list = []

        for start, end in tqdm(get_time_range_list(start_date=start_date, end_date=end_date), "遍历获取百度指数"):

            feed = get_encrypt_json(
                keywords=[keywords],
                start_date=start,
                end_date=end,
                cookies=f"BDUSS={self.setting.bduss}",
                category='feed',
                area=0
            )
            search = get_encrypt_json(
                keywords=[keywords],
                start_date=start,
                end_date=end,
                cookies=f"BDUSS={self.setting.bduss}",
                category='search',
                area=0
            )
            df = pd.DataFrame()
            df["search"] = search[0]["all"]["data"]
            df["feed"] = feed[0]["data"]
            df["date"] = pd.date_range(start=start, end=end)
            df_list.append(df)

        data = pd.concat(df_list)
        data = self.rename_columns(data, "date")
        data = self.use_date_index(data)

        return data

    def mask(self, data: pd.DataFrame, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        mask = pd.DataFrame(index=data.index, columns=data.columns)
        index = pd.Series(mask.index)

        for field in fields:
            mask[field] = list(map(lambda x: datetime.combine(x + pd.DateOffset(days=1), time(0, 0, 0)), index))

        return mask


__all__ = ["BaiduIndexDelegate"]
