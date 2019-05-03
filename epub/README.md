Unpacking and extracting epub formats interactively.  

For script use (Python 3 & BeautifulSoup): `python epub_unpack.py book1.epub book2.epub`. (Works with globs)  

For each epub, a list of internal files is presented for review (open them in a text editor to see their content), and the user can select using ranges (3-17, etc.) the ones that will be extracted (thus it is possible to avoid prefaces, TOCs, etc.).   

