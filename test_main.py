import json

file1 = open("testTable.json")
jsonfile = json.load(file1)
#print(json.dumps(jsonfile, indent=4))
print(jsonfile[0]['children'])

