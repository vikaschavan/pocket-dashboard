import streamlit as st
import pandas as pd
import os
import subprocess

st.set_page_config(page_title="Pocket Summary Dashboard", layout="wide")
st.title("🔍 Pocket Summary Explorer")

# 📥 Download CSV from Google Drive using gdown
FILE_ID = "WuObYzPCvFMRc8E1fVg3XaGMZ1aQChp"  # Replace with your actual file ID
CSV_FILE = "Pocket_Summaries.csv"

# Download only once
if not os.path.exists(CSV_FILE):
    try:
        subprocess.run(["pip", "install", "gdown"])
        import gdown
        gdown.download(id=FILE_ID, output=CSV_FILE, quiet=False)
    except Exception as e:
        st.error(f"❌ Failed to download CSV from Google Drive: {e}")

# 🔄 Load and filter CSV
try:
    df = pd.read_csv(CSV_FILE)

    df["tags"] = df["tags"].fillna("")
    df["tags_list"] = df["tags"].apply(lambda x: [tag.strip() for tag in x.split(",") if tag.strip()])
    all_tags = sorted(set(tag for tags in df["tags_list"] for tag in tags))

    with st.sidebar:
        st.header("📌 Filter by Tags")
        selected_tags = st.multiselect("Select tags", all_tags)
        st.markdown("---")
        st.header("🔍 Search")
        keyword = st.text_input("Search title or summary")

    filtered_df = df.copy()

    if selected_tags:
        filtered_df = filtered_df[filtered_df["tags_list"].apply(lambda tags: any(tag in tags for tag in selected_tags))]

    if keyword:
        keyword = keyword.lower()
        filtered_df = filtered_df[
            filtered_df["title"].str.lower().str.contains(keyword) |
            filtered_df["summary"].str.lower().str.contains(keyword)
        ]

    st.markdown(f"### 📄 Showing {len(filtered_df)} filtered articles")
    st.dataframe(filtered_df[["title", "saved_at", "short_description", "tags", "summary", "url"]], use_container_width=True)

except FileNotFoundError:
    st.error("❌ CSV not found. Make sure it's shared publicly and FILE_ID is correct.")
