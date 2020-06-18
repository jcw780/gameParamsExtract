import struct, zlib, _pickle as pickle, codecs, json
import os, hashlib, shutil

# Derived from:
# https://github.com/EdibleBug/WoWS-GameParams/blob/master/OneFileToRuleThemAll.py


class GPEncode(json.JSONEncoder):
    def cleanDictionary(self, unclean):
        clean = {}
        for k, v in unclean.items():
            #print(k, v)
            if(isinstance(v, dict)):
                v = self.cleanDictionary(v)
            
            if(isinstance(k, tuple)):
                k = str(k)
            clean[k] = v
        return clean

    def default(self, o):
        try:
            for e in ['Cameras', 'DockCamera']:
                o.__dict__.pop(e, o.__dict__)
            
            #print('original', o.__dict__)
            cleaned = self.cleanDictionary(o.__dict__)
            #print('cleaned', cleaned)
            return cleaned
        except:
            return {}

def run(folder, cleanup=True, searchName="gameparams", outputName="GameParams"):
    intermediateFileDirectory = 'intermediate'

    with open(F'{folder}/{searchName}.data', 'rb') as f:
        b = []
        while 1:
            z = f.read(1)
            if not z:
                break
            b.append(z[0])

    if not os.path.exists(F'{folder}/{intermediateFileDirectory}'):
        os.makedirs(F'{folder}/{intermediateFileDirectory}')

    content = zlib.decompress(struct.pack('B'*len(b), *b[::-1]))
    destination = "GameParamsU8NB.txt"
    #outsize = 0
    #lines = 0
    with open(F'{folder}/{intermediateFileDirectory}/{destination}', 'wb') as output:
        for line in content.splitlines():
            #outsize += len(line) + 1
            #lines += 1
            output.write(line + str.encode('\n'))
    with open(F'{folder}/{intermediateFileDirectory}/{destination}', 'rb') as f:
        d = pickle.load(f, encoding='latin1')


    f = codecs.open(F'{folder}/{outputName}.json', 'w', encoding='latin1')
    f.write(json.dumps(d, cls=GPEncode, sort_keys=True, indent=4, separators=(',', ': ')))
    f.close()
    if cleanup:
        shutil.rmtree(F'{folder}/{intermediateFileDirectory}')

    checkHash = True
    if checkHash:
        BUF_SIZE = 32768 # Read file in 32kb chunks
        sha256 = hashlib.sha256()
        with open(F'{folder}/{outputName}.json', 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()


if __name__ == "__main__":
    run('..')