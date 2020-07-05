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
    with open(gpFilePath, 'rb') as f:
        gpBytes: bytes = f.read()
    fileHash = checkByteHash(gpBytes)
    if showHash:
        print(F'{gpFilePath} SHA256: {fileHash}')
    gpPacked: bytes = struct.pack('B' * len(gpBytes), *gpBytes[::-1])
    gpUnpacked: bytes = zlib.decompress(gpPacked)
    gpDict: dict = pickle.loads(gpUnpacked, encoding='windows-1251')
    gpDataStr: str = json.dumps(gpDict, cls=GPEncode, ensure_ascii=False)
    return (json.loads(gpDataStr), fileHash)

def makeEntities(gpData: dict):
    entityTypes = defaultdict(dict)
    for index, value in gpData.items():
        dataType: str = value["typeinfo"]["type"]
        entityTypes[dataType][index] = value
    return entityTypes