import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

st.set_page_config(layout="wide")

# Language selector
lang = st.sidebar.selectbox("🌐 Language / 語言", ["English", "繁體中文"])

# Localized label dictionaries
labels = {
    "English": {
        "title": "🧠 Competitor Intelligence Dashboard",
        "pages": [
            "KPI Snapshot",
            "Funding History Timeline",
            "Competitor News Feed",
            "Scatter Plots by Competitor",
            "News Tag Summary",
            "Competitor Activity Timeline",
            "Competitor by Announcement Type"
        ],
        "filter_by_tag": "Filter by tag",
        "select_competitors": "Select Competitors",
        "select_company": "Select Company",
        "open": "Open",
        "no_data": "No data available."
    },
    "繁體中文": {
        "title": "🧠 競爭對手情報儀表板",
        "pages": [
            "KPI 快照",
            "融資歷程圖",
            "新聞資料流",
            "依公司分類散點圖",
            "新聞類型統計",
            "活動時間軸",
            "公司與公告類型分析"
        ],
        "filter_by_tag": "依標籤篩選",
        "select_competitors": "選擇公司",
        "select_company": "選擇公司",
        "open": "開啟",
        "no_data": "目前無可用資料。"
    }
}

L = labels[lang]
st.title(L["title"])

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
    return 'Other' if lang == "English" else '其他'

page = st.sidebar.selectbox("📂", L["pages"])
news_df = fetch_csv_from_url("news_feed_url", parse_tags=True)

if page == L["pages"][0]:  # KPI Snapshot
    data = fetch_csv_from_url("funding_data_url", parse_tags=False)
    if not data.empty:
        st.subheader(L["pages"][0])
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.bar(data, x="Company", y="Funding ($M)", color="Company"), use_container_width=True)
            st.plotly_chart(px.bar(data, x="Company", y="Patents Filed", color="Company"), use_container_width=True)
        with col2:
            st.plotly_chart(px.bar(data, x="Company", y="Active Products", color="Company"), use_container_width=True)
            st.plotly_chart(px.bar(data, x="Company", y="Clinical Trials", color="Company"), use_container_width=True)
        st.dataframe(data)
    else:
        st.warning(L["no_data"])

elif page == L["pages"][1]:  # Funding Timeline
    history = fetch_csv_from_url("funding_history_url", parse_tags=False)
    if not history.empty and 'Date' in history.columns:
        history['Date'] = pd.to_datetime(history['Date'], errors='coerce')
        valid = history.dropna(subset=['Date'])
        if not valid.empty:
            valid['End'] = valid['Date'] + pd.Timedelta(days=1)
            fig = px.timeline(valid, x_start='Date', x_end='End', y='Company', color='Round' if 'Round' in valid.columns else None)
            fig.update_layout(xaxis=dict(tickformat="%b\n%Y", tickangle=45, dtick="M1"))
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No valid 'Date' entries.")
    else:
        st.warning(L["no_data"])

