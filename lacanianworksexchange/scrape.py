import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup

plain_url = "https://www.lacanianworksexchange.net"

url = plain_url + "/lacan"
print("scraping today")
print(url)
r = requests.get(url).text

soup = BeautifulSoup(r, "html.parser")

soup.find_all("href")
soup.find_all(href=True)

a = soup.find_all(href=re.compile("pdf"))

print("extracted all href links, found:", len(a))

# for el in a:
#     print(el["href"])

links = []
for el in a:
    l = el["href"].strip()
    if re.match("\/", l):
        l = plain_url + l
        links.append(l)
        continue
    if re.match("file", l):
        l = plain_url + re.sub("file://", "", l)
        links.append(l)
        continue
    if re.match("available", l):
        l = re.sub("available here ", "", l)
        links.append(l)
        continue
    links.append(l)

pdf_dir = "pdf"
if not os.path.isdir(pdf_dir):
    os.mkdir(pdf_dir)

for l in links:
    fname = l[l.rfind("/") + 1 :]
    if not os.path.isfile(os.path.join(pdf_dir, fname)):
        try:
            print("scraping:", fname)
            r = requests.get(l, headers={"User-agent": "Lacan-loving bot"})
            if r.status_code != 200:
                print("AOUCH, no status code 200 received")
                break
            else:
                r = r.content
            with open(os.path.join(pdf_dir, fname), "wb") as o:
                o.write(r)
        except KeyboardInterrupt:
            print("ok bye")
            break
        except Exception as e:
            print("=" * 40)
            print("oops:", l)
            print(e)
            print("=" * 40)
            sys.exit()
        time.sleep(1)
    else:
        print("found:   ", fname)
