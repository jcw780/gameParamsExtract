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
    return (json.loads(gpDataStr), fileHash)

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