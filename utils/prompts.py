def get_event_metadata_prompt(content, known_domains):
    domain_list = ", ".join(known_domains)
    return f"""
You're an assistant that processes online content into structured knowledge drops.

If the content is clearly junk, return:
{{"title": "Unprocessable Content", "summary": "The link could not be summarized.", "domain": "Other"}}

Otherwise:
Return a JSON object with:
- title: A clear, informative title for the content
- summary: A helpful 2–4 sentence summary
- domain: One of these categories: {domain_list} (only create new if truly necessary)

Content:
'''{content}'''
"""

def get_reclassification_prompt(row):
    return f"""
You're reclassifying this content into new domains.
Return: {{"domain": "...", "title": "...", "summary": "..."}}

Title: {row['title']}
Summary: {row['summary']}
"""
