from api_class import GoogleSearchAPI, WikiSearchAPI, WolframAPI
from optimizeOpenAI import ExChatGPT,append_API_call
import threading 
import json
import re
import configparser
import os
import requests
program_path = os.path.realpath(__file__)
program_dir = os.path.dirname(program_path)
config_path = os.path.join(program_dir, 'apikey.ini')
config = configparser.ConfigParser()
config.read(program_dir+'/apikey.ini')
if not os.path.exists(config_path):
    print("Config file doesn't exist!")
    exit()
config.read(config_path)
if not config.has_section('OpenAI'):
    print("OpenAI section doesn't exist in config file!")
    exit()
API_PROXY = None
if 'Proxy' in config and 'api_proxy' in config['Proxy']:
    API_PROXY = config['Proxy']['api_proxy']
    if(API_PROXY == ''):
        API_PROXY = None
openAIAPIKeys = []
try:
    items = config.items('OpenAI')
    for key, value in items:
        if key.startswith('key'):
            openAIAPIKeys.append(value)
except configparser.Error as e:
    print(f"Error reading config file: {str(e)}")
    exit()
chatbot = ExChatGPT(api_keys=openAIAPIKeys,apiTimeInterval=20,proxy=API_PROXY)
googleAPIKeys = []
SEARCH_ENGINE_IDs = []
try:
    items = config.items('Google')
    for key, value in items:
        if key.startswith('google_api_key'):
            googleAPIKeys.append(value)
        if key.startswith('search_engine_id'):
            SEARCH_ENGINE_IDs.append(value)
    for i in range(min(len(googleAPIKeys),len(SEARCH_ENGINE_IDs))):
        googleAPIKeys[i] = (googleAPIKeys[i],SEARCH_ENGINE_IDs[i])
    Google = GoogleSearchAPI(googleAPIKeys,proxy=API_PROXY)
except configparser.Error as e:
    print(f"Error reading config file: {str(e)}")

WolframAPIKeys = []
try:
    items = config.items('WolframAlpha')
    for key, value in items:
        if key.startswith('wolframalpha_app_id'):
            WolframAPIKeys.append(value)
    Wolfram = WolframAPI(WolframAPIKeys,proxy=API_PROXY)
except configparser.Error as e:
    print(f"Error reading config file: {str(e)}")
Wiki = WikiSearchAPI([],proxy=API_PROXY)
max_token = 1000
hint_recall_dialog = json.loads(json.dumps({"calls":[{"API":"ExChatGPT","query":"Recall our dialogs…"}]},ensure_ascii=False))
hint_api_finished = json.loads(json.dumps({"calls":[{"API":"System","query":"API calls finished"}]},ensure_ascii=False))



def load_history(user_id: str,conv_id = 'default'):
    chatbot.load_recent_history(user_id,conv_id)
    history = []
    for conv in chatbot.conversation[user_id][conv_id]:
        if conv['role'] == 'system':
            continue
        history.append(conv)
    return history
def detail_old(user_id:str,query):
    call_res0 = search(APIQuery(user_id,query))
    Sum0 = Summary(user_id,query, call_res0)
    call_res1 = search(APIExtraQuery(user_id,query,Sum0))
    Sum1 = Summary(user_id,query, call_res1)
    print('\n\nChatGpt: \n' )
    result  = SumReply(user_id,query, str(Sum0) + str(Sum1))
    return result
def detail(user_id:str,query,conv_id = 'default'):
    chatbot.add_to_db_temp(user_id, str(query), "user", convo_id=conv_id)
    append_API_call(user_id,hint_recall_dialog)
    call_res0 = search(APIQuery(user_id,query),1000)
    print(f'API calls response:\n {call_res0}')
    call_res1 = search(APIExtraQuery(user_id,query,call_res0),1000)
    print(f'API calls response:\n {call_res1}')
    result  = SumReply(user_id,query, str(call_res0) + str(call_res1),max_token=2000,conv_id=conv_id)
    for data in result:
        yield data.encode()
    chatbot.add_to_conversation(user_id,'', "assistant", convo_id=conv_id)
    chatbot.delete_last2_conversation(user_id,conv_id)
    chatbot.add_to_conversation(user_id,str(query), "user", convo_id=conv_id)
    
