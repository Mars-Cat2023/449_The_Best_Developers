import os, json
"""
This file creates the files structure in json format.  
"""

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

# Initiat Directory
directory = "TestDirectory3"
test = os.walk(directory)
fileSystem = {directory : createFolder(directory,1)}

for f in test:
    print(f)
    print(f[0])
    
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
    print(currentFolder)
    for folder in folders:
        children = currentFolder['children']
        children[folder] = createFolder(folder, 1)
        

    #add files
    for file in files:
        children = currentFolder['children']
        children[file] = createFile(file, 1)

    print(os.stat(f[0]))
    print('--------------')

fileSystem = json.dumps(fileSystem, indent=4)
print(fileSystem)

FileSystemData = open("FileSystemData3.json", "w")
FileSystemData.write(fileSystem)

# test = os.scandir(directory)
# for f in test:
#     print(f)
#     print(f.stat().st_mtime)