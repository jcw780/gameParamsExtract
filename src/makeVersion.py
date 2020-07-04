import argparse, os, json, zlib

parser = argparse.ArgumentParser()
parser.add_argument("directory", type=str, help="Target Directory")
args = parser.parse_args()

tgtFolder = args.directory
fileList = []
for root, dirs, files in os.walk(tgtFolder):
    for file in files:
        if file.endswith(".json") and not file.startswith("versions"):
            print(os.path.join(root, file), file)
            fileList.append(file.split('_')[0])

def keyGen(name: str):
    output: int = 0
    nameS = name.split('.')
    length = len(nameS)
    print(nameS)
    for i, s in enumerate(nameS):
        output += int(s) * 1000 ** (length - i - 1)
    print(output)
    return output

fileList = sorted(fileList, key=keyGen)

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

def writeToFile(data, filePath: str, file: str, prettyPrint: bool = True, compress:bool = False):
    filePathAppended = file
    if filePath:
        filePathAppended = F'{filePath}/{file}'
    
    outputString = ''
    if prettyPrint:
        outputString = json.dumps(data, indent=4, sort_keys=True, cls=SetEncoder)
    else:
        outputString = json.dumps(data, cls=SetEncoder)

    output = outputString
    if compress:
        output = outputString.encode('utf-8')
        with open(filePathAppended, 'wb') as f:
            f.write(zlib.compress(output))
    else:
        with open(filePathAppended, 'w') as f:
            f.write(outputString)

print(fileList)
writeToFile(fileList, tgtFolder, 'versions.json')
