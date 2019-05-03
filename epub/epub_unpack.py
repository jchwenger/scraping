#!/usr/bin/env python3

import os
import sys
import glob
import shutil
import zipfile
import shutil
from bs4 import BeautifulSoup

def main(args):
    
    # epub_shell = EpubShell()
    # epub_shell.cmdloop()

    #creating tmp dir for file extraction
    tmp_dir = 'tmp'
    if not os.path.isdir(tmp_dir):
        os.mkdir(tmp_dir)

    # if filenames not specified by user
    if len(args) == 0:

        filenames = []
        while not filenames:
            filenames = input('please specify filenames: ')
            if not filenames:
                print('can\'t do a thing without filenames, please try again')
            else:
                print('thanks, filenames are:')
                filenames = [x for x in filenames.split() if x]
                args = filenames
                
    for filename in args:
        
        print('extracting:', filename)
        
        fn_base = os.path.basename(filename) # filename.epub
        fn_noext = os.path.splitext(fn_base)[0] # filename
        extr_dir = os.path.join(tmp_dir, fn_noext) # destination dir
        
        # create dir named after the original file
        if not os.path.isdir(extr_dir):
            os.mkdir(extr_dir)        
            
        # extract the file
        with zipfile.ZipFile(filename, 'r') as extr_file:
            extr_file.extractall(extr_dir)
                
        # removing META-INF folder
        meta = glob.glob(extr_dir + '/META*')
        shutil.rmtree(meta[0])
            
        to_be_parsed = get_files(extr_dir)
        txt_out = parse_soup(to_be_parsed)
        write_parsed(fn_noext, txt_out)

    shutil.rmtree(tmp_dir)
    print('all done, txt file available in results/', )

def get_files(parse_dir):

    parseable = []
    ftypes = ['xhtml', 'html', 'htm', 'xml']

    for ftype in ftypes:
        parseable.extend(glob.glob(parse_dir + '/**/*.' + ftype, recursive=True))

    if not parseable:
        print('nothing found in', parse_dir)
    else:
        parseable.sort()
        print('found the following files:')
        for i, fparse in enumerate(parseable):
            print(i+1, ':', fparse)
        print('\n---------\n')
    
    indices = input('please select the files to be parsed\
                        \n- press enter to select all\
                        \n- count starts with 1\
                        \n- ranges possible: 1-4 selects files 1 to 4, inclusive\n').split()


    to_be_parsed = []

    # if enter pressed the list is empty
    if not indices:
        to_be_parsed = parseable
    else:
        for index in indices:
            # for ranges, split by '-' then turn into int, use as list slice
            if '-' in index:
                start, end = [int(x)-1 for x in index.split('-')]
                to_be_parsed.extend(parseable[start:end+1]) 
            else:
                to_be_parsed.append(parseable[int(index)])

    print('keeping the following files:')
    for i, fparse in enumerate(to_be_parsed):
        print(fparse)
    print('\n---------\n')

    return to_be_parsed

def parse_soup(to_be_parsed):
    
    txt_out = []
    
    # use beautiful soup to scrape the html/xml files
    for fname in to_be_parsed:
        with open(fname, encoding='utf8', errors='ignore') as f:
            soup = BeautifulSoup(f,features='html5lib')
            
            # the following inspired by this: https://stackoverflow.com/a/22800287
            for script in soup(["script", "style"]):
                script.decompose()    # rip it out
            # get text
            text = soup.get_text()
            # break into lines and remove leading and trailing space on each
            lines = [line.strip() for line in text.splitlines()]
            # join again and remove empty lines
            text = '\n'.join(line for line in lines if line)
            txt_out.append(text)

    return txt_out

def write_parsed(name_noext, txt_out):
    
    resultdir = 'results'
    file_out = os.path.join(resultdir, name_noext + '.txt')
    
    if not os.path.isdir(resultdir):
        os.mkdir(resultdir)  
        
    with open(file_out, 'w') as out:
        for txt in txt_out:
            out.write(txt)

# only select the arguments coming after the name of the program
if __name__ == '__main__':
    main(sys.argv[1:])
