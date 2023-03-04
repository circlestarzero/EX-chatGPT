import json

from flask import Flask, request, jsonify, make_response
from api_class import GoogleSearchAPI, WikiSearchAPI, WolframAPI
import threading 
#from revChatGPT.V1 import ChatbotOld
from revChatGPT.V3 import Chatbot
import json
import re
import configparser
import os
program_path = os.path.realpath(__file__)
program_dir = os.path.dirname(program_path)
# old chatgpt api by access token 
# chatbot = Chatbot(config={
#   "access_token": "YOUR_CHATGPT_ACCESS_TOKEN"
#   # recently openAI has published the GPT-3.5 turbo API, you can replace this with the newsest one.
# })
# new gpt3.5 turbo api by api key
config = configparser.ConfigParser()
config.read(program_dir+'/apikey.ini')
# Access the keys in the configuration file
OPENAI_API_KEY = config['OpenAI']['OPENAI_API_KEY']
chatbot = Chatbot(api_key=str(OPENAI_API_KEY))

def directQuery(query):
    response = ""
    for data in chatbot.ask(query):
        response+=data
    return response
def APIQuery(query):
    with open(program_dir+"/APIPrompt.txt", "r", encoding='utf-8') as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    response = ""
    # prev_text = ""
    # old chatgpt api by access token
    # for data in chatbot.ask(
    #     prompt
    # ):
    #     message = data["message"][len(prev_text) :]
    #     print(message, end="", flush=True)
    #     response+=message
    #     prev_text = data["message"]
    # print()
    for data in chatbot.ask(prompt):
        response+=data
    pattern = r"(\{[\s\S\n]*\"calls\"[\s\S\n]*\})"
    match = re.search(pattern, response)
    if match:
        json_data = match.group(1)
        print(json.loads(json_data))
        return json.loads(json_data)
    return json.loads("{\"calls\":[]}")
def APIExtraQuery(query,callResponse):
    with open(program_dir+"/APIExtraPrompt.txt", "r",encoding='utf-8') as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{callResponse}", str(callResponse))
    response = ""
    # prev_text = ""
    # old chatgpt api by access token
    # for data in chatbot.ask(
    #     prompt
    # ):
    #     message = data["message"][len(prev_text) :]
    #     print(message, end="", flush=True)
    #     response+=message
    #     prev_text = data["message"]
    # print()
    for data in chatbot.ask(prompt):
        response+=data
    pattern = r"(\{[\s\S\n]*\"calls\"[\s\S\n]*\})"
    match = re.search(pattern, response)
    if match:
        json_data = match.group(1)
        print(json.loads(json_data))
        return json.loads(json_data)
    return json.loads("{\"calls\":[]}")
def SumReply(query, apicalls,max_token=2000):
    with open(program_dir+"/ReplySum.txt", "r",encoding='utf-8') as f:
        prompt = f.read()
    apicalls = str(apicalls)[:max_token]
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{apicalls}", apicalls)
    response = ""
    for data in chatbot.ask(prompt):
        print(data, end="", flush=True)
        response+=data
    print()
    return response
def Summary(query, callResponse):
    with open(program_dir+"/summary.txt", "r",encoding='utf-8') as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{callResponse}", callResponse)
    response = ""
    # old chatgpt api by access token
    # prev_text = ""
    # for data in chatbot.ask(
    #     prompt
    # ):
    #     message = data["message"][len(prev_text) :]
    #     print(message, end="", flush=True)
    #     prev_text = data["message"]

    # new gpt3.5 turbo api by api key
    for data in chatbot.ask(prompt):
        print(data, end="", flush=True)
        response+=data
    print()
    return response
def search(content,max_token=2000):
    call_list = content['calls']
    # global search_data
    global call_res
    call_res = {}
    def google_search(query, num_results=4,summarzie = False):
        search_data = GoogleSearchAPI.call(query, num_results=num_results)
        if summarzie:
            summary_data = search_data
            call_res['google/' + query] = summary_data
        else:
            call_res['google/' + query] = search_data
    def wiki_search(query, num_results=3,summarzie = False):
        search_data = WikiSearchAPI.call(query, num_results=num_results)
        if summarzie:
            summary_data = search_data
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
            t = threading.Thread(target=google_search, args=[q, 6, google_summarize])
        elif api.lower() == 'wikisearch':
            t = threading.Thread(target=wiki_search, args=[q, 1, wiki_summarize])
        elif api.lower() == 'calculator':
            t = threading.Thread(target=wolfram_search, args=[q])
        else:
            continue
        all_threads.append(t)
    for t in all_threads:
        t.start()
    for t in all_threads:
        t.join()
    call_res = json.loads(json.dumps(call_res,ensure_ascii=False))
    res = str(call_res)
    while len(res) > max_token:
        flag = 0
        for key,value in call_res.items():
            if len(res) <= max_token: break
            if len(value) > 2:
                flag = 1
                value = value[:-1]
                call_res[key] = value
            res = str(call_res)
        if flag == 0: break
    if len(res) > max_token:
        res = res[:max_token]
    return res
if __name__ == "__main__":
    print(program_dir)