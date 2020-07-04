import os, struct, zlib, pickle, json
from collections import defaultdict

class GPEncode(json.JSONEncoder):
    def default(self, o):
        try:
            for e in ['Cameras', 'DockCamera', 'damageDistribution']:
                o.__dict__.pop(e, o.__dict__)
            return o.__dict__
        except AttributeError:
            return {}

def gpToDict(gpFilePath):
    with open(gpFilePath, 'rb') as f:
        gpBytes: bytes = f.read()
    gpPacked: bytes = struct.pack('B' * len(gpBytes), *gpBytes[::-1])
    gpUnpacked: bytes = zlib.decompress(gpPacked)
    gpDict: dict = pickle.loads(gpUnpacked, encoding='windows-1251')
    gpDataStr: str = json.dumps(gpDict, cls=GPEncode, ensure_ascii=False)
    return json.loads(gpDataStr)

def makeEntities(gpData: dict):
    entityTypes = defaultdict(dict)
    for index, value in gpData.items():
        dataType: str = value["typeinfo"]["type"]
        entityTypes[dataType][index] = value
    return entityTypes

## Make Artillery

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
            print(shipName, artilleryName, ammoCategorized)
            shipShellData[shipName]['artillery'][artilleryName] = ammoCategorized
            shellsReached |= ammoSet
    return (shipShellData, shellsReached)

def formatNationTypeShip(shipArtilleryShell: dict):
    formatted = defaultdict(lambda: defaultdict(dict))
    for ship, data in shipArtilleryShell.items():
        formatted[data['Nation']][data['Type']] = {ship: data}
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
        print(shellData[shell])
    return shellData

def run():
    gpData: dict = gpToDict('test/GameParams.data')
    entityTypes = makeEntities(gpData)
    artilleryComponents = getArtilleryData(entityTypes)
    shipShellData, shellsReached = makeShipArtilleryShell(artilleryComponents, entityTypes)
    output = {
        'shells': getShells(shellsReached, entityTypes), 
        'ships': formatNationTypeShip(shipShellData)
    }

if __name__ == "__main__":
    run()
    pass

