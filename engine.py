from news_sources import fetch_news
from cluster import cluster_news


def dedupe(cluster):
    seen = {}
    for a in cluster["articles"]:
        if a["source"] not in seen:
            seen[a["source"]] = a
    return list(seen.values())


def score(cluster):
    sources = dedupe(cluster)
    return len(sources)  # v1 scoring


def run_engine():
    articles = fetch_news()
    clusters = cluster_news(articles)

    enriched = []

    for c in clusters:
        sources = dedupe(c)

        enriched.append({
            "headline": c["headline"],
            "sources": sources,
            "source_count": len(sources),
            "score": score(c)
        })

    ranked = sorted(enriched, key=lambda x: x["score"], reverse=True)

    return ranked[:5], ranked[5:15]
