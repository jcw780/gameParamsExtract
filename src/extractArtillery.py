import json, argparse
from collections import defaultdict
from gpToDict import gpToDict, makeEntities, getComponentData
from utility import writeToFile
import extractGM

'''
For extracting and packaging shell information - single
'''

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

def makeShipArtilleryAccuracyShell(shipArtilleryData: dict, entityTypes: dict, locale: dict):
    shellsReached = set()
    shipShellData = {}

    turretTargets = ['radiusOnDelim', 'radiusOnMax', 'radiusOnZero', 'delim', 'idealRadius', 'minRadius', 'idealDistance']
    artilleryTargets = ['taperDist', 'sigmaCount', 'maxDist']
    for shipName, artilleryGroup in shipArtilleryData.items():
        shipData = entityTypes['Ship'][shipName]
        shipTypeInfo = shipData['typeinfo']

        localeName = shipName
        localeID = F'IDS_{shipName.split("_")[0]}_FULL'
        if localeID in locale:
            localeName = locale[localeID]
        
        shipShellData[shipName] = {
            'artillery': {},
            'Nation': shipTypeInfo['nation'],
            'Tier': shipData['level'],
            'Type': shipTypeInfo['species'],
            'Name': localeName
        }
        for artilleryName, artillery in artilleryGroup.items():
            ammoSet = set()
            accuracyData = {}
            numBarrels = 0
            for pTurret, pTurretData in artillery.items():
                if type(pTurretData) == dict and 'typeinfo' in pTurretData:
                    typeinfo = pTurretData['typeinfo']
                    if typeinfo['species'] == 'Main' and typeinfo['type'] == 'Gun':
                        ammoSet |= set(pTurretData['ammoList'])
                        numBarrels += pTurretData['numBarrels']
                        for targets in turretTargets:
                            if targets in pTurretData:
                                accuracyData[targets] = pTurretData[targets]
            ammoCategorized = {}
            for ammo in ammoSet:
                data = entityTypes['Projectile'][ammo]
                ammoCategorized[data['ammoType']] = ammo
            #print(shipName, artilleryName, ammoCategorized)
            if len(ammoSet) > 0:
                for targets in artilleryTargets:
                    accuracyData[targets] = artillery[targets]
            shipShellData[shipName]['artillery'][artilleryName] = {
                'shells': ammoCategorized, **accuracyData, 'numBarrels': numBarrels
            }
            shellsReached |= ammoSet
    return (shipShellData, shellsReached)

def formatNationTypeShip(shipArtilleryShell: dict) -> dict:
    formatted = defaultdict(lambda: defaultdict(dict))
    for ship, data in shipArtilleryShell.items():
        nation = data['Nation']
        shipType = data['Type']
        data.pop('Nation')
        data.pop('Type')
        formatted[nation][shipType][ship] = data
    return formatted

def getShells(shellsReached: dict, entityTypes: dict, essential=True) -> dict:
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

def run(gpData: object, accuracy=True, locale={}) -> dict:
    entityTypes = makeEntities(gpData)
    #artilleryComponents = getArtilleryData(entityTypes)
    artilleryComponents = getComponentData(entityTypes, 'artillery')
    if accuracy:
        shipShellData, shellsReached = makeShipArtilleryAccuracyShell(artilleryComponents, entityTypes, locale)
    else:
        shipShellData, shellsReached = makeShipArtilleryShell(artilleryComponents, entityTypes)
    return {
        'shells': getShells(shellsReached, entityTypes), 
        'ships': formatNationTypeShip(shipShellData)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inDirectory", type=str, help="Input directory")
    parser.add_argument("outDirectory", type=str, help="Output directory")
    parser.add_argument("-l", "--locale", type=str, help="Localization Directory")
    parser.add_argument("-o", "--output", type=str, help="Output file name")
    parser.add_argument("--readable", help="Readable Output", action="store_true")
    args = parser.parse_args()

    outputName = 'artillery.json'
    if args.output:
        outputName = args.output
    
    lData = {}
    if locale := args.locale:
        lData = extractGM.run(F'{locale}/global.mo')
    
    data, fileHash = gpToDict(F'{args.inDirectory}/GameParams.data') 
    if args.readable:
        writeToFile(
            run(data, locale=lData), 
            F'{args.outDirectory}/{outputName}',
            indent=4, sort_keys=True
        )
    else:
        writeToFile(
            run(data, locale=lData), 
            F'{args.outDirectory}/{outputName}',
            sort_keys=True
        )

