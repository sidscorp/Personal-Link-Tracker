import json
import os
import google.generativeai as genai
from utils.supabase_helpers import get_supabase_client
from utils.prompts import get_reclassification_prompt

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
supabase = get_supabase_client("service_role")

def reclassify_existing_records(dry_run=True, update_fields=False):
    rows = supabase.table("knowledge_drops").select("*").execute().data
    model = genai.GenerativeModel("gemini-1.5-flash")

    for row in rows:
        prompt = get_reclassification_prompt(row)
        try:
            response = model.generate_content(prompt).text.strip()
            classification = json.loads(response.replace("```json", "").replace("```", "").strip())

            new_domain = classification["domain"]
            new_title = classification.get("title", row["title"])
            new_summary = classification.get("summary", row["summary"])

            if dry_run:
                print(f"\nRecord ID: {row['id']}")
                print(f"  OLD domain: {row['domain']} --> NEW: {new_domain}")
            elif update_fields:
                update = {"domain": new_domain, "title": new_title, "summary": new_summary}
                supabase.table("knowledge_drops").update(update).eq("id", row["id"]).execute()

        except Exception as e:
            print(f"Error processing {row['id']}: {e}")

def update_field(id, field, new_value):
    supabase.table("knowledge_drops").update({field: new_value}).eq("id", id).execute()

def delete_entries(ids):
    for entry_id in ids:
        supabase.table("knowledge_drops").delete().eq("id", entry_id).execute()
