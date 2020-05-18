import os
import argparse
from chardet.universaldetector import UniversalDetector

parser = argparse.ArgumentParser(
    description="Open txt files, attempt to detect encoding using Chardet, reencode in utf-8. Dir containing files. Files must end in '.txt' to be taken into account.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "--dir",
    metavar="DIR",
    type=str,
    required=True,
    help="Dir containing files. Files must end in '.txt' to be taken into account.",
)

def main(args):
    detector = UniversalDetector()
    fnames = [x for x in os.listdir(args.dir) if '.txt' in x]

    for filename in fnames:
        filepath = os.path.join(args.dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as ff:
                txt = ff.read()
            print(f"{filename} ok")
        except:
            detector.reset()
            for line in open(filepath, 'rb'):
                detector.feed(line)
            detector.close()
            print(f"converting: {filename} | encoding detected: {detector.result}")
            enc = detector.result["encoding"]
            with open(filepath, 'r', encoding=enc) as ff:
                txt = ff.read()
                with open(filepath, 'w') as o:
                    o.write(txt)

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
