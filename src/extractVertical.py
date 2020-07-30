import argparse, operator
from collections import defaultdict
from gpToDict import gpToDict, makeEntities
from utility import readFromFile

def run(target):
    fileType = target.split('.')[-1]
    if fileType == 'data':
        entities = makeEntities(gpToDict(target)[0])
    elif fileType == 'json':
        entities = makeEntities(readFromFile(target))
    else:
        raise NotImplementedError

    turretTargets = ['radiusOnDelim', 'radiusOnMax', 'radiusOnZero', 'delim', 'idealRadius', 'minRadius']
    artilleryTargets = ['taperDist']

    radiusShips = defaultdict(list)
    for shipName, shipData in entities['Ship'].items():
        componentSet = set()
        upgrades = shipData['ShipUpgradeInfo']
        for name, data in upgrades.items():
            if type(data) == dict:
                components = data['components']
                if 'artillery' in components:
                    tgtComponents = components['artillery']
                    #print(name, components['artillery'])
                    componentSet |= set(tgtComponents)
        #print(shipName, componentSet)

        #data = {'delim': set(), 'max': set(), 'zero': set()}
        data = defaultdict(set)
        for artilleryName in componentSet:
            artillery = shipData[artilleryName]
            for pTurret, pTurretData in artillery.items():
                if type(pTurretData) == dict and 'typeinfo' in pTurretData:
                    typeinfo = pTurretData['typeinfo']
                    if typeinfo['species'] == 'Main' and typeinfo['type'] == 'Gun':
                        for target in turretTargets:
                            data[target].add(pTurretData[target])

            for target in artilleryTargets:
                data[target].add(artillery[target])

        #print(data)
        try:
            dataTuple = tuple([data[target].pop() for target in (turretTargets + artilleryTargets)])
            radiusShips[dataTuple].append(shipName)
        except:
            pass

    sortedKeys = list(radiusShips.keys())
    sortedKeys.sort(key=operator.itemgetter(slice(0, -1)))
    for disp in sortedKeys:
        ships = radiusShips[disp]
        outstr = ''
        for i, items in enumerate(turretTargets):
            outstr = F'{outstr}{items}: {disp[i]} '
        tLen = len(turretTargets)
        for i, items in enumerate(artilleryTargets):
            outstr = F'{outstr}{items}: {disp[i + tLen]} '
        print(outstr)
        print()
        temp = ''
        for i, ship in enumerate(ships):
            temp = F'{temp}{ship} '
            if(i % 3 == 2):
                print(temp)
                temp = ''
        
        if temp != '':
            print(temp)

        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inDirectory", type=str, help="Input directory")
    #parser.add_argument("outDirectory", type=str, help="Output directory")
    #parser.add_argument("-o", "--output", type=str, help="Output file name")
    args = parser.parse_args()
    run(args.inDirectory)