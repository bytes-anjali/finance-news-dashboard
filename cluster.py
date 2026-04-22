from difflib import SequenceMatcher
import re


def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def similar(a, b):
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def cluster_news(articles, threshold=0.72):
    clusters = []

    for article in articles:
        found = False

        for cluster in clusters:
            if similar(article["title"], cluster["headline"]) >= threshold:
                cluster["articles"].append(article)
                found = True
                break

        if not found:
            clusters.append({
                "headline": article["title"],
                "articles": [article]
            })

    return clusters


def dedupe_sources(cluster):
    seen = {}
    for article in cluster["articles"]:
        source = article["source"]
        if source not in seen:
            seen[source] = article
    return list(seen.values())
