import os, json
from datetime import datetime
from letta import create_client, EmbeddingConfig, LLMConfig, ChatMemory
import letta
from letta import AgentState

# Tools:
# extract_file_content
# summarize_file_content
# garbage_suggestion
# sort_FS
# sort_FS1
# sort_FS2
# sort_FS3


def extract_file_content(self, file_path: str) -> str:
    """
    Extracts content from a text-based file, limiting the amount of content returned.

    Args:
        file_path (str): The path to the file

    Returns:
        str: A portion of the extracted content or an error message if the file is not found or unsupported
    """
    import os
    import PyPDF2
    import magic

    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return None

    # Use python-magic to detect the file type - not reliant on just the extension
    ftype = magic.from_file(file_path, mime=True)
    content = ""

    try:
        if ftype == "text/plain":
            # Text files
            with open(file_path, "r") as file:
                content = file.read()
        elif ftype == "application/pdf":
            # PDF files
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = "\n".join(
                    page.extract_text() for page in pdf_reader.pages
                )
        else:
            print(f"Unsupported file type: {ftype}")
            return None

        # Limit the content to the first 1000 characters (or any number you prefer)
        max_length = 1000
        content_snippet = content[:max_length]

        print(f"Extracted content snippet from {file_path}")
        return content_snippet

    except Exception as e:
        print(f"An error occurred while reading the file: {str(e)}")
        return None


def summarize_file_content(self, file_path: str) -> str:
    """
    Extracts and summarizes the content from a file.

    Args:
        file_path (str): The path to the file

    Returns:
        str: The summary of the file content
    """
    content = self.extract_file_content(file_path)
    if not content:
        return "No content to summarize."

    # Send the content to Letta for summarization
    response = json.loads(
        str(
            client.send_message(
                agent_id=client.get_agent_id("file_extraction_agent"),
                role="user",
                message=f"Extract and summarize the content from the following file path: {file_path}. Provide an objective, assured summary without first-person or second-person language.",
            )
        )
    )
    # print(response)
    for i in response["messages"]:
        if i["message_type"] == "function_call":
            if i["function_call"]["name"] == "send_message":
                s = i["function_call"]["arguments"]
                print(s)
                return s.replace('{\n  "message": "', "").replace('"\n}', "")
    return "File summary unavailable"


def garbage_suggestion(self):
    """
    Goes through the summaries of all files and determines which may be fit for deletion.
    If prompted to recommend files to delete or which files may be garbage, call this function.

    Args:
        tablePath (str): The path to the JSON data table
    """
    import json
    from letta import create_client, EmbeddingConfig, LLMConfig

    background_client = create_client()

    background_client.set_default_embedding_config(
        EmbeddingConfig.default_config(model_name="letta")
    )
    background_client.set_default_llm_config(
        LLMConfig.default_config(model_name="letta")
    )

    # JSON table path
    tableName = "combinedFileDataTable.json"
    path = ""

    summaries = []
    files = []

    def get_all_summaries(dic, path):

        for key, value in dic.items():
            if key == "summary":
                yield (value, path)
            elif isinstance(value, dict):
                path = key
                yield from get_all_summaries(value, path)

    with open(tableName, "r") as f:
        dic = json.load(f)

        for x in get_all_summaries(dic, path):
            summaries.append(x[0])
            files.append(x[1])

    if background_client.get_agent_id("background_agent"):
        background_client.delete_agent(
            background_client.get_agent_id("background_agent")
        )

    agentState = background_client.create_agent("background_agent")

    # Number of deletion suggestions
    num = 3

    message = f"Please decide which {num} entries in the list {summaries} you would recommend deleting based on the content of their summaries. Do not tell me. Use the indices from that list and tell me the corresponding file names from the list {files} that I should delete. Only give me {num} files."

    answer = background_client.send_message(
        message=message, role="user", agent_id=agentState.id
    )

    answer = answer.messages[1].function_call.arguments

    return answer


