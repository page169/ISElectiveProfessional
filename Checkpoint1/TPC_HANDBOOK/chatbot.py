"""
Source-Grounded Chatbot with Gemini
------------------------------------
Fetches one webpage, cleans it, and uses it as the ONLY knowledge source
for a Gemini chatbot. Run this from a VS Code terminal.
"""

import os
import re
import requests
import pymupdf
from io import BytesIO
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------------------------------------------------------------------
# STEP 1: CHOOSE YOUR SOURCE PAGE
# Change this URL to whatever page you want your chatbot to know about.
# ---------------------------------------------------------------------
URL = "https://raw.githubusercontent.com/page169/ISElectiveProfessional/main/TPC%20Student%20Handbook%20(1).pdf"
MAX_CHARS = 300000  # cap so the page doesn't blow up the prompt / quota

def fetch_and_clean_pdf(url: str) -> str:
    """Download a PDF and extract clean text."""
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    
    # Open PDF from bytes
    pdf_file = BytesIO(response.content)
    doc = pymupdf.open(stream=pdf_file, filetype="pdf")
    
    text = ""
    for page in doc:
        text += page.get_text() + " "
    
    text = re.sub(r"\s+", " ", text).strip()
    
    print(f"Extracted {len(text)} characters.")
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
        print(f"Trimmed to {MAX_CHARS} characters.")
    
    return text

def build_system_instruction(source_text: str) -> str:
    """Wrap the source text in a grounded system prompt."""
    return f"""You are a helpful assistant that answers questions
using ONLY the information in the <source> section below. This is the only
knowledge you are allowed to use.

Rules:
1. If the answer is clearly stated or can be reasonably inferred from the
   source, answer it directly and concisely.
2. If the answer is NOT in the source, respond exactly with:
   "I don't have that information on this page."
3. Do not use any outside knowledge, even if you are confident it is correct.
4. Do not guess or speculate. Do not make up details not present in the source.
5. Keep answers under 4 sentences unless the user asks for more detail.
6. At the end of every answer that DOES use the source, add the tag [SOURCED].
   At the end of every refusal, add the tag [NOT IN SOURCE].

<source>
{source_text}
</source>
"""

def main():
    # STEP 2: Load the API key from .env
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit(
            "GEMINI_API_KEY not found. Create a .env file with:\n"
            "GEMINI_API_KEY=your_key_here"
        )

    client = genai.Client(api_key=api_key)

    # STEP 3: Fetch and prep the source page
    print(f"Fetching: {URL}")
    source_text = fetch_and_clean_pdf(URL)
    system_instruction = build_system_instruction(source_text)
    print(f"System instruction length: {len(system_instruction)} characters\n")

    # STEP 4: Create a chat session with grounding applied to every turn
    chat = client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.0,
        ),
    )

    # STEP 5: Interactive command-line loop
    print("Chatbot ready! Ask a question about the source page.")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break
        if not user_input:
            continue

        response = chat.send_message(user_input)
        print(f"Bot: {response.text}\n")

if __name__ == "__main__":
    main()