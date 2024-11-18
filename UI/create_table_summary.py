import os, json
from summarize import FileTools
from letta import EmbeddingConfig, LLMConfig, create_client


def createFile(data, location):
        file_tools = FileTools()
        # print("location: ", location)
        response = file_tools.summarize_file_content(location)
        file = {
            "type" : "file",
            "summary": response,
            "path" : location,
            "data" : data,
        }
        return file

def createFolder(data, location):
        folder = {
            "type" : "folder",
            "path" : location,
            "data" : data,
            "children" : {},
        }
        return folder
"""
This file creates a data table of files
"""
def create_table(directory):
    client = create_client()

    # set automatic defaults for LLM/embedding config
    client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))
    client.set_default_embedding_config(EmbeddingConfig.default_config(model_name="text-embedding-ada-002"))

    # print(type(client.get_agent_id(agent_name="file_extraction_agent")))
    # print(client.get_agent(agent_name="file_extraction_agent"))
    if client.get_agent_id(agent_name="file_extraction_agent"):
        client.delete_agent(client.get_agent_id("file_extraction_agent"))

    file_tools = FileTools()

    file_extraction_tool = client.create_tool(FileTools.extract_file_content)

    file_extraction_agent_state = client.create_agent(
        name="file_extraction_agent",
        tools=[file_extraction_tool.name]
    )

    # print(os.getcwd(), '../' + directory)
    directory = '../' + directory

    test = os.walk(directory)

    fileSystem = {}
    initialdir = ''
    extrabit = ''

    t = directory.split('/')
    initialdir = t.pop(-1)
    t.append('')
    extrabit = "/".join(t)
    # print("extrabit: ", extrabit)
    fileSystem = {initialdir : createFolder(initialdir,1)}

    dataTable = {}

    for f in test:
        
        cwd = f[0].replace(extrabit, '')
        path = cwd.split('/')
        # print(path)
        folders = f[1]
        files = f[2]
        
        #get current folder
        currentFolder = fileSystem[path[0]]
        for p in path[1:]:
            currentFolder = currentFolder['children'] 
            currentFolder = currentFolder[p] 

        #add folders
        # print(currentFolder)
        for folder in folders:
            children = currentFolder['children']
            children[folder] = createFolder(folder, 1)
            
        #add files
        for file in files:
            children = currentFolder['children']
            # file_path = os.path.join(extrabit, f[0], file)
            file_path = os.path.join(f[0], file)
            children[file] = createFile(1, file_path)
            #---- Data Table Section ----
            dataTable[file] = children[file]
            #----------------------------

    fileSystem = json.dumps(fileSystem, indent=4)
    print(fileSystem)

    FileSystemData = open("curr_dir_org.json", "w")
    FileSystemData.write(fileSystem)

    dataTable = json.dumps(dataTable, indent=4)
    print(dataTable)

    dataTableFILE = open("dataTable3.json", "w")
    dataTableFILE.write(dataTable)

    #----Data Table----



    # # Initiat Directory
    # test = os.walk(directory)
    # fileSystem = {}

    # def path_to_dict(path):
    #     name = os.path.basename(path)
    #     d = {}
    #     d[name] = {}
    #     dd = d[name]
    #     if os.path.isdir(path):
    #         dd['type'] = "directory"
    #         dd['children'] = {path_to_dict(os.path.join(path,x)) for x in os.listdir\
    #                             (path)}
    #     else:
    #         dd['type'] = "file"
    #     return d
    # fileSystem = json.dumps(path_to_dict(directory), indent=4)
    # print(fileSystem)

    # FileSystemData = open("curr_dir_org.json", "w")
    # FileSystemData.write(fileSystem)
    
    # for f in test:
    #     print(f)
    #     print(f[0])
        
    #     cwd = f[0]
    #     folders = f[1]
    #     files = f[2]
    #     #add folders
    #     # for folder in folders:
    #     #     fileSystem[folder] = createFolder(folder, 1, cwd)
        
    #     #add files
    #     for file in files:
    #         file_path = os.path.join(f[0], file)
    #         file_entry = createFile(1, file_path)
    #         # fileSystem[file] = createFile(1, file_path)
    #         response = file_tools.summarize_file_content(file_path)
    #         # for message in messages:
    #         #     if message.message_type == "function_call" and message.function_call.name == "send_message":
    #         #         arguments = message.function_call.arguments
    #         #         break 
    #         # arguments_dict = json.loads(arguments)
    #         # summary = arguments_dict["message"]

    #         file_entry["summary"] = response

    #         fileSystem[file] = file_entry

    #     print(os.stat(f[0]))
    #     print('--------------')

    # # fileSystem = json.dumps(fileSystem, indent=4)
    # # print(fileSystem)

    # # FileSystemData = open("curr_dir_org.json", "w")
    # # FileSystemData.write(fileSystem)