def sort_FS(self, mode: str):
    """
    This tool sorts the user's file system. If asked to sort or to organize the file system, call this function. Tell the user the return and results of the function call. This function has a required argument, mode. This argument is required and must be filled. For example, if users say "sort files by content", set mode to "content" when calling this function.

    Args:
        mode (str): The mode for sorting. This argument is required and must be filled. For example, if users say "sort files by content", set mode to "content" when calling this function.

    Returns:
        fileSort (str): This is the new organization of the file system users requested
    """
    # create another client to ask
    # Options are: content, extension, name, or date.
    # Query the user for the mode (valid modes are: content, extension, name, or date), before calling this function.
    from letta import create_client
    from letta import EmbeddingConfig, LLMConfig
    import json, os, re

    client = create_client()
    client.set_default_embedding_config(
        EmbeddingConfig.default_config(model_name="letta")
    )
    client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))

    # get json data
    # file = open('FileSystemData.json') #NOTE: hardCoded
    file = open("dataTable3.json")  # NOTE: hardCoded
    fileData = json.load(file)
    # fileDataS = json.dumps(fileData)

    # create message to send to different agent
    # NOTE: 1 layer simple sort, based on name
    file_keys = fileData.keys()

    template = "\nTemplate:\n[group 1]{item 1, item2, ...}\n[group 2]{item 3, item 4, ...}\n...\nItems:"

    enforceSingle = "If an item has already be grouped, do not group it again. Thus, for each item listed, it should only appear once amoungst all groups. DO NOT CHANGE THE FILE NAMES. Return only the output template and nothing else:"

    if mode == "name":
        prompt = f"Using the template and given the following files, group the files into the template based on the commonalities in the topic, semantics, or meanings of the names. Ignore the file extension or file type"

        message = prompt + enforceSingle + template
        for k in file_keys:
            message = message + "\n" + k

    elif mode == "extension":
        prompt = f"Using the template and given the following files, group the files into the template based on the commonalities of ONLY on the {mode}s of the file, and not on the name."

        message = prompt + enforceSingle + template
        for k in file_keys:
            message = message + "\n" + k
    elif mode == "content":
        # NOTE: when we say content, we are also refereing to file summary
        prompt = f"Using the template and given the following files, group the files into the template based on the commonalities of ONLY on the summary of the file."

        message = prompt + enforceSingle + template
        for k in file_keys:
            # print(k)
            try:
                message = (
                    message
                    + '\n file: "'
                    + k
                    + '" content: "'
                    + fileData[k]["summary"]
                    + '"'
                )
                # TODO: maybe change content to summary
            except KeyError:
                continue

    print(f"Testing Output: {message}")

    # NOTE: for easier testing, try to start fresh so we know effect of prompting
    try:
        agentState = client.create_agent("background_agent")
    except ValueError:
        agentID = client.get_agent_id("background_agent")
        client.delete_agent(agentID)
        agentState = client.create_agent("background_agent")

    answer = client.send_message(
        message=message, role="user", agent_id=agentState.id
    )

    answer = answer.messages[1].function_call.arguments
    answer = json.loads(answer)
    answer = json.dumps(answer["message"])
    print("MY_ANSWER", answer)

    # self.interface.assistant_message(answer)  # , msg_obj=self._messages[-1])
    outputFile = open("newFileSystem.txt", "w")
    outputFile.write(answer)  # NOTE: Store background agent output

    # ----ParsingGPT_FS----
    raw_folders = re.findall(r"(\[[\w\s\-\,\.\\\/\(\)]+\])", answer)
    # print(raw_folders)

    raw_files = re.findall(r"\{[\w\s\-\,\.\\\/\(\)]+\}", answer)
    # print(raw_files)

    # split and clean files
    files = []
    for f in raw_files:
        f = re.sub(r"[\{\}]", "", f)
        files.append(re.split(", ", f))
        # print(files)

    print("Files:  ", files)

    # clean folders
    folders = []
    for f in raw_folders:
        f = re.sub(r"[\[\]]", "", f)
        f = re.sub(r" ", "_", f)
        folders.append(re.split(", ", f)[0])

    print("Folders:  ", folders)

    # generate json file table
    fs_table = {}
    dir_root = "TestDirectory3"  # NOTE: Hard Coded
    for folder_i in range(len(folders)):
        for file_i in range(len(files[folder_i])):
            old_path = fileData[files[folder_i][file_i]]["path"]

            fs_table[files[folder_i][file_i]] = {
                "type": "file",
                "new_path": f"{dir_root}/{folders[folder_i]}",
                "old_path": old_path,
            }

    print(json.dumps(fs_table, indent=4))
    # ---------------------END

    # ----CREATE_NEW_FOLDERS/MOVE_FILES----
    import shutil

    for fileName in fs_table.keys():
        print("MOVING: ", fileName)
        try:
            os.mkdir(fs_table[fileName]["new_path"])
        except FileExistsError:
            continue
        finally:
            shutil.move(
                fs_table[fileName]["old_path"] + "/" + fileName,
                fs_table[fileName]["new_path"] + "/" + fileName,
            )
    # ---------------------END

    # ----DELETE_OLD_FOLDERS----
    for fileName in fs_table.keys():
        try:
            old_path = fs_table[fileName]["old_path"]
            if old_path != dir_root:
                os.rmdir(old_path)
        except FileExistsError:
            continue
    # --------------------------END

    # NOTE: return background agent output to user
    return answer


