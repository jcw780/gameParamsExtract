import json, argparse
from collections import defaultdict
from gpToDict import gpToDict, makeEntities
from utility import writeToFile

# Make Artillery

def getArtilleryData(entityTypes: dict):
    shipComponentData = defaultdict(dict)
    for shipName, v in entityTypes['Ship'].items():
        #print(v['ShipUpgradeInfo'])
        componentSet = set()
        upgrades = v['ShipUpgradeInfo']
        for name, data in upgrades.items():
            if type(data) == dict:
                components = data['components']
                if 'artillery' in components:
                    tgtComponents = components['artillery']
                    #print(name, components['artillery'])
                    componentSet |= set(tgtComponents)
        for component in componentSet:
            if component in v:
                shipComponentData[shipName][component] = v[component]
    return shipComponentData

def makeShipArtilleryShell(shipArtilleryData: dict, entityTypes: dict):
    shellsReached = set()
    shipShellData = {}
    for shipName, artilleryGroup in shipArtilleryData.items():
        shipData = entityTypes['Ship'][shipName]
        shipTypeInfo = shipData['typeinfo']
        shipShellData[shipName] = {
            'artillery': {},
            'Nation': shipTypeInfo['nation'],
            'Tier': shipData['level'],
            'Type': shipTypeInfo['species']
        }
        for artilleryName, artillery in artilleryGroup.items():
            ammoSet = set()
            for pTurret, pTurretData in artillery.items():
                if type(pTurretData) == dict and 'typeinfo' in pTurretData:
                    typeinfo = pTurretData['typeinfo']
                    if typeinfo['species'] == 'Main' and typeinfo['type'] == 'Gun':
                        ammoSet |= set(pTurretData['ammoList'])
            ammoCategorized = {}
            for ammo in ammoSet:
                data = entityTypes['Projectile'][ammo]
                ammoCategorized[data['ammoType']] = ammo
            #print(shipName, artilleryName, ammoCategorized)
            shipShellData[shipName]['artillery'][artilleryName] = ammoCategorized
            shellsReached |= ammoSet
    return (shipShellData, shellsReached)

def formatNationTypeShip(shipArtilleryShell: dict):
    formatted = defaultdict(lambda: defaultdict(dict))
    for ship, data in shipArtilleryShell.items():
        formatted[data['Nation']][data['Type']][ship] = data
    return formatted

def getShells(shellsReached, entityTypes: dict, essential=True):
    def selectEssential(data: dict):
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
    
    shells = entityTypes['Projectile']
    shellData = {}
    for shell in shellsReached:
        if essential:
            shellData[shell] = selectEssential(shells[shell])
        else:
            shellData[shell] = shells[shell]
        #print(shellData[shell])
    return shellData

def run(gpData: object):
    entityTypes = makeEntities(gpData)
    artilleryComponents = getArtilleryData(entityTypes)
    shipShellData, shellsReached = makeShipArtilleryShell(artilleryComponents, entityTypes)
    return {
        'shells': getShells(shellsReached, entityTypes), 
        'ships': formatNationTypeShip(shipShellData)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inDirectory", type=str, help="Input directory")
    parser.add_argument("outDirectory", type=str, help="Output directory")
    parser.add_argument("-o", "--output", type=str, help="Output file name")
    args = parser.parse_args()

    outputName = 'artillery.json'
    if args.output:
        outputName = args.output
    data, fileHash = gpToDict(F'{args.inDirectory}/GameParams.data') 
    writeToFile(
        run(data), 
        F'{args.outDirectory}/{outputName}',
        indent=4, sort_keys=True
    )

