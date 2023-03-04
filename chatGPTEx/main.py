import json
import random
import datetime
import time
from search import search,APIQuery,APIExtraQuery,Summary,SumReply,directQuery
apiTime = 15
def detail_old(query):
    t0 = time.time()
    call_res0 = search(APIQuery(query))
    t1 = time.time()
    print(t1-t0)
    if t1-t0<apiTime:
        time.sleep(apiTime-(t1-t0))
    Sum0 = Summary(query, call_res0)
    t2 = time.time()
    if t2-t1<apiTime:
        time.sleep(apiTime-(t2-t1))
    call_res1 = search(APIExtraQuery(query,Sum0))
    t3 = time.time()
    if t3-t2<apiTime:
        time.sleep(apiTime-(t3-t2))
    Sum1 = Summary(query, call_res1)
    print('\n\nChatGpt: \n' )
    t4 = time.time()
    if t4-t3<apiTime:
        time.sleep(apiTime-(t4-t3))
    result  = SumReply(query, str(Sum0) + str(Sum1))
    return result
def detail(query):
    t0 = time.time()
    call_res0 = search(APIQuery(query),750)
    print(call_res0)
    t1 = time.time()
    if t1-t0<apiTime:
        time.sleep(apiTime-(t1-t0))
    call_res1 = search(APIExtraQuery(query,call_res0),750)
    print(call_res1)
    t2 = time.time()
    if t2-t1<apiTime:
        time.sleep(apiTime-(t2-t1))
    result  = SumReply(query, str(call_res0) + str(call_res1),max_token=1500)
    return result
def web(query):
    apir = APIQuery(query)
    call_res0 = search(apir,1500)
    result = SumReply(query, str(call_res0))
    print(call_res0)
    return result
from flask import Flask, render_template, request

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
        res = directQuery(q).replace("\n","<br>")
        return res
    elif mode == "web":
        q = 'current Time: '+ str(now) + ' Query:'+ str(userText)
        res = web(q).replace("\n","<br>")
        return res
    elif mode == "detail":
        q = 'current Time: '+ str(now) + ' Query:'+ str(userText)
        res = detail(q).replace("\n","<br>")
        return res
    return "Error"
if __name__ == "__main__":
# get the current date and time
    
    # format the time using strftime()
    # current_time = now.strftime("%I:%M %p ")
    # print(now)
    app.run()