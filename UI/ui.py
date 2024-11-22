from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask import redirect
import requests
import json
import pathlib
from create_table_summary import create_table
from letta import EmbeddingConfig, LLMConfig, create_client

app = Flask(__name__)

client = create_client()

# set automatic defaults for LLM/embedding config
client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))
client.set_default_embedding_config(
    EmbeddingConfig.default_config(model_name="text-embedding-ada-002")
)

agentname = client.get_agent_id(
    agent_name="FileMindr"
)


@app.route("/")
def chatbox():
    return render_template("ui.html")


# this is what handles file uploads + saves them
# can change where the file is located here
# NO LONGER NEEDED!
@app.route("/upload", methods=["POST"])
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
@app.route("/filetree", methods=["GET"])
def file_tree():
    with open("test.json") as f:
        d = json.load(f)
        # print(d)
        return jsonify(**d), 201


# ok here is where we handle loading the filetree into the json format
@app.route("/filetree", methods=["POST"])
def file_tree_create():
    directory_json = request.json
    # print(comment_json)
    d_path = directory_json["input"]
    create_table(d_path)
    with open("curr_dir_org.json") as f:
        d = json.load(f)
        # print(d)
        return jsonify(**d), 201


# this is what gets the new filetree when you want to view a proposed new organization from the ui
@app.route("/newfiletree", methods=["POST"])
def file_tree_new():
    with open("new_dir_org.json") as f:
        d = json.load(f)
        # print(d)
        return jsonify(**d), 201


# this provides a way to get chat messages and such
# trying to do this with javascript alone wasnt working because it runs in the browser and
# therefore was throwing a CORS error when trying to fetch data from letta
# hence this solution
@app.route("/api/v1/chat/", methods=["GET"])
def get_chat():
    url = f"http://localhost:8283/v1/agents/{agentname}/messages?limit=1000&msg_object=true"
    headers = {"Authorization": "Bearer <token>"}
    response = requests.request("GET", url, headers=headers)
    responses = json.loads(response.text)
    cb = []
    msgs_since_sort = 10
    for i in responses:
        if i["role"] == "assistant":
            print(i)
            fxn = i["tool_calls"][0]["function"]["name"]
            if fxn == "send_message":
                txt = json.loads(i["tool_calls"][0]["function"]["arguments"])
                cb.append(
                    {
                        "id": i["id"],
                        "name": "assistant",
                        "text": txt["message"],
                    }
                )
                msgs_since_sort = msgs_since_sort + 1
            elif (
                (fxn == "sort_FS3")
                or (fxn == "sort_FS2")
                or (fxn == "sort_FS1")
            ):
                print("FOUND!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                msgs_since_sort = 0
            print("\n")
        elif i["role"] == "user":
            txt = json.loads(i["text"])
            if txt["type"] == "user_message":
                cb.append(
                    {"id": i["id"], "name": "you", "text": txt["message"]}
                )

    cb.reverse()
    # basically we need to keep track of how many msgs it has been since the sort call bc if it was a recent call we want the UI to show the proposed new files
    if msgs_since_sort <= 2:
        has_new_filesys = True
    else:
        has_new_filesys = False
    context = {"messages": cb, "new-filesys": has_new_filesys}
    # print(context['messages'])
    return jsonify(**context), 201


# receives the chat messages and sends them off to letta
@app.route("/api/v1/chat/", methods=["POST"])
def post_message():
    url = f"http://localhost:8283/v1/agents/{agentname}/messages"
    headers = {
        "Authorization": "Bearer <token>",
        "Content-Type": "application/json",
    }
    comment_json = request.json
    # print(comment_json)
    text = comment_json["input"]
    data = {
        "messages": [{"role": "user", "name": "human", "text": text}],
        "stream_steps": True,
        "stream_tokens": True,
    }
    response = requests.request(
        "POST", url, headers=headers, data=json.dumps(data)
    )
    return jsonify(**comment_json), 201
