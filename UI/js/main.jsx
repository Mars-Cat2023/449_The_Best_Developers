import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import Chatbox from "./chatbox";
import {FileUploader} from "./upload";

// upload button
const upload = createRoot(document.getElementById("fileUploader"));
upload.render(
    <StrictMode>
        <FileUploader />
    </StrictMode>
);

// Chatbox
const root = createRoot(document.getElementById("reactEntry"));
root.render(
  <StrictMode>
    <Chatbox agentName="yay" />
  </StrictMode>
);

