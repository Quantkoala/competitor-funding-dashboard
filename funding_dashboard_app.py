import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

st.set_page_config(layout="wide")
st.title("🧠 競爭對手情報儀表板")

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
            st.error(f"讀取資料失敗：{url}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"錯誤：'{secret_key}' 讀取失敗: {e}")
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
    return '其他'

page = st.sidebar.selectbox("📂 選擇頁面", [
    "KPI 快照",
    "融資歷程圖",
    "新聞資料流",
    "依公司分類散點圖",
    "新聞類型統計",
    "活動時間軸",
    "公司與公告類型分析"
])

news_df = fetch_csv_from_url("news_feed_url", parse_tags=True)

if page == "KPI 快照":
    data = fetch_csv_from_url("funding_data_url", parse_tags=False)
    if not data.empty:
        st.subheader("📊 KPI 快照")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.bar(data, x="Company", y="Funding ($M)", color="Company"), use_container_width=True)
            st.plotly_chart(px.bar(data, x="Company", y="Patents Filed", color="Company"), use_container_width=True)
        with col2:
            st.plotly_chart(px.bar(data, x="Company", y="Active Products", color="Company"), use_container_width=True)
            st.plotly_chart(px.bar(data, x="Company", y="Clinical Trials", color="Company"), use_container_width=True)
        st.dataframe(data)
    else:
        st.warning("無法取得 KPI 資料。")

elif page == "融資歷程圖":
    history = fetch_csv_from_url("funding_history_url", parse_tags=False)
    if not history.empty and 'Date' in history.columns:
        history['Date'] = pd.to_datetime(history['Date'], errors='coerce')
        valid = history.dropna(subset=['Date'])
        if not valid.empty:
            valid['End'] = valid['Date'] + pd.Timedelta(days=1)
            hover_cols = [col for col in valid.columns if col not in ['Date', 'End']]
            fig = px.timeline(valid, x_start='Date', x_end='End', y='Company', color='Round' if 'Round' in valid.columns else None, hover_data=hover_cols)
            fig.update_layout(xaxis=dict(tickformat="%b\n%Y", tickangle=45, dtick="M1", title="月份"))
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ 沒有有效的日期格式 (YYYY-MM-DD)。")
    else:
        st.warning("缺少 'Date' 欄位或資料無法讀取。")

elif page == "新聞資料流":
    if not news_df.empty:
        st.subheader("📰 競爭對手新聞")
        tag_filter = st.selectbox("依標籤篩選", ["全部"] + sorted(news_df['tag'].dropna().unique().tolist()))
        if tag_filter != "全部":
            news_df = news_df[news_df['tag'] == tag_filter]
        news_df = news_df.sort_values(by="date", ascending=False)
        news_df['link'] = news_df['link'].apply(lambda x: f"[開啟]({x})")
        st.markdown(news_df[['date', 'competitor', 'title', 'tag', 'link']].to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.warning("無新聞資料。")

elif page == "依公司分類散點圖":
    if not news_df.empty:
        st.subheader("📌 散點圖：新聞類型分佈")
        competitors = sorted(news_df['competitor'].dropna().unique())
        selected = st.multiselect("選擇公司", competitors, default=competitors)
        for comp in selected:
            sub = news_df[news_df['competitor'] == comp]
            if not sub.empty:
                fig = px.scatter(sub, x="date", y="tag", color="tag",
                                 hover_data=["title", "link"], title=f"{comp} 的新聞類型散點圖")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("無資料可供顯示。")

elif page == "新聞類型統計":
    if not news_df.empty:
        summary = news_df['tag'].value_counts().reset_index()
        summary.columns = ['標籤', '數量']
        fig = px.bar(summary, x='標籤', y='數量', color='標籤')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("無新聞資料可用。")

elif page == "活動時間軸":
    if not news_df.empty:
        news_df['month'] = news_df['date'].dt.to_period("M").astype(str)
        pivot = news_df.groupby(['month', 'competitor']).size().reset_index(name='發佈數')
        competitors = sorted(news_df['competitor'].dropna().unique())
        selected = st.multiselect("選擇公司", competitors, default=competitors)
        filtered = pivot[pivot['competitor'].isin(selected)]
        fig = px.line(filtered, x='month', y='發佈數', color='competitor')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("目前無活動資料。")

elif page == "公司與公告類型分析":
    if not news_df.empty:
        competitor_order = news_df['competitor'].value_counts().index.tolist()
        summary = news_df.groupby(['competitor', 'tag']).size().reset_index(name='數量')
        fig = px.bar(summary, x="competitor", y="數量", color="tag",
                     category_orders={"competitor": competitor_order},
                     title="各公司依公告類型之統計")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("尚無可用資料。")
