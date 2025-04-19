import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from processors.content_processor import process_link
from utils.supabase_helpers import insert_knowledge_drop
from html import escape

st.set_page_config(page_title="Add Knowledge Drop", layout="centered")

st.title("📅 Submit a Link to Knowledge Drops")

url = st.text_input("Paste a link to submit")
user = st.text_input("Your name or handle (optional)", value="sidd")

if st.button("Add to Drops") and url:
    with st.spinner("Checking for duplicates..."):
        try:
            user = user.strip()
            check_result = insert_knowledge_drop({}, url, user=user, check_only=True)

            if check_result["status"] == "exists":
                st.info(f"🔁 Link already exists in the database (ID: {check_result['id']})")
            else:
                with st.spinner("Processing with LLM..."):
                    drop_data = process_link(url)

                    drop_data["title"] = drop_data["title"].replace(",", " ").replace("'", "").strip()
                    drop_data["summary"] = drop_data["summary"].replace(",", " ").replace("'", "").strip()

                    result = insert_knowledge_drop(drop_data, url, user=user)

                    if result["status"] == "inserted":
                        st.success("✅ Successfully added to Knowledge Drops!")
                        st.markdown(f"**Title:** {escape(drop_data['title'])}")
                        st.markdown(f"**Summary:** {escape(drop_data['summary'])}")
                        st.markdown(f"**Domain:** `{drop_data['domain']}`")
                    else:
                        st.warning("⚠️ Something unexpected happened. Try again or check logs.")

        except Exception as e:
            st.error(f"❌ Not added: {str(e)}")
