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

tab1, tab2 = st.tabs(["📊 KPI Snapshot", "📈 Funding History Timeline"])

# --- Tab 1 ---
with tab1:
    df = fetch_csv_from_url("funding_data_url")
    if not df.empty:
        st.subheader("📊 Funding & KPI Overview")
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

# --- Tab 2 ---
with tab2:
    history = fetch_csv_from_url("funding_history_url")
    if not history.empty:
        st.subheader("📈 Funding Timeline (debug)")
        st.dataframe(history)  # Debug preview

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

st.caption("This dashboard tracks competitor funding activity and strategic metrics to support market intelligence.")
