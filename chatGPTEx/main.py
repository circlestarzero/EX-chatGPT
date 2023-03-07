import json
import datetime
from flask import Flask, render_template, request
from search import directQuery,web,detail,webDirect,WebKeyWord,load_history,APICallList
from markdown_it import MarkdownIt
from graiax.text2img.playwright.plugins.code.highlighter import Highlighter
from graiax.text2img.playwright import MarkdownConverter
def parse_text(text):
    md = MarkdownIt("commonmark", {"highlight": Highlighter()}).enable("table")
    res = MarkdownConverter(md).convert(text)
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
    now = now.strftime("%Y-%m-%d %H:%M")
    if mode=="chat":
        q = str(userText)
        res = parse_text(directQuery(q))
        return res
    elif mode == "web":
        q = 'current Time: '+ str(now) + '\n\nQuery:'+ str(userText)
        res = parse_text(web(q))
        return res
    elif mode == "detail":
        q = 'current Time: '+ str(now) + '\n\nQuery:'+ str(userText)
        res = parse_text(detail(q))
        return res
    elif mode =='webDirect':
        q = 'current Time: '+ str(now) + '\n\nQuery:'+ str(userText)
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
lastAPICallListLength = len(APICallList)
@app.route("/APIProcess")
def APIProcess():
    global lastAPICallListLength
    if len(APICallList) > lastAPICallListLength:
        lastAPICallListLength +=1
        print('233:'+json.dumps(APICallList[lastAPICallListLength-1],ensure_ascii=False))
        return json.dumps(APICallList[lastAPICallListLength-1],ensure_ascii=False)
    else:
        return {}
if __name__ == "__main__":
    app.config['JSON_AS_ASCII'] = False
    app.config['DEBUG'] = True
    app.run(port = 1234)