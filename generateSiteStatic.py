import json, os

shellData = {}
with open('shipShells/shipShellDataEssentials.json') as f:
    shellData = json.load(f)

output = {}
output['nationList'] = set()
for ship, data in shellData.items():
    nation = data['Nation'] 
    if not nation in output:
        output['nationList'].add(data['Nation'])
        output[nation] = {}
        output[nation]['shiptypes'] = set()

    Type = data['Type']
    if not Type in output[nation]:
        output[nation]['shiptypes'].add(Type)
        output[nation][Type] = {}
    
    output[nation][Type][ship] = data

def checkMakeDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def writeToFile(data, filePath, file):
    filePathAppended = file
    if filePath:
        filePathAppended = F'{filePath}/{file}'
    
    with open(filePathAppended, 'w') as f:
        f.write(json.dumps(data, indent=4))

versionFolder = '0.9.1.1'
checkMakeDir(versionFolder)
writeToFile(sorted(list(output['nationList'])), versionFolder, 'nations.json')

for nations in output['nationList']:
    checkMakeDir(F'{versionFolder}/{nations}')

for nations, nationData in output.items():
    if type(nationData) == dict:
        #print(nationData)
        for types, typeData in nationData.items():
            if types != 'shiptypes':
                writeToFile(typeData, F'{versionFolder}/{nations}', F'{nations}_{types}.json')
        writeToFile(sorted(list(nationData['shiptypes']), reverse=True), F'{versionFolder}/{nations}', F'shiptypes.json')






