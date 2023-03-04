import json
import random
import datetime
import time
import evaluator
from search import search, APIQuery, APIExtraQuery, Summary, SumReply, directQuery, conversation_summary, \
    clear_conversation, load_conversation, token_cost, dump_conversation

# Load the configuration file
apiTime = 20
lastAPICallTime = time.time() - 30


def api_sleep():
    global lastAPICallTime
    if (time.time() - lastAPICallTime < apiTime):
        time.sleep(apiTime - (time.time() - lastAPICallTime))
    lastAPICallTime = time.time()


def detail_old(query):
    api_sleep()
    call_res0 = search(APIQuery(query))
    api_sleep()
    Sum0 = Summary(query, call_res0)
    api_sleep()
    call_res1 = search(APIExtraQuery(query, Sum0))
    api_sleep()
    Sum1 = Summary(query, call_res1)
    print('\n\nChatGpt: \n')
    api_sleep()
    result = SumReply(query, str(Sum0) + str(Sum1))
    return result


def detail(query):
    api_sleep()
    last_conv = dump_conversation()
    clear_conversation()
    call_res0 = search(APIQuery(query), 750)
    print(call_res0)
    api_sleep()
    clear_conversation()
    call_res1 = search(APIExtraQuery(query, call_res0), 750)
    print(call_res1)
    api_sleep()
    clear_conversation()
    result = SumReply(query, str(call_res0) + str(call_res1), max_token=1500)
    clear_conversation()
    last_conv.append({'role': 'user', 'content': query})
    last_conv.append({'role': 'assistant', 'content': result})
    load_conversation(last_conv)
    return result + '\n\n token_cost: ' + str(token_cost())


def web(query):
    last_conv = dump_conversation()
    clear_conversation()
    api_sleep()
    resp = directQuery('刚才的聊天信息:' + str(last_conv) + ' query: ' + query)
    api_sleep()
    clear_conversation()
    apir = APIQuery(query, resp=resp)
    call_res0 = search(apir, 1500)
    clear_conversation()
    api_sleep()
    result = SumReply('刚才的聊天信息:' + str(last_conv) + ' query: ' + query, str(call_res0))
    clear_conversation()
    last_conv.append({'role': 'user', 'content': query})
    last_conv.append({'role': 'assistant', 'content': result})
    load_conversation(last_conv)
    print(call_res0)
    return result + '\n\n token_cost: ' + str(token_cost())


def parse_text(text):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "```" in line:
            items = line.split('`')
            if items[-1]:
                lines[i] = f'<pre><code class="{items[-1]}">'
            else:
                lines[i] = f'</code></pre>'
        else:
            if i > 0:
                line = line.replace("<", "&lt;")
                line = line.replace(">", "&gt;")
                lines[i] = '<br/>' + line.replace(" ", "&nbsp;")
    return "".join(lines)


from flask import Flask, render_template, request

app = Flask(__name__)
app.static_folder = 'static'


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    conversation_summary()
    # print(load_conversation())
    print(dump_conversation())
    mode = str(request.args.get('mode'))
    userText = str(request.args.get('msg'))
    now = datetime.datetime.now()
    if mode == "auto":
        mode = evaluator.get_mode(userText)
    if mode == "chat":
        q = str(userText)
        api_sleep()
        res = parse_text(directQuery(q))
        return res
    elif mode == "web":
        q = 'current Time: ' + str(now) + ' Query:' + str(userText)
        res = parse_text(web(q))
        return res
    elif mode == "detail":
        q = 'current Time: ' + str(now) + ' Query:' + str(userText)
        res = parse_text(detail(q))
        return res
    return "Error"


if __name__ == "__main__":
    app.run()