def sort_FS1(
    self,
):
    """
    This tool sorts the user's file system. If asked to sort or to organize the file system by the NAMES and/or TITLE of the files, call this function. Tell the user the return and results of the function call. This function has a required argument, mode. This argument is required and must be filled. For example, if users say "sort files by content", set mode to "content" when calling this function.

    Args:

    Returns:
        fileSort (str): This is the new organization of the file system users requested
    """
    # create another client to ask
    # Options are: content, extension, name, or date.
    # Query the user for the mode (valid modes are: content, extension, name, or date), before calling this function.
    from letta import create_client
    from letta import EmbeddingConfig, LLMConfig
    import json, os, re

    client = create_client()
    client.set_default_embedding_config(
        EmbeddingConfig.default_config(model_name="letta")
    )
    client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))

    # get json data
    # file = open('FileSystemData.json') #NOTE: hardCoded
    file = open("dataTable3.json")  # NOTE: hardCoded
    fileData = json.load(file)
    # fileDataS = json.dumps(fileData)

    # create message to send to different agent
    # NOTE: 1 layer simple sort, based on name
    file_keys = fileData.keys()

    template = "\nTemplate:\n[group 1]{item 1, item2, ...}\n[group 2]{item 3, item 4, ...}\n...\nItems:"

    enforceSingle = "If an item has already be grouped, do not group it again. Thus, for each item listed, it should only appear once amoungst all groups. DO NOT CHANGE THE FILE NAMES. Return only the output template and nothing else:"

    prompt = f"Using the template and given the following files, group the files into the template based on the commonalities in the topic, semantics, or meanings of the names. Ignore the file extension or file type"

    message = prompt + enforceSingle + template
    for k in file_keys:
        message = message + "\n" + k

    print(f"Testing Output: {message}")

    # NOTE: for easier testing, try to start fresh so we know effect of prompting
    try:
        agentState = client.create_agent("background_agent")
    except ValueError:
        agentID = client.get_agent_id("background_agent")
        client.delete_agent(agentID)
        agentState = client.create_agent("background_agent")

    answer = client.send_message(
        message=message, role="user", agent_id=agentState.id
    )

    answer = answer.messages[1].function_call.arguments
    answer = json.loads(answer)
    answer = json.dumps(answer["message"])
    print("MY_ANSWER", answer)

    # self.interface.assistant_message(answer)  # , msg_obj=self._messages[-1])
    outputFile = open("newFileSystem.txt", "w")
    outputFile.write(answer)  # NOTE: Store background agent output

    # ----ParsingGPT_FS----
    raw_folders = re.findall(r"(\[[\w\s\-\,\.\\\/\(\)]+\])", answer)
    # print(raw_folders)

    raw_files = re.findall(r"\{[\w\s\-\,\.\\\/\(\)]+\}", answer)
    # print(raw_files)

    # split and clean files
    files = []
    for f in raw_files:
        f = re.sub(r"[\{\}]", "", f)
        files.append(re.split(", ", f))
        # print(files)

    print("Files:  ", files)

    # clean folders
    folders = []
    for f in raw_folders:
        f = re.sub(r"[\[\]]", "", f)
        f = re.sub(r" ", "_", f)
        folders.append(re.split(", ", f)[0])

    print("Folders:  ", folders)

    # generate json file table
    fs_table = {}
    dir_root = "TestDirectory3"  # NOTE: Hard Coded
    for folder_i in range(len(folders)):
        for file_i in range(len(files[folder_i])):
            old_path = fileData[files[folder_i][file_i]]["path"]

            fs_table[files[folder_i][file_i]] = {
                "type": "file",
                "new_path": f"{dir_root}/{folders[folder_i]}",
                "old_path": old_path,
            }

    print(json.dumps(fs_table, indent=4))
    # ---------------------END

    # ----CREATE_NEW_FS----
    import shutil

    for fileName in fs_table.keys():
        print("MOVING: ", fileName)
        try:
            os.mkdir(fs_table[fileName]["new_path"])
        except FileExistsError:
            continue
        finally:
            shutil.move(
                fs_table[fileName]["old_path"] + "/" + fileName,
                fs_table[fileName]["new_path"] + "/" + fileName,
            )
    # ---------------------END

    # ----DELETE_OLD_FOLDERS----
    for fileName in fs_table.keys():
        try:
            old_path = fs_table[fileName]["old_path"]
            if old_path != dir_root:
                os.rmdir(old_path)
        except FileExistsError:
            continue
    # --------------------------END

    # ----Generate_File_Data_Tree----
    import os, json

    """
    This file creates the files structure in json format.  
    THIS IS NOT THE SAME AS TURNING FILE SYSTEM TO DATA TABLE
    """

    # Initiat Directory
    directory = dir_root
    test = os.walk(directory)

    def createFile(name: str, data):
        file = {"type": "file", "data": data}
        return file

    def createFolder(name: str, data):
        folder = {"type": "folder", "data": data, "children": {}}
        return folder

    fileSystem = {directory: createFolder(directory, 1)}
    for f in test:
        cwd = f[0]
        path = cwd.split("/")
        folders = f[1]
        files = f[2]

        # get current folder
        currentFolder = fileSystem[path[0]]
        for p in path[1:]:
            currentFolder = currentFolder["children"]
            currentFolder = currentFolder[p]

        # add folders
        # print(currentFolder)
        for folder in folders:
            children = currentFolder["children"]
            children[folder] = createFolder(folder, 1)

        # add files
        for file in files:
            children = currentFolder["children"]
            children[file] = createFile(file, 1)

        # print(os.stat(f[0]))
        # print('--------------')

    fileSystem = json.dumps(fileSystem, indent=4)
    print(fileSystem)

    FileSystemData = open("new_dir_org.json", "w")
    FileSystemData.write(fileSystem)
    # -------------------------------END

    # NOTE: return background agent output to user
    return answer


