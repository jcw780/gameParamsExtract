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
            return [current, selector(current_data), locale[localeName]]
        else: 
            return [current, selector(current_data), ""]
        

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
        componentDict = item[1]["components"]
        for componentType, components in componentDict.items():
            for component in components:
                componentsReached.add(component)
    return list(componentsReached)

def run(gpData: object, locale={}):# -> dict:
    entityTypes = makeEntities(gpData)
    shipData = {}
    
    for shipName, shipData in entityTypes['Ship'].items():
        upgrades = shipData['ShipUpgradeInfo']
        upgradesParsed = parseUpgrades(upgrades, locale, selectComponents)
        
        artilleryList = []
        fireControlList = []
        if "_Artillery" in upgradesParsed:
            artilleryList = acquireUsableComponents(upgradesParsed["_Artillery"])
        
        if "_Suo" in upgradesParsed:
            fireControlList = acquireUsableComponents(upgradesParsed["_Suo"])

        print(shipName, json.dumps(upgradesParsed, indent=4), artilleryList, fireControlList)

        shipTypeInfo = shipData['typeinfo']
        localeName = shipName
        localeID = F'IDS_{shipName.split("_")[0]}_FULL'
        if localeID in locale:
            localeName = locale[localeID]
        singleShipData = {
            'artillery': {},
            'Nation': shipTypeInfo['nation'],
            'Tier': shipData['level'],
            'Type': shipTypeInfo['species'],
            'Name': localeName
        }
        

    #return {
    #    'shells': getShells(shellsReached, entityTypes), 
    #    'ships': formatNationTypeShip(shipShellData)
    #}

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
    
    print(json.dumps(lData, indent=4))
    run(data, locale=lData)
    '''
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
        )'''