import os
import re
from bs4 import BeautifulSoup


def main():
    source_dir = "théâtre-classique-source"
    files_txt = []
    files_html = []
    for f in os.listdir(source_dir):
        if ".txt" in f:
            files_txt.append(f)
        elif ".html" in f:
            files_html.append(f)
    # make result dir
    output_dirs = make_dir()

    # process_txt_files(source_dir, output_dirs['txt'], files_txt)
    process_html_files(source_dir, output_dirs['html'], files_html)

    # if no result, remove dir
    for output_dir in output_dirs.values():
        if len(os.listdir(output_dir)) == 0:
            print(f"result directory {output_dir} empty, removing it")
            os.removedirs(output_dir)


def process_txt_files(source_dir, output_dir, files_txt):
    total = len(files_txt)
    l = len(str(total))
    err = re.escape("***************** Erreur dans l'interprétation du texte (ligne ")
    err += "[0-9]+"
    err += re.escape(", programme : edition_txt.php)")
    err_re = re.compile(err)
    for i, fname in enumerate(files_txt):
        if os.path.isfile(os.path.join(output_dir, fname)):
            print(f"{i+1:{l}}/{total}: already processed {fname}")
        else:
            print(f"{i+1:{l}}/{total}: processing {fname}")
            with open(os.path.join(source_dir, fname), "r") as f:
                txt = f.read()
                start = txt.find("*\n\n") + 1
                end = txt.rfind("\t=")
                txt = txt[start:end].strip()
                txt = re.sub(err_re, "", txt)
                with open(os.path.join(output_dir, fname), "w") as o:
                    o.write(txt)


def process_html_files(source_dir, output_dir, files_html):

    total = len(files_html)
    l = len(str(total))

    # various clean-up utilities
    html_blacklist = {
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
    }
    blank_line = re.compile("^\s+$")
    require_tabs = {"didascalie", "didascalieLongue"}
    require_nl = {"datedoc", "soustitre", "casting", "imprimeur"}
    init_space = re.compile('^\s+')
    space_riddance = re.compile('(^\s+|\s\s+)')

    for i, fname in enumerate(files_html):
        out_fname = f"{os.path.splitext(fname)[0]}.txt"
        if os.path.isfile(os.path.join(output_dir, out_fname)):
            print(f"{i+1:{l}}/{total}: already processed {fname}")
        else:
            print(f"{i+1:{l}}/{total}: processing {fname}")
            with open(os.path.join(source_dir, fname), "rb") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                all_text = soup(text=True)
                purged = []
                for a in all_text:
                    if a.parent.name not in html_blacklist:
                        # the end
                        if a.parent("a", attrs={"name": "fin"}):
                            break
                        # no unnecessary blank lines
                        if not re.match(blank_line, a):
                            if "class" in a.parent.attrs:
                                if a.parent.attrs["class"][0] in require_tabs:
                                    purged.append(f"\t{a}")
                                    continue
                                elif a.parent.attrs["class"][0] in require_nl:
                                    purged.append(f"\n{a}\n")
                                    continue
                                elif a.parent.attrs["class"][0] == "acte":
                                    purged.append(f"\n\t\t\t{a}\n")
                                    continue
                                elif a.parent.attrs["class"][0] == "info":
                                    continue
                                elif a.parent.attrs['class'][0] == 'proseincise':
                                    a = re.sub(init_space, '', a)
                                    a = re.sub(space_riddance, ' ', a)
                                    purged.append(a)
                                    continue
                            purged.append(a)
                with open(os.path.join(output_dir, out_fname), "w") as o:
                    o.write("\n".join(purged))


def make_dir():
    source_dirs = {"txt": "théâtre-classique-txt", "html": "théâtre-classique-html"}
    for sd in source_dirs.values():
        if not os.path.isdir(sd):
            print(f"creating result directory {sd}")
            os.mkdir(sd)
        else:
            print(f"directory {sd} already exists")
    return source_dirs


if __name__ == "__main__":
    main()
