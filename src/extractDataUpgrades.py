import json, argparse
from typing import Callable
from collections import defaultdict, deque
from gpToDict import gpToDict, makeEntities, getComponentData
from utility import writeToFile
import extractGM

def parseUpgrades(upgrades: dict, locale: dict = {}, selector : Callable[[dict], dict] = lambda inDict: inDict):
    reached = set([])
    groupedSortedUpgrades = defaultdict(lambda: list())

    def makeElement(current, current_data):
        localeName = F'IDS_{current}'
        if localeName in locale:
            return [current, locale[localeName], selector(current_data)]
        else: 
            return [current, "", selector(current_data)]
        

    for current, current_data in upgrades.items():
        if type(current_data) == dict and not current in reached:
            ucType = current_data['ucType']
            prev = current_data['prev']
            startType = ucType
            toAdd = deque([makeElement(current, current_data)])
            reached.add(current)
            while prev != "" and startType == ucType and not prev in reached:
                current = prev
                current_data = upgrades[current]
                ucType = current_data['ucType']
                prev = current_data['prev']
                toAdd.appendleft(makeElement(current, current_data))
                reached.add(current)
            groupedSortedUpgrades[ucType].extend(list(toAdd))
    return groupedSortedUpgrades

def selectComponents(inDict: dict) -> dict:
    include = set(["artillery", "fireControl"])
    components = inDict["components"]
    components_filtered = {}
    for k, v in components.items():
        if k in include:
            components_filtered[k] = v

    return {
        "components": components_filtered
    }
    
def acquireUsableComponents(upgrades: list) -> list:
    componentsReached = set()
    for item in upgrades:
        componentDict = item[2]["components"]
        for componentType, components in componentDict.items():
            for component in components:
                componentsReached.add(component)
    return list(componentsReached)

def formatNationTypeShip(shipArtilleryShell: dict) -> dict:
    formatted = defaultdict(lambda: defaultdict(dict))
    for ship, data in shipArtilleryShell.items():
        if len(data['artillery'].keys()) > 0:
            nation = data['Nation']
            shipType = data['Type']
            data.pop('Nation')
            data.pop('Type')
            formatted[nation][shipType][ship] = data
    return formatted

def getShells(shellsReached: set, entityTypes: dict, essential=True) -> dict:
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

def run(gpData: object, locale={}):# -> dict:
    entityTypes = makeEntities(gpData)
    extractedShipData = {}
    
    shellsReached = set()
    turretTargets = ['radiusOnDelim', 'radiusOnMax', 'radiusOnZero', 'delim', 'idealRadius', 'minRadius', 'idealDistance']
    artilleryTargets = ['taperDist', 'sigmaCount', 'maxDist']

    for shipName, shipData in entityTypes['Ship'].items():
        upgrades = shipData['ShipUpgradeInfo']
        upgradesParsed = parseUpgrades(upgrades, locale, selectComponents)
        
        artilleryList = []
        fireControlList = []
        if "_Artillery" in upgradesParsed:
            artilleryList = acquireUsableComponents(upgradesParsed["_Artillery"])
        
        if "_Suo" in upgradesParsed:
            fireControlList = acquireUsableComponents(upgradesParsed["_Suo"])

        shipTypeInfo = shipData['typeinfo']
        localeName = shipName
        localeID = F'IDS_{shipName.split("_")[0]}_FULL'
        if localeID in locale:
            localeName = locale[localeID]
        singleShipData = {
            'artillery': defaultdict(lambda: dict()),
            'fireControl': defaultdict(lambda: dict()),
            'upgrades': upgradesParsed,
            'Nation': shipTypeInfo['nation'],
            'Tier': shipData['level'],
            'Type': shipTypeInfo['species'],
            'Name': localeName
        }
                
        for artilleryName in artilleryList:
            artillery = shipData[artilleryName]
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
            
            singleShipData['artillery'][artilleryName] = {
                'shells': ammoCategorized, **accuracyData, 'numBarrels': numBarrels
            }

            shellsReached |= ammoSet
            
        for fireControlName in fireControlList:
            singleShipData['fireControl'][fireControlName] = shipData[fireControlName]
        extractedShipData[shipName] = singleShipData
    
    return {
        'shells': getShells(shellsReached, entityTypes), 
        'ships': formatNationTypeShip(extractedShipData)
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
    
    result = run(data, locale=lData)
    outputPath = F'{args.outDirectory}/{outputName}'
    
    print(json.dumps(result, indent=4))
    if args.readable:
        writeToFile(
            result, outputPath,
            indent=4, sort_keys=True
        )
    else:
        writeToFile(
            result, outputPath,
            sort_keys=True
        )