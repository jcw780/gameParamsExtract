import json, argparse
from gpToDict import gpToDict, makeEntities, getComponentData
from utility import writeToFile
import extractGM
from matplotlib import pyplot as plt
import numpy as np

'''
For extracting and packaging shell information - single
'''

def getHullData(entityTypes: dict, locale={}):
    shipHullData = getComponentData(entityTypes, 'hull')
    dragDeceleration = []
    speeds = []
    lBR = []
    for shipName, hulls in shipHullData.items():
        for hull, hullData in hulls.items():
            #print(shipName, hull)
            speed = hullData['maxSpeed'] * 0.514444 * hullData['speedCoef'] #To m/s
            power = hullData['enginePower'] * 735.49875 #To Watts
            mass = hullData['mass']
            draft = hullData['draft']
            size = hullData['size']
            lengthBeamRatio = size[1] * draft * size[0] ** 0.5
            deceleration = power / speed
            #if shipName[3] == 'C':
            if shipName[0:4] == 'PASC':
            #if True:
                print(shipName, deceleration, speed, lengthBeamRatio)
                dragDeceleration.append(deceleration)
                speeds.append(speed)
                lBR.append(lengthBeamRatio)
                lShipName = shipName
                searchName = F'IDS_{shipName.split("_")[0]}'
                if searchName in locale:
                    lShipName = locale[searchName]
                plt.annotate(lShipName, (speed, deceleration))
            
            #print(speed, power, mass, deceleration)

    plt.scatter(np.array(speeds), np.array(dragDeceleration), c=np.array(lBR))
    plt.show()

    return shipHullData

def getEngineData(entityTypes: dict):
    shipEngineData = getComponentData(entityTypes, 'engine')
    for shipName, engines in shipEngineData.items():
        for engine, engineData in engines.items():
            print(shipName, engine)
            print('backwardForsage: Multiplier: ', engineData['backwardEngineForsag'], 'Speed: ', engineData['backwardEngineForsagMaxSpeed'])
            print('forwardForsage: Multiplier: ', engineData['forwardEngineForsag'], 'Speed: ', engineData['forwardEngineForsagMaxSpeed'])
            pass
    return shipEngineData

def run(gpData: object, accuracy=True, locale={}):
    entityTypes = makeEntities(gpData)
    #hullComponents = getHullData(entityTypes, locale=locale)
    engineComponents = getEngineData(entityTypes)
    #print(hullComponents)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inDirectory", type=str, help="Input directory")
    parser.add_argument("outDirectory", type=str, help="Output directory")
    parser.add_argument("-l", "--locale", type=str, help="Localization Directory")
    parser.add_argument("-o", "--output", type=str, help="Output file name")
    parser.add_argument("--readable", help="Readable Output", action="store_true")
    args = parser.parse_args()

    outputName = 'hull.json'
    if args.output:
        outputName = args.output
    
    data, fileHash = gpToDict(F'{args.inDirectory}/GameParams.data') 
    lData = {}
    if locale := args.locale:
        lData = extractGM.run(F'{locale}/global.mo')
    
    run(data, locale=lData)
    '''
    
    if args.readable:
        writeToFile(
            run(data, locale=lData), 
            F'{args.outDirectory}/{outputName}',
            indent=4, sort_keys=True
        )
    else:
        writeToFile(
            run(data, locale=lData), 
            F'{args.outDirectory}/{outputName}',
            sort_keys=True
        )
    '''