def sort_FS2(
    self,
):
    """
    This tool sorts the user's file system. If asked to sort or to organize based on the EXTENSIONS of the files, call this function. Tell the user the return and results of the function call. This function has a required argument, mode. This argument is required and must be filled. For example, if users say "sort files by content", set mode to "content" when calling this function.


    Args:

    Returns:
        fileSort (str): This is the new organization of the file system users requested
    """
    # create another client to ask
    # Options are: content, extension, name, or date.
    # Query the user for the mode (valid modes are: content, extension, name, or date), before calling this function.
    from letta import create_client
    from letta import EmbeddingConfig, LLMConfig
    import json, os, re

    client = create_client()
    client.set_default_embedding_config(
        EmbeddingConfig.default_config(model_name="letta")
    )
    client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))

    # get json data
    # file = open('FileSystemData.json') #NOTE: hardCoded
    file = open("dataTable3.json")  # NOTE: hardCoded
    fileData = json.load(file)
    # fileDataS = json.dumps(fileData)

    # create message to send to different agent
    # NOTE: 1 layer simple sort, based on name
    file_keys = fileData.keys()

    template = "\nTemplate:\n[group 1]{item 1, item2, ...}\n[group 2]{item 3, item 4, ...}\n...\nItems:"

    enforceSingle = "If an item has already be grouped, do not group it again. Thus, for each item listed, it should only appear once amoungst all groups. DO NOT CHANGE THE FILE NAMES. Return only the output template and nothing else:"

    prompt = f"Using the template and given the following files, group the files into the template based on the commonalities of ONLY on the extensions of the file, and not on the name."

    message = prompt + enforceSingle + template
    for k in file_keys:
        message = message + "\n" + k

    print(f"Testing Output: {message}")

    # NOTE: for easier testing, try to start fresh so we know effect of prompting
    try:
        agentState = client.create_agent("background_agent")
    except ValueError:
        agentID = client.get_agent_id("background_agent")
        client.delete_agent(agentID)
        agentState = client.create_agent("background_agent")

    answer = client.send_message(
        message=message, role="user", agent_id=agentState.id
    )

    answer = answer.messages[1].function_call.arguments
    answer = json.loads(answer)
    answer = json.dumps(answer["message"])
    print("MY_ANSWER", answer)

    # self.interface.assistant_message(answer)  # , msg_obj=self._messages[-1])
    outputFile = open("newFileSystem.txt", "w")
    outputFile.write(answer)  # NOTE: Store background agent output

    # ----ParsingGPT_FS----
    raw_folders = re.findall(r"(\[[\w\s\-\,\.\\\/\(\)]+\])", answer)
    # print(raw_folders)

    raw_files = re.findall(r"\{[\w\s\-\,\.\\\/\(\)]+\}", answer)
    # print(raw_files)

    # split and clean files
    files = []
    for f in raw_files:
        f = re.sub(r"[\{\}]", "", f)
        files.append(re.split(", ", f))
        # print(files)

    print("Files:  ", files)

    # clean folders
    folders = []
    for f in raw_folders:
        f = re.sub(r"[\[\]]", "", f)
        f = re.sub(r" ", "_", f)
        folders.append(re.split(", ", f)[0])

    print("Folders:  ", folders)

    # generate json file table
    fs_table = {}
    dir_root = "TestDirectory3"  # NOTE: Hard Coded
    for folder_i in range(len(folders)):
        for file_i in range(len(files[folder_i])):
            old_path = fileData[files[folder_i][file_i]]["path"]

            fs_table[files[folder_i][file_i]] = {
                "type": "file",
                "new_path": f"{dir_root}/{folders[folder_i]}",
                "old_path": old_path,
            }

    print(json.dumps(fs_table, indent=4))
    # ---------------------END

    # ----CREATE_NEW_FS----
    import shutil

    for fileName in fs_table.keys():
        print("MOVING: ", fileName)
        try:
            os.mkdir(fs_table[fileName]["new_path"])
        except FileExistsError:
            continue
        finally:
            shutil.move(
                fs_table[fileName]["old_path"] + "/" + fileName,
                fs_table[fileName]["new_path"] + "/" + fileName,
            )
    # ---------------------END

    # ----DELETE_OLD_FOLDERS----
    for fileName in fs_table.keys():
        try:
            old_path = fs_table[fileName]["old_path"]
            if old_path != dir_root:
                os.rmdir(old_path)
        except FileExistsError:
            continue
    # --------------------------END

    # ----Generate_File_Data_Tree----
    import os, json

    """
    This file creates the files structure in json format.  
    THIS IS NOT THE SAME AS TURNING FILE SYSTEM TO DATA TABLE
    """

    # Initiat Directory
    directory = dir_root
    test = os.walk(directory)

    def createFile(name: str, data):
        file = {"type": "file", "data": data}
        return file

    def createFolder(name: str, data):
        folder = {"type": "folder", "data": data, "children": {}}
        return folder

    fileSystem = {directory: createFolder(directory, 1)}
    for f in test:
        cwd = f[0]
        path = cwd.split("/")
        folders = f[1]
        files = f[2]

        # get current folder
        currentFolder = fileSystem[path[0]]
        for p in path[1:]:
            currentFolder = currentFolder["children"]
            currentFolder = currentFolder[p]

        # add folders
        # print(currentFolder)
        for folder in folders:
            children = currentFolder["children"]
            children[folder] = createFolder(folder, 1)

        # add files
        for file in files:
            children = currentFolder["children"]
            children[file] = createFile(file, 1)

        # print(os.stat(f[0]))
        # print('--------------')

    fileSystem = json.dumps(fileSystem, indent=4)
    print(fileSystem)

    FileSystemData = open("new_dir_org.json", "w")
    FileSystemData.write(fileSystem)
    # -------------------------------END

    # NOTE: return background agent output to user
    return answer


