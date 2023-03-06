import json
import random
import datetime
import time
from flask import Flask, render_template, request,render_template_string
from search import search,APIQuery,APIExtraQuery,Summary,SumReply,directQuery,web,detail,webDirect,WebKeyWord,load_history
from markdown import markdown
from pygments.formatters import HtmlFormatter
from markdown_it import MarkdownIt
from graiax.text2img.playwright.plugins.code.highlighter import Highlighter
from graiax.text2img.playwright import HTMLRenderer, MarkdownConverter, PageOption, ScreenshotOption
from mdit_py_plugins.dollarmath.index import dollarmath_plugin
import evaluator
# Load the configuration file

def parse_text(text):
    md = MarkdownIt("commonmark", {"highlight": Highlighter()}).use(
        dollarmath_plugin,
        allow_labels=True,
        allow_space=True,
        allow_digits=True,
        double_inline=True,
    ).enable("table")
    res = MarkdownConverter(md).convert(text)
    # res = res.replace('<code', '<code class="lang-python"')
    return res
app = Flask(__name__)
app.static_folder = 'static'
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/get")
def get_bot_response():
    mode = str(request.args.get('mode'))
    userText = str(request.args.get('msg'))
    now = datetime.datetime.now()
    if mode=="auto":
        mode = evaluator.get_mode(query=str(userText))
    if mode=="chat":
        q = str(userText)
        res = parse_text(directQuery(q))
        return res
    elif mode == "web":
        q = 'current Time: '+ str(now) + '\nQuery:'+ str(userText)
        res = parse_text(web(q))
        return res
    elif mode == "detail":
        q = 'current Time: '+ str(now) + '\nQuery:'+ str(userText)
        res = parse_text(detail(q))
        return res
    elif mode =='webDirect':
        q = 'current Time: '+ str(now) + '\nQuery:'+ str(userText)
        res = parse_text(webDirect(q))
        return res
    elif mode == 'WebKeyWord':
        q = str(userText)
        res = parse_text(WebKeyWord(q))
        return res
    return "Error"
@app.route("/history")
def send_history():
    msgs = []
    chats  = load_history()[1:]
    for chat in chats:
        if chat['role']=='user':
            msgs.append({'name': 'You', 'img': 'static/styles/person.jpg', 'side': 'right', 'text': parse_text(chat['content']), 'mode': ''})
        else:
            msgs.append({'name': 'ExChatGPT', 'img': 'static/styles/ChatGPT_logo.png', 'side': 'left', 'text': parse_text(chat['content']), 'mode': ''})
    return json.dumps(msgs,ensure_ascii=False)
if __name__ == "__main__":
    app.run(port = 1234)