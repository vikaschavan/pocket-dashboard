import streamlit as st
import pandas as pd
import os
import gdown

st.set_page_config(page_title="Pocket Summary Dashboard", layout="wide")
st.title("🔍 Pocket Summary Explorer")

# 📥 Download CSV from Google Drive using gdown
FILE_ID = "1-WuObYzPCvFMRc8E1fVg3XaGMZ1aQChp"
CSV_FILE = "Pocket_Summaries.csv"

# Download only once
if not os.path.exists(CSV_FILE):
    try:
        gdown.download(f"https://drive.google.com/uc?id={FILE_ID}", output=CSV_FILE, quiet=False)
    except Exception as e:
        st.error(f"❌ Failed to download CSV from Google Drive: {e}")

# 🔄 Load and filter CSV
try:
    df = pd.read_csv(CSV_FILE)

    df["tags"] = df["tags"].fillna("")
    df["tags_list"] = df["tags"].apply(lambda x: [tag.strip() for tag in x.split(",") if tag.strip()])
    all_tags = sorted(set(tag for tags in df["tags_list"] for tag in tags))

    df["saved_at"] = pd.to_datetime(df["saved_at"])
    min_date = df["saved_at"].min().date()
    max_date = df["saved_at"].max().date()

    with st.sidebar:
        st.header("📌 Filter by Tags")
        selected_tags = st.multiselect("Select tags", all_tags)

        st.markdown("---")
        st.header("🔍 Search")
        keyword = st.text_input("Search title or summary")

        st.markdown("---")
        st.header("📅 Filter by Date")
        date_range = st.date_input("Select date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    filtered_df = df.copy()

    if selected_tags:
        filtered_df = filtered_df[filtered_df["tags_list"].apply(lambda tags: any(tag in tags for tag in selected_tags))]

    if keyword:
        keyword = keyword.lower()
        filtered_df = filtered_df[
            filtered_df["title"].str.lower().str.contains(keyword) |
            filtered_df["summary"].str.lower().str.contains(keyword)
        ]

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df["saved_at"].dt.date >= start_date) &
            (filtered_df["saved_at"].dt.date <= end_date)
        ]

    # 🔃 Sort by most recent first
    filtered_df = filtered_df.sort_values(by="saved_at", ascending=False)

    # 🔗 Make URL clickable
    filtered_df["🔗 URL"] = filtered_df["url"].apply(lambda x: f'<a href="{x}" target="_blank">Link</a>')

    display_df = filtered_df[[
        "title", "🔗 URL", "saved_at", "short_description", "tags", "summary"
    ]].rename(columns={
        "title": "📖 Title",
        "saved_at": "🕒 Saved At",
        "short_description": "🧠 Short",
        "tags": "🏷️ Tags",
        "summary": "📝 Summary"
    })

    # 🪄 Word wrap styling
    st.markdown("""
        <style>
            table {
                table-layout: fixed;
                width: 100%;
                word-wrap: break-word;
                border-collapse: collapse;
            }
            th, td {
                text-align: left;
                vertical-align: top;
                padding: 8px;
                white-space: pre-wrap;
            }
            th {
                background-color: #444;
                color: white;
            }
            td a {
                color: #1f77b4;
                text-decoration: none;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"### 📄 Showing {len(display_df)} filtered articles")
    st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

except FileNotFoundError:
    st.error("❌ CSV not found. Make sure it's shared publicly and FILE_ID is correct.")
