from flask import Flask
# from flask import render_template
from flask import jsonify
import requests
import json

app = Flask(__name__)

@app.route("/api/v1/chat/")
def chatbox():
    url = "http://localhost:8283/v1/agents/agent-a70f49e9-ed6d-48d4-ac04-26ec4c2908fa/messages?limit=1000&msg_object=true"
    headers = {"Authorization": "Bearer <token>"}
    response = requests.request("GET", url, headers=headers)
    responses = json.loads(response.text)
    cb = []
    for i in responses:
        if i['role'] == 'assistant':
            txt = json.loads(i['tool_calls'][0]['function']['arguments'])
            print('NEW MESSAGE!!!!!!!!!!!!!!!! ASSISTANT!!!!!!!!!')
            print(txt['message'])
            cb.append({'name': 'assistant', 'text': txt['message']})
        elif i['role'] == 'user':
            txt = json.loads(i['text'])
            if txt['type'] == 'user_message':
                print('NEW MESSAGE!!!!!!!!!!!!!!!! USER')
                print(txt['message'])
                cb.append({'name': 'you', 'text': txt['message']})
    
    context = {"messages": cb}
    # print(context['messages'])
    return jsonify(**context), 201