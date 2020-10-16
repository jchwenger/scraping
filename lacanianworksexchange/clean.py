import os
import ftfy

src = "miner"

if not os.path.isdir(src):
    print("miner/ dir not found, please scrape & convert pdf to text first")

dest = "clean"

if not os.path.isdir(dest):
    os.mkdir(dest)
    print("making dir clean/")

for f in os.listdir(src):
    if not os.path.isfile(os.path.join(dest, f)):
        print(f"processing: {f}")
        with open(os.path.join(src, f), "r") as i:
            with open(os.path.join(dest, f), "w") as o:
                o.write(ftfy.fix_text(i.read()))
    else:
        print(f"found     : {f}")

