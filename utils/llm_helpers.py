import json
import re

def clean_llm_json_response(response_text):
    if response_text.startswith("```json") or response_text.startswith("```"):
        response_text = re.sub(r"```(?:json)?", "", response_text).replace("```", "").strip()
    return json.loads(response_text)