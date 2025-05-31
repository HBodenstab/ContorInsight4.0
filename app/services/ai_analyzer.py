import os
from dotenv import load_dotenv
from openai import OpenAI, APIError

# Load environment variables from .env
load_dotenv()

# The OpenAI client will automatically use the OPENAI_API_KEY from the environment
client = OpenAI()

def analyze_text_with_openai(text_content: str) -> dict:
    """
    Analyzes the given text using OpenAI's chat completion API (v1+ syntax).
    Returns a dictionary with a summary and a list of keywords.
    """
    prompt = (
        "You are an expert document analyst. "
        "Given the following text, do two things:\n"
        "1. Generate a concise summary of the text.\n"
        "2. Extract a list of the 5-7 most important keywords or key phrases from the text.\n"
        "Return your response as a JSON object with two fields: 'summary' (string) and 'keywords' (list of strings).\n"
        f"\nText to analyze:\n{text_content}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.5,
        )
        reply = response.choices[0].message.content
        import json
        try:
            result = json.loads(reply)
            summary = result.get("summary", "")
            keywords = result.get("keywords", [])
        except Exception:
            # Fallback: try to extract summary and keywords from plain text
            summary = ""
            keywords = []
            lines = reply.splitlines()
            for line in lines:
                if line.lower().startswith("summary"):
                    summary = line.split(":", 1)[-1].strip()
                elif line.lower().startswith("keywords"):
                    kw_str = line.split(":", 1)[-1].strip()
                    keywords = [k.strip() for k in kw_str.split(",") if k.strip()]
        return {
            "summary": summary,
            "keywords": keywords
        }
    except APIError as e:
        return {
            "summary": "",
            "keywords": [],
            "error": f"OpenAI API error: {e}"
        }
    except Exception as e:
        return {
            "summary": "",
            "keywords": [],
            "error": str(e)
        }

# Note: For very long texts that may exceed OpenAI's token limits, consider splitting the text into smaller chunks,
# summarizing each chunk, and then summarizing the summaries. This can be implemented as a future improvement. 