import struct, zlib, _pickle as pickle, codecs, json
import os, hashlib

# Derived from:
# https://github.com/EdibleBug/WoWS-GameParams/blob/master/OneFileToRuleThemAll.py

class GPEncode(json.JSONEncoder):
    def default(self, o):
        try:
            for e in ['Cameras', 'DockCamera']:
                o.__dict__.pop(e, o.__dict__)
            return o.__dict__
        except:
            return {}

def run(folder):
    intermediateFileDirectory = 'intermediate'

    if not os.path.exists(F'{folder}/{intermediateFileDirectory}'):
        os.makedirs(F'{folder}/{intermediateFileDirectory}')

    with open(F'{folder}/GameParams.data', 'rb') as f:
        b = []
        while 1:
            z = f.read(1)
            if not z:
                break
            b.append(z[0])

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


    f = codecs.open(F'{folder}/GameParams.json', 'w', encoding='latin1')
    f.write(json.dumps(d, cls=GPEncode, sort_keys=True, indent=4, separators=(',', ': ')))
    f.close()

    BUF_SIZE = 32768 # Read file in 32kb chunks
    sha256 = hashlib.sha256()
    with open(F'{folder}/GameParams.json', 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)

    print(F'SHA256: {sha256.hexdigest()}')

if __name__ == "__main__":
    run('..')