import json
import requests
import urllib.parse
import re
import os
import string
import time
import threading
from queue import PriorityQueue as PQ
import jieba
program_path = os.path.realpath(__file__)
program_dir = os.path.dirname(program_path)
with open(program_dir+'/cn_stopwords.txt', encoding='utf-8') as f:
    zh_stopwords = [line.strip() for line in f]
def remove_stopwords(text):
    zh_words = jieba.cut(text, cut_all=False)
    zh_filtered_words = [word.strip() for word in zh_words if word not in zh_stopwords and word != ' ']
    filtered_words = zh_filtered_words
    return "".join(filtered_words)
def clean_string(input_str):
    # Replace multiple spaces with a single space
    res = re.sub(r'\s+', ' ', input_str)
    # Remove spaces except between words
    res = re.sub(r'(?<!\w)\s+|\s+(?!\w)', '', res)
    # Replace Chinese symbols with English equivalents
    symbol_dict = {
        '，': ' ',
        '。': ' ',
        '！': ' ',
        '？': ' ',
        '；': ' ',
        '：': ' ',
        '“': ' ',
        '”': ' ',
        '‘': " ",
        '’': " ",
        '（': ' ',
        '）': ' ',
        '《': ' ',
        '》': ' ',
        '【': ' ',
        '】': ' ',
        '｛': ' ',
        '｝': ' ',
        '〔': ' ',
        '〕': ' ',
        '〈': ' ',
        '〉': ' ',
        '「': ' ',
        '」': ' ',
        '『': ' ',
        '』': ' ',
        '﹃': ' ',
        '﹄': ' ',
        '﹁': ' ',
        '﹂': ' ',
        '、': ' ',
    }
    pattern = re.compile('|'.join(re.escape(key) for key in symbol_dict.keys()))
    res = pattern.sub(lambda x: symbol_dict[x.group()], res)
    # Remove consecutive periods
    # res = re.sub(r'\.+', '.', res)
    pattern = re.compile(r'[,.;:!?]+$')
    res = pattern.sub('', res)
    res = re.sub(r'<.+?>', '', res)  # Remove HTML tags
    res = re.sub(r'\W{2,}', '', res)
    res = re.sub(r'(\d) +(\d)', r'\1,\2', res)
    res = res.strip()  # Remove leading/trailing spaces
    res = remove_stopwords(res)
    return res
class MetaAPI():
    def __init__(
        self,
        api_keys: list,
        api_name: str,
        base_url: str,
        apiTimeInterval:float = 0.1,
        lastAPICallTime:float = time.time()-100,
        proxy=None,
    )->None:
        self.apiTimeInterval = apiTimeInterval
        self.proxy = proxy
        self.session = requests.Session()
        if self.proxy:
            proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }
            self.session.proxies = proxies
        self.api_name = api_name
        self.base_url = base_url
        self.api_keys = PQ()
        self.trash_api_keys = PQ()
        self.lock = threading.Lock()
        for key in api_keys:
            self.api_keys.put((lastAPICallTime,key))
    def get_api_key(self):
        with self.lock:
            while(self.trash_api_keys.qsize() and self.api_keys.qsize()):
                trash_key = self.trash_api_keys.get()
                apiKey = self.api_keys.get()
                if(trash_key[1] == apiKey[1]):
                    self.api_keys.put((time.time()+24*3600, apiKey[1]))
                    continue
                else:
                    self.trash_api_keys.put(trash_key)
                    self.api_keys.put(apiKey)
                    break
            apiKey = self.api_keys.get()
            if apiKey[0] > time.time():
                print('API key exhausted')
                raise Exception('API key Exhausted')
            delay = self._calculate_delay(apiKey)
            time.sleep(delay)
            self.api_keys.put((time.time(), apiKey[1]))
            return apiKey[1]
    def _calculate_delay(self, apiKey):
        elapsed_time = time.time() - apiKey[0]
        if elapsed_time < self.apiTimeInterval:
            return self.apiTimeInterval - elapsed_time
        else:
            return 0


