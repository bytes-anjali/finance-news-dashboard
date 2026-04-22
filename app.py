import streamlit as st
from engine import run_engine
from ipo import get_ipo_data

st.set_page_config(page_title="Market Dashboard", page_icon="📈", layout="wide")

st.title("📈 Market News Dashboard")

# 🔄 Refresh
if st.button("🔄 Refresh"):
    st.rerun()

st.divider()

# 🔥 TOP 5
st.subheader("🔥 Top 5 Stories")

top, backup = run_engine()

if top:
    for story in top:
        st.markdown(f"### {story['headline']}")

        for src in story["sources"]:
            st.markdown(f"- [{src['source']}]({src['link']})")

        st.caption(f"Sources: {story['source_count']}")
        st.divider()
else:
    st.info("No top stories available.")

# 📦 BACKUP
st.subheader("📦 Backup Stories")

if backup:
    for story in backup:
        st.markdown(f"### {story['headline']}")

        for src in story["sources"]:
            st.markdown(f"- [{src['source']}]({src['link']})")

        st.caption(f"Sources: {story['source_count']}")
        st.divider()
else:
    st.info("No backup stories available.")

# 🗓 IPO
st.subheader("🗓 IPO Calendar")

ipo_df = get_ipo_data()

if not ipo_df.empty:
    st.dataframe(ipo_df, use_container_width=True, hide_index=True)
else:
    st.info("No IPO data available.")
