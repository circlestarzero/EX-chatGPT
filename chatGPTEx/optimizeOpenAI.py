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

ENGINE = os.environ.get("GPT_ENGINE") or "gpt-3.5-turbo"
ENCODER = tiktoken.get_encoding("gpt2")
program_path = os.path.realpath(__file__)
program_dir = os.path.dirname(program_path)
apiTime = 20
chatHistoryPath = program_dir + '/chatHistory.json'
hint_token_exceed = json.loads(
    json.dumps(
        {
            "calls": [{
                "API":
                "ExChatGPT",
                "query":
                "Shortening your query since exceeding token limits..."
            }]
        },
        ensure_ascii=False))
hint_dialog_sum = json.loads(
    json.dumps(
        {
            "calls": [{
                "API": "ExChatGPT",
                "query": "Auto summarizing our dialogs to save tokens…"
            }]
        },
        ensure_ascii=False))
APICallList = []
backup_dir = program_dir + "/backup"


class ExChatGPT:
    """
    Official ChatGPT API
    """

    def __init__(
        self,
        api_keys: list,
        engine=None,
        proxy=None,
        api_proxy=None,
        max_tokens: int = 3000,
        temperature: float = 0.5,
        top_p: float = 1.0,
        reply_count: int = 1,
        system_prompt="You are ExChatGPT, a web-based large language model, Respond conversationally.Remember to specify the programming language after the first set of three backticks (```) in your code block. Additionally, wrap mathematical formulas in either $$ or $$$$.",
        lastAPICallTime=time.time() - 100,
        apiTimeInterval=20,
        maxBackup=10,
    ) -> None:
        self.maxBackup = maxBackup
        self.system_prompt = system_prompt
        self.apiTimeInterval = apiTimeInterval
        self.engine = engine or ENGINE
        self.session = requests.Session()
        self.api_keys = PQ()
        self.trash_api_keys = PQ()
        for key in api_keys:
            self.api_keys.put((lastAPICallTime, key))
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
        self.convo_history = {}
        if self.token_str(self.system_prompt) > self.max_tokens:
            raise Exception("System prompt is too long")
        self.load_chat_history()
        self.lock = threading.Lock()

    def get_api_key(self):
        with self.lock:
            while (self.trash_api_keys.qsize() and self.api_keys.qsize()):
                trash_key = self.trash_api_keys.get()
                apiKey = self.api_keys.get()
                if (trash_key[1] == apiKey[1]):
                    self.api_keys.put((time.time() + 24 * 3600, apiKey[1]))
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

    def backup_chat_history(self):
        if not os.path.exists(backup_dir):
            os.mkdir(backup_dir)
        backup_filename = "chathistory_backup_" + time.strftime(
            "%Y%m%d-%H%M") + ".json"
        backup_filepath = os.path.join(backup_dir, backup_filename)
        with open(backup_filepath, "w", encoding="utf-8") as f:
            json.dump(self.convo_history, f, ensure_ascii=False, indent=4)
        print("Chat history backup completed:", backup_filename)

    def load_chat_history(self):
        if not os.path.exists(backup_dir):
            os.mkdir(backup_dir)
        backup_files = sorted(
            os.listdir(backup_dir),
            key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)),
            reverse=True)
        if (len(backup_files) > self.maxBackup):
            for outDatedFile in backup_files[self.maxBackup + 1:]:
                os.remove(os.path.join(backup_dir, outDatedFile))
        for backup_file in backup_files:
            latest_backup_file = backup_file
            backup_filepath = os.path.join(backup_dir, latest_backup_file)
            if self.load(backup_filepath):
                break
            print(
                f"Chat history: {backup_filepath} can't be loaded, try next one"
            )
            os.remove(backup_filepath)
        if self.convo_history == {}:
            self.reset('default')
            self.backup_chat_history()

    def add_to_conversation(self,
                            message: str,
                            role: str,
                            convo_id: str = "default"):
        if (convo_id not in self.conversation):
            self.reset(convo_id)
        self.conversation[convo_id].append({"role": role, "content": message})
        self.convo_history[convo_id].append({"role": role, "content": message})

        self.backup_chat_history()

    def __truncate_conversation(self, convo_id: str = "default"):
        """
        Truncate the conversation
        """
        last_dialog = self.conversation[convo_id][-1]
        query = str(last_dialog['content'])
        if (len(ENCODER.encode(str(query))) > self.max_tokens):
            query = query[:int(1.5 * self.max_tokens)]
        while (len(ENCODER.encode(str(query))) > self.max_tokens):
            query = query[:self.decrease_step]
        self.conversation[convo_id] = self.conversation[convo_id][:-1]
        self.convo_history[convo_id] = self.convo_history[convo_id][:-1]
        full_conversation = "\n".join(
            [x["content"] for x in self.conversation[convo_id]], )
        if len(ENCODER.encode(full_conversation)) > self.max_tokens:
            self.conversation_summary(convo_id=convo_id)
        full_conversation = ""
        for x in self.conversation[convo_id]:
            full_conversation = x["content"] + "\n"
        while True:
            if (len(ENCODER.encode(full_conversation + query)) >
                    self.max_tokens):
                query = query[:-self.decrease_step]
            else:
                break
        last_dialog['content'] = query
        self.conversation[convo_id].append(last_dialog)
        self.convo_history[convo_id].append(last_dialog)

    def ask_stream(
        self,
        prompt: str,
        role: str = "user",
        convo_id: str = "default",
        **kwargs,
    ) -> Generator:
        if convo_id not in self.conversation:
            self.reset(convo_id=convo_id)
        self.add_to_conversation(prompt, "user", convo_id=convo_id)
        self.__truncate_conversation(convo_id=convo_id)
        apiKey = self.get_api_key()
        response = self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {kwargs.get('api_key', apiKey)}"
            },
            json={
                "model": self.engine,
                "messages": self.conversation[convo_id],
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
            if response.status_code == 403:  # API key error
                self.trash_api_keys.put((time.time(), apiKey))
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

    def ask(self,
            prompt: str,
            role: str = "user",
            convo_id: str = "default",
            **kwargs):
        """
        Non-streaming ask
        """
        response = self.ask_stream(
            prompt=prompt,
            role=role,
            convo_id=convo_id,
            **kwargs,
        )
        full_response: str = "".join(response)
        self.add_to_conversation(full_response, role, convo_id=convo_id)
        return full_response

    def rollback(self, n: int = 1, convo_id: str = "default"):
        """
        Rollback the conversation
        """
        for _ in range(n):
            self.conversation[convo_id].pop()

    def reset(self, convo_id: str = "default", system_prompt=None):
        """
        Reset the conversation
        """
        self.conversation[convo_id] = [
            {
                "role": "system",
                "content": str(system_prompt or self.system_prompt)
            },
        ]
        self.convo_history[convo_id] = [{
            "role":
            "system",
            "content":
            str(system_prompt or self.system_prompt)
        }]

    def save(self, file: str, *convo_ids: str):
        try:
            with open(file, "w", encoding="utf-8") as f:
                if convo_ids:
                    json.dump({k: self.convo_history[k]
                               for k in convo_ids},
                              f,
                              indent=2)
                else:
                    json.dump(self.convo_history,
                              f,
                              indent=2,
                              ensure_ascii=False)
        except (FileNotFoundError, KeyError):
            return False
        return True
        # print(f"Error: {file} could not be created")

    def conversation_summary(self, convo_id: str = "default"):
        global APICallList
        APICallList.append(hint_dialog_sum)
        input = ""
        role = ""
        for conv in self.conversation[convo_id]:
            if (conv["role"] == 'user'):
                role = 'User'
            else:
                role = 'ChatGpt'
            input += role + ' : ' + conv['content'] + '\n'
        with open(program_dir + "/prompts/conversationSummary.txt",
                  "r",
                  encoding='utf-8') as f:
            prompt = f.read()
        if (self.token_str(str(input) + prompt) > self.max_tokens):
            input = input[self.token_str(str(input)) - self.max_tokens:]
        while self.token_str(str(input) + prompt) > self.max_tokens:
            input = input[self.decrease_step:]
        prompt = prompt.replace("{conversation}", input)
        self.reset(convo_id='conversationSummary')
        response = self.ask(prompt, convo_id='conversationSummary')
        while self.token_str(str(response)) > self.max_tokens:
            response = response[:-self.decrease_step]
        self.reset(convo_id='conversationSummary',
                   system_prompt='Summariaze our diaglog')
        self.conversation[convo_id] = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": "Summariaze our diaglog"
            },
            {
                "role": 'assistant',
                "content": response
            },
        ]
        return self.conversation[convo_id]

    def delete_last2_conversation(self, convo_id: str = "default"):
        if len(self.conversation[convo_id]) > 0:
            self.conversation[convo_id].pop()
        if len(self.conversation[convo_id]) > 0:
            self.conversation[convo_id].pop()
        if len(self.convo_history[convo_id]) > 0:
            self.convo_history[convo_id].pop()
        if len(self.convo_history[convo_id]) > 0:
            self.convo_history[convo_id].pop()
        self.backup_chat_history()

    def summarize_last_message(self, convo_id: str = "default"):
        last_message = self.conversation[convo_id][-1]["content"]

    def token_cost(self, convo_id: str = "default"):
        return len(
            ENCODER.encode("\n".join(
                [x["content"] for x in self.conversation[convo_id]])))

    def token_str(self, content: str):
        return len(ENCODER.encode(content))

    def load(self, file: str, *convo_ids: str):
        """
        Load the conversation from a JSON  file
        """
        try:
            with open(file, encoding="utf-8") as f:
                if convo_ids:
                    convos = json.load(f)
                    self.conversation.update({k: convos[k] for k in convo_ids})
                else:
                    self.conversation = json.load(f)
                self.convo_history = copy.deepcopy(self.conversation)
        except (FileNotFoundError, KeyError, json.decoder.JSONDecodeError):
            return False
        return True


def main():
    return
