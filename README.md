# Competitor Funding Intelligence Dashboard

This Streamlit app visualizes real-time funding data and funding histories of biotech competitors.

## 📁 Structure

- `funding_dashboard_app.py` — main dashboard file
- `.streamlit/secrets.toml.example` — secret config for Google Sheets CSV URLs

## 🚀 How to Use

1. Upload the Excel sheets to Google Sheets:
   - Sheet 1: `Funding_Snapshot`
   - Sheet 2: `Funding_History`

2. Publish each sheet to the web in CSV format:
   - File → Share → Publish to web → CSV

3. Replace the placeholder URLs in `.streamlit/secrets.toml.example` with your actual links.

4. Move the filled-in file to:
   ```
   ~/.streamlit/secrets.toml
   ```

5. Run the app:
   ```
   streamlit run funding_dashboard_app.py
   ```

This dashboard provides a dual-view of high-level funding KPIs and historical round-by-round timelines.
