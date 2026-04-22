import streamlit as st
from engine import run_engine
from ipo import get_ipo_data

st.set_page_config(page_title="Market Dashboard", page_icon="📈", layout="wide")
st.title("📈 Market News Dashboard")

if st.button("🔄 Refresh"):
    st.rerun()

st.divider()

top, backup = run_engine()

st.subheader("🔥 Top 5 Stories")

if top:
    for story in top:
        st.markdown(f"### {story['headline']}")
        st.caption(
            f"Category: {story['category']} | Trend: {story['trend']} | SV: {story['sv_display']} ({story['sv_bucket']})"
        )
        if story["publish_time"]:
            st.caption(f"Publish Time: {story['publish_time']}")
        if story["status_flag"]:
            st.warning(story["status_flag"])

        for src in story["sources"]:
            st.markdown(f"- [{src['source']}]({src['link']})")

        st.divider()
else:
    st.info("No top stories available.")

st.subheader("📦 Backup Stories")

if backup:
    for story in backup:
        st.markdown(f"### {story['headline']}")
        st.caption(
            f"Category: {story['category']} | Trend: {story['trend']} | SV: {story['sv_display']} ({story['sv_bucket']})"
        )
        if story["publish_time"]:
            st.caption(f"Publish Time: {story['publish_time']}")
        if story["status_flag"]:
            st.warning(story["status_flag"])

        for src in story["sources"]:
            st.markdown(f"- [{src['source']}]({src['link']})")

        st.divider()
else:
    st.info("No backup stories available.")

st.subheader("🗓 IPO Calendar")

ipo_df = get_ipo_data()
if not ipo_df.empty:
    st.dataframe(ipo_df, use_container_width=True, hide_index=True)
else:
    st.info("No IPO data available.")
