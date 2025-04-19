import requests
from bs4 import BeautifulSoup
from newspaper import Article
import fitz
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
from utils.prompts import get_event_metadata_prompt
from utils.llm_helpers import clean_llm_json_response
from utils.supabase_helpers import get_supabase_client

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_text_from_pdf(url):
    response = requests.get(url)
    doc = fitz.open(stream=response.content, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)[:5000]

def fetch_known_domains():
    client = get_supabase_client("submitter")
    res = client.table("knowledge_drops").select("domain").execute()
    return sorted(set(r["domain"] for r in res.data if "domain" in r and r["domain"]))

def process_link(url):
    content = ""

    try:
        if url.endswith(".pdf"):
            content = extract_text_from_pdf(url)
        else:
            article = Article(url)
            article.download()
            article.parse()
            content = article.text

            if not content:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                content = "\n".join(t.get_text() for t in soup.find_all(["p", "h1", "li"]))[:5000]

    except Exception:
        raise ValueError("Failed to extract content from link")

    if len(content.strip()) < 100:
        print("⚠️ Extracted content too short:\n", content[:300])
        return {
            "title": "Unprocessable Content",
            "summary": "The provided link could not be meaningfully summarized.",
            "domain": "Other"
        }

    domains = fetch_known_domains()
    prompt = get_event_metadata_prompt(content, known_domains=domains)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    drop = clean_llm_json_response(response.text)

    return drop
