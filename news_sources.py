import requests
import xml.etree.ElementTree as ET

SOURCES = {
    "Business Standard": "https://www.business-standard.com/rss/markets-106.rss",
    "Mint": "https://www.livemint.com/rss/markets",
    "Economic Times": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "Moneycontrol": "https://www.moneycontrol.com/rss/business.xml",
}


def fetch_news():
    articles = []

    for source, url in SOURCES.items():
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            root = ET.fromstring(resp.content)

            for item in root.findall(".//item")[:15]:
                articles.append({
                    "title": item.findtext("title", ""),
                    "link": item.findtext("link", ""),
                    "published": item.findtext("pubDate", ""),
                    "source": source
                })
        except:
            continue

    return articlesnews_sources.py