elif page == L["pages"][2]:  # News Feed
    if not news_df.empty:
        st.subheader(L["pages"][2])
        tag_filter = st.selectbox(L["filter_by_tag"], ["All"] + sorted(news_df['tag'].dropna().unique().tolist()))
        if tag_filter != "All":
            news_df = news_df[news_df['tag'] == tag_filter]
        news_df = news_df.sort_values(by="date", ascending=False)
        news_df['link'] = news_df['link'].apply(lambda x: f"[{L['open']}]({x})")
        st.markdown(news_df[['date', 'competitor', 'title', 'tag', 'link']].to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.warning(L["no_data"])

elif page == L["pages"][3]:  # Scatter Plots
    if not news_df.empty:
        st.subheader(L["pages"][3])
        competitors = sorted(news_df['competitor'].dropna().unique())
        selected = st.multiselect(L["select_company"], competitors, default=competitors)
        for comp in selected:
            sub = news_df[news_df['competitor'] == comp]
            if not sub.empty:
                fig = px.scatter(sub, x="date", y="tag", color="tag", hover_data=["title", "link"])
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(L["no_data"])

elif page == L["pages"][4]:  # Tag Summary
    if not news_df.empty:
        summary = news_df['tag'].value_counts().reset_index()
        summary.columns = ['Tag', 'Count']
        fig = px.bar(summary, x='Tag', y='Count', color='Tag')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(L["no_data"])

elif page == L["pages"][5]:  # Activity Timeline
    if not news_df.empty:
        news_df['month'] = news_df['date'].dt.to_period("M").astype(str)
        pivot = news_df.groupby(['month', 'competitor']).size().reset_index(name='Announcements')
        selected = st.multiselect(L["select_competitors"], sorted(news_df['competitor'].unique()), default=sorted(news_df['competitor'].unique()))
        filtered = pivot[pivot['competitor'].isin(selected)]
        fig = px.line(filtered, x='month', y='Announcements', color='competitor')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(L["no_data"])

elif page == L["pages"][6]:  # Bar by tag
    if not news_df.empty:
        summary = news_df.groupby(['competitor', 'tag']).size().reset_index(name='Count')
        fig = px.bar(summary, x="competitor", y="Count", color="tag", title=L["pages"][6])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(L["no_data"])

# This code snippet should be inserted into your Streamlit app after loading `news_df`
# and selecting the page. Add this to your bilingual dashboard under a new page.

# --- Material Tracker temporarily disabled ---
# if page == L["pages"][7] if len(L["pages"]) > 7 else "Material Events Tracker":
#     if not news_df.empty:
#         def classify_material_tag(title):
#             title = title.lower()
#             if any(kw in title for kw in ['series a', 'series b', 'series c', 'ipo', 'spac', 'raises', 'funding']):
#                 return "Material: Fundraising" if lang == "English" else "重大：募資"
#             elif any(kw in title for kw in ['fda approval', 'ce mark', '510(k)', 'phase iii', 'pivotal trial']):
#                 return "Material: Clinical/Regulatory" if lang == "English" else "重大：臨床/法規"
#             elif any(kw in title for kw in ['strategic partnership', 'licensing deal', 'collaboration', 'joint venture']):
#                 return "Material: Strategic Alliance" if lang == "English" else "重大：策略聯盟"
#             elif any(kw in title for kw in ['launches new platform', 'commercial launch', 'global launch']):
#                 return "Material: Global Product Launch" if lang == "English" else "重大：產品上市（全球）"
#             elif any(kw in title for kw in ['layoffs', 'lawsuit', 'ceo steps down', 'resignation', 'delisting']):
#                 return "Material: Crisis" if lang == "English" else "重大：危機/法律"
#             elif any(kw in title for kw in ['award', 'grant', 'honored', 'recognition']):
#                 return "Recognition" if lang == "English" else "獲獎/補助"
#             elif any(kw in title for kw in ['appoints', 'hires', 'joins advisory']):
#                 return "Leadership" if lang == "English" else "領導團隊異動"
#             elif any(kw in title for kw in ['rebrands', 'opens office', 'corporate update']):
#                 return "Corporate Update" if lang == "English" else "品牌/企業動態"
#             else:
#                 return "General" if lang == "English" else "一般消息"
# 
#         news_df['material_tag'] = news_df['title'].fillna("").apply(classify_material_tag)
#         material_only = news_df[news_df['material_tag'].str.contains("Material|重大")].copy()
# 
#         st.subheader("🛎️ " + ("Material Events Tracker" if lang == "English" else "重大消息追蹤"))
#         category_filter = st.selectbox(
#             "📌 Select a material category" if lang == "English" else "📌 選擇重大類別",
#             sorted(material_only['material_tag'].dropna().unique().tolist())
#         )
#         filtered = material_only[material_only['material_tag'] == category_filter]
# 
#         filtered = filtered.sort_values(by="date", ascending=False)
#         filtered['link'] = filtered['link'].apply(lambda x: f"[{L['open']}]({x})")
#         st.markdown(filtered[['date', 'competitor', 'material_tag', 'title', 'link']].to_markdown(index=False), unsafe_allow_html=True)
#     else:
#         st.warning(L["no_data"])