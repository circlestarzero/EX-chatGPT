import json

from flask import Flask, request, jsonify, make_response
from api_class import GoogleSearchAPI, WikiSearchAPI, WolframAPI
import threading 
import json
import re
import configparser
import os
import requests
import tiktoken
from optimizeOpenAI import ExChatGPT
ENCODER = tiktoken.get_encoding("gpt2")
program_path = os.path.realpath(__file__)
program_dir = os.path.dirname(program_path)
# api config load
config = configparser.ConfigParser()
config.read(program_dir+'/apikey.ini')
openAIAPIKeys = []
for i in range(0,10):
    key = 'key'+str(i)
    
    if key in config['OpenAI']:
        openAIAPIKeys.append(config['OpenAI'][key])
    else:
        break
print(openAIAPIKeys)
chatbot = ExChatGPT(api_keys=openAIAPIKeys,apiTimeInterval=20)
chatbot.load(program_dir+'/chatHistory.json')
max_token = 1000
def chatReplyProcess(prompt):
    return chatbot.ask_stream_copy(prompt)
def load_history(conv_id = 'default'):
    return chatbot.conversation[conv_id]
def detail_old(query):
    call_res0 = search(APIQuery(query))
    Sum0 = Summary(query, call_res0)
    call_res1 = search(APIExtraQuery(query,Sum0))
    Sum1 = Summary(query, call_res1)
    print('\n\nChatGpt: \n' )
    result  = SumReply(query, str(Sum0) + str(Sum1))
    return result
def detail(query,conv_id = 'default'):
    if chatbot.token_cost(conv_id) > max_token:
        chatbot.conversation_summary(convo_id=conv_id)
    call_res0 = search(APIQuery(query),750)
    print(f'API calls response:\n {call_res0}')
    call_res1 = search(APIExtraQuery(query,call_res0),750)
    print(f'API calls response:\n {call_res1}')
    result  = SumReply(query, str(call_res0) + str(call_res1),max_token=1500,conv_id=conv_id)
    return result +'\n\n token_cost: '+ str(chatbot.token_cost(conv_id))
def web(query,conv_id = 'default'):
    chatbot.conversation_summary(convo_id=conv_id)
    resp = directQuery(f'Chat History info: {chatbot.conversation[conv_id]}\n Query: {query}', conv_id=  conv_id)
    apir = APIQuery(query,resp=resp)
    call_res0 = search(apir,1500)
    print(f'API calls response:\n {call_res0}')
    result = SumReply(f'Chat History info: {chatbot.conversation[conv_id]}\n Query: {query}' ,str(call_res0),max_token=1000, conv_id=conv_id)
    chatbot.conversation[conv_id] = chatbot.conversation[conv_id][:-4]
    chatbot.conversation[conv_id].append({'role':'user','content':str(query)})
    chatbot.conversation[conv_id].append({'role':'assistant','content':str(result)})
    chatbot.save(program_dir+'/chatHistory.json')
    return result +'\n\n token_cost: '+ str(chatbot.token_cost(conv_id))
def webDirect(query,conv_id = 'default'):
    if chatbot.token_cost(conv_id) > max_token:
        chatbot.conversation_summary(convo_id=conv_id)
    apir = APIQuery(query)
    call_res0 = search(apir,1500)
    print(f'API calls response:\n {call_res0}')
    result = SumReply(f'{query}', str(call_res0), conv_id=conv_id)
    chatbot.conversation[conv_id] = chatbot.conversation[conv_id][:-2]
    chatbot.add_to_conversation(str(query), "user", convo_id=conv_id)
    chatbot.add_to_conversation(str(result), "assistant", convo_id=conv_id)
    chatbot.save(program_dir+'/chatHistory.json')
    return result +'\n\n token_cost: '+ str(chatbot.token_cost(conv_id))
