import json, os, sys, hashlib
import toJsonReduceIntermediary

tgtFolder = sys.argv[1]
#versionFolderName = sys.argv[1]

toJsonReduceIntermediary.run(tgtFolder)

def checkMakeDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def writeToFile(data, filePath, file):
    filePathAppended = file
    if filePath:
        filePathAppended = F'{filePath}/{file}'
    
    with open(filePathAppended, 'w') as f:
        f.write(json.dumps(data, indent=4, sort_keys=True))

def checkHash(file):
    BUF_SIZE = 32768 # Read file in 32kb chunks
    sha256 = hashlib.sha256()
    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

# Basically condenseGameParams.py ...
condenseShip = {}
condenseSecondaryGun = {}
condenseMainGun = {}
condenseShell = {}
typeInfo = {}
with open(F"{tgtFolder}/GameParams.json", 'r') as f:
    data = json.load(f)
    for k, v in data.items():
        #print(k)
        #print(v["typeinfo"])
        species = v["typeinfo"]["species"]
        typeV = v["typeinfo"]["type"]
        if not typeV in typeInfo:
            typeInfo[typeV] = set()
        typeInfo[typeV].add(species)

        if v["typeinfo"]["type"] == 'Ship':
            condenseShip[k] = v
        if v["typeinfo"]["type"] == 'Projectile' and v["typeinfo"]["species"] == 'Artillery':
            condenseShell[k] = v
        elif v["typeinfo"]["type"] == 'Gun' and v["typeinfo"]["species"] == 'Main':
            condenseMainGun[k] = v
        elif v["typeinfo"]["type"] == 'Gun' and v["typeinfo"]["species"] == 'Secondary':
            condenseSecondaryGun[k] = v

#print(typeInfo)
condensedDirectory = F'{tgtFolder}/condensed'
writeCondensed = True
if writeCondensed:
    print('Writing Condensed Files')
    checkMakeDir(condensedDirectory)
    writeToFile(condenseShip        , condensedDirectory, 'condensedShips.json')
    writeToFile(condenseShell       , condensedDirectory, 'condensedShells.json')
    writeToFile(condenseMainGun     , condensedDirectory, 'condensedMainGuns.json')
    writeToFile(condenseSecondaryGun, condensedDirectory, 'condensedSecondaryGuns.json')

def selectEssential(data):
    targetKeys = set([
        "alphaPiercingHE",
        "alphaPiercingCS",
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
        if target in data:
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
shipShellsDirectory = F'{tgtFolder}/shipShells'
if writeShipShells:
    checkMakeDir(shipShellsDirectory)
    print('Writing Ship Shells')
    writeToFile(shipShells, shipShellsDirectory, 'shipShells.json')
    writeToFile(shipShellData, shipShellsDirectory, 'shipShellData.json')
    writeToFile(shipShellDataEssential, shipShellsDirectory, 'shipShellDataEssentials.json')

shellData = shipShellDataEssential
#with open('shipShells/shipShellDataEssentials.json') as f:
#    shellData = json.load(f)

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

versionFolder = F'{tgtFolder}/version'
checkMakeDir(versionFolder)
writeToFile(sorted(list(output['nationList'])), versionFolder, 'nations.json')

for nations in output['nationList']:
    checkMakeDir(F'{versionFolder}/{nations}')

print('Writing static files')
nationTypeHashes = {}
for nations, nationData in output.items():
    if type(nationData) == dict:
        #print(nationData)
        for types, typeData in nationData.items():
            if types != 'shiptypes':
                writeToFile(typeData, F'{versionFolder}/{nations}', F'{nations}_{types}.json')
                nationTypeHashes[F'{nations}_{types}'] = checkHash(F'{versionFolder}/{nations}/{nations}_{types}.json')
        writeToFile(sorted(list(nationData['shiptypes']), reverse=True), F'{versionFolder}/{nations}', F'shiptypes.json')

writeToFile(nationTypeHashes, tgtFolder, 'hashes.json')