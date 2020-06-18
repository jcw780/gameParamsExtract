import json, os, hashlib, zlib, argparse
from multiprocessing import Pool
import toJsonReduceIntermediary

def checkMakeDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, Something):
            return 'CustomSomethingRepresentation'
        return json.JSONEncoder.default(self, obj)

def writeToFile(data, filePath: str, file: str, prettyPrint: bool = True, compress:bool = False):
    filePathAppended = file
    if filePath:
        filePathAppended = F'{filePath}/{file}'
    
    outputString = ''
    if prettyPrint:
        outputString = json.dumps(data, indent=4, sort_keys=True, cls=SetEncoder)
    else:
        outputString = json.dumps(data, cls=SetEncoder)

    output = outputString
    if compress:
        output = outputString.encode('utf-8')
        with open(filePathAppended, 'wb') as f:
            f.write(zlib.compress(output))
    else:
        with open(filePathAppended, 'w') as f:
            f.write(outputString)

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

def run(tgtFolder, outputName, existing):
    extract = True
    readFile = 'gameparams'
    gPHash = ''
    if existing:
        tempRF = existing
        if os.path.isfile(F'{tgtFolder}/{tempRF}.json'):
            extract = False
            gPHash = checkHash(F'{tgtFolder}/{tempRF}.json')
            readFile = tempRF
    if extract:
        gPHash = toJsonReduceIntermediary.run(tgtFolder, cleanup=True, outputName=readFile)
    print(F'{os.path.basename(tgtFolder)}: SHA256: {gPHash}')

    # Basically condenseGameParams.py ...
    condenseShip = {}
    condenseSecondaryGun = {}
    condenseMainGun = {}
    condenseShell = {}
    typeInfo = {}
    with open(F"{tgtFolder}/{readFile}.json", 'r') as f:
        data = json.load(f)
        for k, v in data.items():
            #print(k)
            #print(v["typeinfo"])
            #print(v)
            species = v["typeinfo"]["species"]
            typeV = v["typeinfo"]["type"]
            if not typeV in typeInfo:
                typeInfo[typeV] = set()
            typeInfo[typeV].add(species)

            #Isolate each object type
            if typeV == 'Ship':
                condenseShip[k] = v
            if typeV == 'Projectile' and species == 'Artillery':
                condenseShell[k] = v
            elif typeV == 'Gun' and species == 'Main':
                condenseMainGun[k] = v
            elif typeV == 'Gun' and species == 'Secondary':
                condenseSecondaryGun[k] = v

    #print(typeInfo)
    condensedDirectory = F'{tgtFolder}/condensed'
    writeCondensed = False
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

    # Convert to: 
    # ship : {artGroup: {shell : data}}
    shipShellName = {}
    for ship, attributes in condenseShip.items(): #Ship Art
        added = False
        upgrades = attributes["ShipUpgradeInfo"]
        artilleryNames = set()
        for upgradeName, upgradeInfo in upgrades.items():
            if type(upgradeInfo) is dict:
                if 'artillery' in upgradeInfo['components']:
                    for artilleryName in upgradeInfo['components']['artillery']:
                        artilleryNames.add(artilleryName)

        shellGroupsEnumerated = {}
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
                            shellGroupsEnumerated[artilleryName] = shellGroup  
        
        if added:
            nameOnly = {'artillery': {},}
            nameOnlyArt = nameOnly['artillery']
            for shellGroupNumbers, shellGroupAdded in shellGroupsEnumerated.items():
                nameOnlyArt[shellGroupNumbers] = {}
                nameOnlySGN = nameOnlyArt[shellGroupNumbers]

                for shell in shellGroupAdded:
                    ammoType = condenseShell[shell]['ammoType']
                    if not ammoType in nameOnlySGN:
                        nameOnlySGN[ammoType] = {}
                    nameOnlySGN[ammoType] = shell
            
            tier = attributes['level']
            nation = attributes['typeinfo']['nation']
            sType = attributes['typeinfo']['species']
            ammo = len(shellGroupsEnumerated)
            
            nameOnly['Tier'] = tier
            nameOnly['Nation'] = nation
            nameOnly['Type'] = sType
            nameOnly['ammo_num'] = ammo

            shipShellName[ship] = nameOnly

    compressed = {'ships' : {}, 'shells' : {}}
    cShells = compressed['shells']
    cShips = compressed['ships']
    for ships, data in shipShellName.items():
        artGroup = data['artillery']
        nation = data['Nation']
        sType = data['Type']

        #Create ship search tree: nation -> type -> ship
        if not nation in cShips:
            cShips[nation] = {}
        if not sType in cShips[nation]:
            cShips[nation][sType] = {}
        cShips[nation][sType][ships] = data

        for artGroupName, artGroupShells in artGroup.items():
            for shellType, shellName in artGroupShells.items():
                #Add shell to compressed if not already there
                if not shellName in cShells:
                    cShells[shellName] = selectEssential(condenseShell[shellName])

    writeToFile(compressed, tgtFolder, F'{outputName}.json', prettyPrint=True)
    writeToFile(compressed, tgtFolder, F'{outputName}.gz', prettyPrint=False, compress=True)

    hashes = {'gameparams': gPHash}
    hashes['full'] = checkHash(F'{tgtFolder}/{outputName}.json')
    hashes['compressed'] = checkHash(F'{tgtFolder}/{outputName}.gz')

    writeToFile(hashes, tgtFolder, 'hashes.json')

def batchRun(tgtFolder, root, dirs, files):
    if root != tgtFolder:
        baseName = os.path.basename(root)
        baseNameSplit = baseName.split('.')
        outputName = ''
        if len(baseNameSplit) < 4:
            outputName = F'{baseName}.0'
        else:
            outputName = '.'.join(baseNameSplit[:4])
        print(baseName, outputName)
        run(root, F'{outputName}_s', baseName)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str, help="Target Directory")
    parser.add_argument("-e", "--existing", type=str, help="use existing json if available")
    parser.add_argument("-o", "--output", type=str, help="output file name")
    parser.add_argument("-b", "--batch", help="batch folders within folders", action="store_true")

    args = parser.parse_args()
    tgtFolder = args.directory

    if args.batch:
        #print(list(os.walk(tgtFolder)))
        tgt = [(tgtFolder,) + rdf for rdf in os.walk(tgtFolder)]
        #print(tgt)
        with Pool(4) as p:
            r = p.starmap_async(batchRun, tgt)
            r.wait()

        if False:
            #print(r, d, f)
            for root, dirs, files in os.walk(tgtFolder):
                if root != tgtFolder:
                    baseName = os.path.basename(root)
                    baseNameSplit = baseName.split('.')
                    outputName = ''
                    if len(baseNameSplit) < 4:
                        outputName = F'{baseName}.0'
                    else:
                        outputName = '.'.join(baseNameSplit[:4])
                    print(baseName, outputName)
                    run(root, F'{outputName}_s', baseName)
        pass
    else:
        outputName = 'compressed'
        if args.output:
            outputName = args.output
        run(tgtFolder, outputName, args.existing)