def sort_FS3(
    self,
):
    """
    This tool sorts the user's file system. If asked to sort or to organize the file system based on the contents, summary, or text of the file, then call this function. Tell the user the return and results of the function call. This function has a required argument, mode. This argument is required and must be filled. For example, if users say "sort files by content", set mode to "content" when calling this function.

    Args:

    Returns:
        fileSort (str): This is the new organization of the file system users requested
    """
    # create another client to ask
    # Options are: content, extension, name, or date.
    # Query the user for the mode (valid modes are: content, extension, name, or date), before calling this function.
    from letta import create_client
    from letta import EmbeddingConfig, LLMConfig
    import json, os, re

    client = create_client()
    client.set_default_embedding_config(
        EmbeddingConfig.default_config(model_name="letta")
    )
    client.set_default_llm_config(LLMConfig.default_config(model_name="letta"))

    # get json data
    # file = open('FileSystemData.json') #NOTE: hardCoded
    file = open("dataTable3.json")  # NOTE: hardCoded
    fileData = json.load(file)
    # fileDataS = json.dumps(fileData)

    # create message to send to different agent
    # NOTE: 1 layer simple sort, based on name
    file_keys = fileData.keys()

    template = "\nTemplate:\n[group 1]{item 1, item2, ...}\n[group 2]{item 3, item 4, ...}\n...\nItems:"

    enforceSingle = "If an item has already be grouped, do not group it again. Thus, for each item listed, it should only appear once amoungst all groups. DO NOT CHANGE THE FILE NAMES. Return only the output template and nothing else:"

    # NOTE: when we say content, we are also refereing to file summary
    prompt = f"Using the template and given the following files, group the files into the template based on the commonalities of ONLY on the summary of the file."

    message = prompt + enforceSingle + template
    for k in file_keys:
        # print(k)
        try:
            message = (
                message
                + '\n file: "'
                + k
                + '" content: "'
                + fileData[k]["summary"]
                + '"'
            )
            # TODO: maybe change content to summary
        except KeyError:
            continue

    print(f"Testing Output: {message}")

    # NOTE: for easier testing, try to start fresh so we know effect of prompting
    try:
        agentState = client.create_agent("background_agent")
    except ValueError:
        agentID = client.get_agent_id("background_agent")
        client.delete_agent(agentID)
        agentState = client.create_agent("background_agent")

    answer = client.send_message(
        message=message, role="user", agent_id=agentState.id
    )

    answer = answer.messages[1].function_call.arguments
    answer = json.loads(answer)
    answer = json.dumps(answer["message"])
    print("MY_ANSWER", answer)

    # self.interface.assistant_message(answer)  # , msg_obj=self._messages[-1])
    outputFile = open("newFileSystem.txt", "w")
    outputFile.write(answer)  # NOTE: Store background agent output

    # ----ParsingGPT_FS----
    raw_folders = re.findall(r"(\[[\w\s\-\,\.\\\/\(\)]+\])", answer)
    # print(raw_folders)

    raw_files = re.findall(r"\{[\w\s\-\,\.\\\/\(\)]+\}", answer)
    # print(raw_files)

    # split and clean files
    files = []
    for f in raw_files:
        f = re.sub(r"[\{\}]", "", f)
        files.append(re.split(", ", f))
        # print(files)

    print("Files:  ", files)

    # clean folders
    folders = []
    for f in raw_folders:
        f = re.sub(r"[\[\]]", "", f)
        f = re.sub(r" ", "_", f)
        folders.append(re.split(", ", f)[0])

    print("Folders:  ", folders)

    # generate json file table
    fs_table = {}
    dir_root = "TestDirectory3"  # NOTE: Hard Coded
    for folder_i in range(len(folders)):
        for file_i in range(len(files[folder_i])):
            old_path = fileData[files[folder_i][file_i]]["path"]

            fs_table[files[folder_i][file_i]] = {
                "type": "file",
                "new_path": f"{dir_root}/{folders[folder_i]}",
                "old_path": old_path,
            }

    print(json.dumps(fs_table, indent=4))
    # ---------------------END

    # ----CREATE_NEW_FS----
    import shutil

    for fileName in fs_table.keys():
        print("MOVING: ", fileName)
        try:
            os.mkdir(fs_table[fileName]["new_path"])
        except FileExistsError:
            continue
        finally:
            shutil.move(
                fs_table[fileName]["old_path"] + "/" + fileName,
                fs_table[fileName]["new_path"] + "/" + fileName,
            )
    # ---------------------END

    # ----DELETE_OLD_FOLDERS----
    for fileName in fs_table.keys():
        try:
            old_path = fs_table[fileName]["old_path"]
            if old_path != dir_root:
                os.rmdir(old_path)
        except FileNotFoundError:
            continue
    # --------------------------END

    # ----Generate_File_Data_Tree----
    import os, json

    """
    This file creates the files structure in json format.  
    THIS IS NOT THE SAME AS TURNING FILE SYSTEM TO DATA TABLE
    """

    # Initiat Directory
    directory = dir_root
    test = os.walk(directory)

    def createFile(name: str, data):
        file = {"type": "file", "data": data}
        return file

    def createFolder(name: str, data):
        folder = {"type": "folder", "data": data, "children": {}}
        return folder

    fileSystem = {directory: createFolder(directory, 1)}
    for f in test:
        cwd = f[0]
        path = cwd.split("/")
        folders = f[1]
        files = f[2]

        # get current folder
        currentFolder = fileSystem[path[0]]
        for p in path[1:]:
            currentFolder = currentFolder["children"]
            currentFolder = currentFolder[p]

        # add folders
        # print(currentFolder)
        for folder in folders:
            children = currentFolder["children"]
            children[folder] = createFolder(folder, 1)

        # add files
        for file in files:
            children = currentFolder["children"]
            children[file] = createFile(file, 1)

        # print(os.stat(f[0]))
        # print('--------------')

    fileSystem = json.dumps(fileSystem, indent=4)
    print(fileSystem)

    FileSystemData = open("new_dir_org.json", "w")
    FileSystemData.write(fileSystem)
    # -------------------------------END

    # NOTE: return background agent output to user
    return answer