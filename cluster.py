from difflib import SequenceMatcher
import re


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return text


def similar(a, b):
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def cluster_news(articles, threshold=0.7):
    clusters = []

    for article in articles:
        found = False

        for cluster in clusters:
            if similar(article["title"], cluster["headline"]) > threshold:
                cluster["articles"].append(article)
                found = True
                break

        if not found:
            clusters.append({
                "headline": article["title"],
                "articles": [article]
            })

    return clusters
