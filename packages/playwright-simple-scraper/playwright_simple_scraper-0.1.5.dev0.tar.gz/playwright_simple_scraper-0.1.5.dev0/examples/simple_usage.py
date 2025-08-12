import pprint
import logging
from playwright_simple_scraper import scrape_context, scrape_href

general_sites = [
    {"url": "https://news.ycombinator.com", "selector": ".athing .titleline > a"},
    {"url": "https://en.wikipedia.org/wiki/Constans_II_(son_of_Constantine_III)",  "selector": "h1"},
    {"url": "https://www.bls.gov/news.release/cpi.htm", "selector": ".normalnews > pre"},
    {"url": "https://www.census.gov/retail/sales.html", "selector": "div.richtext"}
]

href_sites = [
    {"url": "https://www.whitehouse.gov/news/", "selector": "a"},
    {"url": "https://www.bbc.com/news", "selector": "#main-content > article > section:nth-child(3) > div > div > div.sc-666b6d83-0.sc-d2e835e5-2.icCajy.hOJtTi > div:nth-child(2) > div > a"},
]

logging.basicConfig(filename="output.log", level=logging.INFO)

def main():
    # 1. general context scraping
    for site in general_sites:
        url      = site["url"]
        selector = site["selector"]
        print(f"--- CONTEXT: {url=} {selector=} ---")
        context_res = scrape_context(url, selector)
        with open("test01.log", "w", encoding="utf-8") as f:
            pprint.pprint(context_res, stream=f)

    # 2. href scraping
    for site in href_sites:
        url      = site["url"]
        selector = site["selector"]
        print(f"--- HREFs: {url=} {selector=} ---")
        href_res = scrape_href(url, selector)
        with open("test02.log", "w", encoding="utf-8") as f:
            pprint.pprint(href_res, stream=f)

if __name__ == "__main__":
    main()
