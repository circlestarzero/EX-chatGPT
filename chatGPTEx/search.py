import json

from flask import Flask, request, jsonify, make_response
from api_class import GoogleSearchAPI, GPT3API, WikiSearchAPI, WolframAPI
import threading 
#from revChatGPT.V1 import ChatbotOld
from revChatGPT.V3 import Chatbot

import json
import re
import time
# old chatgpt api by access token 
# chatbot = Chatbot(config={
#   "access_token": "YOUR_CHATGPT_ACCESS_TOKEN"
#   # recently openAI has published the GPT-3.5 turbo API, you can replace this with the newsest one.
# })
# new gpt3.5 turbo api by api key
    # old chatgpt api by access token
    # prev_text = ""
    # for data in chatbot.ask(
    #     prompt
    # ):
    #     message = data["message"][len(prev_text) :]
    #     print(message, end="", flush=True)
    #     prev_text = data["message"]

    # new gpt3.5 turbo api by api key
chatbot = Chatbot(api_key="YOU_OPENAI_API_KEY")

# ask the API call
def APIQuery(query):
    with open("chatGPTEx/APIPrompt.txt", "r") as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    response = ""
    for data in chatbot.ask(prompt):
        response+=data
    pattern = r"(\{[\s\S\n]*\"calls\"[\s\S\n]*\})"
    match = re.search(pattern, response)
    if match:
        json_data = match.group(1)
        print(json.loads(json_data))
        return json.loads(json_data)
    return json.loads("{\"calls\":[]}")

# ask some extra information to the API call response
def APIExtraQuery(query,callResponse):
    with open("chatGPTEx/APIExtraPrompt.txt", "r") as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{callResponse}", str(callResponse))
    response = ""
    for data in chatbot.ask(prompt):
        response+=data
    pattern = r"(\{[\s\S\n]*\"calls\"[\s\S\n]*\})"
    match = re.search(pattern, response)
    if match:
        json_data = match.group(1)
        print(json.loads(json_data))
        return json.loads(json_data)
    return json.loads("{\"calls\":[]}")

# summary the give the final reply
def SumReply(query, apicalls):
    with open("chatGPTEx/ReplySum.txt", "r") as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{apicalls}", apicalls)
    response = ""
    for data in chatbot.ask(prompt):
        print(data, end="", flush=True)
        response+=data
    print()
    return response

# summary the search result
def Summary(query, callResponse):
    with open("chatGPTEx/summary.txt", "r") as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{callResponse}", callResponse)
    response = ""
    for data in chatbot.ask(prompt):
        print(data, end="", flush=True)
        response+=data
    print()
    return response
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
    # print(json.dumps(call_res, ensure_ascii=False))
    return json.dumps(call_res, ensure_ascii=False)
if __name__ == "__main__":
    # print time 
    print()
    query = 'current date: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' query:' + input()
    # APIQuery(query)
    call_res0 = search(APIQuery(query))
    Sum0 = Summary(query, call_res0)
    call_res1 = search(APIExtraQuery(query,Sum0))
    Sum1 = Summary(query, call_res1)
    print('\n\nChatGpt: \n' )
    SumReply(query, str(Sum0)+str(Sum1))