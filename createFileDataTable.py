import os, json

"""
This file creates a data table of files
"""

def createFile(data, location):
    file = {
        "type" : "file",
        "path" : location,
        "data" : data,
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
directory = "TestDirectory2"
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
        fileSystem[file] = createFile(1, cwd)

    print(os.stat(f[0]))
    print('--------------')

fileSystem = json.dumps(fileSystem, indent=4)
print(fileSystem)

FileSystemData = open("dataTable.json", "w")
FileSystemData.write(fileSystem)