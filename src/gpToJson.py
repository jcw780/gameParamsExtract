import argparse
from utility import writeToFile, checkMakeDir
from gpToDict import gpToDict

def run(target: str, output: str) -> None:
    data, fileHash = gpToDict(target)
    writeToFile(
        data, output, 
        indent=4, sort_keys=True
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inDirectory", type=str, help="Input directory")
    parser.add_argument("outDirectory", type=str, help="Output directory")
    parser.add_argument("-o", "--output", type=str, help="Output file name")
    args = parser.parse_args()

    checkMakeDir(args.outDirectory)
    outName = 'GameParams.json'
    if args.output:
        outName = args.output
    run(F'{args.inDirectory}/GameParams.data', F'{args.outDirectory}/{outName}')
    