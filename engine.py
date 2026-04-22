from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from cluster import cluster_news, dedupe_sources
from news_sources import fetch_news

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except Exception:
    PYTRENDS_AVAILABLE = False


TREND = None
if PYTRENDS_AVAILABLE:
    try:
        TREND = TrendReq(hl="en-IN", tz=330)
    except Exception:
        TREND = None


CATEGORY_RULES = {
    "IT Earnings / Dividend": ["results", "q4", "q3", "fy26", "dividend", "guidance", "earnings"],
    "Global Macro / Oil / Geopolitics": ["iran", "oil", "brent", "ceasefire", "war", "us", "china", "hormuz"],
    "Banking / Analyst Upgrade": ["bank", "brokerage", "target price", "upgrade", "downgrade"],
    "Mutual Funds / Retail Sentiment": ["sip", "mutual fund", "inflows", "amfi"],
    "IPO": ["ipo", "listing", "anchor", "gmp", "allotment"],
    "Power / Energy Stocks / Corporate": ["power", "energy", "nuclear", "coal"],
    "Economy / Macro Data / Policy": ["inflation", "cpi", "wpi", "iip", "core sector", "rbi", "gdp"],
    "Stocks in News": []
}


def parse_published_date(date_str):
    if not date_str:
        return None
    try:
        dt = parsedate_to_datetime(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def within_last_24h(date_str):
    dt = parse_published_date(date_str)
    if not dt:
        return False
    now = datetime.now(timezone.utc)
    return dt >= now - timedelta(hours=24)


def pick_latest_published(articles):
    dated = []
    for article in articles:
        dt = parse_published_date(article.get("published", ""))
        dated.append((dt, article))
    dated.sort(key=lambda x: x[0] or datetime(1970, 1, 1, tzinfo=timezone.utc), reverse=True)
    return dated[0][1] if dated else None


def extract_keywords(headline):
    h = headline.lower()

    words = [w for w in headline.replace("—", " ").replace("-", " ").split() if len(w) > 2]
    core = " ".join(words[:4]).strip()

    event = core
    fallback = "stock market news india"

    if "q4" in h or "results" in h or "earnings" in h:
        event = core
        fallback = "q4 results india"
    elif "ipo" in h:
        event = core
        fallback = "ipo india"
    elif any(x in h for x in ["iran", "oil", "brent", "war", "hormuz"]):
        event = core
        fallback = "crude oil india"
    elif "sip" in h or "mutual fund" in h:
        event = core
        fallback = "mutual fund india"
    elif "bank" in h:
        event = core
        fallback = "bank stocks india"

    return [k for k in [core, event, fallback] if k]


def get_trend_signal(keyword_list):
    if TREND is None:
        return "Unknown", 0, "Unknown"

    for keyword in keyword_list:
        try:
            TREND.build_payload([keyword], timeframe="now 1-d", geo="IN")
            data = TREND.interest_over_time()
            if data.empty or keyword not in data.columns:
                continue

            values = list(data[keyword].values)
            if not values:
                continue

            latest = int(values[-1])
            avg = sum(values) / len(values)

            if avg == 0 and latest > 0:
                return "Spike", latest, keyword
            if latest > avg * 1.5:
                return "Spike", latest, keyword
            if latest > avg:
                return "Rising", latest, keyword
            if latest > 10:
                return "Active", latest, keyword
            return "Inactive", latest, keyword
        except Exception:
            continue

    return "Unknown", 0, keyword_list[0] if keyword_list else "Unknown"


def get_sv_estimate(keyword_list):
    """
    Placeholder until keywordtool MCP wiring is finalized.
    Returns number + bucket.
    """
    keyword = keyword_list[0] if keyword_list else "Unknown"
    return {
        "keyword": keyword,
        "sv": None,
        "sv_display": "Pending MCP",
        "sv_bucket": "Pending"
    }


def classify_category(headline):
    h = headline.lower()
    for category, rules in CATEGORY_RULES.items():
        if any(rule in h for rule in rules):
            return category
    return "Stocks in News"


def build_story(cluster):
    sources = dedupe_sources(cluster)
    latest_article = pick_latest_published(sources)
    headline = cluster["headline"]

    fresh_sources = [s for s in sources if within_last_24h(s.get("published", ""))]
    source_count = len(fresh_sources)

    keywords = extract_keywords(headline)
    trend_label, trend_score, chosen_keyword = get_trend_signal(keywords)
    sv_data = get_sv_estimate(keywords)

    category = classify_category(headline)

    freshness_score = 20 if latest_article and within_last_24h(latest_article.get("published", "")) else 0
    source_score = source_count * 20

    trend_points_map = {
        "Spike": 40,
        "Rising": 25,
        "Active": 10,
        "Inactive": 0,
        "Unknown": 0
    }
    trend_points = trend_points_map.get(trend_label, 0)

    sv_points_map = {
        "Strong": 40,
        "Moderate": 20,
        "Low": 5,
        "Pending": 0
    }
    sv_points = sv_points_map.get(sv_data["sv_bucket"], 0)

    total_score = freshness_score + source_score + trend_points + sv_points

    return {
        "headline": headline,
        "category": category,
        "sources": fresh_sources if fresh_sources else sources,
        "source_count": source_count,
        "trend": trend_label,
        "trend_score": trend_score,
        "keyword": chosen_keyword,
        "sv": sv_data["sv"],
        "sv_display": sv_data["sv_display"],
        "sv_bucket": sv_data["sv_bucket"],
        "publish_time": latest_article.get("published", "") if latest_article else "",
        "score": total_score,
        "status_flag": "⚠️ 1 source confirmed" if source_count == 1 else ""
    }


def filter_clusters(clusters):
    filtered = []

    for cluster in clusters:
        fresh_articles = [a for a in cluster["articles"] if within_last_24h(a.get("published", ""))]
        if fresh_articles:
            filtered.append({
                "headline": cluster["headline"],
                "articles": fresh_articles
            })

    return filtered


def run_engine():
    articles = fetch_news()
    clusters = cluster_news(articles)
    clusters = filter_clusters(clusters)

    stories = [build_story(cluster) for cluster in clusters]

    stories.sort(key=lambda x: x["score"], reverse=True)

    top = []
    backup = []

    for story in stories:
        if story["source_count"] >= 2 and len(top) < 5:
            top.append(story)
        elif len(backup) < 10:
            backup.append(story)

    remaining = [s for s in stories if s not in top and s not in backup]
    for story in remaining:
        if len(backup) < 10:
            backup.append(story)

    return top, backup
