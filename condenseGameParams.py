import json

condenseShip = {}
condenseGun = {}
condenseShell = {}
#counter = 0

with open("GameParams.json", 'r') as f:
    data = json.load(f)
    for k, v in data.items():
        #print(k)
        #print(v["typeinfo"])
        if v["typeinfo"]["type"] == 'Ship':
            condenseShip[k] = v
        if v["typeinfo"]["type"] == 'Projectile':
            condenseShell[k] = v
        elif v["typeinfo"]["type"] == 'Gun' and v["typeinfo"]["species"] == 'Main':
            condenseGun[k] = v

#print(counter)
with open("GameParamsCondensedShips.json", 'w') as f:
    f.write(json.dumps(condenseShip, indent=4))

with open("GameParamsCondensedGuns.json", 'w') as f:
    f.write(json.dumps(condenseGun, indent=4))

with open("GameParamsCondensedShells.json", 'w') as f:
    f.write(json.dumps(condenseShell, indent=4))