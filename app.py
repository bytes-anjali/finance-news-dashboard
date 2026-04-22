import streamlit as st
from engine import run_engine
from ipo import get_ipo_data

st.title("📈 Market Dashboard")

st.subheader("🔥 Top 5 Stories")

top, backup = run_engine()

for story in top:
    st.markdown(f"### {story['headline']}")
    for src in story["sources"]:
        st.markdown(f"- [{src['source']}]({src['link']})")
    st.caption(f"Sources: {story['source_count']}")
    st.divider()


st.subheader("📦 Backup Stories")

for story in backup:
    st.markdown(f"### {story['headline']}")
    for src in story["sources"]:
        st.markdown(f"- [{src['source']}]({src['link']})")
    st.caption(f"Sources: {story['source_count']}")
    st.divider()


st.subheader("🗓 IPO Calendar")

ipo_df = get_ipo_data()
st.dataframe(ipo_df, use_container_width=True)
