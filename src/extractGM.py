import argparse
import polib

def run(directory):
    f = polib.mofile(directory)
    data = {}
    for line in f:
        data[line.msgid] = line.msgstr
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inDirectory", type=str, help="Input directory")
    #parser.add_argument("outDirectory", type=str, help="Output directory")
    #parser.add_argument("-o", "--output", type=str, help="Output file name")
    args = parser.parse_args()
    run(args.inDirectory)

