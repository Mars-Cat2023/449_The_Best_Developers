import os, json
from letta import create_client 
from letta import EmbeddingConfig, LLMConfig
import letta

client = create_client()
client.set_default_embedding_config(EmbeddingConfig.default_config(model_name="letta"))
client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))

import os, json
from letta import create_client 
from letta import EmbeddingConfig, LLMConfig
import letta
from letta import AgentState

# client.delete_tool('sort_FS')

def sort_FS1(self,):
    """
    This tool sorts the user's file system. If asked to sort or to organize the file system by the NAMES and/or TITLE of the files, call this function. Tell the user the return and results of the function call. This function has a required argument, mode. This argument is required and must be filled. For example, if users say "sort files by content", set mode to "content" when calling this function.

    Args: 

    Returns: 
        fileSort (str): This is the new organization of the file system users requested
    """
    #create another client to ask
    #Options are: content, extension, name, or date.
    # Query the user for the mode (valid modes are: content, extension, name, or date), before calling this function. 
    from letta import create_client 
    from letta import EmbeddingConfig, LLMConfig
    import json, os, re
    
    client = create_client()
    client.set_default_embedding_config(EmbeddingConfig.default_config(model_name="letta"))
    client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))

    #get json data
    #file = open('FileSystemData.json') #NOTE: hardCoded
    file = open('dataTable3.json') #NOTE: hardCoded
    fileData = json.load(file)
    #fileDataS = json.dumps(fileData)

    #create message to send to different agent
    #NOTE: 1 layer simple sort, based on name
    file_keys = fileData.keys()

    
    template = "\nTemplate:\n[group 1]{item 1, item2, ...}\n[group 2]{item 3, item 4, ...}\n...\nItems:"

    enforceSingle = "If an item has already be grouped, do not group it again. Thus, for each item listed, it should only appear once amoungst all groups. DO NOT CHANGE THE FILE NAMES. Return only the output template and nothing else:"
    
    prompt = f"Using the template and given the following files, group the files into the template based on the commonalities in the topic, semantics, or meanings of the names. Ignore the file extension or file type"

    message = prompt + enforceSingle + template
    for k in file_keys:
        message = message + "\n" + k
    
    

    print(f'Testing Output: {message}')

    #NOTE: for easier testing, try to start fresh so we know effect of prompting
    try:
        agentState = client.create_agent('background_agent')
    except ValueError:
        agentID = client.get_agent_id('background_agent')
        client.delete_agent(agentID)
        agentState = client.create_agent('background_agent')
    
    
    answer = client.send_message(
        message=message,
        role='user',
        agent_id=agentState.id
    )

    

    answer = answer.messages[1].function_call.arguments
    answer = json.loads(answer)
    answer = json.dumps(answer['message'])
    print("MY_ANSWER", answer)

    #self.interface.assistant_message(answer)  # , msg_obj=self._messages[-1])
    outputFile = open("newFileSystem.txt", 'w')
    outputFile.write(answer) #NOTE: Store background agent output

    #----ParsingGPT_FS----
    raw_folders = re.findall(r'(\[[\w\s\-\,\.\\\/\(\)]+\])', answer)
    # print(raw_folders)

    raw_files = re.findall(r'\{[\w\s\-\,\.\\\/\(\)]+\}', answer)
    # print(raw_files)

    #split and clean files
    files = []
    for f in raw_files:
        f = re.sub(r'[\{\}]', '', f)
        files.append(re.split(', ', f))
        # print(files)

    print('Files:  ', files)

    #clean folders
    folders = []
    for f in raw_folders:
        f = re.sub(r'[\[\]]', '', f)
        f = re.sub(r' ', '_', f)
        folders.append(re.split(', ', f)[0])

    print('Folders:  ', folders)

    #generate json file table
    fs_table = {}
    dir_root = 'uploads' #NOTE: Hard Coded
    for folder_i in range(len(folders)):
        for file_i in range(len(files[folder_i])):
            old_path = fileData[files[folder_i][file_i]]['path']

            fs_table[files[folder_i][file_i]] = {
                "type" : "file",
                "new_path" : f"{dir_root}/{folders[folder_i]}",
                "old_path" : old_path
            }
        
    print(json.dumps(fs_table, indent=4))
    #---------------------END


    #----CREATE_NEW_FS----
    import shutil
    for fileName in fs_table.keys():
        print('MOVING: ', fileName)
        try:
            os.mkdir(fs_table[fileName]['new_path'])
        except FileExistsError: 
            continue
        finally:
            shutil.move(fs_table[fileName]['old_path'] + "/" + fileName, fs_table[fileName]['new_path'] + "/" + fileName)
    #---------------------END

    #----DELETE_OLD_FOLDERS----
    for fileName in fs_table.keys():
        try:
            old_path = fs_table[fileName]['old_path']
            if old_path != dir_root:
                os.rmdir(old_path)
        except FileExistsError: 
            continue
    #--------------------------END

    #----Generate_File_Data_Tree----
    import os, json
    """
    This file creates the files structure in json format.  
    THIS IS NOT THE SAME AS TURNING FILE SYSTEM TO DATA TABLE
    """

    # Initiat Directory
    directory = dir_root
    test = os.walk(directory)

    def createFile(name: str, data):
        file = {
            "type" : "file",
            "data" : data
        }
        return file

    def createFolder(name: str, data):
        folder = {
            "type" : "folder",
            "data" : data,
            "children" : {}
        }
        return folder

    fileSystem = {directory : createFolder(directory,1)}
    for f in test:
        cwd = f[0]
        path = cwd.split('/')
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
            children[file] = createFile(file, 1)

        #print(os.stat(f[0]))
        #print('--------------')

    fileSystem = json.dumps(fileSystem, indent=4)
    print(fileSystem)

    FileSystemData = open("new_dir_org.json", "w")
    FileSystemData.write(fileSystem)
    #-------------------------------END

    #NOTE: return background agent output to user
    return answer

