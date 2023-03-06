import json
import re

from revChatGPT.V3 import Chatbot
import os
import configparser
from optimizeOpenAI import ExChatGPT

program_path = os.path.realpath(__file__)
program_dir = os.path.dirname(program_path)

# new gpt3.5 turbo api by api key
config = configparser.ConfigParser()
config.read(program_dir + '/apikey.ini')
# Access the keys in the configuration file
# OPENAI_API_KEY = config['OpenAI']['OPENAI_API_KEY']
# chatbot = Chatbot(api_key=str(OPENAI_API_KEY))
openAIAPIKeys = []
for i in range(0, 10):
    key = 'key' + str(i)

    if key in config['OpenAI']:
        openAIAPIKeys.append(config['OpenAI'][key])
    else:
        break
print(openAIAPIKeys)
chatbot = ExChatGPT(api_keys=openAIAPIKeys, apiTimeInterval=0)


def get_mode(query):
    with open(program_dir + "/evaluator_prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    prompt = prompt.replace("{query}", query)
    response = ""
    for data in chatbot.ask(prompt):
        response += data
    pattern = r'(\{[\s\S\n]*"time_sensitive"[\s\S\n]*"academic"[\s\S\n]*\})'
    match = re.search(pattern, response)
    if match:
        json_data = match.group(1)
        j = json.loads(json_data)
        print(f'时间敏感度：{j["time_sensitive"]}\t学术性：{j["academic"]}')
        if j["academic"] >= 0.8:
            return "detail"
        elif j["time_sensitive"] >= 0.5 or j["academic"] >= 0.5:
            return "web"
        else:
            return "chat"
    return "chat"
