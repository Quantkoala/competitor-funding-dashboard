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
            df['tag'] = df.apply(tag_news_item, axis=1)
            return df
        else:
            st.error(f"Failed to fetch data from: {url}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching '{secret_key}': {e}")
        return pd.DataFrame()

# Enhanced tagging logic for competitor news
def tag_news_item(row):
    title = row['title'].lower()
    if any(kw in title for kw in ['series a', 'series b', 'series c', 'funding', 'investment', 'raises']):
        return 'Funding'
    elif any(kw in title for kw in ['launch', 'introduces', 'unveils', 'releases', 'new product']):
        return 'Product Launch'
    elif any(kw in title for kw in ['merger', 'acquisition', 'acquires', 'buys']):
        return 'M&A'
    elif any(kw in title for kw in ['partnership', 'collaboration', 'teams up', 'joins']):
        return 'Partnership'
    elif any(kw in title for kw in ['sec filing', 'ipo', 'public offering', 'spac']):
        return 'IPO / Capital Market'
    elif any(kw in title for kw in ['clinical trial', 'phase i', 'phase ii', 'phase iii']):
        return 'Clinical Development'
    elif any(kw in title for kw in ['patent', 'intellectual property']):
        return 'Patent'
    elif any(kw in title for kw in ['award', 'recognition', 'grants']):
        return 'Recognition'
    else:
        return 'General'

# Sidebar Navigation
page = st.sidebar.selectbox("📂 Select a Page", [
    "KPI Snapshot",
    "Funding History Timeline",
    "Competitor News Feed"
])

# --- Competitor News Feed Page ---
if page == "Competitor News Feed":
    st.header("📰 Competitor News Feed (Enhanced Tagging)")
    news = fetch_csv_from_url("news_feed_url")
    if not news.empty:
        tag_filter = st.selectbox("Filter by tag", ["All"] + sorted(news['tag'].dropna().unique().tolist()))
        if tag_filter != "All":
            news = news[news['tag'] == tag_filter]
        news = news.sort_values(by="date", ascending=False)
        news['link'] = news['link'].apply(lambda x: f"[Open]({x})")
        st.markdown(news[['date', 'competitor', 'title', 'tag', 'link']].to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.warning("No news data available. Check your 'news_feed_url' secret.")

st.caption("This dashboard provides strategic insights on competitor funding and media activity.")