def sort_FS2(self,):
    """
    This tool sorts the user's file system. If asked to sort or to organize based on the EXTENSIONS of the files, call this function. Tell the user the return and results of the function call. This function has a required argument, mode. This argument is required and must be filled. For example, if users say "sort files by content", set mode to "content" when calling this function.


    Args: 

    Returns: 
        fileSort (str): This is the new organization of the file system users requested
    """
    #create another client to ask
    #Options are: content, extension, name, or date.
    # Query the user for the mode (valid modes are: content, extension, name, or date), before calling this function. 
    from letta import create_client 
    from letta import EmbeddingConfig, LLMConfig
    import json, os, re
    
    client = create_client()
    client.set_default_embedding_config(EmbeddingConfig.default_config(model_name="letta"))
    client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))

    #get json data
    #file = open('FileSystemData.json') #NOTE: hardCoded
    file = open('curr_dir_org.json') #NOTE: hardCoded
    fileData = json.load(file)
    #fileDataS = json.dumps(fileData)

    #create message to send to different agent
    #NOTE: 1 layer simple sort, based on name
    file_keys = fileData.keys()

    
    template = "\nTemplate:\n[group 1]{item 1, item2, ...}\n[group 2]{item 3, item 4, ...}\n...\nItems:"

    enforceSingle = "If an item has already be grouped, do not group it again. Thus, for each item listed, it should only appear once amoungst all groups. DO NOT CHANGE THE FILE NAMES. Return only the output template and nothing else:"

    prompt = f"Using the template and given the following files, group the files into the template based on the commonalities of ONLY on the extensions of the file, and not on the name."

    message = prompt + enforceSingle + template
    for k in file_keys:
        message = message + "\n" + k

    

    print(f'Testing Output: {message}')

    #NOTE: for easier testing, try to start fresh so we know effect of prompting
    try:
        agentState = client.create_agent('background_agent')
    except ValueError:
        agentID = client.get_agent_id('background_agent')
        client.delete_agent(agentID)
        agentState = client.create_agent('background_agent')
    
    
    answer = client.send_message(
        message=message,
        role='user',
        agent_id=agentState.id
    )

    

    answer = answer.messages[1].function_call.arguments
    answer = json.loads(answer)
    answer = json.dumps(answer['message'])
    print("MY_ANSWER", answer)

    #self.interface.assistant_message(answer)  # , msg_obj=self._messages[-1])
    outputFile = open("newFileSystem.txt", 'w')
    outputFile.write(answer) #NOTE: Store background agent output

    #----ParsingGPT_FS----
    raw_folders = re.findall(r'(\[[\w\s\-\,\.\\\/\(\)]+\])', answer)
    # print(raw_folders)

    raw_files = re.findall(r'\{[\w\s\-\,\.\\\/\(\)]+\}', answer)
    # print(raw_files)

    #split and clean files
    files = []
    for f in raw_files:
        f = re.sub(r'[\{\}]', '', f)
        files.append(re.split(', ', f))
        # print(files)

    print('Files:  ', files)

    #clean folders
    folders = []
    for f in raw_folders:
        f = re.sub(r'[\[\]]', '', f)
        f = re.sub(r' ', '_', f)
        folders.append(re.split(', ', f)[0])

    print('Folders:  ', folders)

    #generate json file table
    fs_table = {}
    dir_root = 'uploads' #NOTE: Hard Coded
    for folder_i in range(len(folders)):
        for file_i in range(len(files[folder_i])):
            old_path = fileData[files[folder_i][file_i]]['path']

            fs_table[files[folder_i][file_i]] = {
                "type" : "file",
                "new_path" : f"{dir_root}/{folders[folder_i]}",
                "old_path" : old_path
            }
        
    print(json.dumps(fs_table, indent=4))
    #---------------------END


    #----CREATE_NEW_FS----
    import shutil
    for fileName in fs_table.keys():
        print('MOVING: ', fileName)
        try:
            os.mkdir(fs_table[fileName]['new_path'])
        except FileExistsError: 
            continue
        finally:
            shutil.move(fs_table[fileName]['old_path'] + "/" + fileName, fs_table[fileName]['new_path'] + "/" + fileName)
    #---------------------END

    #----DELETE_OLD_FOLDERS----
    for fileName in fs_table.keys():
        try:
            old_path = fs_table[fileName]['old_path']
            if old_path != dir_root:
                os.rmdir(old_path)
        except FileExistsError: 
            continue
    #--------------------------END

    #----Generate_File_Data_Tree----
    import os, json
    """
    This file creates the files structure in json format.  
    THIS IS NOT THE SAME AS TURNING FILE SYSTEM TO DATA TABLE
    """

    # Initiat Directory
    directory = dir_root
    test = os.walk(directory)

    def createFile(name: str, data):
        file = {
            "type" : "file",
            "data" : data
        }
        return file

    def createFolder(name: str, data):
        folder = {
            "type" : "folder",
            "data" : data,
            "children" : {}
        }
        return folder

    fileSystem = {directory : createFolder(directory,1)}
    for f in test:
        cwd = f[0]
        path = cwd.split('/')
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
            children[file] = createFile(file, 1)

        #print(os.stat(f[0]))
        #print('--------------')

    fileSystem = json.dumps(fileSystem, indent=4)
    print(fileSystem)

    FileSystemData = open("new_dir_org.json", "w")
    FileSystemData.write(fileSystem)
    #-------------------------------END
    
    #NOTE: return background agent output to user
    return answer

