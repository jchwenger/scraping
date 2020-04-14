import os
import bs4
import sys
import regex
import pprint
import urllib3
import certifi
from time import sleep
from bs4 import BeautifulSoup

pp = pprint.PrettyPrinter(indent=2)


def main():
    base_url = "http://www2.univ-paris8.fr/deleuze/"
    http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())

    out_dir = "deleuze-txt"
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    init_links = []
    all_href = get_soup(base_url, http).find_all("a", href=True)
    for init_link in all_href:
        txt = init_link.get_text()
        if not regex.search(
            r"(La voix de Gilles Deleuze en ligne|L’association Siècle Deleuzien)", txt
        ):
            init_links.append(
                {"coursetitle": init_link.get_text(), "url": init_link["href"]}
            )

    print_separator()
    underprint("all course links:")
    for l in init_links:
        title = l["coursetitle"]
        url = l["url"]
        print(f"cours: {title}")
        print(f"       {url}")
    print_separator()

    all_course_pages = []
    for link in init_links:
        link_url = base_url + link["url"]
        print(f"Joy! Scraping: {link_url}")
        all_course_pages.append({"data": link, "soup": get_soup(link_url, http)})
        sleep(0.6)

    all_articles_links = []
    for course_page in all_course_pages:
        all_href = course_page["soup"].find_all("a", href=True)
        for a_with_href in all_href:
            url = a_with_href["href"]
            txt = a_with_href.get_text()
            if "article" in url and not regex.search(
                r"([Ee]nglish|Siècle Deleuzien|voix de Gilles Deleuze)", txt
            ):  # riddance of course in English & paradeleuzialia
                all_articles_links.append(
                    {
                        "title": course_page["data"]["coursetitle"],
                        "subtitle": txt,
                        "url": url,
                    }
                )

    max_length = find_max_string_length(all_articles_links)

    print_separator()
    underprint("all article links:")
    current_title = ""
    for al in all_articles_links:
        title = al["title"]
        subtitle = al["subtitle"]
        url = al["url"]
        if title != current_title:
            print()
            underprint(title)
            current_title = title
        print(f"- '{subtitle:<{max_length}}' | {url}")
    print_separator()

    all_articles = []
    for article_link in all_articles_links:
        article_url = base_url + article_link["url"]
        print(f"Joy! Scraping: {article_url}")
        soup = get_soup(article_url, http)
        all_articles.append(
            {
                "title": article_link["title"],
                "subtitle": article_link["subtitle"],
                "soup": soup.find("td", {"class": "textearticle"}),
            }
        )
        sleep(0.6)

    print_separator()

    underprint("writing:")
    for article in all_articles:
        title = article["title"]
        subtitle = article["subtitle"]
        soup = article["soup"]
        plain_text_article = "\n".join(
            [x.get_text() for x in soup.find_all("p", {"class": "spip"})]
        )
        if plain_text_article:
            title = title.replace("\xa0", "")
            title = regex.sub(r"[\p{Z}/]+", "-", title)
            title = regex.sub(r"-+", "-", title)
            title = regex.sub(r"^-", "", title)
            subtitle = regex.sub(r"[\p{Z}/]+", "-", subtitle)
            subtitle = regex.sub(r"-+", "-", subtitle)
            subtitle = regex.sub(r"^-", "", subtitle)
            outname = f"{title}-{subtitle}.txt"
            outname = os.path.join(out_dir, outname)
            print(f"- {title}-{subtitle}.txt")
            with open(outname, "w") as o:
                o.write(plain_text_article)

    print_separator()
    underprint(f"found {len(all_articles)} article pages.")


def get_soup(url, http):
    r = http.request("GET", url)
    return BeautifulSoup(r.data, "html.parser")


def get_page(url, http):
    r = http.request("GET", url)
    return r.data


def underprint(x):
    print(x)
    print("-" * len(x))


def print_separator():
    print("-" * 40)


def find_max_string_length(links):
    max_len = 0
    for l in links:
        if len(l["subtitle"]) > max_len:
            max_len = len(l["subtitle"])
    return max_len


if __name__ == "__main__":
    main()
