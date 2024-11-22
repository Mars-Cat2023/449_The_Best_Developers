import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";

dayjs.extend(relativeTime);
dayjs.extend(utc);

function newTree() {
  let d = "new_dir_org.json"
  const json = JSON.stringify({'input': d});
    console.log(json)

    fetch('/newfiletree', {
        credentials: "same-origin",
        method: "post",
        headers: {
          "Content-Type": "application/json",
        },
        body: json,
      })
    .then(response => response.json())
    .then(data => {
        treeData = data; // Save the full tree data
        displayTree(treeData); // Display the entire tree initially
    })
    .catch(error => console.error('Error loading JSON:', error));

    const tr = document.getElementById('new-filesys-msg');
    tr.innerHTML = 'New organization:';
}

function ChatForm({ setMessages }) {
  const [something, setSomething] = useState("");
  function handleSubmit(e) {
    // Prevent the browser from reloading the page
    e.preventDefault();

    // Read the form data
    const form = e.target;
    const formData = new FormData(form);
    const shit = Object.fromEntries(formData.entries());

    // agent = `agent-a70f49e9-ed6d-48d4-ac04-26ec4c2908fa`;
    // let url = `http://localhost:8283/v1/agents/${String(agent)}/messages`;
    // let url = `/api/v1/comments/?postid=${String(postId)}`;
    
    let url = "/api/v1/chat/";

    // prep json and send req to api to update databse
    const json = JSON.stringify(shit);
    fetch(url, {
      credentials: "same-origin",
      method: form.method,
      headers: {
        "Content-Type": "application/json",
      },
      body: json,
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then(() => {
        // update the chatlist on the ppage
        url = `/api/v1/chat`;
        fetch(url, { credentials: "same-origin" })
          .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
          })
          .then((data) => {
            setMessages(data["messages"])
            setSomething("")
            if (data["new-filesys"]) {
              // HERE IS WHERE WE UPDATE
              newTree()
              // we will need to grab  a component by id and change it, perhaps the new filetree structure and slap a new file in there
            }
          })
          .catch((error) => console.log(error));
      })
      .catch((error) => console.log(error));

    console.log(json);
  }

  return (
    <form class="chat-form" method="post" onSubmit={handleSubmit}>
      <input class="chat-form-box" type="text" name="input" value={something} onChange={e => setSomething(e.target.value)}/>
    </form>
  );
}

ChatForm.propTypes = {
  setMessages: PropTypes.func.isRequired,
};

function ChatMessage({ id, name, text }) {
  return (
    <section className="message">
        <b>{name}: </b>{" "}
      <span data-testid="message-text">{text}</span>
    </section>
  );
}

export default function Chatbox({ agentName }) { // i intend to make this work for other agents but havent yet
  const [messages, setMessages] = useState([]);
  let url = "http://localhost:8000/api/v1/chat/";

  useEffect(() => {
    let ignoreStaleRequest = false;

    fetch(url)
      .then((response) => response.json()) //response.json()
      .then((data) => {
        if (!ignoreStaleRequest) {
          console.log(data["messages"]); // change
          setMessages(data["messages"])
        }
      })
      .catch((error) => console.error("Error fetching post data:", error));
    return () => {
      ignoreStaleRequest = true; // important for cleanup
    };
  }, [url]);

  return (
    <div className="chatbox">
      <div className="chatbox-msgs">
      {messages.map((msg) => (
        <ChatMessage
          id={msg.id}
          name={msg.name}
          text={msg.text}
        />
      ))}
      </div>
      <ChatForm setMessages={setMessages}/>
    </div>
  );
}

// Chat.propTypes = {
//   name: PropTypes.string.isRequired,
//   text: PropTypes.string.isRequired,
// };