def web(user_id:str,query,conv_id = 'default'):
    chatbot.add_to_db_temp(user_id, str(query), "user", convo_id=conv_id)
    append_API_call(user_id,hint_recall_dialog)
    resp = directQuery(user_id,f'Query: {query}', conv_id=  conv_id)
    chatbot.delete_last2_conversation(user_id,conv_id)
    apir = APIQuery(user_id,query,resp=resp)
    call_res0 = search(apir,1600)
    append_API_call(user_id,hint_api_finished)
    print(f'API calls response:\n {call_res0}')
    result = SumReply(user_id,f'Query: {query}' ,str(call_res0),max_token=2000, conv_id=conv_id)
    for data in result:
        yield data.encode()
    chatbot.add_to_conversation(user_id,'', "assistant", convo_id=conv_id)
    chatbot.delete_last2_conversation(user_id,conv_id)
    chatbot.add_to_conversation(user_id,str(query), "user", convo_id=conv_id)
    
def webDirect(user_id:str,query,conv_id = 'default'):
    chatbot.add_to_db_temp(user_id, str(query), "user", convo_id=conv_id)
    apir = APIQuery(user_id,query)
    call_res0 = search(apir,1600)
    append_API_call(user_id,hint_api_finished)
    print(f'API calls response:\n {call_res0}')
    result = SumReply(user_id,f'{query}', str(call_res0), conv_id=conv_id)
    for data in result:
        yield data.encode()
    chatbot.add_to_conversation(user_id,'', "assistant", convo_id=conv_id)
    chatbot.delete_last2_conversation(user_id,conv_id)
    chatbot.add_to_conversation(user_id,str(query), "user", convo_id=conv_id)
    
def WebKeyWord(user_id:str,query,conv_id = 'default'):
    chatbot.add_to_db_temp(user_id, str(query), "user", convo_id=conv_id)
    q = chatbot.ask(
                user_id,
                f'Given a user prompt "{query}", respond with "none" if it is directed at the chatbot or cannot be answered by an internet search. Otherwise, provide a concise search query for a search engine. Avoid adding any additional text to the response to minimize token cost.',
                convo_id="search",
                temperature=0.0,
            ).strip()
    print("Searching for: ", q, "")
    if q == "none":
        search_results = '{"results": "No search results"}'
    else:
        append_API_call(user_id,json.loads(json.dumps({"calls":[{"API":"ddg-api","query": "Searching for:" + q }]})))
        search_results = requests.post(
            url="https://ddg-api.herokuapp.com/search",
            json={"query": q, "limit": 4},
            timeout=10,
        ).text
    search_res = json.dumps(json.loads(search_results), indent=4,ensure_ascii=False)
    chatbot.add_to_conversation(
        user_id,
        "Search results:" + search_res,
        "system",
        convo_id=conv_id,
    )
    append_API_call(user_id,hint_answer_generating)
    result = chatbot.ask_stream(prompt = query,user_id = user_id,role = "user", convo_id=conv_id)
    for data in result:
        yield data.encode()
    chatbot.add_to_conversation(user_id,'', "assistant", convo_id=conv_id)
    chatbot.delete_last2_conversation(user_id,conv_id)
    chatbot.add_to_conversation(user_id,str(query), "user", convo_id=conv_id)
def directQuery(user_id:str, query,conv_id = 'default',prompt = ''):
    append_API_call(user_id,hint_answer_generating)
    response = chatbot.ask(user_id,prompt+'\n'+query,convo_id=conv_id)
    chatbot.delete_last2_conversation(user_id,conv_id)
    chatbot.add_to_conversation(user_id, str(query), "user", convo_id=conv_id)
    chatbot.add_to_conversation(user_id, str(response), "assistant", convo_id=conv_id)
    print(f'Direct Query: {query}\nChatGpt: {response}')
    return response+ '\n\n token_cost: '+ str(chatbot.token_cost(user_id))
def directQuery_stream(user_id: str, query,conv_id = 'default',prompt = ''):
    append_API_call(user_id,hint_answer_generating)
    chatbot.add_to_db_temp(user_id, str(query), "user", convo_id=conv_id)
    if(prompt!=''):
        chatbot.add_to_conversation(user_id = user_id ,message = prompt, role="system", convo_id=conv_id)
    response = chatbot.ask_stream(user_id = user_id ,prompt= prompt+'\n'+query,convo_id=conv_id)
    for data in response:
        yield data.encode()
    chatbot.add_to_conversation(user_id,'TEST!', "assistant", convo_id=conv_id)
    chatbot.delete_last2_conversation(user_id,conv_id)
    chatbot.add_to_conversation(user_id,str(query), "user", convo_id=conv_id)
    print(f'Direct Query: {query}\nChatGpt: {response}')
