import requests
import pandas as pd


def get_ipo_data():
    ipos = []
    statuses = ["open", "upcoming", "announced"]

    try:
        for status in statuses:
            url = f"https://api.ipoalerts.in/ipos?status={status}"
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            data = resp.json()

            for item in data:
                ipos.append({
                    "Company": item.get("company_name", ""),
                    "Open": item.get("open_date", ""),
                    "Close": item.get("close_date", ""),
                    "Price Band": item.get("price_band", ""),
                    "Status": status.capitalize(),
                })

        return pd.DataFrame(ipos)

    except:
        return pd.DataFrame([{"Company": "IPO data unavailable"}])
