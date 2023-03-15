#polished by GPT4
import sqlite3
from sqlite3 import Error
import json
import datetime
import os
import configparser
from promptsSearch import SearchPrompt, promptsDict
from markdown_it import MarkdownIt
from flask import Flask, render_template, request, Response
from flask import Flask, redirect, url_for, session, jsonify
from flask_oauthlib.client import OAuth
from functools import wraps
import requests
from search import (
    directQuery,
    web,
    detail,
    webDirect,
    WebKeyWord,
    load_history,
    APICallList,
    directQuery_stream,
    chatbot,
)
from graiax.text2img.playwright.plugins.code.highlighter import Highlighter
from graiax.text2img.playwright import MarkdownConverter

program_path = os.path.realpath(__file__)
program_dir = os.path.dirname(program_path)

config = configparser.ConfigParser()
config.read(program_dir + "/apikey.ini")
user_db_name = "users.db"
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(program_dir+'/'+user_db_name)
    except Error as e:
        print(e)
    return conn
def create_users_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        github_id INTEGER UNIQUE NOT NULL,
                        username TEXT NOT NULL,
                        access_token TEXT NOT NULL
                     );''')
    except Error as e:
        print(e)
def save_user(conn, github_id, username, access_token):
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO users (github_id, username, access_token)
                  VALUES (?, ?, ?)''', (github_id, username, access_token))
    conn.commit()


def parse_text(text):
    md = MarkdownIt("commonmark", {"highlight": Highlighter()}).enable("table")
    res = MarkdownConverter(md).convert(text)
    return res


app = Flask(__name__)
app.static_folder = "static"
app.secret_key = os.environ.get("SECRET_KEY") or "a-very-secret-key"
app.debug = True

oauth = OAuth(app)
GITHUB_CLIENT_ID =  os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
github = oauth.remote_app(
    'github',
    consumer_key=GITHUB_CLIENT_ID,
    consumer_secret=GITHUB_CLIENT_SECRET,
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
)

def get_user_access_token(conn, github_id=None, username=None):
    c = conn.cursor()
    if github_id:
        c.execute("SELECT access_token FROM users WHERE github_id=?", (github_id,))
    elif username:
        c.execute("SELECT access_token FROM users WHERE username=?", (username,))
    else:
        return None

    result = c.fetchone()
    return result[0] if result else None

def get_github_id_by_access_token(conn, access_token):
    c = conn.cursor()
    c.execute("SELECT github_id FROM users WHERE access_token=?", (str(access_token),))
    result = c.fetchone()
    return result[0] if result else None


@app.route('/login')
def login():
    return github.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('github_token')
    return redirect(url_for('index'))


