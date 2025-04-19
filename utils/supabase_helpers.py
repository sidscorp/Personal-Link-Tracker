import streamlit as st
from supabase import create_client
from datetime import datetime

SUPABASE_URL = st.secrets["SUPABASE_URL"]

ROLE_KEYS = {
    "submitter": st.secrets["SUBMITTER_KEY"],
    "admin": st.secrets["ADMIN_KEY"],
    "service_role": st.secrets["ADMIN_KEY"]
}

def get_supabase_client(role="submitter"):
    key = ROLE_KEYS.get(role)
    if not key:
        raise ValueError(f"Missing key for role {role}")
    return create_client(SUPABASE_URL, key)

def insert_knowledge_drop(data, url, user="anonymous", check_only=False, role="submitter"):
    supabase = get_supabase_client(role)

    existing = supabase.table("knowledge_drops") \
        .select("id") \
        .eq("link", url) \
        .limit(1) \
        .execute()

    if existing.data:
        return {"status": "exists", "id": existing.data[0]["id"]}

    if check_only:
        return {"status": "not_found"}

    payload = {
        "link": url,
        "title": data.get("title", ""),
        "summary": data.get("summary", ""),
        "domain": data.get("domain", "Other"),
        "user": user,
        "created_at": datetime.utcnow().isoformat()
    }

    inserted = supabase.table("knowledge_drops").insert(payload).execute()

    if inserted.data:
        return {"status": "inserted", "id": inserted.data[0]["id"]}
    else:
        return {"status": "error", "error": inserted.error}
