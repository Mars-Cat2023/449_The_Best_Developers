from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask import redirect
import requests
import json
import pathlib

app = Flask(__name__)

agentname = "agent-a70f49e9-ed6d-48d4-ac04-26ec4c2908fa"

@app.route("/")
def chatbox():
    return render_template("ui.html")

# this is what handles file uploads + saves them
# can change where the file is located here
@app.route("/upload", methods=['POST'])
def upload_file():
    print(request.files)
    # print(request.form)
    fileobj = request.files["file"]
    # fileobj = request.form["file"]

    if fileobj is None:
        return "No file found", 400
    else:
        print("saving file")
        filename = fileobj.filename
        path = pathlib.Path(__file__).resolve().parent / "uploads" / filename
        fileobj.save(path)
        return redirect("/")

# heres where we get the json for the filetree component
# this should be easily configurable to return whatever json file we want
@app.route("/filetree")
def file_tree():
    with open('test.json') as f:
        d = json.load(f)
        # print(d)
        return jsonify(**d), 201

# this provides a way to get chat messages and such
# trying to do this with javascript alone wasnt working because it runs in the browser and 
# therefore was throwing a CORS error when trying to fetch data from letta
# hence this solution
@app.route("/api/v1/chat/", methods=['GET'])
def get_chat():
    url = f"http://localhost:8283/v1/agents/{agentname}/messages?limit=1000&msg_object=true"
    headers = {"Authorization": "Bearer <token>"}
    response = requests.request("GET", url, headers=headers)
    responses = json.loads(response.text)
    cb = []
    for i in responses:
        if i['role'] == 'assistant':
            print(i)
            if i['tool_calls'][0]['function']['name'] == "send_message":
                txt = json.loads(i['tool_calls'][0]['function']['arguments'])
                cb.append({'id': i['id'], 'name': 'assistant', 'text': txt['message']})
            print("\n")
        elif i['role'] == 'user':
            txt = json.loads(i['text'])
            if txt['type'] == 'user_message':
                cb.append({'id': i['id'], 'name': 'you', 'text': txt['message']})
    
    cb.reverse()
    context = {"messages": cb}
    # print(context['messages'])
    return jsonify(**context), 201

# receives the chat messages and sends them off to letta
@app.route('/api/v1/chat/', methods=['POST'])
def post_message():
    url = f'http://localhost:8283/v1/agents/{agentname}/messages'
    headers = {"Authorization": "Bearer <token>",
               'Content-Type': 'application/json'}
    comment_json = request.json
    # print(comment_json)
    text = comment_json["input"]
    data = {"messages":[{"role":"user","name":"human","text":text}],"stream_steps":True,"stream_tokens":True}
    response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    return jsonify(**comment_json), 201
