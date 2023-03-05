import json
import random
import datetime
import time
from flask import Flask, render_template, request,render_template_string
from search import search,APIQuery,APIExtraQuery,Summary,SumReply,directQuery,web,detail,webDirect,WebKeyWord,load_history
# Load the configuration file
def parse_text(text):
    lines = text.split("\n")
    for i,line in enumerate(lines):
        if "```" in line:
            items = line.split('`')
            if items[-1]:
                lines[i] = f'<pre><code class="{items[-1]}">'
            else:
                lines[i] = f'</code></pre>'
        else:
            if i>0:
                line = line.replace("<", "&lt;")
                line = line.replace(">", "&gt;")
                lines[i] = '<br/>'+line.replace(" ", "&nbsp;")
    return "".join(lines)


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
    app.run()