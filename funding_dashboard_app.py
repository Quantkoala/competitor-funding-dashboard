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
            return pd.read_csv(io.StringIO(response.text))
        else:
            st.error(f"Failed to fetch data from: {url}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching '{secret_key}': {e}")
        return pd.DataFrame()

# Sidebar Navigation
page = st.sidebar.selectbox("📂 Select a Page", [
    "KPI Snapshot",
    "Funding History Timeline",
    "Competitor News Feed"
])

# --- KPI Snapshot Page ---
if page == "KPI Snapshot":
    df = fetch_csv_from_url("funding_data_url")
    st.header("📊 KPI Snapshot")
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Funding Raised")
            st.plotly_chart(px.bar(df, x='Company', y='Funding ($M)', color='Company'), use_container_width=True)
            st.markdown("### Patents Filed")
            st.plotly_chart(px.bar(df, x='Company', y='Patents Filed', color='Company'), use_container_width=True)
        with col2:
            st.markdown("### Active Products")
            st.plotly_chart(px.bar(df, x='Company', y='Active Products', color='Company'), use_container_width=True)
            st.markdown("### Clinical Trials")
            st.plotly_chart(px.bar(df, x='Company', y='Clinical Trials', color='Company'), use_container_width=True)
        st.markdown("### Notes")
        st.dataframe(df[['Company', 'Funding Rounds', 'Investors', 'Last Round Date', 'Notes']])
    else:
        st.warning("No KPI data available. Check your 'funding_data_url' secret.")

# --- Funding History Timeline Page ---
elif page == "Funding History Timeline":
    history = fetch_csv_from_url("funding_history_url")
    st.header("📈 Funding History Timeline")
    if not history.empty:
        st.dataframe(history)  # Show raw data for debugging
        try:
            history['Date'] = pd.to_datetime(history['Date'], errors='coerce')
            valid_history = history.dropna(subset=['Date'])

            if valid_history.empty:
                st.warning("⚠️ No valid dates found. Please format the 'Date' column as YYYY-MM-DD in Google Sheets.")
            else:
                fig = px.timeline(
                    valid_history,
                    x_start='Date',
                    x_end='Date',
                    y='Company',
                    color='Round',
                    hover_data=['Amount ($M)', 'Investors', 'Notes']
                )
                fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to render timeline: {e}")
    else:
        st.warning("No funding history data available. Check your 'funding_history_url' secret.")

# --- Competitor News Feed Page ---
elif page == "Competitor News Feed":
    st.header("📰 Competitor News Feed")
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
