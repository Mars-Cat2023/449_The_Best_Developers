// import { ChangeEvent, useState } from 'react';
// import { useRef } from "react";
import React from "react";

export function FileUploader() {  // Create a reference to the hidden file input element
    const hiddenFileInput = document.getElementById("fileUploader");
    
    // Programatically click the hidden file input element
    // when the Button component is clicked
    const handleClick = event => {
      hiddenFileInput.current.click();
    }; 
    const handleChange = event => {
      const fileUploaded = event.target.files[0];
      console.log(fileUploaded.name)

      document.getElementById("upload-formt").submit(handleSubmit);

    };
    // function handleSubmit(e) {
    //   // Prevent the browser from reloading the page
    //   e.preventDefault();
  
    //   console.log(e)
    //   // Read the form data
    //   const form = e.target;
    //   const formData = new FormData(form);
    //   const shit = Object.fromEntries(formData.entries());
  
    //   let url = "/upload";
  
    //   // prep json and send req to api to update databse
    //   const json = JSON.stringify(shit);
    //   fetch(url, {
    //     credentials: "same-origin",
    //     method: form.method,
    //     headers: {
    //       "Content-Type": "application/json",
    //     },
    //     body: json,
    //   })
    // };
    return (
      <form id="upload-formt" action="/upload" method="post" enctype="multipart/form-data" onSubmit={handleSubmit}>
        <button className="button-upload" onClick={handleClick}>
          Upload a file
        </button>
        <input
          type="file"
          name="file"
          onChange={handleChange}
          ref={hiddenFileInput}
          style={{display: 'none'}} // Make the file input element invisible
          accept="image/*" required
        />
      </form>
    );
}