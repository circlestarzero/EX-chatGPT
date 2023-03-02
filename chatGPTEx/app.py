import json

from flask import Flask, request, jsonify, make_response
import requests
from api_class import GoogleSearchAPI, GPT3API, WikiSearchAPI, WolframAPI
import threading 
from revChatGPT.V1 import Chatbot
import json
import re
from flask import Flask, jsonify
chatbot = Chatbot(config={
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiJkZXNpZGVyaW9yNjI5QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJnZW9pcF9jb3VudHJ5IjoiVVMifSwiaHR0cHM6Ly9hcGkub3BlbmFpLmNvbS9hdXRoIjp7InVzZXJfaWQiOiJ1c2VyLUpOa3VyQXpyUG1rUmNUb2xkV1BIOUJXViJ9LCJpc3MiOiJodHRwczovL2F1dGgwLm9wZW5haS5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDU1MTE1Njg4NzEzMTMxNDYzMTAiLCJhdWQiOlsiaHR0cHM6Ly9hcGkub3BlbmFpLmNvbS92MSIsImh0dHBzOi8vb3BlbmFpLm9wZW5haS5hdXRoMGFwcC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjc2Njk2MjEzLCJleHAiOjE2Nzc5MDU4MTMsImF6cCI6IlRkSkljYmUxNldvVEh0Tjk1bnl5d2g1RTR5T282SXRHIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBtb2RlbC5yZWFkIG1vZGVsLnJlcXVlc3Qgb3JnYW5pemF0aW9uLnJlYWQgb2ZmbGluZV9hY2Nlc3MifQ.lsB1noQM5BMvQYDEa3t43h9aoKhVs1Pt28FAf3nZ9nAv78vGkWvDdJLPW8ZcOXFy8lkhoxggRBg1bFiABzZAmx5HwmwkVWoM5w_csFdM_3qnAtEQnVIFvI_PR5KGWkODXkAnDfiOqLNA6MSp8ndF7N4mz3CWuwGwPXw6dZCFXlRM1py6C1BO5ZZkVj-SvWBCA20-tG7tupdg0s2M-6G-GFGnI1Ye2pboPh2Yk1TW1WlCKoqpRpTVkwJGapb7QCtQChRwnDqSjp-4hBTBuIb5eo0YdIskc4lBYpIZX5HfTPRfniBOuXzChitpSBkLBf5BLsPcHbus4BQjFq_HcKRXdg"
})
def APIQuery(query):
    with open("APIPromptTools/chatgptEx/API_Prompt.txt", "r") as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    response = ""
    prev_text = ""
    for data in chatbot.ask(
        prompt
    ):
        message = data["message"][len(prev_text) :]
        print(message, end="", flush=True)
        response+=message
        prev_text = data["message"]
    print()
    pattern = r"(\{[\s\S\n]*\"calls\"[\s\S\n]*\})"
    match = re.search(pattern, response)
    if match:
        json_data = match.group(1)
        return json.loads(json_data)
    return json.loads("{\"calls\":[]}")
def SumReply(query, apicalls):
    with open("APIPromptTools/chatgptEx/ReplySum.txt", "r") as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{apicalls}", apicalls)
    response = ""
    prev_text = ""
    for data in chatbot.ask(
        prompt
    ):
        message = data["message"][len(prev_text) :]
        print(message, end="", flush=True)
        prev_text = data["message"]
    print()
def wolfram_query(query):
    params = {
        'input': query,
        'format': 'plaintext',
        'output': 'JSON',
        'appid': '2URRW5-LUR8EY5QUT',
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Cookie': 'WR_SID=278cad0a.5f54ac6b8d820; pageWidth=1156.3636474609375; seenMathInputPromoPopover=true; activeInput=math; openedTray=%7B%22name%22%3A%22popular%22%2C%22inputMode%22%3A%22math%22%2C%22remember%22%3Atrue%7D; JSESSIONID=3508C3AB928F7B8F64C3D22A3D12543A',
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
    responseFromWolfram = requests.get(
        'https://api.wolframalpha.com/v2/query', params=params, headers=headers)
    pods = responseFromWolfram.json()['queryresult']['pods'][:3]
    pods = json.dumps(pods, ensure_ascii=False)
    print(pods)
    return pods
def google_search(content):
    call_list = content
    global call_res_google
    call_res_google = {}
    def search_and_summary(query, num_results=4):
        search_data = GoogleSearchAPI.call(query, num_results=num_results)
        summary_data = GPT3API.call(query, search_data)
        call_res_google[query] = json.dumps(summary_data, ensure_ascii=False)
    if(len(call_list) ==0 ):
        return ''
    elif(len(call_list) ==1 ):
        q = call_list[0]['query']
        search_data = GoogleSearchAPI.call(q, num_results=7)
        call_res_google[q] = search_data
    else:
        all_threads = []
        for call in call_list[:]:
            q = call['query']
            t = threading.Thread(target=search_and_summary, args=[q])
            all_threads.append(t)
        for t in all_threads:
            t.start()
        for t in all_threads:
            t.join()
    print(json.dumps(call_res_google, ensure_ascii=False))
    return json.dumps(call_res_google, ensure_ascii=False)
def search(content):
    call_list = content['calls']
    # global search_data
    global call_res
    call_res = {}
    def google_search(query, num_results=4,summarzie = False):
        search_data = GoogleSearchAPI.call(query, num_results=num_results)
        if summarzie:
            summary_data = GPT3API.call(query, search_data)
            call_res['google/' + query] = summary_data
        else:
            call_res['google/' + query] = search_data
        
    def wiki_search(query, num_results=3,summarzie = False):
        search_data = WikiSearchAPI.call(query, num_results=num_results)
        if summarzie:
            summary_data = GPT3API.call(query, search_data)
            call_res['wiki/' + query] = summary_data
        else:
            call_res['wiki/' + query] = search_data
        call_res['wiki/' + query] = search_data
    def wolfram_search(query, num_results=3):
        search_data = WolframAPI.call(query, num_results)
        call_res['wolfram/' + query] = search_data
    all_threads = []
    google_summarize = False
    google_cnt = 0
    wiki_summarize = False
    wiki_cnt = 0
    for call in call_list[:]:
        q = call['API']
        if q.lower() == 'google':
            google_cnt += 1
        if q.lower() == 'wikisearch':
            wiki_cnt += 1
    if google_cnt > 3:
        google_summarize = True
    if wiki_cnt > 2:
        wiki_summarize = True
    for call in call_list[:]:
        q = call['query']
        api = call['API']
        if api.lower() == 'google':
            t = threading.Thread(target=google_search, args=[q, 5, google_summarize])
        elif api.lower() == 'wikisearch':
            t = threading.Thread(target=wiki_search, args=[q, 2, wiki_summarize])
        elif api.lower() == 'calculator':
            t = threading.Thread(target=wolfram_search, args=[q])
        else:
            continue
        all_threads.append(t)

    for t in all_threads:
        t.start()

    for t in all_threads:
        t.join()

    print(json.dumps(call_res, ensure_ascii=False))
    return json.dumps(call_res, ensure_ascii=False)
if __name__ == "__main__":
    query = input()
    call_res = search(APIQuery(query))
    print('\n\nChatGpt: \n' )
    SumReply(query, call_res)