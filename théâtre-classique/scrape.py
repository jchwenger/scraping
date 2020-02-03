import os
import re
import pprint
import random
import urllib3
import certifi
import argparse
from time import sleep
from bs4 import BeautifulSoup
from collections import defaultdict


def main(args):

    delay = args.delay
    pp = pprint.PrettyPrinter(indent=2)

    url = 'http://www.theatre-classique.fr/pages/programmes/PageEdition.php'

    # request, get & soup
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    req = http.request('GET', url)
    soup = BeautifulSoup(req.data, 'html.parser')

    # get links to all ebooks
    links = defaultdict(list)
    soup = soup('tbody')[0]  # reduce search only to the data table
    rows = soup(string=re.compile('^HTML$'))  # find element containing html link
    for r in rows:
        author, info = get_links(r, try_for_txt=args.try_for_txt)
        links[author].append(info)
    # pp.pprint(links)

    # make result dir
    source_dir = make_dir()
    total = total_ebooks(links)
    print(f'{total} links in total')
    i = 1
    for author, books in links.items():
        for book in books:
            save_ebook(
                book['link'], book['nature'], source_dir, i, total, delay, http
            )
            i += 1

    # if no download, remove dir
    if len(os.listdir(source_dir)) == 0:
        os.removedirs(source_dir)


def get_links(row, try_for_txt=True):
    el = row.parent.parent  # local <td> with link
    parent = el.parent  # main <td> with all categories
    author = parent.find_all(attrs={'href': '../bio/auteurs.htm#'})[0]
    title = author.parent.next_sibling.next_sibling
    # preemptively store html version
    result = el
    nature = 'xml'
    if try_for_txt:
        txt_re = re.compile('^TXT$')
        result = parent(string=txt_re)  # search for txt category
        # if no txt available, return html
        if len(result) != 0: # if found, return txt el
            result = result[0].parent.parent
            nature = 'txt'
    link = result.a['href']
    return author.text, {'title': title.text, 'link': link, 'nature': nature}


def save_ebook(link, nature, source_dir, i, total, delay, http):
    # format title
    fname_orig = link[link.rfind('/')+1:]
    if nature == 'txt':
        fname = fname_orig
    elif nature == 'xml':
        fname = fname_orig[:fname_orig.rfind('.')] + '.html'
    fname = fname.lower().replace('_', '-')
    if not os.path.isfile(os.path.join(source_dir, fname)):
        ebook = get_ebook(link, http, delay=delay).decode('latin-1')
        l = len(str(total))
        print(f'{i:{l}}/{total}, saving: {fname}')
        with open(os.path.join(source_dir, fname), 'w') as f:
            f.write(ebook)
    else:
        print(f'{i:4}/{total}, already downloaded {fname.lower()}, continuing')


def get_ebook(link, http, delay=1):
    # go to list of formats
    sleep(delay)  # get thee not blocked
    url = 'http://www.theatre-classique.fr/pages/programmes/'
    r = http.request('GET', url + link)
    return r.data


def total_ebooks(links):
    total = 0
    for author, books in links.items():
        total += len(books)
    return total


def make_dir():
    source_dir = 'théâtre-classique-source'
    if not os.path.isdir(source_dir):
        print(f'creating new directory {source_dir}')
        os.mkdir(source_dir)
    else:
        print(f'{source_dir} already exists')
    return source_dir


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="""Downloading all books by one author from Théâtre Classique:
        http://www.theatre-classique.fr"""
    )

    parser.add_argument(
        '-d',
        '--delay',
        type=float,
        default=1,
        help='The delay to wait between each download, default: 1 second',
    )

    parser.add_argument(
        '-t',
        '--try_for_txt',
        type=bool,
        default=False,
        help='Attempt to download the txt version if available, default: False',
    )

    args = parser.parse_args()
    main(args)
