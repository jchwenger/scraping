import os
import sys
import time
import json
import regex
import string
import pprint
import urllib3
import certifi
from bs4 import BeautifulSoup
from collections import defaultdict

pp = pprint.PrettyPrinter(indent=2)

CACHE_DIR = "cache"

def data_dir():
    if not os.path.isdir(CACHE_DIR):
        os.mkdir(CACHE_DIR)

def get_soup(url, http):
    data_dir()
    punct_re = regex.compile(f"[{string.punctuation}]")
    fname = punct_re.sub("-", url)
    if not os.path.isfile(os.path.join(CACHE_DIR, fname)):
        r = http.request("GET", url)
        data = r.data
        with open(os.path.join(CACHE_DIR, fname), "wb") as o:
            o.write(data)
    else:
        with open(os.path.join(CACHE_DIR, fname)) as i:
            data = i.read()
    return BeautifulSoup(data, "html.parser")


def main():
    ur_url = "https://fr.wikisource.org"
    base_url = (
        "https://fr.wikisource.org/wiki/Lexique_de_l%E2%80%99ancien_fran%C3%A7ais"
    )
    http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())

    out_dir = "lexique-moyen-fr"
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    init_links = []
    title_re = regex.compile("^Lexique.*\d$")
    all_href = get_soup(base_url, http).find_all("a", title=title_re)

    init_star = regex.compile(r"^\*\s*")
    num_re = regex.compile(r"^(\d+\.)\s*(.*)")
    init_space_comma = regex.compile(r"^\s*,\s*")
    final_dot = regex.compile(r"\.$")
    dot_comma_space = regex.compile(r"(?<=\.),\s*")

    les_words = defaultdict(list) # dicts are now ordered by default (> 3.7), https://stackoverflow.com/a/53657523/9638108

    longest = len(max([i.text for i in all_href], key=len))
    # with open(os.path.join(out_dir, "lexique-moyen-fr.txt"), "w"):
    for init_link in all_href:
        if init_link.text != "ADDITIONS ET CORRECTIONS":
            print(f"{init_link.text:{longest}} | {init_link['href']}")
            dict_page = get_soup(ur_url + init_link["href"], http)
            list_li = dict_page.find("ul").find_all("li")
            for li in list_li:
                try:
                    le_w, le_rest = li.text.split(",", 1)
                except:
                    le_w, le_rest = li.text.split(".", 1)
                    # print("*****", li.text)
                le_rest = le_rest.split("‖")
                gram_def = defaultdict(list)
                # gram_def["sanity"] = le_rest
                curr_gram = None
                for chunk in le_rest: # go thru chunks to find grammatical specs
                    rr = regex.search(dot_comma_space, chunk)
                    if rr: # if a gramm spec is found, store a new key
                        curr_gramm = chunk[:rr.span()[0]].strip()
                        gram_def[curr_gramm].append(chunk[rr.span()[1]:].strip())
                    else:
                        gram_def[curr_gramm].append(chunk.strip())
                le_w = init_star.sub("", le_w)
                les_words[num_re.sub(r"\2", le_w)].append(gram_def)
                # le_w = num_re.sub(r"\2, \1", le_w)
                # print(le_w, "|", le_rest)
                # le_w = li.find("b")
                # print(num_re.sub(r"\2, \1", le_w.text))
                # le_rest = le_w.next_sibling
                # print(le_rest)
                # le_rest = final_dot.sub("", init_space_comma.sub("", le_rest))
                # for chunk in le_rest.split("‖"):
                #     print(chunk)
                    # if "," in chunk:
                    #     chunk = chunk.split(",")
                    #     print(f"({chunk[0]})")
                    #     print("- ", chunk[1])
                    # else:
                    #     print("- ", chunk)
            # time.sleep(.1)
            # break

    # print("-" * 40)
    # pp.pprint(les_words.keys())

    w_file = os.path.join(out_dir, "lexique-moyen-fr.txt")
    dict_file = os.path.join(out_dir, "lexique-moyen-fr.json")
    with open(w_file, "w") as o, open(dict_file, "w") as oo:
        o.write("\n".join(les_words.keys()))
        json.dump(les_words, oo, ensure_ascii=False, indent=2)
    print("-" * 40)
    print(f"written words to {w_file}")


if __name__ == "__main__":
    main()
