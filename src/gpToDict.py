import struct, zlib, pickle, json, typing
from collections import defaultdict
from utility import checkByteHash

""" 
Much of the code in this file is derived from 
https://github.com/imkindaprogrammermyself/GameParams2Json
"""

class GPEncode(json.JSONEncoder):
    def default(self, o):
        try:
            for e in ['Cameras', 'DockCamera', 'damageDistribution']:
                o.__dict__.pop(e, o.__dict__)
            return o.__dict__
        except AttributeError:
            return {}

def gpToDict(gpFilePath, showHash=True) -> typing.Tuple[object, str]:
    """
    Reads GameParams.data and converts it to list/dict 
    
    Parameters:
        gpFilePath (str): Full file path of GameParams.data
        showHash (bool) = True: Print hash at read
    Returns:
        tuple(object, str): [json data, hash]
    """
    with open(gpFilePath, 'rb') as f:
        gpBytes: bytes = f.read()
    fileHash: str = checkByteHash(gpBytes)
    if showHash:
        print(F'SHA256: {fileHash}')
    gpPacked: bytes = struct.pack('B' * len(gpBytes), *gpBytes[::-1])
    gpUnpacked: bytes = zlib.decompress(gpPacked)
    gpDict: dict = pickle.loads(gpUnpacked, encoding='windows-1251')
    gpDataStr: str = json.dumps(gpDict, cls=GPEncode, ensure_ascii=False)
    gpDataParsed = json.loads(gpDataStr)
    if isinstance(gpDataParsed, list):
        gpDataParsed = gpDataParsed[0]
    
    return (gpDataParsed, fileHash)

def makeEntities(gpData: dict) -> dict:
    """
    Takes GameParams data and formats it by type
    Parameters:
        gpData (dict): GameParams data
    Returns:
        (dict): format: [type] : {entityName: value}
    """
    entityTypes = defaultdict(dict)
    for index, value in gpData.items():
        dataType: str = value["typeinfo"]["type"]
        entityTypes[dataType][index] = value
    return entityTypes

def getComponentData(entityTypes: dict, target, exclude=True):
    if exclude:
        shipComponentData = getComponentExclude(entityTypes, target)
    else:
        shipComponentData = getComponentInclude(entityTypes, target)
    return shipComponentData

def getComponentExclude(entityTypes: dict, target):
    exclude = set(['disabled', 'preserved', 'unavailable'])
    shipComponentData = defaultdict(dict)
    for shipName, v in entityTypes['Ship'].items():
        if not v['group'] in exclude: 
            getComponentIncluded(shipComponentData, shipName, v, target)
    return shipComponentData

def getComponentInclude(entityTypes: dict, target):
    shipComponentData = defaultdict(dict)
    for shipName, v in entityTypes['Ship'].items():
        getComponentIncluded(shipComponentData, shipName, v, target)
    return shipComponentData

def getComponentIncluded(shipComponentData: dict, shipName, v, target):
    componentSet = set()
    upgrades = v['ShipUpgradeInfo']
    for name, data in upgrades.items():
        if type(data) == dict:
            components = data['components']
            if target in components:
                tgtComponents = components[target]
                componentSet |= set(tgtComponents)
    for component in componentSet:
        if component in v:
            shipComponentData[shipName][component] = v[component]