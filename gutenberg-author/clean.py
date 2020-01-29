import os
import re
import argparse
from shutil import copyfile


def main(args):
    input_dir = args.dir
    p = re.compile('-source')
    output_dir = re.sub(p, '', input_dir)
    make_dir(output_dir)
    files = os.listdir(input_dir)
    transfer(files, input_dir, output_dir)


def transfer(files, input_dir, output_dir):
    total = len(files)
    for i, fname in enumerate(files):
        msg = f"file {i+1:4}/{total}, name: {fname}"
        blank = os.get_terminal_size()[0] - len(msg)
        print(msg + " " * blank)
        f = openfile(os.path.join(input_dir, fname))
        eoh = end_of_header(f, fname)
        sof = start_of_footer(f, fname)
        stripped_f = strip_lines(f[eoh:sof])
        writefile(os.path.join(output_dir, fname), stripped_f)


def end_of_header(lines, fname):
    start = 0
    # try to find *** START OF TH... or end
    pattern = re.compile(
        r"(^ *\*+ *start of th|^ *\*+.*end.*the small print)", re.IGNORECASE
    )
    limit = len(lines) // 3  # only search the first third of the document
    for i, l in enumerate(lines[:limit]):
        if re.match(pattern, l):
            ind = 0  # find the end of the paragraph
            while not "\n" == lines[i + ind]:
                ind += 1
            start = i + ind
            break
    if start == 0:
        print(f"Header not found: {fname}")
    # try to find lines starting with 'Produced/Distributed'
    pattern = re.compile(r"(.*etext.*prepared|^produced|^distributed)", re.IGNORECASE)
    for i, l in enumerate(lines[start : start + 50]):
        if re.match(pattern, l):
            ind = 1
            # find the end of the paragraph
            while not "\n" == lines[start + i + ind]:
                ind += 1
            # remove empty lines
            start = start + i + ind
            break
    # try to find a title
    # for i, l in enumerate(lines[start : start + 50]):
    #     if l.isupper():
    #         start = start + i
    #         break
    return start


def start_of_footer(lines, fname):
    pattern = re.compile(r"^(\*\*\*)* *end of.*project gutenberg", re.IGNORECASE)
    start = 0
    for i, l in enumerate(lines):
        if re.match(pattern, l):
            start = i - 1
            break
    if start == 0:
        print(f"Footer not found: {fname}, start: {start}")
        start = len(lines) - 1
    return start


def strip_lines(lines):
    start = 0
    end = len(lines) - 1
    for i, l in enumerate(lines):
        if "\n" != l:
            start = i
            break
    for i, l in enumerate(reversed(lines)):
        if "\n" != l:
            end = len(lines) - i
            break
    return lines[start:end]


def reencode(lines, fname):
    newlines = []
    if "ï»¿" in lines[0]:
        for i in range(len(lines)):
            try:
                newlines.append(lines[i].encode("latin-1").decode("utf-8"))
            except:
                newlines.append(lines[i].encode("latin-1").decode("utf-8", "ignore"))
                print(f"ignoring error in file {fname}, line: {i}:")
                print(f"before: {lines[i]}")
                print(f"after: {newlines[-1]}")
        return newlines
    return lines


# utils


def openfile(fname):
    try:
        with open(fname, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except:
        with open(fname, "r", encoding="latin-1") as f:
            lines = f.readlines()
    lines = reencode(lines, fname)
    return lines


def writefile(fname, lines):
    with open(fname, "w") as wr:
        wr.writelines(lines)


def make_dir(output_dir):
    if os.path.isdir(output_dir):
        return
    os.mkdir(output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copying & cleaning Gutenberg files")
    parser.add_argument(
        "-d", "--dir", type=str, help="The input directory with raw files"
    )
    args = parser.parse_args()
    main(args)
