# EX-chatGPT introduction

## update

- update OpenAI GPT3.5 Turbo offical API support, super fast and cheap.
- update extra API calls and search summarizations to give a more comprehensive and detailed answer.
- update better suppoer chinese query and add current date info
![date](img/date.jpg)
- update web chatmode and fix some bugs(below is the detailed mode)
![web](img/web.jpg)

## Background

"ChatGPT as Inherent Toolformer" means that ChatGPT has the ability to become a tool for various tasks without requiring additional adjustments.

However, ChatGPT has some limitations such as being unable to connect to the internet and difficulty solving math problems.

ToolFormer enables language models to use specific tools for different tasks. Can ChatGPT be equipped with ToolFormer's abilities?

The challenge is how to adapt ToolFormer's API generation process to ChatGPT.

Recent experiments demonstrate that given a specific prompt, ChatGPT has a natural ability to create APIs for text.

Therefore, it can be concluded that ChatGPT has inherent ToolFormer capabilities!

[Toolformer Paper](https://arxiv.org/abs/2302.04761)
the subproject WebChatGPT enchanced is based on [WebChatGPT chrome extension](https://github.com/qunash/chatgpt-advanced)

## Demo

[ExChatGPT-bilibili](https://www.bilibili.com/video/BV19Y411r7Bd/)
API call Demos:
![API](img/API.jpg)
QA Demos:
![math](img/math.jpg)
![zhihu](img/zhihuq0.jpg)
![zhihu](img/zhihuq1.jpg)
![zhihu](img/zhihuq2.jpg)
![zhihu](img/zhihuq3.jpg)

# Usage

## Ex-chatGPT
- `pip install`
`pip install -r requirements.txt`
- fill your `API keys` in `api_class.py` and `main.py`
  -  `Google api key and client id`
  -  `wolframAlpha api key`
  -  `openAI api key`
     -  use to summarize when there are too many querys
  -   `openAI api key`(new feature) or `chatGPT access_token`(old version)
     -  (3.2, OpenAI has published the `GPT-3.5 Turbo API` , you can replace it with the newsest one)
- run the `main.py` and click the local url like `http://127.0.0.1:5000/`
- if you need detailed, mode uncomment it in the `main.py`

## WebChatGPTEnhance
- fill you `Googgle api key and client id` in `chatGPTChromeEhance/src/util/apiManager.ts/getDefaultAPI`
- run `npm install`
- run `npm run build-prod`
- get the extension in `chatGPTChromeEhance/build`
- add your `prompts` and `APIs` in option page.
  - `APIs` and `prompts` examples are in `/WebChatGPTAPI`
  - `wolframAlpha` needs to run local sever - `WebChatGPTAPI/WolframLocalServer.py`