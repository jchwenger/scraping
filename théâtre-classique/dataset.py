import os
import re
import argparse

def main(args):
    files = os.listdir(args.dir)
    print(files)
    total = len(files)
    regices = make_regices()
    for i, f in enumerate(files):
        print(f'{i:4}/{total} | processing {f}')
        datasetize(f, args.dir, args.out_dir, regices)

def make_regices():
    regices = []

    regices.append(re.compile('SCÈNE (I|PREMIÈRE)[.,]'), re.MULTILINE)
    regices.append(re.compile('\s*ACTE I\.*\s*$'), re.MULTILINE)
    regices.append(re.compile('\s*PREMIER INTERMÈDE\.*\s*$'), re.MULTILINE)

    return regices

def datasetize(fname, in_dir, out_dir, regices):

    with open(os.path.join(in_dir, fname), 'r') as f:
        txt = f.read()

    # with open(os.path.join(out_dir, fname) as o:
    #           o.write(txt)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="""Turning clean .txt Théâtre Classique files 
        into a dataset (notably: adding <startoflines> and <endoflines> and
        other markers."""
    )

    parser.add_argument(
        '-d',
        '--dir',
        type=str,
        default='théâtre-classique',
        help='The directory containing the .txt files, defaults to théâtre-classique',
    )

    parser.add_argument(
        '-o',
        '--out_dir',
        type=str,
        default='théâtre-classique-clean',
        help='The directory containing the .txt files, defaults to
        théâtre-classique-clean',
    )

    args = parser.parse_args()
    main(args)
