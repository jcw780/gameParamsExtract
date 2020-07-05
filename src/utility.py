import json, os, hashlib

def checkMakeDir(directory: str) -> None:
    """
    Checks to see if directory exists and 
    makes it if it does not exist 
    
    Parameters:
        directory (str): Full file path of GameParams.data

    Returns:
        None
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def readFromFile(target: str) -> object:
    """
    Reads json file
    
    Parameters:
        target (str): Full file path of json file

    Returns:
        (object): list / dict 
    """
    with open(target, 'r') as f:
        data = json.load(f)
    return data

def writeToFile(data: object, target: str, **kwargs) -> None:
    """
    Writes json to file
    
    Parameters:
        data (object): Json data to write into file
        target (str): Full file path of json file to write into
        **kwargs: Same as json.dumps()
    Returns:
        None
    """
    with open(target, 'w') as f:
        f.write(json.dumps(data, **kwargs))

def checkFileHash(target: str) -> str:
    """
    Computes SHA256 hash of a file

    Parameters:
        target (str): Full path of file
    Returns: 
        (str): HEX String of Hash
    """
    BUF_SIZE = 32768 # Read file in 32kb chunks
    sha256 = hashlib.sha256()
    with open(target, 'rb') as f:
        while chunk := f.read(BUF_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()

def checkByteHash(data: bytes) -> str:
    """
    Computes SHA256 hash of bytes

    Parameters:
        data (bytes): Byte data
    Returns: 
        (str): HEX String of Hash
    """
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()
