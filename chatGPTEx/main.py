import json
import datetime
from flask import Flask, render_template, request
from search import directQuery,web,detail,webDirect,WebKeyWord,load_history,APICallList
from markdown_it import MarkdownIt
from graiax.text2img.playwright.plugins.code.highlighter import Highlighter
from graiax.text2img.playwright import MarkdownConverter
import os


program_path = os.path.realpath(__file__)
program_dir = os.path.dirname(program_path)


def parse_text(text):
    md = MarkdownIt("commonmark", {"highlight": Highlighter()}).enable("table")
    res = MarkdownConverter(md).convert(text)
    return res
app = Flask(__name__)
app.static_folder = 'static'


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/query")
def get_bot_response():
    mode = str(request.args.get('mode'))
    userText = str(request.args.get('msg'))
    uuid = str(request.args.get('uuid'))
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M")
    if mode=="chat":
        q = str(userText)
        res = parse_text(directQuery(q,conv_id=uuid))
        return res
    elif mode == "web":
        q = 'current Time: '+ str(now) + '\n\nQuery:'+ str(userText)
        res = parse_text(web(q,conv_id=uuid))
        return res
    elif mode == "detail":
        q = 'current Time: '+ str(now) + '\n\nQuery:'+ str(userText)
        res = parse_text(detail(q,conv_id=uuid))
        return res
    elif mode =='webDirect':
        q = 'current Time: '+ str(now) + '\n\nQuery:'+ str(userText)
        res = parse_text(webDirect(q,conv_id=uuid))
        return res
    elif mode == 'WebKeyWord':
        q = str(userText)
        res = parse_text(WebKeyWord(q,conv_id=uuid))
        return res
    return "Error"


@app.route("/api/chatLists")
def get_chat_lists():
    if os.path.isfile(program_dir+'/chatLists.json'):
        with open(program_dir+'/chatLists.json', 'r', encoding='utf-8') as f:
            chatLists = json.load(f)
            chatLists["chatLists"] = list(reversed(chatLists["chatLists"]))
            return json.dumps(chatLists)
    else:
        with open(program_dir+'/chatLists.json', 'w', encoding='utf-8') as f:
            defaultChatLists = {
            "chatLists": [{
                    "uuid": "default",
                    "chatName": "Default"
            }]}
            json.dump(defaultChatLists,f,ensure_ascii=False)
            return json.dumps(defaultChatLists)


@app.route("/api/history")
def send_history():
    uuid = str(request.args.get('uuid'))
    msgs = []
    chats  = load_history(conv_id=uuid)[1:]
    for chat in chats:
        queryTime = ''
        firstLine = chat['content'].split('\n')[0]
        # print(firstLine)
        if firstLine.find('current Time:')!=-1:
            queryTime = firstLine.split('current Time:')[-1]
        if chat['content'].find('Query:')!=-1:
            query = chat['content'].split('Query:')[1]
            chat['content'] = query
        if chat['role']=='user':
            msgs.append({'name': 'You', 'img': 'static/styles/person.jpg', 'side': 'right', 'text': parse_text(chat['content']), 'time': queryTime})
        else:
            msgs.append({'name': 'ExChatGPT', 'img': 'static/styles/ChatGPT_logo.png', 'side': 'left', 'text': parse_text(chat['content']),'time': queryTime})
    return json.dumps(msgs,ensure_ascii=False)
lastAPICallListLength = len(APICallList)


@app.route("/api/APIProcess")
def APIProcess():
    global lastAPICallListLength
    if len(APICallList) > lastAPICallListLength:
        lastAPICallListLength +=1
        return json.dumps(APICallList[lastAPICallListLength-1],ensure_ascii=False)
    else:
        return {}


@app.route('/api/setChatLists',methods=['POST'])
def set_chat_lists():
    with open(program_dir+'/chatLists.json', 'w', encoding='utf-8') as f:
        json.dump(request.json,f,ensure_ascii=False)
        return 'ok'
if __name__ == "__main__":
    app.config['JSON_AS_ASCII'] = False
    app.config['DEBUG'] = True
    app.run(host="0.0.0.0", port = 5000)
