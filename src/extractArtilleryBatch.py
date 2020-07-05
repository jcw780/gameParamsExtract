import argparse, os
from multiprocessing import Pool

from gpToDict import gpToDict
from utility import writeToFile, readFromFile
import extractArtillery

def run(tgtFolder:str, outputDirectory:str, outputName:str, existing:str, cleanup:bool=False):
    readFile = 'gameparams'
    gPHash = ''
    data = {}
    extract = True
    if existing:
        tempRF = existing
        if os.path.isfile(F'{tgtFolder}/{tempRF}.json'):
            extract = False
            cleanup = False
            data = readFromFile(F'{tgtFolder}/{tempRF}.json')
    if extract:
        data, gPHash = gpToDict(F'{tgtFolder}/{readFile}.data')
    formattedArtillery = extractArtillery.run(data)
    writeToFile(formattedArtillery, F'{outputDirectory}/{outputName}.json', indent=4, sort_keys=True)

def batchRunFunction(tgtFolder: str, outputDirectory: str, root, dirs, files):
    if root != tgtFolder:
        baseName = os.path.basename(root)
        baseNameSplit = baseName.split('.')
        outputName = ''
        if len(baseNameSplit) < 4:
            outputName = F'{baseName}.0'
        else:
            outputName = '.'.join(baseNameSplit[:4])
        print(baseName, outputName)
        run(root, outputDirectory, F'{outputName}_s', baseName)

def batchRun(tgtFolder: str, outputDirectory: str):
    def batchGenerator(tgtFolder: str, outputDirectory):
        for rdf in os.walk(tgtFolder):
            yield (tgtFolder, outputDirectory) + rdf
    with Pool(4) as p:
        r = p.starmap_async(batchRunFunction, batchGenerator(tgtFolder, outputDirectory))
        r.wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str, help="Target Directory")
    parser.add_argument("-e", "--existing", type=str, help="use existing json if available")
    parser.add_argument("-d", "--outputDirectory", type=str, help="output directory")
    parser.add_argument("-o", "--output", type=str, help="output file name")
    parser.add_argument("-b", "--batch", help="batch folders within folders", action="store_true")

    args = parser.parse_args()
    tgtFolder = args.directory

    if args.batch:
        #print(args)
        batchRun(tgtFolder, args.outputDirectory)
    else:
        outputName = 'compressed'
        if args.output:
            outputName = args.output
        run(tgtFolder, args.outputDirectory, outputName, args.existing)