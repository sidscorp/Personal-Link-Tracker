
import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUBMITTER_KEY = st.secrets["SUBMITTER_KEY"]

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.supabase_helpers import get_supabase_client
from datetime import datetime
import os

st.set_page_config(page_title="Knowledge Drops Viewer", layout="wide")

DOMAIN_ICONS = {
    "AI": "🤖",
    "Healthcare": "💊",
    "Climate": "🌍",
    "Regulation": "📜",
    "Other": "🧠",
}

st.markdown("""
    <style>
    .drop-card {
        background-color: #1e1e22;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: transform 0.2s ease-in-out;
        margin-bottom: 1rem;
    }
    .drop-card:hover {
        transform: scale(1.01);
        box-shadow: 0 0 16px rgba(0,0,0,0.3);
    }
    a.title-link {
        font-size: 1.2rem;
        font-weight: bold;
        color: #58c6ff;
        text-decoration: none;
    }
    a.title-link:hover {
        text-decoration: underline;
    }
    .domain-tag {
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 999px;
        background-color: #333;
        color: #aafad6;
        margin-right: 6px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("## 📚 Knowledge Drops Viewer")
st.caption("Curated AI & tech content, auto-summarized by Gemini 🔮")

supabase = get_supabase_client("submitter")
res = supabase.table("knowledge_drops").select("*").execute()
all_drops = res.data if res.data else []

domains = sorted(set(d["domain"] for d in all_drops))
col1, col2 = st.columns([3, 1])

with col1:
    selected_domain = st.selectbox("Filter by domain", ["All"] + domains)

with col2:
    sort_order = st.selectbox("Sort by date", ["Newest first", "Oldest first"])

search_term = st.text_input("Search title or summary")

filtered = [
    d for d in all_drops
    if (selected_domain == "All" or d["domain"] == selected_domain)
    and (search_term.lower() in d["title"].lower() or search_term.lower() in d["summary"].lower())
]

reverse = sort_order == "Newest first"
drops = sorted(filtered, key=lambda x: x["created_at"], reverse=reverse)

for drop in drops:
    st.markdown(f"""
    <div class="drop-card">
        <a href="{drop['link']}" class="title-link" target="_blank">{DOMAIN_ICONS.get(drop['domain'], '🧠')} {drop['title']}</a>
        <p style="margin-top: 0.6rem; color: #ddd; font-size: 0.9rem;">{drop['summary']}</p>
        <p style="font-size: 0.8rem; color: #999;">
            <span class="domain-tag">{drop['domain']}</span>
            <code>{drop['user']}</code> • {datetime.fromisoformat(drop['created_at']).strftime('%b %d, %Y')}
        </p>
    </div>
    """, unsafe_allow_html=True)
