import os
import re
import re
import random
import pprint
import urllib3
import certifi
import argparse
from time import sleep
from bs4 import BeautifulSoup


def main(args):
    author = args.author
    auth_re = re.compile('^'+author, re.IGNORECASE) 
    lang = re.compile(args.language, re.IGNORECASE)
    delay = args.delay
    # browse page with first letter
    letter = author[0].lower()
    url = 'http://www.gutenberg.org/browse/authors/' + letter
    # request, get & soup
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    r = http.request('GET', url)
    soup = BeautifulSoup(r.data, 'html.parser')
    # get links to all ebooks
    links = get_links(auth_re, soup, lang)
    # make result dir
    author_dir = make_dir(author)
    total = len(list(links.keys()))
    print(f'{total} links in total')
    i = 1
    for title, link in links.items():
        save_ebook(title, link, author_dir, i, total, delay, http)
        i += 1

    # if no download, remove dir
    if len(os.listdir(author_dir) == 0: 
           os.removedirs(author_dir)

def get_links(auth_re, soup, lang):
    # find section
    h2 = soup.find_all(string=auth_re)
    choice = 0
    if len(h2) > 1:
        print('more than one possibility, please choose:')
        for i, n in enumerate(h2):
            print(f'{i}: {n}')
        choice = int(input())
    # find list of books
    ul = h2[choice].next
    while ul.name != 'ul':
        ul = ul.next
    # only direct authorship
    as_auth = re.compile('as Author')
    links = {}
    for li in ul.find_all(class_='pgdbetext'):
        if li.find(string=as_auth) and li.find(string=lang):
            links[li.a.text.replace('\r',' ')] = li.a['href']
    return links

def save_ebook(title, link, author_dir, i, total, delay, http):
    # format title
    riddance = re.compile('[!?.()"";:,\']')
    t = re.sub(riddance, '', title.lower()).replace(' ', '-') + '.txt'
    if not os.path.isfile(os.path.join(author_dir, t)):
        ebook = get_ebook(link, http, delay=delay)
        l = len(str(total))
        print(f'{i:{l}}/{total}, saving: {t}')
        with open(os.path.join(author_dir, t), 'wb') as f:
            f.write(ebook)
    else:
        print(f'{i:4}/{total}, already downloaded {t}, continuing')    

def get_ebook(link, http, delay=1):
    G = 'http://www.gutenberg.org'
    # go to list of formats
#     http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    r = http.request('GET', G+link)
    s = BeautifulSoup(r.data, 'html.parser')
    # find utf-8 plain text version
    txt = re.compile('plain text', re.IGNORECASE)
    l = s(string=txt)[0].parent['href'] # link
    sleep(delay) # get thee not blocked
    # download ebook & return it
    h = http.request('Get', G+l)
    return(h.data)

def make_dir(author):
    author_dir = '-'.join(map(str.lower, author.split(', '))) + '-source'
    if not os.path.isdir(author_dir):
        print(f'creating new directory {author_dir}')
        os.mkdir(author_dir)
    else: print(f'{author_dir} already exists')
    return author_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Downloading all books by one author from Gutenberg"
    )
    parser.add_argument(
        "-a",
        "--author",
        type=str,
        default='Shakespeare, William',
        help="""The author's name in such a format: 'lastname, first name'. 
                Case insensitiv.e Must start by the same character the same as
                on the gutenberg browse page, e.g.  
                http://www.gutenberg.org/browse/authors/a""",
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="English",
        help="The language of the selected ebooks, default: any",
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=1,
        help="The delay to wait between each download, default: 1 second",
    )
    args = parser.parse_args()
    main(args)