def sort_FS3(self,):
    """
    This tool sorts the user's file system. If asked to sort or to organize the file system based on the contents, summary, or text of the file, then call this function. Tell the user the return and results of the function call. This function has a required argument, mode. This argument is required and must be filled. For example, if users say "sort files by content", set mode to "content" when calling this function.

    Args: 

    Returns: 
        fileSort (str): This is the new organization of the file system users requested
    """
    #create another client to ask
    #Options are: content, extension, name, or date.
    # Query the user for the mode (valid modes are: content, extension, name, or date), before calling this function. 
    from letta import create_client 
    from letta import EmbeddingConfig, LLMConfig
    import json, os, re
    
    client = create_client()
    client.set_default_embedding_config(EmbeddingConfig.default_config(model_name="letta"))
    client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))

    #get json data
    #file = open('FileSystemData.json') #NOTE: hardCoded
    file = open('dataTable3.json') #NOTE: hardCoded
    fileData = json.load(file)
    #fileDataS = json.dumps(fileData)

    #create message to send to different agent
    #NOTE: 1 layer simple sort, based on name
    file_keys = fileData.keys()

    
    template = "\nTemplate:\n[group 1]{item 1, item2, ...}\n[group 2]{item 3, item 4, ...}\n...\nItems:"

    enforceSingle = "If an item has already be grouped, do not group it again. Thus, for each item listed, it should only appear once amoungst all groups. DO NOT CHANGE THE FILE NAMES. Return only the output template and nothing else:"
    
    #NOTE: when we say content, we are also refereing to file summary
    prompt = f"Using the template and given the following files, group the files into the template based on the commonalities of ONLY on the summary of the file."

    message = prompt + enforceSingle +template
    for k in file_keys:
        # print(k)
        try:
            message =  message + '\n file: "' + k + '" content: "' + fileData[k]['summary'] + '"'
            #TODO: maybe change content to summary 
        except KeyError:
            continue 
    
    

    print(f'Testing Output: {message}')

    #NOTE: for easier testing, try to start fresh so we know effect of prompting
    try:
        agentState = client.create_agent('background_agent')
    except ValueError:
        agentID = client.get_agent_id('background_agent')
        client.delete_agent(agentID)
        agentState = client.create_agent('background_agent')
    
    
    answer = client.send_message(
        message=message,
        role='user',
        agent_id=agentState.id
    )

    

    answer = answer.messages[1].function_call.arguments
    answer = json.loads(answer)
    answer = json.dumps(answer['message'])
    print("MY_ANSWER", answer)

    #self.interface.assistant_message(answer)  # , msg_obj=self._messages[-1])
    outputFile = open("newFileSystem.txt", 'w')
    outputFile.write(answer) #NOTE: Store background agent output

    #----ParsingGPT_FS----
    raw_folders = re.findall(r'(\[[\w\s\-\,\.\\\/\(\)]+\])', answer)
    # print(raw_folders)

    raw_files = re.findall(r'\{[\w\s\-\,\.\\\/\(\)]+\}', answer)
    # print(raw_files)

    #split and clean files
    files = []
    for f in raw_files:
        f = re.sub(r'[\{\}]', '', f)
        files.append(re.split(', ', f))
        # print(files)

    print('Files:  ', files)

    #clean folders
    folders = []
    for f in raw_folders:
        f = re.sub(r'[\[\]]', '', f)
        f = re.sub(r' ', '_', f)
        folders.append(re.split(', ', f)[0])

    print('Folders:  ', folders)

    #generate json file table
    fs_table = {}
    dir_root = 'uploads' #NOTE: Hard Coded
    for folder_i in range(len(folders)):
        for file_i in range(len(files[folder_i])):
            old_path = fileData[files[folder_i][file_i]]['path']

            fs_table[files[folder_i][file_i]] = {
                "type" : "file",
                "new_path" : f"{dir_root}/{folders[folder_i]}",
                "old_path" : old_path
            }
        
    print(json.dumps(fs_table, indent=4))
    #---------------------END


    #----CREATE_NEW_FS----
    import shutil
    for fileName in fs_table.keys():
        print('MOVING: ', fileName)
        try:
            os.mkdir(fs_table[fileName]['new_path'])
        except FileExistsError: 
            continue
        finally:
            shutil.move(fs_table[fileName]['old_path'] + "/" + fileName, fs_table[fileName]['new_path'] + "/" + fileName)
    #---------------------END

    #----DELETE_OLD_FOLDERS----
    for fileName in fs_table.keys():
        try:
            old_path = fs_table[fileName]['old_path']
            if old_path != dir_root:
                os.rmdir(old_path)
        except FileNotFoundError: 
            continue
    #--------------------------END

    #----Generate_File_Data_Tree----
    import os, json
    """
    This file creates the files structure in json format.  
    THIS IS NOT THE SAME AS TURNING FILE SYSTEM TO DATA TABLE
    """

    # Initiat Directory
    directory = dir_root
    test = os.walk(directory)

    def createFile(name: str, data):
        file = {
            "type" : "file",
            "data" : data
        }
        return file

    def createFolder(name: str, data):
        folder = {
            "type" : "folder",
            "data" : data,
            "children" : {}
        }
        return folder

    fileSystem = {directory : createFolder(directory,1)}
    for f in test:
        cwd = f[0]
        path = cwd.split('/')
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
            children[file] = createFile(file, 1)

        #print(os.stat(f[0]))
        #print('--------------')

    fileSystem = json.dumps(fileSystem, indent=4)
    print(fileSystem)

    FileSystemData = open("new_dir_org.json", "w")
    FileSystemData.write(fileSystem)
    #-------------------------------END
    
    #NOTE: return background agent output to user
    return answer

sort_FS_tool1 = client.create_tool(sort_FS1)
sort_FS_tool2 = client.create_tool(sort_FS2)
sort_FS_tool3 = client.create_tool(sort_FS3)

agentName = "interfaceAgent"

try:
    agent_1 = client.create_agent(
    name=agentName,
    tools=[x.name for x in client.list_tools()]
    )
except ValueError:
    agentID = client.get_agent_id(agentName)
    client.delete_agent(agentID)
    agent_1 = client.create_agent(
    name=agentName,
    tools=[x.name for x in client.list_tools()]
    )

# #NOTE: RESETS ENVIRONMENT TEST
# import shutil, os
# shutil.rmtree('TestDirectory3/')
# # os.mkdir('TestDirectory3')
# shutil.copytree('TestDirectory3(Origin)', 'TestDirectory3')