import json
import random
import datetime
import re
from flask import Flask, render_template, request
from search import search,APIQuery,APIExtraQuery,Summary,SumReply,directQuery
def getResponse(query):
    call_res0 = search(APIQuery(query))
    
    # if you need detailed mode , uncomment below. 
    # Sum0 = Summary(query, call_res0)
    # call_res1 = search(APIExtraQuery(query,Sum0))
    # Sum1 = Summary(query, call_res1)
    # print('\n\nChatGpt: \n' )
    # result  = SumReply(query, str(Sum0)+str(Sum1))

    result = SumReply(query, str(call_res0))
    return result
def chatbot_response(query):
    res = {}
    res = getResponse(query)
    res = res.replace("\n","<br>")
    print(res)
    return res


app = Flask(__name__)
app.static_folder = 'static'
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/get")
def get_bot_response():
    userText = str(request.args.get('msg'))
    now = datetime.datetime.now()
    q = 'current Time: '+ str(now) + ' Query:'+ str(userText)
    # use /chat to offline chat 
    if(userText.find('/chat')!=-1):
        q = userText.replace('/chat','')
        return directQuery(q)
    return chatbot_response(q)
if __name__ == "__main__":
    app.run()