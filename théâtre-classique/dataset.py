import os
import regex
import argparse
from bs4 import BeautifulSoup


def main(args):
    files = [x for x in os.listdir(args.dir) if ".html" in x]
    total = len(files)
    print(f"{total} files to process in source dir {args.dir}")
    make_dir(args.out_dir)
    regices = make_regices()
    for i, f in enumerate(files):
        out_f = os.path.splitext(f)[0] + ".txt"
        if not os.path.isfile(os.path.join(args.out_dir, out_f)):
            print(f"{i:4}/{total} | processing {f}")
            datasetize(f, out_f, args.dir, args.out_dir, regices)
        else:
            print(f"{i:4}/{total} | already processed {f}, passing")
    clean_dir(args.out_dir)


def make_regices():
    return {
        "blacklist": {
            "[document]",
            "html",
            "meta",
            "link",
            "body",
            "head",
            "div",
            "script",
            "table",
            "tr",
            "span",
            "small",
            "title",
        },
        "class_riddance": {
            "didascalie",
            "didascalieLongue",
            "scene",
            "acte",
            "datedoc",
            "soustitre",
            "casting",
            "imprimeur",
            "info",
            "titre",
            "auteur",
            "distribution",
            "scenographie",
            "texte",
            "note",
            "prose",
        },
        "blank_line": regex.compile("^\s+$"),
        "init_space": regex.compile("^\s+"),
        "space_riddance": regex.compile("(\s\s+|\n$)"),
        "cace_dédi": regex.compile("^\s*[AÀ] ", regex.UNICODE),
        "various_riddances": [
            regex.compile(
                "^\s*[ÉE]dition .*(d|établie|soutien|critique)",
                regex.UNICODE | regex.IGNORECASE,
            ),
            regex.compile(
                "^\s*(Publié|[ÉE]dité) par", regex.UNICODE | regex.IGNORECASE
            ),
            regex.compile(
                "^\s*T?exte (conforme|saisi|[eé]tabli|[eé]dit[eé]|extrait)",
                regex.UNICODE | regex.IGNORECASE,
            ),
            regex.compile("^\s*Transcription", regex.UNICODE | regex.IGNORECASE),
            regex.compile("^\s*D'après", regex.UNICODE | regex.IGNORECASE),
            regex.compile("^\s*Tiré d", regex.UNICODE | regex.IGNORECASE),
            regex.compile("^\s*Extrait d", regex.UNICODE | regex.IGNORECASE),
            regex.compile("^\s*Page \d+", regex.UNICODE | regex.IGNORECASE),
            regex.compile("^.*in tome.*"),
            regex.compile(
                "^\s*(PERSONNAGES?|(LES )?ACTEURS?|NOMS (ET|DES))", regex.IGNORECASE
            ),
            regex.compile("^\s*((\p{Lu}+)[ \p{posix-punct}]*)+$", regex.UNICODE),
            regex.compile(
                "\** +"
                + regex.escape("Erreur dans l'interprétation du texte (ligne ")
                + "[0-9]+"
                + regex.escape(", programme : edition")
                + "(_txt)*"
                + regex.escape(".php)")
            ),
        ],
    }


def datasetize(fname, out_fname, in_dir, out_dir, regices):

    with open(os.path.join(in_dir, fname), "r") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        all_text = soup(text=True)

        purged = []
        incipit = False
        check_dedication = True
        for a in all_text:
            if a.parent.name not in regices["blacklist"]:
                # the end
                if a.parent("a", attrs={"name": "fin"}):
                    purged.append("<|finderéplique|>")
                    break
                # no blank lines
                if not regex.match(regices["blank_line"], a):
                    if "class" in a.parent.attrs:
                        # all the riddances
                        if a.parent.attrs["class"][0] in regices["class_riddance"]:
                            continue
                        # prose needs reformatting
                        elif a.parent.attrs["class"][0] == "proseincise":
                            a = regex.sub(regices["init_space"], "", a)
                            a = regex.sub(regices["space_riddance"], " ", a)
                            purged.append(a)
                            continue
                        # use 'locuteurs' to define dialogue boundaries
                        elif a.parent.attrs["class"][0] == "locuteur":
                            # skip very first line
                            # stop search for dedication
                            if not incipit:
                                incipit = True
                                check_dedictaion = False
                            else:
                                purged.append("<|finderéplique|>")
                            purged.append(a)
                            purged.append("<|débutderéplique|>")
                            continue
                    # annoying untagged dedications
                    if check_dedication and regex.match(regices["cace_dédi"], a):
                        continue
                    # more riddance ("Publié par..", "Texte établi..", etc., or full caps lines)
                    found = False
                    for riddance in regices["various_riddances"]:
                        if regex.search(riddance, a):
                            found = True
                            break
                    if found:
                        continue
                    purged.append(a)

        # some texts are only a monologue, make sure they have an initial tag
        # incipit was never set to True in loop
        if not incipit:
            purged = ["<|débutderéplique|>"] + purged

        # remove empty docs (only ["<|débutderéplique|>", # "<|finderéplique|>"])
        if len(purged) <= 2:
            return

        with open(os.path.join(out_dir, out_fname), "w") as o:
            o.write("\n".join(purged))


def make_dir(out_dir):
    if not os.path.isdir(out_dir):
        print(f"creating result directory {out_dir}")
        os.mkdir(out_dir)
    else:
        print(f"directory {out_dir} already exists")


def clean_dir(out_dir):
    # if no result, remove dir
    if len(os.listdir(out_dir)) == 0:
        print(f"result directory {out_dir} empty, removing it")
        os.removedirs(out_dir)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="""Turning clean .txt Théâtre Classique files
        into a dataset (notably: adding <startoflines> and <endoflines> and
        other markers."""
    )

    parser.add_argument(
        "-d",
        "--dir",
        type=str,
        default="théâtre-classique-source",
        help="The directory containing the .txt files, defaults to théâtre-classique",
    )

    parser.add_argument(
        "-o",
        "--out_dir",
        type=str,
        default="théâtre-classique-dataset",
        help="""The directory containing the .txt files, defaults to
        théâtre-classique-clean""",
    )

    args = parser.parse_args()
    main(args)
