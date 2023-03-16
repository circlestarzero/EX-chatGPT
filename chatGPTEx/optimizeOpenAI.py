"""
A simple wrapper for the official ChatGPT API
"""
import json
import os
import threading
import time
import requests
import tiktoken
from typing import Generator
from queue import PriorityQueue as PQ
import configparser
import copy
import json
import os
import time
from chatSQL import *
ENGINE = os.environ.get("GPT_ENGINE") or "gpt-3.5-turbo"
ENCODER = tiktoken.get_encoding("gpt2")
program_path = os.path.realpath(__file__)
program_dir = os.path.dirname(program_path)
apiTime = 20
chatHistoryPath = program_dir+'/chatHistory.json'
hint_token_exceed = json.loads(json.dumps({"calls":[{"API":"ExChatGPT","query":"Shortening your query since exceeding token limits..."}]},ensure_ascii=False))
hint_dialog_sum = json.loads(json.dumps({"calls":[{"API":"ExChatGPT","query":"Auto summarizing our dialogs to save tokens…"}]},ensure_ascii=False))
APICallList = {}
backup_dir = program_dir+"/backup"
def append_API_call(user_id:str,hint):
    global APICallList
    if(user_id not in APICallList):
            APICallList[user_id] = []
    APICallList[user_id].append(hint)
