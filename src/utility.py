import json, os, hashlib

def checkMakeDir(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)

def readFromFile(target: str) -> object:
    with open(target, 'r') as f:
        data = json.load(f)
    return data

def writeToFile(data: object, target: str, **kwargs) -> None:
    with open(target, 'w') as f:
        f.write(json.dumps(data, **kwargs))

def checkFileHash(target: str) -> str:
    BUF_SIZE = 32768 # Read file in 32kb chunks
    sha256 = hashlib.sha256()
    with open(target, 'rb') as f:
        while chunk := f.read(BUF_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()

def checkByteHash(data: bytes) -> str:
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()
