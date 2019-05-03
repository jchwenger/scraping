#!/bin/usr/python

# Useable like so
# python(3) scraper.py sourcefile.json

from bs4 import BeautifulSoup
import os, sys, re, urllib3, certifi, json
from time import sleep

def main(file):

    source_file = file # must be in the same format as given examples

    with open(source_file, 'r') as rs:
        urls = json.load(rs)

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    def get_data(url):
        r = http.request('GET', url)
        # print(r.status)
        if r.status == 200: 
            # clear_output()
            print('Joy! Able to scrape', url)
            soup = BeautifulSoup(r.data, 'html.parser')
            # the following inspired by this: https://stackoverflow.com/a/22800287
            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.decompose()    # rip it out
            # get text
            text = soup.get_text()
            # break into lines and remove leading and trailing space on each
            lines = [line.strip() for line in text.splitlines()]
            # join again and remove empty lines
            text = '\n'.join(line for line in lines if line)
            return text
        else:
            print('Oops, issue:', r.status)
            print('Url:', url)
            print('-'*60)

    source_name = os.path.splitext(os.path.basename(source_file))[0]
    if not os.path.isdir(source_name):
        os.mkdir(source_name)

    for i, url in enumerate(urls["urls"]):
        txt = get_data(url)
        with open(source_name + '/{}.txt'.format(i+1), 'w') as r:
            r.write(txt)
        sleep(0.5)

    print('Generated texts:', *os.listdir(source_name), sep='\n')

if __name__ == '__main__':
    main(sys.argv[1])
