"""
A simple wrapper for the official ChatGPT API
"""
import argparse
import json
import os
import sys
import time
import requests
import tiktoken
import datetime
from queue import PriorityQueue as PQ
ENGINE = os.environ.get("GPT_ENGINE") or "gpt-3.5-turbo"
ENCODER = tiktoken.get_encoding("gpt2")
program_path = os.path.realpath(__file__)
program_dir = os.path.dirname(program_path)
apiTime = 20
class ExChatGPT:
    """
    Official ChatGPT API
    """
    def __init__(
        self,
        api_keys: list,
        engine: str = None,
        proxy: str = None,
        max_tokens: int = 3000,
        temperature: float = 0.5,
        top_p: float = 1.0,
        reply_count: int = 1,
        system_prompt: str = "You are ExChatGPT, a web-based large language model, Respond conversationally",
        lastAPICallTime = time.time()-100,
        apiTimeInterval = 20,
    ) -> None:
        """
        Initialize Chatbot with API key (from https://platform.openai.com/account/api-keys)
        """
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
        self.conversation: dict = {
            "default": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
            ],
        }
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.reply_count = reply_count

        initial_conversation = "\n".join(
            [x["content"] for x in self.conversation["default"]],
        )
        if len(ENCODER.encode(initial_conversation)) > self.max_tokens:
            raise Exception("System prompt is too long")
    def add_to_conversation(self, message: str, role: str, convo_id: str = "default"):
        """
        Add a message to the conversation
        """
        self.conversation[convo_id].append({"role": role, "content": message})

    def __truncate_conversation(self, convo_id: str = "default"):
        """
        Truncate the conversation
        """
        while True:
            full_conversation = "\n".join(
                [x["content"] for x in self.conversation[convo_id]],
            )
            if (
                len(ENCODER.encode(full_conversation)) > self.max_tokens
                and len(self.conversation[convo_id]) > 1
            ):
                # Don't remove the first message
                self.conversation[convo_id].pop(1)
            else:
                break
    def ask_stream_copy(
        self,
        prompt: str,
        role: str = "user",
        convo_id: str = "default",
        **kwargs,
    ) -> any: # type: ignore
        """
        Ask a question
        """
        # Make conversation if it doesn't exist
        if convo_id not in self.conversation:
            self.reset(convo_id=convo_id, system_prompt=self.system_prompt)
        self.add_to_conversation(prompt, "user", convo_id=convo_id)
        self.__truncate_conversation(convo_id=convo_id)
        apiKey = self.api_keys.get()
        print(time.time() - apiKey[0])
        if time.time() - apiKey[0]<self.apiTimeInterval:
            time.sleep(self.apiTimeInterval - (time.time() - apiKey[0]))
        self.api_keys.put((time.time(),apiKey[1]))
        # Get response
        response = self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {kwargs.get('api_key', apiKey[1])}"},
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
            raise Exception(
                f"Error: {response.status_code} {response.reason} {response.text}",
            )
        return response
    def ask_stream(
        self,
        prompt: str,
        role: str = "user",
        convo_id: str = "default",
        **kwargs,
    ) -> str:
        """
        Ask a question
        """
        # Make conversation if it doesn't exist
        if convo_id not in self.conversation:
            self.reset(convo_id=convo_id, system_prompt=self.system_prompt)
        self.add_to_conversation(prompt, "user", convo_id=convo_id)
        self.__truncate_conversation(convo_id=convo_id)
        apiKey = self.api_keys.get()
        print(time.time() - apiKey[0])
        if time.time() - apiKey[0]<self.apiTimeInterval:
            time.sleep(self.apiTimeInterval - (time.time() - apiKey[0]))
        self.api_keys.put((time.time(),apiKey[1]))
        # Get response
        response = self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {kwargs.get('api_key', apiKey[1])}"},
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
            raise Exception(
                f"Error: {response.status_code} {response.reason} {response.text}",
            )
        response_role: str = None
        full_response: str = ""
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
            if "role" in delta:
                response_role = delta["role"]
            if "content" in delta:
                content = delta["content"]
                full_response += content
                yield content
        self.add_to_conversation(full_response, response_role, convo_id=convo_id)
    def ask(self, prompt: str, role: str = "user", convo_id: str = "default", **kwargs):
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
        self.save(program_dir+"/chatHistory.json")
        return full_response
    def rollback(self, n: int = 1, convo_id: str = "default"):
        """
        Rollback the conversation
        """
        for _ in range(n):
            self.conversation[convo_id].pop()

    def reset(self, convo_id: str = "default", system_prompt: str = None):
        """
        Reset the conversation
        """
        self.conversation[convo_id] = [
            {"role": "system", "content": system_prompt or self.system_prompt},
        ]
    def save(self, file: str, *convo_ids: str):
        """
        Save the conversation to a JSON file
        """
        try:
            with open(file, "w", encoding="utf-8") as f:
                if convo_ids:
                    json.dump({k: self.conversation[k] for k in convo_ids}, f, indent=2)
                else:
                    json.dump(self.conversation, f, indent=2)
        except (FileNotFoundError, KeyError):
            return False
        return True
        # print(f"Error: {file} could not be created")
    def conversation_summary(self, convo_id: str = "default"):
        input = ""
        role = ""
        for conv in self.conversation[convo_id]:
            if (conv["role"]=='user'):
                role = 'User'
            else:
                role = 'ChatGpt'
            input+=role+' : '+conv['content']+'\n'
        with open(program_dir+"/conversationSummary.txt", "r", encoding='utf-8') as f:
            prompt = f.read()
        prompt = prompt.replace("{conversation}", input)
        response = self.ask(prompt)
        self.conversation[convo_id] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "Summariaze our diaglog"},
            {"role": 'assistant', "content": response},
        ]
        self.save(program_dir+"/chatHistory.json")
        return self.conversation[convo_id]
    def summarize_last_message(self, convo_id: str = "default"):
        last_message = self.conversation[convo_id][-1]["content"]
    def token_cost(self,convo_id: str = "default"):
        return len(ENCODER.encode("\n".join([x["content"] for x in self.conversation[convo_id]])))
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
        except (FileNotFoundError, KeyError, json.decoder.JSONDecodeError):
            return False
        return True

    def print_config(self, convo_id: str = "default"):
        """
        Prints the current configuration
        """
        print(
            f"""
ChatGPT Configuration:
  Messages:         {len(self.conversation[convo_id])} / {self.max_tokens}
  Engine:           {self.engine}
  Temperature:      {self.temperature}
  Top_p:            {self.top_p}
  Reply count:      {self.reply_count}
            """,
        )


    


def main():
    return





