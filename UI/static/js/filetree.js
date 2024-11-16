let currentIndex = -1;
let highlightedElements = [];
let treeData = null;  // Store the entire tree data
let historyStack = []; // Stack to keep track of navigation history

// Function to create the tree structure recursively
function createTree(container, obj) {
    const ul = document.createElement('ul');
    for (let key in obj) {
        if (obj.hasOwnProperty(key)) {
            const li = document.createElement('li');
            const span = document.createElement('span');

            if (obj[key].type === 'folder') {
                span.textContent = "📁 " + key;  // Add folder icon
                span.classList.add('folder');
                li.appendChild(span);

                // Add click event to set this folder as the new root
                span.addEventListener('click', () => {
                    if (obj[key].children) {
                        historyStack.push(treeData); // Save the full tree data to the stack
                        document.getElementById('back').style.display = 'inline'; // Show the Back button
                        displayTree(obj[key].children); // Display only the subtree
                    }
                });

                // Recursively add children if they exist
                if (obj[key].children) {
                    createTree(li, obj[key].children);
                }
            } else if (obj[key].type === 'file') {
                span.textContent = "📄 " + key;  // Add file icon
                span.classList.add('file');
                li.appendChild(span);
            }

            ul.appendChild(li);
        }
    }
    container.appendChild(ul);
}

// Function to display the tree data in #tree container
function displayTree(data) {
    const treeContainer = document.getElementById('tree');
    treeContainer.innerHTML = ''; // Clear the container
    createTree(treeContainer, data); // Build the tree structure
}

// Fetch JSON data and display the initial full tree
fetch('/filetree')
    .then(response => response.json())
    .then(data => {
        treeData = data; // Save the full tree data
        displayTree(treeData); // Display the entire tree initially
    })
    .catch(error => console.error('Error loading JSON:', error));

// Function to highlight matching items
function highlightMatches() {
    const searchValue = document.getElementById('search-bar').value.toLowerCase();
    const items = document.querySelectorAll('#tree span');

    // Clear previous highlights and reset navigation
    highlightedElements.forEach(item => item.classList.remove('highlight', 'current-highlight'));
    highlightedElements = [];
    currentIndex = -1;

    items.forEach(item => {
        const itemName = item.textContent.toLowerCase().replace(/📁 |📄 /, ""); // Remove icon for comparison

        // Check if the item's name starts with the search value
        if (itemName.startsWith(searchValue) && searchValue !== "") {
            item.classList.add('highlight');
            highlightedElements.push(item);
        }
    });

    // If there are matches, set the first match as the current one
    if (highlightedElements.length > 0) {
        currentIndex = 0;
        updateCurrentHighlight();
    }
}

// Function to update the current highlighted element
function updateCurrentHighlight() {
    // Remove 'current-highlight' from all elements
    highlightedElements.forEach(item => item.classList.remove('current-highlight'));

    // Scroll to the current element and add 'current-highlight'
    if (highlightedElements[currentIndex]) {
        highlightedElements[currentIndex].classList.add('current-highlight');
        highlightedElements[currentIndex].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Navigate to the previous match
document.getElementById('prev').addEventListener('click', () => {
    if (highlightedElements.length > 0) {
        currentIndex = (currentIndex - 1 + highlightedElements.length) % highlightedElements.length;
        updateCurrentHighlight();
    }
});

// Navigate to the next match
document.getElementById('next').addEventListener('click', () => {
    if (highlightedElements.length > 0) {
        currentIndex = (currentIndex + 1) % highlightedElements.length;
        updateCurrentHighlight();
    }
});

// Go back to the full tree
document.getElementById('back').addEventListener('click', () => {
    displayTree(treeData); // Display the full tree
    historyStack = []; // Clear the history stack
    document.getElementById('back').style.display = 'none'; // Hide the Back button
});

// Attach event listener to the search bar
document.getElementById('search-bar').addEventListener('input', highlightMatches);