def APIQuery(user_id:str,query,resp =''):
    with open(program_dir+"/prompts/APIPrompt.txt", "r", encoding='utf-8') as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{resp}", resp)
    response = ""
    chatbot.reset(user_id = user_id,convo_id='api',system_prompt='Your are a API caller for a LLM, you need to call some APIs to get the information you need.')
    response =  chatbot.ask(user_id = user_id,prompt = prompt,convo_id='api')
    pattern = r"(\{[\s\S\n]*\"calls\"[\s\S\n]*\})"
    match = re.search(pattern, response)
    if match:
        json_data = match.group(1)
        result = json.loads(json_data)
        print(f'API calls: {result}\n')
        append_API_call(user_id, result)
        return result
    return json.loads("{\"calls\":[]}")
def APIExtraQuery(user_id:str , query, callResponse):
    with open(program_dir+"/prompts/APIExtraPrompt.txt", "r",encoding='utf-8') as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{callResponse}", str(callResponse))
    chatbot.reset(user_id = user_id, convo_id='api',system_prompt='Your are a API caller for a LLM, you need to call some APIs to get the information you need.')
    response = chatbot.ask(user_id = user_id, prompt = prompt,convo_id='api')
    pattern = r"(\{[\s\S\n]*\"calls\"[\s\S\n]*\})"
    match = re.search(pattern, response)
    if match:
        json_data = match.group(1)
        result = json.loads(json_data)
        append_API_call(user_id, result)
        print(f'API calls: {result}\n')
        return result
    return json.loads("{\"calls\":[]}")
hint_answer_generating = json.loads(json.dumps({"calls":[{"API":"ExChatGPT","query":"Generating answers for you…"}]}))
def SumReply(user_id:str,query, apicalls, max_token=2000, conv_id = 'default'):
    append_API_call(user_id, hint_answer_generating)
    with open(program_dir+"/prompts/ReplySum.txt", "r",encoding='utf-8') as f:
        prompt = f.read()
    apicalls = str(apicalls)
    while(chatbot.token_str(apicalls) > max_token):
        apicalls = apicalls[:-100]
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{apicalls}", apicalls)
    response = chatbot.ask_stream(user_id = user_id, prompt = prompt,convo_id=conv_id)
    for data in response:
        yield data
    print(f'ChatGPT SumReply:\n  {response}\n')
def Summary(user_id:str,query, callResponse):
    with open(program_dir+"/prompts/summary.txt", "r",encoding='utf-8') as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    prompt = prompt.replace("{callResponse}", callResponse)
    chatbot.reset(user_id,convo_id='sum',system_prompt='Your need to summarize the information you got from the APIs.')
    response = chatbot.ask_stream(user_id = user_id,prompt = prompt,convo_id='sum')
    print(f'Summary : {response}\n')
    return response
def search(content,max_token=2000,max_query=5):
    call_list = content['calls']
    # global search_data
    global call_res
    call_res = {}
    def google_search(query, num_results=4,summarzie = False):
        search_data = Google.call(query, num_results=num_results)
        if summarzie:
            summary_data = search_data
            call_res['google/' + query] = summary_data
        else:
            call_res['google/' + query] = search_data
    def wiki_search(query, num_results=3,summarzie = False):
        search_data = Wiki.call(query, num_results=num_results)
        if summarzie:
            summary_data = search_data
            call_res['wiki/' + query] = summary_data
        else:
            call_res['wiki/' + query] = search_data
        call_res['wiki/' + query] = search_data
    def wolfram_search(query, num_results=3):
        search_data = Wolfram.call(query, num_results)
        call_res['wolfram/' + query] = search_data
    all_threads = []
    for call in call_list[:max_query]:
        q = call['query']
        api = call['API']
        if api.lower() == 'google':
            t = threading.Thread(target=google_search, args=[q, 4, False])
        elif api.lower() == 'wikisearch':
            t = threading.Thread(target=wiki_search, args=[q, 1, False])
        elif api.lower() == 'calculator':
            t = threading.Thread(target=wolfram_search, args=[q])
        else:
            continue
        all_threads.append(t)
    for t in all_threads:
        t.start()
    for t in all_threads:
        t.join()
    call_res = {key: value for key, value in call_res.items() if len(str(value)) >= 10}
    call_res = json.loads(json.dumps(call_res,ensure_ascii=False))
    res = str(call_res)
    while chatbot.token_str(res) > max_token:
        flag = 0
        for key,value in call_res.items():
            if chatbot.token_str(res) <= max_token: break
            if len(value) > 2 and key.find('wolfram') == -1:
                flag = 1
                value = value[:-1]
                call_res[key] = value
            res = str(call_res)
        if flag == 0: break
    while chatbot.token_str(res) > max_token:
        res = res[:-100]
    return res
if __name__ == "__main__":
    print(Google.call('狂飙电视剧', num_results=10))