class WikiSearchAPI(MetaAPI):
    def __init__(
        self,
        apikeys: list,
        proxy=None,
    )-> None:
        self.proxy = proxy
        self.session = requests.Session()
        if self.proxy:
            proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }
            self.session.proxies = proxies
        api_name = 'Wiki Search'
        base_url = 'https://en.wikipedia.org/w/api.php'
        super(WikiSearchAPI, self).__init__(api_name=api_name, base_url=base_url,api_keys=[''])
    def call(self,query, num_results=2):
        def remove_html_tags(text):
            clean = re.compile('<.*?>')
            return re.sub(clean, '', text)
        base_url = 'https://en.wikipedia.org/w/api.php?'
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
        }
        call_url = base_url + urllib.parse.urlencode(params)
        r = self.session.get(call_url)
        data = r.json()['query']['search']
        data = [d['title'] + ": " + remove_html_tags(d["snippet"]) for d in data][:num_results]
        return data

class GoogleSearchAPI(MetaAPI):
    def __init__(
        self,
        apikeys: list,
        proxy=None,
    )-> None:
        self.proxy = proxy
        self.session = requests.Session()
        if self.proxy:
            proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }
            self.session.proxies = proxies
        api_name = 'Google Search'
        base_url = 'https://customsearch.googleapis.com/customsearch/v1?'
        super(GoogleSearchAPI, self).__init__(api_name=api_name, base_url=base_url,api_keys=apikeys)
    def call(self, query, num_results=2):
        try:
            GOOGLE_API_KEY,GOOGLE_SEARCH_ENGINE_ID= self.get_api_key()
        except Exception as e:
            print("Error occurred while getting API key:", e)
            return []
        params = {
            'q': query,
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_SEARCH_ENGINE_ID,
            'c2coff': '0',
            'num': num_results
        }
        call_url = self.base_url + urllib.parse.urlencode(params)
        try:
            res = self.session.get(call_url)
            if "items" in res.json():
                items = res.json()["items"]
                filter_data = [
                    clean_string(item["title"] + ": " + item["snippet"]) for item in items
                ]
                return ('\n').join(filter_data)
            else:
                return []
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 403:  # API key error
                self.trash_api_keys.put((time.time(), (GOOGLE_API_KEY,GOOGLE_SEARCH_ENGINE_ID)))
                return self.call(query, num_results)
            else:
                raise err
class WolframAPI(MetaAPI):
    def __init__(
        self,
        apikeys: list,
        proxy=None,
    )-> None:
        self.proxy = proxy
        self.session = requests.Session()
        if self.proxy:
            proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }
            self.session.proxies = proxies
        api_name = 'wolfram'
        base_url = 'https://api.wolframalpha.com/v2/query'
        super(WolframAPI, self).__init__(api_name=api_name, base_url=base_url,api_keys=apikeys)
    def call(self, query, num_results=3):
        query = query.replace('+', ' plus ')
        try:
            APPID = self.get_api_key()
        except Exception as e:
            print("Error occurred while getting API key:", e)
            return []
        params = {
            'input': query,
            'format': 'plaintext',
            'output': 'JSON',
            'appid': APPID, # get from wolfram Alpha document
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        try:
            responseFromWolfram = self.session.get(
                self.base_url, params=params, headers=headers)
            if  'queryresult' in responseFromWolfram.json() and 'pods' in responseFromWolfram.json()['queryresult']:
                pods = responseFromWolfram.json()['queryresult']['pods'][:num_results]
                pods_id = [pod["id"]for pod in pods]
                subplots = [(pod['subpods']) for pod in pods]
                pods_plaintext = []
                for subplot in subplots:
                    text = '\n'.join([c['plaintext'] for c in subplot])
                    pods_plaintext.append(text)
                # pods_plaintext = ['\n'.join(pod['subpods']['plaintext']) for pod in pods]
                res = [pods_id[i] + ": " + pods_plaintext[i]  for i in range(len(pods_plaintext)) if pods_plaintext[i].strip() != '']
                return res
            else:
                return []
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 403:  # API key error
                self.trash_api_keys.put((time.time(),(APPID)))
                return self.call(query, num_results)
            else:
                raise err
