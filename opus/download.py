import os
import gzip
import shutil
import argparse
import opustools
import numpy as np


def main(args):
    og = opustools.opus_get.OpusGet(
        source=args.language,
        preprocess="mono",
        list_resources=True,
        suppress_prompts=True,
        download_dir=args.download_dir,
    )

    corpora, file_n, total_size = og.get_corpora_data()

    # selecting only the txt ones, not the tok ones
    no_tok = []
    sizes = []
    file_n = 0
    total_size = 0
    for c in corpora:
        if "tok" not in c["url"]:
            no_tok.append(c)
            sizes.append(c["size"])
            file_n += 1
            total_size += c["size"]

    # sorting in ascending download size
    ordered_indz = np.argsort(np.array(sizes))
    ordered_no_tok = np.array(no_tok)[ordered_indz]
    total_size = og.format_size(total_size)
    underprint(f"Available resources for language {args.language}")
    og.print_files(ordered_no_tok[:3], file_n, total_size)
    if not args.list:
        og.download(ordered_no_tok[:3], file_n, total_size)

    # gunzipping: https://stackoverflow.com/a/41270260

    underprint(f"Gunzipping files in {args.download_dir}")
    if not args.no_gunzip:
        fnames = [f for f in os.listdir(args.download_dir)]
        for fname in fnames:
            path_in = os.path.join(args.download_dir, fname)
            with gzip.GzipFile(path_in, "rb") as i:
                path_out = os.path.join(
                    args.download_dir, os.path.splitext(fname)[0]
                )
                print(f"- {path_in} -> {path_out}")
                with open(path_out, "wb") as o:
                    shutil.copyfileobj(i, o)

def underprint(msg):
    print()
    print(msg)
    print("-" * len(msg))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="""Downloading all books from Opus: http://opus.nlpl.eu/.
        This is meant for language modelling rather than translation: the aim
        is to get large amounts of plain text, rather than language pairs."""
    )

    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="fr",
        help="""The language code chosen. Defaults to 'fr'.""",
    )

    parser.add_argument(
        "-dl",
        "--download_dir",
        type=str,
        default="opus",
        help="""The directory to be downloaded into. Defaults to 'opus'.""",
    )

    parser.add_argument(
        "-i",
        "--list",
        action="store_true",
        help="""Lists all resources available instead of downloading. Defaults
        to false.""",
    )

    parser.add_argument(
        "-g",
        "--no_gunzip",
        action="store_true",
        help="""Gunzips the files after downloading. Defaults to false.""",
    )

    args = parser.parse_args()

    main(args)
