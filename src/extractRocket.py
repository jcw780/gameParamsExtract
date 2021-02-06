import argparse
from gpToDict import gpToDict, makeEntities

def run(target):
    entities = makeEntities(gpToDict(target)[0])

    def calcPenetrationOld(krupp, mass, caliber, velocity):
        return 0.5561613 * krupp / 2400 * (mass ** 0.5506) / ((caliber * 1000) ** 0.6521) * (velocity ** 1.1001)
    
    def calcPenetration(krupp, mass, caliber, velocity):
        return 0.00046905491615181766 * krupp / 2400 * (mass ** 0.5506) / ((caliber) ** 0.6521) * (velocity ** 1.4822064892953855)

    for name, value in entities['Projectile'].items():
        if value['typeinfo']['species'] == 'Bomb':
            if value['ammoType'] == 'AP':
                krupp = value["bulletKrupp"]
                mass = value["bulletMass"]
                caliber = value["bulletDiametr"]
                velocity = value["bulletSpeed"]
                model = (value['model'].split('/')[-1])
                #idTrimmed = '_'.join(model.split('_')[1:])
                print(name, round(calcPenetration(krupp, mass, caliber, velocity), 3), value["bulletDetonator"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inDirectory", type=str, help="Input directory")
    #parser.add_argument("outDirectory", type=str, help="Output directory")
    #parser.add_argument("-o", "--output", type=str, help="Output file name")
    args = parser.parse_args()
    run(args.inDirectory)
