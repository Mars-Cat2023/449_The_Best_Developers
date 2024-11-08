"""
import os
import matplotlib.pyplot as plt
import networkx as nx

def create_file_tree(start_path):
    file_tree = {}
    for dirpath, dirnames, filenames in os.walk(start_path):
        # Filter out system files and generate folder structure
        filenames = [f for f in filenames if f not in ['.DS_Store']]
        folder = os.path.basename(dirpath)
        file_tree[folder] = dirnames + filenames
    return file_tree

def draw_file_tree(tree, root_folder):
    # Create a directed graph
    G = nx.DiGraph()
    # Add the root node
    G.add_node(root_folder)

    # Track which nodes are folders
    folder_nodes = set(tree.keys())

    # Build graph from tree
    for folder, contents in tree.items():
        for item in contents:
            G.add_edge(folder, item)
            if item in tree:
                folder_nodes.add(item)

    # Use Graphviz layout for a tree-like structure
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot')

    # Create color mapping: folders as light blue, files as light green
    node_colors = []
    for node in G.nodes:
        if node in folder_nodes:
            node_colors.append("lightblue")
        else:
            node_colors.append("lightgreen")

    # Draw the tree using networkx and matplotlib
    plt.figure(figsize=(12, 12))
    nx.draw(
        G, pos, with_labels=True, arrows=False, node_size=3000,
        node_color=node_colors, font_size=10, font_weight='bold'
    )
    plt.show()

# Set the root folder to visualize
start_path = "/Users/anshulsinha/Documents/EECS449_Project/Documents"

# Generate the file tree structure
file_tree = create_file_tree(start_path)

# Visualize the file tree
draw_file_tree(file_tree, os.path.basename(start_path))
"""

import os
import matplotlib.pyplot as plt
import networkx as nx
import webbrowser

def create_file_tree(start_path):
    file_tree = {}
    for dirpath, dirnames, filenames in os.walk(start_path):
        # Filter out system files and generate folder structure
        filenames = [f for f in filenames if f not in ['.DS_Store']]
        folder = os.path.basename(dirpath)
        file_tree[folder] = dirnames + filenames
    return file_tree

def draw_file_tree(tree, root_folder, output_path):
    # Create a directed graph
    G = nx.DiGraph()
    # Add the root node
    G.add_node(root_folder)

    # Track which nodes are folders
    folder_nodes = set(tree.keys())

    # Build graph from tree
    for folder, contents in tree.items():
        for item in contents:
            G.add_edge(folder, item)
            if item in tree:
                folder_nodes.add(item)

    # Use Graphviz layout for a tree-like structure
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot')

    # Create color mapping: folders as light blue, files as light green
    node_colors = []
    for node in G.nodes:
        if node in folder_nodes:
            node_colors.append("lightblue")
        else:
            node_colors.append("lightgreen")

    # Draw the tree using networkx and matplotlib
    plt.figure(figsize=(12, 12))
    nx.draw(
        G, pos, with_labels=True, arrows=False, node_size=3000,
        node_color=node_colors, font_size=10, font_weight='bold'
    )
    
    # Save the graph as an image
    plt.savefig(output_path)
    plt.close()

def generate_html(image_path, html_path):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>File Tree Visualization</title>
    </head>
    <body>
        <h2>File Tree Visualization</h2>
        <img src="{image_path}" alt="File Tree">
    </body>
    </html>
    """
    with open(html_path, 'w') as html_file:
        html_file.write(html_content)

def open_html_file(html_path):
    webbrowser.open(f'file://{os.path.realpath(html_path)}')

# Set the root folder to visualize
start_path = "/Users/anshulsinha/Documents/EECS449_Project/Documents"
output_image_path = "file_tree.png"
output_html_path = "file_tree.html"

# Generate the file tree structure
file_tree = create_file_tree(start_path)

# Visualize and save the file tree as an image
draw_file_tree(file_tree, os.path.basename(start_path), output_image_path)

# Generate the HTML file
generate_html(output_image_path, output_html_path)

# Open the HTML file in the browser
open_html_file(output_html_path)
