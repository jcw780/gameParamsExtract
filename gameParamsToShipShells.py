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
writeCondensed = False
if writeCondensed:
    print('Writing Condensed Files')
    checkMakeDir(condensedDirectory)
    writeToFile(condenseShip , condensedDirectory, 'condensendShips.json')
    writeToFile(condenseShell, condensedDirectory, 'condensendShells.json')
    writeToFile(condenseGun  , condensedDirectory, 'condensendGuns.json')

def selectEssential(data):
    targetKeys = set([
        "bulletAirDrag", 
        "bulletAlwaysRicochetAt",
        "bulletDetonator", 
        "bulletDetonatorThreshold", 
        "bulletDiametr", 
        "bulletKrupp", 
        "bulletMass", 
        "name", 
        "bulletRicochetAt", 
        "bulletSpeed",
        "bulletCapNormalizeMaxAngle"
    ])
    output = {}
    for target in targetKeys:
        output[target] = data[target]
    return output


shipShells = {}
shipShellData = {}
shipShellDataEssential = {}
for ship, attributes in condenseShip.items(): #Ship Art
    added = False
    upgrades = attributes["ShipUpgradeInfo"]
    artilleryNames = set()
    shellGroups = set()
    for upgradeName, upgradeInfo in upgrades.items():
        if type(upgradeInfo) is dict:
            if 'artillery' in upgradeInfo['components']:
                for artilleryName in upgradeInfo['components']['artillery']:
                    artilleryNames.add(artilleryName)

    shells = set()
    for artilleryName in artilleryNames:
        artilleryConfig = attributes[artilleryName]
        for turrets, turretValues in artilleryConfig.items():
            if type(turretValues) is dict:
                if 'typeinfo' in turretValues:
                    if turretValues['typeinfo']['species'] == 'Main':
                        shellGroup = ()
                        for shell in turretValues['ammoList']:
                            added = True
                            shells.add(shell)
                            shellGroup += shell,
                        shellGroups.add(shellGroup)
    
    shipShells[ship] = list(shells)
    if added:
        temp = {}
        tempEssential = {}
        for shell in shipShells[ship]:
            ammoType = condenseShell[shell]['ammoType']
            if not ammoType in temp:
                temp[ammoType] = {}
                tempEssential[ammoType] = {}
            temp[ammoType][shell] = condenseShell[shell]
            tempEssential[ammoType][shell] = selectEssential(condenseShell[shell])
        
        temp['Tier'] = attributes['level']
        temp['Nation'] = attributes['typeinfo']['nation']
        temp['ShellGroups'] = list(shellGroups)

        tempEssential['Tier'] = attributes['level']
        tempEssential['Nation'] = attributes['typeinfo']['nation']
        tempEssential['ShellGroups'] = list(shellGroups)

        shipShellData[ship] = temp
        shipShellDataEssential[ship] = tempEssential

writeShipShells = True
shipShellsDirectory = 'shipShells'
if writeShipShells:
    checkMakeDir(shipShellsDirectory)
    writeToFile(shipShells, shipShellsDirectory, 'shipShells.json')
    writeToFile(shipShellData, shipShellsDirectory, 'shipShellData.json')
    writeToFile(shipShellDataEssential, shipShellsDirectory, 'shipShellDataEssentials.json')            


    