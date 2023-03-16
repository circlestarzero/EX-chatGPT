import json
import datetime
import os
from promptsSearch import SearchPrompt,promptsDict
from markdown_it import MarkdownIt
from flask import Flask, render_template, request,  Response
from search import directQuery,web,detail,webDirect,WebKeyWord,load_history,APICallList,directQuery_stream,chatbot
from graiax.text2img.playwright.plugins.code.highlighter import Highlighter
from graiax.text2img.playwright import MarkdownConverter
import configparser
program_path = os.path.realpath(__file__)
program_dir = os.path.dirname(program_path)
config = configparser.ConfigParser()
config.read(program_dir+'/apikey.ini')
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
        promptName = str(request.args.get('prompt'))
        print(promptName)
        if promptName != "":
            if promptName in promptsDict:
                prompt = promptsDict[promptName]
            else:
                prompt = str(SearchPrompt(promptName)[0])
                prompt = promptsDict[prompt]
            return Response(directQuery_stream(q,conv_id=uuid,prompt=prompt), direct_passthrough=True, mimetype='application/octet-stream')
        else:
            return Response(directQuery_stream(q,conv_id=uuid), direct_passthrough=True, mimetype='application/octet-stream')
    elif mode == "web":
        q = 'current Time: '+ str(now) + '\n\nQuery:'+ str(userText)
        return  Response(web(q,conv_id=uuid), direct_passthrough=True, mimetype='application/octet-stream')
    elif mode == "detail":
        q = 'current Time: '+ str(now) + '\n\nQuery:'+ str(userText)
        return Response(detail(q,conv_id=uuid), direct_passthrough=True, mimetype='application/octet-stream')
    elif mode =='webDirect':
        q = 'current Time: '+ str(now) + '\n\nQuery:'+ str(userText)
        return Response(webDirect(q,conv_id=uuid), direct_passthrough=True, mimetype='application/octet-stream')
    elif mode == 'WebKeyWord':
        q = str(userText)
        return Response(WebKeyWord(q,conv_id=uuid), direct_passthrough=True, mimetype='application/octet-stream')
    return "Error"

@app.route("/api/addChat",methods=['POST'])
def add_chat():
    uuid = str(request.form.get('uuid'))
    message = str(request.form.get('msg'))
    chatbot.add_to_conversation(message,role='assistant',convo_id=str(uuid))
    return parse_text(message+"\n\ntoken cost:"+str(chatbot.token_cost(convo_id=uuid))) 
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
    chats  = load_history(conv_id=uuid)
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
        elif chat['role']=='assistant':
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
    
@app.route('/api/promptsCompletion',methods=['get'])
def promptsCompletion():
    prompt = str(request.args.get('prompt'))
    res = json.dumps(SearchPrompt(prompt),ensure_ascii=False)
    return res

subscriptionKey = None
region = None
if 'Azure' in config:
    if 'subscriptionKey' in config['Azure']:
        subscriptionKey = config['Azure']['subscriptionKey']
    if 'region' in config['Azure']:
        region = config['Azure']['region']
@app.route('/api/getAzureAPIKey',methods=['GET'])
def AzureAPIKey():
    return json.dumps({'subscriptionKey':subscriptionKey, 'region':region},ensure_ascii=False)

if __name__ == "__main__":
    app.config['JSON_AS_ASCII'] = False
    app.config['DEBUG'] = True
    #local config uncomment this line
    app.run(host="127.0.0.1",port=1234)
    #docker config uncomment this line
    # app.run(host="0.0.0.0", port = 5000)
