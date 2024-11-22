document.getElementById('directory-go').addEventListener('click', () => {
    d = document.getElementById('directory-input').value

    // prep json and send req to api to update databse
    const json = JSON.stringify({'input': d});
    console.log(json)

    fetch('/filetree', {
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
    tr.innerHTML = '';
});

