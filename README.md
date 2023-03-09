# Ex-ChatGPT - ChatGPT with ToolFormer

![language](https://img.shields.io/badge/language-python-blue) ![GitHub](https://img.shields.io/github/license/circlestarzero/EX-chatGPT) ![GitHub last commit](https://img.shields.io/github/last-commit/circlestarzero/EX-chatGPT) ![GitHub Repo stars](https://img.shields.io/github/stars/circlestarzero/EX-chatGPT?style=social)

简体中文 [English](./README.en.md) / [Background](./BACKGROUND.md)

ChatGPT 无需调整就能自己作为toolformer, 生成问题的API请求来帮助回答。而 Ex-ChatGPT 使得 ChatGPT 能够自己调用外部 API，例如 WolframAlpha 和 Google, WikiMedia，从而给出更准确且具有时效性的回答。

本项目分为 Ex-ChatGPT 和 WebChatGPTEnhance，前者是使用 ChatGPT API 的服务，后者是浏览器插件,支持chatgpt网页调用不同api和propmts。

### ExChatGPT

![chatHistory](img/newPage.jpg)

### WebChatGPTEnhance

![WebChatGPT](img/chatGPTChromeEnhance.png)

## Highlights

- **docker 和 proxy 支持**
- **聊天记录冗余备份**
- 支持 OpenAI GPT-3.5 Turbo API
- 允许 ChatGPT 调用外部 API 接口(**Google,WolframAlpha,WikiMedia**)
- 自动保存载入对话历史，**自动压缩对话**
- **可显示使用的 Token 数量**
- **openAI api key池**
- **Markdown and MathJax** 渲染
- 调用**API过程显示动画**, 类似必应
- **历史对话管理**载入,类chatgpt页面布局
- **快捷键**快速选择模式`Tab`和换行`Shift+Enter`,`Enter`发送, `up`,`down`选择历史发送消息,类似终端
- chat模式下**prompt自动补全**选择,支持模糊搜索, 拼音搜索, 支持自定义prompt
![promptCompletion](img/promptCompletion.gif)

## 安装

### Ex-chatGPT Installation

- `pip install`
`pip install -r requirements.txt`
- 在 `apikey.ini` 中填入你的 API 密钥
  - `Google api key and search engine id` [apply](https://developers.google.com/custom-search/v1/overview?hl=en)
  - `wolframAlpha app id key` [apply](https://products.wolframalpha.com/api/)
  - `openAI api key`(新功能) 或 `chatGPT access_token`(旧版本) [apply](https://platform.openai.com)
- 运行 `main.py` 并打开 `http://127.0.0.1:1234/`
- 调整模式，例如 `chat,detail,web,webDirect,WebKeyWord`

### WebChatGPTEnhance Installation

- 在 `chatGPTChromeEhance/src/util/apiManager.ts/getDefaultAPI` 中填入 Google API 信息
- 运行 `npm install`
- 运行 `npm run build-prod`
- 在 `chatGPTChromeEhance/build` 中获取构建好的扩展
- add your `prompts` and `APIs` in option page.
  - `APIs` and `prompts` examples are in `/WebChatGPTAPI`
  - `wolframAlpha` needs to run local sever - `WebChatGPTAPI/WolframLocalServer.py`

## 模式介绍

### Web Mode

Web Mode 开始时会直接询问 ChatGPT 一个问题。ChatGPT 会生成一系列与查询相关的 API 调用，并使用第一个返回的结果和问题进行验证和补充。最后，ChatGPT 会对信息进行总结。Web Mode 具有比仅总结响应更好的聊天能力。

### Chat Mode

Chat Mode 仅调用 OpenAI API 接口，类似于 ChatGPT 的 Web 版本。您可以通过输入 `/promtname` 来搜索和选择不同的提示，它还支持模糊搜索。

### WebDirect Mode

WebDirect Mode 首先让 ChatGPT 生成一系列与查询相关的 API 调用。然后，它直接调用第三方 API 搜索每个查询的答案，最后 ChatGPT 对信息进行总结。WebDirect Mode 对于单个查询信息更快且相对更准确。

### Detail Mode

Detail Mode 是 WebDirect Mode 的扩展，它会进行额外的 API 调用来补充当前结果中未找到的信息（例如之前未搜索到的信息）。最后，ChatGPT 对信息进行总结。

### Keyword Mode

Keyword Mode 直接从 ChatGPT 中生成关键词进行查询，使用 DDG 进行查询，不需要其他 API 密钥。但是其准确性相对较差。

## 更新日志

- 聊天记录冗余备份
- chat模式下prompt自动补全选择,支持模糊搜索, 拼音搜索
![promptCompletion](img/promptCompletion.gif)
- update docker 和 proxy 支持
- 支持 OpenAI GPT-3.5 Turbo API，快速且价格低廉
- 额外的 API 调用和搜索摘要，以提供更全面和详细的答案
- 快捷键快速选择模式`Tab`和换行`Shift+Enter`,`Enter`发送`up`,`down`选择历史发送消息,类似终端
- 更新历史对话管理,支持载入删除保存历史对话
![chatHistory](img/newPage.jpg)
- update API calls processing animation
![APIAnimation](img/APIAnimation.png)
- 页面美化
![WebBeautification](img/WebPageBeautification.jpg)
- Markdown and MathJax renderer
![MathJax](img/mathjax.jpg)
- 更新聊天记录token优化器，web模式可以根据聊天记录进行响应；添加token成本计数器
![history](img/webHistory.jpg)
- upate web chatmode selection in webpage and optimize the prompt and the token cost, and restrict the token limit.
![mode](img/mode.jpg)
- update better suppoer chinese query and add current date info
![date](img/date.jpg)
- update web chatmode and fix some bugs
- update api config
- 更新api池
- 自动保存载入对话历史，ChatGPT 可联系之前对话
