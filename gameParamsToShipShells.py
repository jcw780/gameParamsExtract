import json, os

def checkMakeDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def writeToFile(data, filePath, file):
    filePathAppended = file
    if filePath:
        filePathAppended = F'{filePath}/{file}'
    
    with open(filePathAppended, 'w') as f:
        f.write(json.dumps(data, indent=4))
    

condenseShip = {}
condenseGun = {}
condenseShell = {}
#counter = 0

with open("GameParams.json", 'r') as f:
    data = json.load(f)
    for k, v in data.items():
        #print(k)
        #print(v["typeinfo"])
        if v["typeinfo"]["type"] == 'Ship':
            condenseShip[k] = v
        if v["typeinfo"]["type"] == 'Projectile':
            condenseShell[k] = v
        elif v["typeinfo"]["type"] == 'Gun' and v["typeinfo"]["species"] == 'Main':
            condenseGun[k] = v

condensedDirectory = 'condensed'
writeCondensed = True
if writeCondensed:
    print('Writing Condensed Files')
    checkMakeDir(condensedDirectory)
    writeToFile(condenseShip , condensedDirectory, 'condensendShips.json')
    writeToFile(condenseShell, condensedDirectory, 'condensendShells.json')
    writeToFile(condenseGun  , condensedDirectory, 'condensendGuns.json')


shipShells = {}
shipShellData = {}
for ship, artillery in condenseShip.items(): #Ship Art
    added = False
    for gun, gunV in artillery.items(): #Art HP
        if type(gunV) == type(dict()):
            for k, v in gunV.items(): #HP AL
                #print(vv)
                if type(v) == type(dict()):
                    if 'ammoList' in v:
                        if v['typeinfo']['species'] == 'Main':
                            ammoList = set()
                            for kvv, vvv in gunV.items():
                                #print(type(vvv))
                                #print(vvv)
                                if type(vvv) == type(dict()) and 'ammoList' in vvv:
                                    added = True
                                    for shell in vvv['ammoList']:
                                        ammoList.add(shell)
                                #ammoList.add(vvv['ammoList'])
                            
                            #print(ammoList)
                            if ship in shipShells:
                                shipShellsSet = set(shipShells[ship])
                                #print(shipShellsSet)
                                for shell in ammoList:
                                    shipShellsSet.add(shell)
                                if len(shipShells[ship]) <= 2 and len(shipShellsSet) > 2:
                                    print(ship)
                                shipShells[ship] = list(shipShellsSet)
                            else:
                                shipShells[ship] = list(ammoList)
                                if len(ammoList) > 2:
                                    print(ship)
                            #print(shipShells[ship])
    if added:
        temp = {}
        for shell in shipShells[ship]:
            temp[shell] = condenseShell[shell]
        shipShellData[ship] = temp

writeToFile(shipShells, '', 'shipShells.json')
writeToFile(shipShellData, '', 'shipShellData.json')            


    