class ExChatGPT:
    """
    Official ChatGPT API
    """
    def __init__(
        self,
        api_keys: list,
        engine = None,
        proxy = None,
        api_proxy = None,
        max_tokens: int = 3000,
        temperature: float = 0.5,
        top_p: float = 1.0,
        reply_count: int = 1,
        system_prompt = "You are ExChatGPT, a web-based large language model, Respond conversationally.Remember to specify the programming language after the first set of three backticks (```) in your code block. Additionally, wrap mathematical formulas in either $$ or $$$$.",
        lastAPICallTime = time.time()-100,
        apiTimeInterval = 20,
        maxBackup = 10,
    ) -> None:
        self.maxBackup = maxBackup
        self.system_prompt = system_prompt
        self.apiTimeInterval = apiTimeInterval
        self.engine = engine or ENGINE
        self.session = requests.Session()
        self.api_keys = PQ()
        for key in api_keys:
            self.api_keys.put((lastAPICallTime,key))
        self.proxy = proxy
        if self.proxy:
            proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }
            self.session.proxies = proxies
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.reply_count = reply_count
        self.decrease_step = 250
        self.conversation = {}
        self.new_add_conversation = {}
        if self.token_str(self.system_prompt) > self.max_tokens:
            raise Exception("System prompt is too long")
        self.lock = threading.Lock()
    


    def load_recent_history(self, user_id: str, convo_id: str = "default"):
        conn = create_connection()
        create_tables(conn)
        recent_history = get_user_recent_history(conn=conn,user_id=user_id,convo_id=convo_id,limit=100)
        if conn:
            conn.close()
        self.reset(user_id=user_id,convo_id=convo_id)
        self.conversation[user_id][convo_id] += recent_history[-10:]
    def get_api_key(self):
        with self.lock:
            apiKey = self.api_keys.get()
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

    def add_to_conversation(self, user_id: str, message: str, role: str, convo_id: str = "default"):
        if(user_id not in self.conversation or convo_id not in self.conversation[user_id]):
            self.reset(user_id=user_id,convo_id=convo_id)
        self.conversation[user_id][convo_id].append({"role": role, "content": message})

    def add_to_db_temp(self, user_id: str, message: str, role: str, convo_id: str = "default"):
        if(user_id not in self.new_add_conversation):
            self.new_add_conversation[user_id] = []
        created_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.new_add_conversation[user_id].append({"convo_id":convo_id, "role": role,"content": message,"time":created_time})
        conn = create_connection()
        insert_user_history(conn,user_id,self.new_add_conversation[user_id])
        if conn:
            conn.close()
        self.new_add_conversation[user_id] = []
        

    def __truncate_conversation(self,user_id: str, convo_id: str = "default"):
        """
        Truncate the conversation
        """
        last_dialog = self.conversation[user_id][convo_id][-1]
        query = str(last_dialog['content'])
        if(len(ENCODER.encode(str(query)))>self.max_tokens):
            query = query[:int(1.5*self.max_tokens)]
        while(len(ENCODER.encode(str(query)))>self.max_tokens):
            query = query[:self.decrease_step]
        self.conversation[user_id][convo_id] = self.conversation[user_id][convo_id][:-1]
        full_conversation = "\n".join([x["content"] for x in self.conversation[user_id][convo_id]],)
        if len(ENCODER.encode(full_conversation)) > self.max_tokens:
            self.conversation_summary(user_id,convo_id=convo_id)
        last_dialog['content'] = query
        self.conversation[user_id][convo_id].append(last_dialog)
        while True:
            full_conversation = ""
            for x in self.conversation[user_id][convo_id]:
                full_conversation = x["content"] + "\n"
            if (len(ENCODER.encode(full_conversation)) > self.max_tokens):
                self.conversation[user_id][convo_id][-1] = self.conversation[user_id][convo_id][-1][:-self.decrease_step]
            else:
                break

    def ask_stream(
        self,
        prompt: str,
        user_id: str,
        role: str = "user",
        convo_id: str = "default",
        **kwargs,
    ) -> Generator:
        if user_id not in self.conversation or convo_id not in self.conversation[user_id]:
            self.reset(user_id = user_id, convo_id=convo_id)
        self.add_to_conversation(user_id, prompt, "user", convo_id=convo_id)
        self.__truncate_conversation(user_id, convo_id=convo_id)
        apiKey = self.get_api_key()
        response = self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {kwargs.get('api_key', apiKey)}"},
            json={
                "model": self.engine,
                "messages": self.conversation[user_id][convo_id],
                "stream": True,
                # kwargs
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p),
                "n": kwargs.get("n", self.reply_count),
                "user": role,
            },
            stream=True,
        ) 
        if response.status_code != 200:
            raise Exception(
                f"Error: {response.status_code} {response.reason} {response.text}",
            )
        for line in response.iter_lines():
            if not line:
                continue
            # Remove "data: "
            line = line.decode("utf-8")[6:]
            if line == "[DONE]":
                break
            resp: dict = json.loads(line)
            choices = resp.get("choices")
            if not choices:
                continue
            delta = choices[0].get("delta")
            if not delta:
                continue
            if "content" in delta:
                content = delta["content"]
                yield content
    def ask(self,user_id: str, prompt: str, role: str = "user", convo_id: str = "default", **kwargs):
        """
        Non-streaming ask
        """
        response = self.ask_stream(
            user_id=user_id,
            prompt=prompt,
            role=role,
            convo_id=convo_id,
            **kwargs,
        )
        full_response: str = "".join(response)
        self.add_to_conversation(user_id, full_response, role, convo_id=convo_id)
        return full_response


    # def rollback(self, n: int = 1, convo_id: str = "default"):
    #     """
    #     Rollback the conversation
    #     """
    #     for _ in range(n):
    #         self.conversation[user_id][convo_id].pop()


    def reset(self,user_id: str, convo_id: str = "default", system_prompt = None):
        """
        Reset the conversation
        """
        if user_id not in self.conversation:
            self.conversation[user_id] = {}
        self.conversation[user_id][convo_id] = [
            {"role": "system", "content": str(system_prompt or self.system_prompt)},
        ]



    def conversation_summary(self, user_id: str,  convo_id: str = "default"):
        append_API_call(user_id, hint_dialog_sum)
        input = ""
        role = ""
        for conv in self.conversation[user_id][convo_id]:
            if (conv["role"]=='user'):
                role = 'User'
            else:
                role = 'ChatGpt'
            input+=role+' : '+conv['content']+'\n'
        with open(program_dir+"/prompts/conversationSummary.txt", "r", encoding='utf-8') as f:
            prompt = f.read()
        if(self.token_str(str(input)+prompt)>self.max_tokens):
            input = input[self.token_str(str(input))-self.max_tokens:]
        while self.token_str(str(input)+prompt)>self.max_tokens:
            input = input[self.decrease_step:]
        prompt = prompt.replace("{conversation}", input)
        self.reset(user_id,convo_id='conversationSummary')
        response = self.ask(user_id,prompt,convo_id='conversationSummary')
        while self.token_str(str(response))>self.max_tokens:
            response = response[:-self.decrease_step]
        self.reset(user_id,convo_id='conversationSummary',system_prompt='Summariaze our diaglog')
        self.conversation[user_id][convo_id] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "Summariaze our diaglog"},
            {"role": 'assistant', "content": response},
        ]
        return self.conversation[user_id][convo_id]


    def delete_last2_conversation(self, user_id:str, convo_id: str = "default"):
        if len(self.conversation[user_id][convo_id]) > 0:
            self.conversation[user_id][convo_id].pop()
        if len(self.conversation[user_id][convo_id]) > 0:
            self.conversation[user_id][convo_id].pop()

    def token_cost(self,user_id:str,convo_id: str = "default"):
        return len(ENCODER.encode("\n".join([x["content"] for x in self.conversation[user_id][convo_id]])))
 

    def token_str(self,content:str):
        return len(ENCODER.encode(content))


def main():
    return