def WebKeyWord(query,conv_id = 'default'):
    if chatbot.token_cost(conv_id) > max_token:
        chatbot.conversation_summary(convo_id=conv_id)
    q = chatbot.ask(
                f'Given a user prompt "{query}", respond with "none" if it is directed at the chatbot or cannot be answered by an internet search. Otherwise, provide a concise search query for a search engine. Avoid adding any additional text to the response to minimize token cost.',
                convo_id="search",
                temperature=0.0,
            ).strip()
    print("Searching for: ", query, "")
    if query == "none":
        search_results = '{"results": "No search results"}'
    else:
        search_results = requests.post(
            url="https://ddg-api.herokuapp.com/search",
            json={"query": query, "limit": 4},
            timeout=10,
        ).text
    search_res = json.dumps(json.loads(search_results), indent=4,ensure_ascii=False)
    chatbot.add_to_conversation(
        "Search results:" + search_res,
        "system",
        convo_id=conv_id,
    )
    result = chatbot.ask(query, "user", convo_id=conv_id)
    chatbot.conversation[conv_id] = chatbot.conversation[conv_id][:-2]
    chatbot.add_to_conversation(str(query), "user", convo_id=conv_id)
    chatbot.add_to_conversation(str(result), "assistant", convo_id=conv_id)
    chatbot.save(program_dir+'/chatHistory.json')
    print(result)
    return result +'\n\n token_cost: '+ str(chatbot.token_cost())
def directQuery(query,conv_id = 'default'):
    response = chatbot.ask(query)
    print(f'Direct Query: {query}\nChatGpt: {response}')
    return response +'\n\n token_cost: '+ str(chatbot.token_cost())
def APIQuery(query,resp =''):
    with open(program_dir+"/APIPrompt.txt", "r", encoding='utf-8') as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{resp}", resp)
    response = ""
    chatbot.reset(convo_id='api',system_prompt='Your are a API caller for a LLM, you need to call some APIs to get the information you need.')
    response =  chatbot.ask(prompt,convo_id='api')
    pattern = r"(\{[\s\S\n]*\"calls\"[\s\S\n]*\})"
    match = re.search(pattern, response)
    if match:
        json_data = match.group(1)
        result = json.loads(json_data)
        print(f'API calls: {result}\n')
        return result
    return json.loads("{\"calls\":[]}")
def APIExtraQuery(query,callResponse):
    with open(program_dir+"/APIExtraPrompt.txt", "r",encoding='utf-8') as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{callResponse}", str(callResponse))
    chatbot.reset(convo_id='api',system_prompt='Your are a API caller for a LLM, you need to call some APIs to get the information you need.')
    response = chatbot.ask(prompt,convo_id='api')
    pattern = r"(\{[\s\S\n]*\"calls\"[\s\S\n]*\})"
    match = re.search(pattern, response)
    if match:
        json_data = match.group(1)
        result = json.loads(json_data)
        print(f'API calls: {result}\n')
        return result
    return json.loads("{\"calls\":[]}")
def SumReply(query, apicalls, max_token=2000, conv_id = 'default'):
    with open(program_dir+"/ReplySum.txt", "r",encoding='utf-8') as f:
        prompt = f.read()
    apicalls = str(apicalls)[:max_token]
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{apicalls}", apicalls)
    response = chatbot.ask(prompt,convo_id=conv_id)
    print(f'ChatGPT SumReply:\n  {response}\n')
    return response
def Summary(query, callResponse):
    with open(program_dir+"/summary.txt", "r",encoding='utf-8') as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{callResponse}", callResponse)
    chatbot.reset(convo_id='sum',system_prompt='Your need to summarize the information you got from the APIs.')
    response = chatbot.ask(prompt,convo_id='sum')
    print(f'Summary : {response}\n')
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
            if len(value) > 2 and key.find('wolfram') == -1:
                flag = 1
                value = value[:-1]
                call_res[key] = value
            res = str(call_res)
        if flag == 0: break
    if len(res) > max_token:
        res = res[:max_token]
    return res
if __name__ == "__main__":
    response = chatbot.ask_stream(
            prompt='hello',
            role='user',
            convo_id='default',
    )