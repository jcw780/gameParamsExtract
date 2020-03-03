import os, json, glob

staticDir = '../overpen_calculator/static/data'
shellDir = 'condensed'

shell = {}
with open(F'{shellDir}/condensedShells.json') as f:
    shell = json.load(f)

#print(shell.keys())

def normalization(caliber):
    if caliber <= 0.13:
        return 10.0
    elif caliber <= 0.152:
        return 8.5
    elif caliber <= 0.24:
        return 7.0
    else:
        return 6.0

essentialKeys = [
    "alphaPiercingHE",
    "bulletAirDrag", 
    "bulletAlwaysRicochetAt",
    "bulletDetonator", 
    "bulletDetonatorThreshold", 
    "bulletDiametr", 
    "bulletKrupp", 
    "bulletMass", 
    "name", 
    "bulletRicochetAt", 
    "bulletSpeed",
    "bulletCapNormalizeMaxAngle"
]

for path, subdirs, files in os.walk(staticDir):
    for name in files:
        if name.endswith(".json") and ('_' in name) and not ('shiptypes' in name):
            #print(os.path.join(path, name))
            with open(os.path.join(path, name)) as f:
                fileData = json.load(f)
            
            for ships, shipData in fileData.items():
                for keys, values in shipData.items():
                    if 'Artillery' in keys:
                        for shellType, shellData in values.items():
                            if 'bulletName' in shellData:
                                shellName = shellData['bulletName']
                                fileData[ships][keys][shellType].pop('bulletName', None)
                                fileData[ships][keys][shellType]['name'] = shellName

                                if shellName in shell:
                                    for items in essentialKeys:
                                        if not items in fileData[ships][keys][shellType]:
                                            fileData[ships][keys][shellType][items] = shell[shellName][items]

                                    #fileData[ships][keys][shellType]['alphaPiercingHE'] = shell[shellName]['alphaPiercingHE']
                                    #fileData[ships][keys][shellType]['bulletCapNormalizeMaxAngle'] = shell[shellName]['bulletCapNormalizeMaxAngle']
                                else:
                                    fileData[ships][keys][shellType]['alphaPiercingHE'] = 0
                                    caliber = fileData[ships][keys][shellType]['bulletDiametr'] 
                                    fileData[ships][keys][shellType]['bulletCapNormalizeMaxAngle'] = normalization(caliber)
                                    print(F'Shell {shellName} not found')
                                print(fileData[ships][keys][shellType])
            
            with open(os.path.join(path, name), 'w') as f:
                json.dump(fileData, f, indent=4)
                        

            


