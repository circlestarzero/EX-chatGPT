# Ex-ChatGPT - ChatGPT with ToolFormer

![language](https://img.shields.io/badge/language-python-blue) ![GitHub](https://img.shields.io/github/license/circlestarzero/EX-chatGPT) ![GitHub last commit](https://img.shields.io/github/last-commit/circlestarzero/EX-chatGPT) ![GitHub Repo stars](https://img.shields.io/github/stars/circlestarzero/EX-chatGPT?style=social)

[简体中文](./README.md) English / [Background](./BACKGROUND.md)

ChatGPT has the ability to become a tool for various tasks without requiring additional adjustments. And Ex-ChatGPT allows ChatGPT to call external APIs, e.g. WolframAlpha & Bing, to give more precise & time-sensitive answers.

This repository contains Ex-ChatGPT, which is a chatting service that uses ChatGPT API, and WebChatGPTEnhance, which is a browser extension.

## Highlights

- Supports OpenAI GPT-3.5 Turbo API
- Allows ChatGPT to call external APIs(Google,WolframAlpha,WikiMedia)
- Can summerize contents from external APIs using GPT-3
- openAI API keys pool
- Markdown and MathJax renderer
## Installation

## Ex-chatGPT

- `pip install`
`pip install -r requirements.txt`
- fill your `API keys` in `apikey.ini`
  - `Google api key and search engine id` [apply](https://developers.google.com/custom-search/v1/overview?hl=en)
  - `wolframAlpha app id key` [apply](https://products.wolframalpha.com/api/)
  - `openAI api key`(new feature) or `chatGPT access_token`(old version) [apply](https://platform.openai.com)
- run the `main.py` and click the local url like `http://127.0.0.1:5000/`
- change the mode in the selection box, now have `chat,detail,web,webDirect,WebKeyWord`

## WebChatGPTEnhance

- fill you `Googgle api key and client id` in `chatGPTChromeEhance/src/util/apiManager.ts/getDefaultAPI`
- run `npm install`
- run `npm run build-prod`
- get the extension in `chatGPTChromeEhance/build`
- add your `prompts` and `APIs` in option page.
  - `APIs` and `prompts` examples are in `/WebChatGPTAPI`
  - `wolframAlpha` needs to run local sever - `WebChatGPTAPI/WolframLocalServer.py`

## Update Log

- update OpenAI GPT3.5 Turbo offical API support, super fast and cheap.
- update extra API calls and search summarizations to give a more comprehensive and detailed answer.
- update Markdown and MathJax renderer
![MathJax](img/mathjax.jpg)
- update chat history token optimizer, and the web mode can response according to the chat history.Add token cost counter.
![history](img/webHistory.jpg)
- upate web chatmode selection in webpage and optimize the prompt and the token cost, and restrict the token limit.
![mode](img/mode.jpg)
- update better suppoer chinese query and add current date info
![date](img/date.jpg)
- update web chatmode and fix some bugs
- update api config
- update api pool
- Automatic saving and loading of conversation history, ChatGPT can retrieve previous conversations.
  