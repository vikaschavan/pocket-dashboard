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
        filtered_df = filtered_df[(filtered_df["saved_at"].dt.date >= start_date) & (filtered_df["saved_at"].dt.date <= end_date)]

    # Format URL as hyperlink text
    filtered_df["🔗 URL"] = filtered_df["url"].apply(lambda x: f"[Link]({x})")

    # Reorder columns
    display_df = filtered_df[[
        "title",
        "🔗 URL",
        "saved_at",
        "short_description",
        "tags",
        "summary"
    ]].rename(columns={
        "title": "📖 Title",
        "saved_at": "🕒 Saved At",
        "short_description": "🧠 Short Description",
        "tags": "🏷️ Tags",
        "summary": "📝 Summary"
    })

    # Apply custom styling to improve readability
    st.markdown("""
        <style>
        .element-container:has(.dataframe) {
            overflow-x: auto;
        }
        .dataframe td {
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            vertical-align: top;
        }
        .dataframe th {
            text-align: left;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"### 📄 Showing {len(display_df)} filtered articles")
    st.dataframe(display_df, use_container_width=True)

except FileNotFoundError:
    st.error("❌ CSV not found. Make sure it's shared publicly and FILE_ID is correct.")
