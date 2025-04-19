import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

st.set_page_config(layout="wide")
st.title("🧠 Competitor Funding Intelligence Dashboard")

# --- Functions to fetch data from Google Sheets CSV links ---
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

# --- Tabs ---
tab1, tab2 = st.tabs(["📊 KPI Snapshot", "📈 Funding History Timeline"])

# --- Tab 1: Summary KPIs ---
with tab1:
    df = fetch_csv_from_url("funding_data_url")
    if not df.empty:
        st.subheader("📊 Funding & KPI Overview")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Funding Raised")
            fig1 = px.bar(df, x='Company', y='Funding ($M)', color='Company')
            st.plotly_chart(fig1, use_container_width=True)

            st.markdown("### Patents Filed")
            fig2 = px.bar(df, x='Company', y='Patents Filed', color='Company')
            st.plotly_chart(fig2, use_container_width=True)

        with col2:
            st.markdown("### Active Products")
            fig3 = px.bar(df, x='Company', y='Active Products', color='Company')
            st.plotly_chart(fig3, use_container_width=True)

            st.markdown("### Clinical Trials")
            fig4 = px.bar(df, x='Company', y='Clinical Trials', color='Company')
            st.plotly_chart(fig4, use_container_width=True)

        st.markdown("### Notes")
        st.dataframe(df[['Company', 'Funding Rounds', 'Investors', 'Last Round Date', 'Notes']])
    else:
        st.warning("No KPI data available. Check your 'funding_data_url' secret.")

# --- Tab 2: Funding History Timeline ---
with tab2:
    history = fetch_csv_from_url("funding_history_url")
    if not history.empty:
        st.subheader("📈 Funding Timeline")
        history['Date'] = pd.to_datetime(history['Date'])
        fig = px.timeline(
            history,
            x_start='Date',
            x_end='Date',
            y='Company',
            color='Round',
            hover_data=['Amount ($M)', 'Investors', 'Notes']
        )
        fig.update_yaxes(autorange='reversed')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No funding history data available. Check your 'funding_history_url' secret.")

st.caption("This dashboard tracks competitor funding activity and strategic metrics to support market intelligence.")
