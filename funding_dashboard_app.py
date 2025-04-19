import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

st.set_page_config(layout="wide")
st.title("🧠 Competitor Funding Intelligence Dashboard")

@st.cache_data
def fetch_csv_from_url(secret_key):
    try:
        url = st.secrets[secret_key]
        response = requests.get(url)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            df['title'] = df['title'].fillna("")
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['tag'] = df.apply(tag_news_item, axis=1)
            df = df.dropna(subset=['date'])
            return df
        else:
            st.error(f"Failed to fetch data from: {url}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching '{secret_key}': {e}")
        return pd.DataFrame()

def tag_news_item(row):
    title = row['title'].lower()
    tag_keywords = {
        'Funding': ['series a', 'series b', 'series c', 'funding', 'investment', 'raises', 'venture capital', 'financing'],
        'Product Launch': ['launch', 'introduces', 'unveils', 'releases', 'new product', 'commercial availability', 'rolls out'],
        'M&A': ['merger', 'acquisition', 'acquires', 'buys', 'takeover', 'merges with'],
        'Partnership': ['partnership', 'collaboration', 'teams up', 'joins forces', 'strategic alliance'],
        'IPO / Capital Market': ['sec filing', 'ipo', 'public offering', 'spac', 'files s-1'],
        'Clinical Development': ['clinical trial', 'phase i', 'phase ii', 'phase iii', 'first-in-human', 'pivotal trial'],
        'Patent': ['patent', 'intellectual property', 'ip protection', 'trademark'],
        'Recognition': ['award', 'recognition', 'grants', 'honor', 'winner', 'recipient'],
        'Regulatory': ['fda approval', 'ce mark', '510(k)', 'regulatory clearance', 'notified body'],
        'Corporate Update': ['expands', 'rebrands', 'opens office', 'hiring', 'growth update', 'board member'],
    }
    for tag, keywords in tag_keywords.items():
        if any(kw in title for kw in keywords):
            return tag
    return 'Other'

# Sidebar Navigation
page = st.sidebar.selectbox("📂 Select a Page", [
    "KPI Snapshot",
    "Funding History Timeline",
    "Competitor News Feed",
    "Scatter Plots by Competitor",
    "News Tag Summary",
    "Competitor Activity Timeline",
    "Competitor by Announcement Type"
])

if page == "Competitor by Announcement Type":
    st.header("📚 Competitor by Announcement Type")
    df = fetch_csv_from_url("news_feed_url")
    if not df.empty:
        competitor_order = df['competitor'].value_counts().index.tolist()
        summary = df.groupby(['competitor', 'tag']).size().reset_index(name='Count')
        fig = px.bar(
            summary,
            x="competitor",
            y="Count",
            color="tag",
            title="Announcement Types by Competitor",
            category_orders={"competitor": competitor_order},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available.")
