import argparse, os
from multiprocessing import Pool

from gpToDict import gpToDict
from utility import writeToFile, readFromFile
import extractDataUpgrades
import extractGM

'''
For extracting and packaging shell information - batch
'''

def run(tgtFolder:str, outputDirectory:str, locale:dict, outputName:str, existing:str, cleanup:bool=False):
    readFile: str = 'gameparams'
    gPHash: str = ''
    data: dict = {}
    extract = True
    if existing:
        tempRF = existing
        if os.path.isfile(F'{tgtFolder}/{tempRF}.json'):
            extract = False
            cleanup = False
            data = readFromFile(F'{tgtFolder}/{tempRF}.json')
    if extract:
        data, gPHash = gpToDict(F'{tgtFolder}/{readFile}.data')
    formattedArtillery: dict = extractDataUpgrades.run(data, locale=locale)
    writeToFile(formattedArtillery, F'{outputDirectory}/{outputName}.json', sort_keys=True)

def batchRunFunction(tgtFolder: str, outputDirectory: str, locale: dict, root, dirs, files):
    if root != tgtFolder:
        baseName = os.path.basename(root)
        baseNameSplit = baseName.split('.')
        outputName = ''
        if len(baseNameSplit) < 4:
            outputName = F'{baseName}.0'
        else:
            outputName = '.'.join(baseNameSplit[:4])
        print(baseName, outputName)
        run(root, outputDirectory, locale, F'{outputName}_s', baseName)

def batchRun(tgtFolder: str, outputDirectory: str, locale: dict):
    def batchGenerator(tgtFolder: str, outputDirectory):
        for rdf in os.walk(tgtFolder):
            yield (tgtFolder, outputDirectory, locale) + rdf
    with Pool(4) as p:
        r = p.starmap_async(batchRunFunction, batchGenerator(tgtFolder, outputDirectory))
        r.wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str, help="Target Directory")
    parser.add_argument("outDirectory", type=str, help="Output directory")
    parser.add_argument("-l", "--locale", type=str, help="Localization Directory")

    args = parser.parse_args()
    tgtFolder = args.directory

    lData = {}
    if locale := args.locale:
        lData = extractGM.run(F'{locale}/global.mo')

    if True:
        batchRun(tgtFolder, args.outDirectory, lData)
    '''else:
        outputName = 'compressed'
        if args.output:
            outputName = args.output
        run(tgtFolder, args.outputDirectory, outputName, args.existing)'''