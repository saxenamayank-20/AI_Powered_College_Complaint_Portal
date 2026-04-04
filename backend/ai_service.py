import json
import os
from groq import Groq

# ---- ADD YOUR FREE GROQ API KEY HERE ----
# Get it free from: https://console.groq.com
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "Api key HERE")
# -----------------------------------------


def analyze_complaint(complaint_text: str) -> dict:ss
    """
    Send complaint to Groq AI.
    Returns category, priority, and summary.
    """
    prompt = f"""You are an assistant for a college complaint management system.
Analyze the following student complaint and respond ONLY in valid JSON format.
No extra text, no markdown, just raw JSON.

Complaint: "{complaint_text}"

Return exactly this JSON structure:
{{
  "category": "one of: Hostel, Canteen, Infrastructure, Academic, Transport, Other",
  "priority": "one of: Low, Medium, High",
  "summary": "one short sentence summary of the complaint (max 15 words)"
}}

    Priority rules:
- High: safety issues, no water/electricity, urgent health concerns
- Medium: food quality, cleanliness, minor facility issues
- Low: suggestions, minor inconveniences
"""

    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)
        return result
    except Exception as e:
        print(f"Groq error: {e}")
        # Fallback if AI fails
        return {
            "category": "Other",
            "priority": "Medium",
            "summary": complaint_text[:80]
        }
