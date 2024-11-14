import os, json
from summarize import FileTools
from letta import create_client

"""
This file creates a data table of files
"""
client = create_client()

file_tools = FileTools()

client.delete_agent(client.get_agent_id("file_extraction_agent"))

file_extraction_tool = client.create_tool(FileTools.extract_file_content)

file_extraction_agent_state = client.create_agent(
    name="file_extraction_agent",
    tools=[file_extraction_tool.name]
)

def createFile(data, location):
    file = {
        "type" : "file",
        "path" : location,
        "data" : data,
        "summary": None,
    }
    return file

def createFolder(data, location):
    folder = {
        "type" : "folder",
        "path" : cwd,
        "data" : data,
        "children" : {},
    }
    return folder

# Initiat Directory
directory = "TestDirectory3"
test = os.walk(directory)
fileSystem = {}

for f in test:
    print(f)
    print(f[0])
    
    cwd = f[0]
    folders = f[1]
    files = f[2]

    #add folders
    # for folder in folders:
    #     fileSystem[folder] = createFolder(folder, 1, cwd)
    
    #add files
    for file in files:
        file_path = os.path.join(f[0], file)
        file_entry = createFile(1, file_path)
        # fileSystem[file] = createFile(1, file_path)
        response = file_tools.summarize_file_content(file_path)
        messages = response.messages
        for message in messages:
            if message.message_type == "function_call" and message.function_call.name == "send_message":
                arguments = message.function_call.arguments
                break 
        arguments_dict = json.loads(arguments)
        summary = arguments_dict["message"]
        file_entry["summary"] = summary

        fileSystem[file] = file_entry

    print(os.stat(f[0]))
    print('--------------')

fileSystem = json.dumps(fileSystem, indent=4)
print(fileSystem)

FileSystemData = open("dataTable3.json", "w")
FileSystemData.write(fileSystem)