@app.route('/github-callback')
@github.authorized_handler
def authorized(resp):
    if resp is None:
        error_reason = request.args.get('error_reason', 'Unknown reason')
        error_description = request.args.get('error_description', 'No description')
        return f'Access denied: reason={error_reason} error={error_description}'
    session['github_token'] = resp['access_token']
    me = github.get('user')
    # Save user data and access token to the database
    conn = create_connection()
    create_users_table(conn)
    print(me.data['id'], me.data['login'], resp['access_token'])
    save_user(conn, me.data['id'], me.data['login'], resp['access_token'])
    conn.close()
    return redirect(url_for('index'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'github_token' not in session:
            return redirect(url_for('login'))
        access_token = session['github_token']
        conn = create_connection()
        githubID = get_github_id_by_access_token(conn, access_token)
        conn.close()
        if not githubID:
            return redirect(url_for('login'))
        kwargs['githubID'] = githubID
        return f(*args, **kwargs)
    return decorated_function

@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


# @app.route("/")
# def index():
#     if "user_info" in session:
#         user_info = session["user_info"]
#         return f"Hello, {user_info['name']}!"
#     else:
#         return '<a href="/login">Log in with Google</a>'

@app.route('/')
@login_required
def index(githubID):
    return render_template("index.html")


@app.route("/api/query")
@login_required
def get_bot_response(githubID):
    mode = str(request.args.get("mode"))
    userText = str(request.args.get("msg"))
    uuid = str(request.args.get("uuid"))
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M")

    if mode == "chat":
        q = str(userText)
        promptName = str(request.args.get("prompt"))

        if promptName != "":
            if promptName in promptsDict:
                prompt = promptsDict[promptName]
            else:
                prompt = str(SearchPrompt(promptName)[0])
                prompt = promptsDict[prompt]
            return Response(
                directQuery_stream(q, conv_id=uuid, prompt=prompt),
                direct_passthrough=True,
                mimetype="application/octet-stream",
            )
        else:
            return Response(
                directQuery_stream(q, conv_id=uuid),
                direct_passthrough=True,
                mimetype="application/octet-stream",
            )
    elif mode == "web":
        q = "current Time: " + str(now) + "\n\nQuery:" + str(userText)
        return Response(
            web(q, conv_id=uuid),
            direct_passthrough=True,
            mimetype="application/octet-stream",
        )
    elif mode == "detail":
        q = "current Time: " + str(now) + "\n\nQuery:" + str(userText)
        return Response(
            detail(q, conv_id=uuid),
            direct_passthrough=True,
            mimetype="application/octet-stream",
        )
    elif mode == "webDirect":
        q = "current Time: " + str(now) + "\n\nQuery:" + str(userText)
        return Response(
            webDirect(q, conv_id=uuid),
            direct_passthrough=True,
            mimetype="application/octet-stream",
        )
    elif mode == "WebKeyWord":
        q = str(userText)
        return Response(
            WebKeyWord(q, conv_id=uuid),
            direct_passthrough=True,
            mimetype="application/octet-stream",
        )
    return "Error"


@app.route("/api/addChat", methods=["POST"])
@login_required
def add_chat(githubID):
    uuid = str(request.form.get("uuid"))
    message = str(request.form.get("msg"))
    chatbot.add_to_conversation(message, role="assistant", convo_id=str(uuid))
    return parse_text(
        message + "\n\ntoken cost:" + str(chatbot.token_cost(convo_id=uuid))
    )


@app.route("/api/chatLists")
@login_required
def get_chat_lists(githubID):
    if os.path.isfile(program_dir + "/chatLists.json"):
        with open(program_dir +"/chatLists.json", "r", encoding="utf-8") as f:
            chatLists = json.load(f)
            chatLists["chatLists"] = list(reversed(chatLists["chatLists"]))
        return json.dumps(chatLists)
    else:
        with open(program_dir + "/chatLists.json", "w", encoding="utf-8") as f:
            defaultChatLists = {
            "chatLists": [
            {
            "uuid": "default",
            "chatName": "Default",
            }
            ]
            }
        json.dump(defaultChatLists, f, ensure_ascii=False)
        return json.dumps(defaultChatLists)

@app.route("/api/history")
@login_required
def send_history(githubID):
    uuid = str(request.args.get("uuid"))
    msgs = []
    chats = load_history(conv_id=uuid)
    for chat in chats:
        queryTime = ""
        firstLine = chat["content"].split("\n")[0]
        if firstLine.find("current Time:") != -1:
            queryTime = firstLine.split("current Time:")[-1]
        if chat["content"].find("Query:") != -1:
            query = chat["content"].split("Query:")[1]
            chat["content"] = query
        if chat["role"] == "user":
            msgs.append(
                {
                    "name": "You",
                    "img": "static/styles/person.jpg",
                    "side": "right",
                    "text": parse_text(chat["content"]),
                    "time": queryTime,
                }
            )
        elif chat["role"] == "assistant":
            msgs.append(
                {
                    "name": "ExChatGPT",
                    "img": "static/styles/ChatGPT_logo.png",
                    "side": "left",
                    "text": parse_text(chat["content"]),
                    "time": queryTime,
                }
            )
    return json.dumps(msgs, ensure_ascii=False)
lastAPICallListLength = len(APICallList)

@app.route("/api/APIProcess")
@login_required
def APIProcess(githubID):
    global lastAPICallListLength
    if len(APICallList) > lastAPICallListLength:
        lastAPICallListLength += 1
        return json.dumps(
        APICallList[lastAPICallListLength - 1], ensure_ascii=False
        )
    else:
        return {}

@app.route("/api/setChatLists", methods=["POST"])
@login_required
def set_chat_lists(githubID):
    with open(program_dir + "/chatLists.json", "w", encoding="utf-8") as f:
        json.dump(request.json, f, ensure_ascii=False)
        return "ok"

@app.route("/api/promptsCompletion", methods=["get"])
@login_required
def promptsCompletion(githubID):
    prompt = str(request.args.get("prompt"))
    res = json.dumps(SearchPrompt(prompt), ensure_ascii=False)
    return res

subscriptionKey = None
region = None
if "Azure" in config:
    if "subscriptionKey" in config["Azure"]:
        subscriptionKey = config["Azure"]["subscriptionKey"]
    if "region" in config["Azure"]:
        region = config["Azure"]["region"]

@app.route("/api/getAzureAPIKey", methods=["GET"])
@login_required
def AzureAPIKey(githubID):
    return json.dumps(
    {"subscriptionKey": subscriptionKey, "region": region}, ensure_ascii=False
    )

if __name__ == "__main__":
    app.config["JSON_AS_ASCII"] = False
    app.config["DEBUG"] = True
    # local config uncomment this line
    app.run(host="127.0.0.1", port=1234)
    # docker config uncomment this line
    # app.run(host="0.0.0.0", port=5000)
