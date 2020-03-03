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
#typeInfoTypes = set()
#typeInfoSpecies = set()
typeInfo = set()
with open("GameParams.json", 'r') as f:
    data = json.load(f)
    for k, v in data.items():
        #print(k)
        #print(v["typeinfo"])
        typeInfo.add((v["typeinfo"]["type"], v["typeinfo"]["species"]))
        if v["typeinfo"]["type"] == 'Ship':
            condenseShip[k] = v
        if v["typeinfo"]["type"] == 'Projectile':
            condenseShell[k] = v
        elif v["typeinfo"]["type"] == 'Gun' and v["typeinfo"]["species"] == 'Main':
            condenseGun[k] = v

print(typeInfo)
condensedDirectory = 'condensed'
writeCondensed = True
if writeCondensed:
    print('Writing Condensed Files')
    checkMakeDir(condensedDirectory)
    writeToFile(condenseShip , condensedDirectory, 'condensedShips.json')
    writeToFile(condenseShell, condensedDirectory, 'condensedShells.json')
    writeToFile(condenseGun  , condensedDirectory, 'condensedGuns.json')

def selectEssential(data):
    targetKeys = set([
        "alphaPiercingHE",
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
    for upgradeName, upgradeInfo in upgrades.items():
        if type(upgradeInfo) is dict:
            if 'artillery' in upgradeInfo['components']:
                for artilleryName in upgradeInfo['components']['artillery']:
                    artilleryNames.add(artilleryName)

    shellGroups = set()
    for artilleryName in artilleryNames:
        artilleryConfig = attributes[artilleryName]
        for turrets, turretValues in artilleryConfig.items():
            if type(turretValues) is dict:
                if 'typeinfo' in turretValues:
                    if turretValues['typeinfo']['species'] == 'Main':
                        shellGroup = ()
                        for shell in turretValues['ammoList']:
                            added = True
                            shellGroup += shell,
                        shellGroups.add(shellGroup)
    
    shellGroupsEnumerated = {F'Artillery{k}':v for k,v in enumerate(shellGroups)}
    shipShells[ship] = shellGroupsEnumerated
    if added:
        temp = {}
        tempEssential = {}
        #for shell in shipShells[ship]:
        for shellGroupNumbers, shellGroupAdded in shellGroupsEnumerated.items():
            temp[shellGroupNumbers] = {}
            tempEssential[shellGroupNumbers] = {}
            for shell in shellGroupAdded:
                ammoType = condenseShell[shell]['ammoType']
                if not ammoType in temp[shellGroupNumbers]:
                    temp[shellGroupNumbers][ammoType] = {}
                    tempEssential[shellGroupNumbers][ammoType] = {}
                temp[shellGroupNumbers][ammoType] = condenseShell[shell]
                tempEssential[shellGroupNumbers][ammoType] = selectEssential(condenseShell[shell])
        
        temp['Tier'] = attributes['level']
        temp['Nation'] = attributes['typeinfo']['nation']
        temp['Type'] = attributes['typeinfo']['species']
        temp['ammo_num'] = len(shellGroupsEnumerated)
        #temp['ShellGroups'] = {k: v for k, v in enumerate(shellGroups)}

        tempEssential['Tier'] = attributes['level']
        tempEssential['Nation'] = attributes['typeinfo']['nation']
        tempEssential['Type'] = attributes['typeinfo']['species']
        tempEssential['ammo_num'] = len(shellGroupsEnumerated)
        #tempEssential['ShellGroups'] = {k: v for k, v in enumerate(shellGroups)}

        shipShellData[ship] = temp
        shipShellDataEssential[ship] = tempEssential

writeShipShells = True
shipShellsDirectory = 'shipShells'
if writeShipShells:
    checkMakeDir(shipShellsDirectory)
    writeToFile(shipShells, shipShellsDirectory, 'shipShells.json')
    writeToFile(shipShellData, shipShellsDirectory, 'shipShellData.json')
    writeToFile(shipShellDataEssential, shipShellsDirectory, 'shipShellDataEssentials.json')            


    