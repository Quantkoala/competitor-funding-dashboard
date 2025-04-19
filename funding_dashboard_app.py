import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

st.set_page_config(layout="wide")
st.title("🧠 Competitor Funding Intelligence Dashboard")

@st.cache_data
def fetch_csv_from_url(secret_key, parse_tags=True):
    try:
        url = st.secrets[secret_key]
        response = requests.get(url)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            if parse_tags:
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

news_df = fetch_csv_from_url("news_feed_url", parse_tags=True)

if page == "KPI Snapshot":
    data = fetch_csv_from_url("funding_data_url", parse_tags=False)
    if not data.empty:
        st.subheader("📊 KPI Snapshot")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.bar(data, x="Company", y="Funding ($M)", color="Company"), use_container_width=True)
            st.plotly_chart(px.bar(data, x="Company", y="Patents Filed", color="Company"), use_container_width=True)
        with col2:
            st.plotly_chart(px.bar(data, x="Company", y="Active Products", color="Company"), use_container_width=True)
            st.plotly_chart(px.bar(data, x="Company", y="Clinical Trials", color="Company"), use_container_width=True)
        st.dataframe(data)
    else:
        st.warning("No KPI data available.")

elif page == "Funding History Timeline":
    history = fetch_csv_from_url("funding_history_url", parse_tags=False)
    if not history.empty and 'Date' in history.columns:
        history['Date'] = pd.to_datetime(history['Date'], errors='coerce')
        valid = history.dropna(subset=['Date'])
        if not valid.empty:
            valid['End'] = valid['Date'] + pd.Timedelta(days=1)
            hover_cols = [col for col in valid.columns if col not in ['Date', 'End']]
            fig = px.timeline(
                valid,
                x_start='Date',
                x_end='End',
                y='Company',
                color='Round' if 'Round' in valid.columns else None,
                hover_data=hover_cols
            )
            fig.update_layout(
                xaxis=dict(
                    tickformat="%b\n%Y",
                    tickangle=45,
                    dtick="M1",
                    title="Date (Monthly)"
                )
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No valid 'Date' entries found.")
    else:
        st.warning("Funding history data not available or missing 'Date' column.")

elif page == "Competitor News Feed":
    if not news_df.empty:
        st.subheader("📰 Competitor News Feed")
        tag_filter = st.selectbox("Filter by tag", ["All"] + sorted(news_df['tag'].dropna().unique().tolist()))
        if tag_filter != "All":
            news_df = news_df[news_df['tag'] == tag_filter]
        news_df = news_df.sort_values(by="date", ascending=False)
        news_df['link'] = news_df['link'].apply(lambda x: f"[Open]({x})")
        st.markdown(news_df[['date', 'competitor', 'title', 'tag', 'link']].to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.warning("No news data available.")

elif page == "Scatter Plots by Competitor":
    if not news_df.empty:
        st.subheader("📌 Competitor News Tag Clustering (Scatter View)")
        competitors = sorted(news_df['competitor'].dropna().unique())
        selected = st.multiselect("Select Competitor(s)", competitors, default=competitors)
        for comp in selected:
            sub = news_df[news_df['competitor'] == comp]
            if not sub.empty:
                fig = px.scatter(sub, x="date", y="tag", color="tag",
                                 hover_data=["title", "link"], title=f"News Tag Clustering for {comp}")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data for scatter plot.")

elif page == "News Tag Summary":
    if not news_df.empty:
        summary = news_df['tag'].value_counts().reset_index()
        summary.columns = ['Tag', 'Count']
        fig = px.bar(summary, x='Tag', y='Count', color='Tag')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No news data available.")

elif page == "Competitor Activity Timeline":
    if not news_df.empty:
        news_df['month'] = news_df['date'].dt.to_period("M").astype(str)
        pivot = news_df.groupby(['month', 'competitor']).size().reset_index(name='Announcements')
        competitors = sorted(news_df['competitor'].dropna().unique())
        selected = st.multiselect("Select Competitors", competitors, default=competitors)
        filtered = pivot[pivot['competitor'].isin(selected)]
        fig = px.line(filtered, x='month', y='Announcements', color='competitor')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available.")

elif page == "Competitor by Announcement Type":
    if not news_df.empty:
        competitor_order = news_df['competitor'].value_counts().index.tolist()
        summary = news_df.groupby(['competitor', 'tag']).size().reset_index(name='Count')
        fig = px.bar(summary, x="competitor", y="Count", color="tag",
                     category_orders={"competitor": competitor_order},
                     title="Announcement Types by Competitor")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available.")
