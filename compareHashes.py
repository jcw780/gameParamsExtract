import json, sys

tgt1 = sys.argv[1]
tgt2 = sys.argv[2]

tgt1Hashes = {}
tgt2Hashes = {}

with open(F'{tgt1}/hashes.json') as f:
    tgt1Hashes = json.load(f)

with open(F'{tgt2}/hashes.json') as f:
    tgt2Hashes = json.load(f)

keysRemaining2 = set(tgt2Hashes.keys())
for key, hashValue in tgt1Hashes.items():
    if key in tgt2Hashes:
        keysRemaining2.remove(key)
        if tgt2Hashes[key] == tgt1Hashes[key]:
            print(F'SAME {key}')
        else:
            print(F'DIFF {key}')
    else:
        print(F'NOT2 {key}')

for keysRemaing in keysRemaining2:
    print(F'NOT1 {keysRemaing}')

