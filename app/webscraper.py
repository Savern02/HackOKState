import requests
from bs4 import BeautifulSoup
import logging
import os
from dotenv import load_dotenv
import json
from .models import Scrape
from . import db
from urllib.parse import urljoin
from google import genai
from google.genai import types 
from typing import List, TypedDict, Literal # Use for schema definition
import typing
from pydantic import BaseModel, Field


# ---------- html ---------- \
def getHTML(url):
    if not url.startswith('http'):
        url = "https://" + url
    
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed:", response.status_code)
        return None
    html_data = response.text
    return html_data

# -------------soup--------------------------
# def parseHTML(html_data):
#     soup = BeautifulSoup(html_data, "html.parser")
#     return soup.body.get_text(separator="\n", strip=True)
# ------------------Google Gemini ---------------------------
class Opportunity(BaseModel):
    name: str = Field(description="The name of the volunteer opportunity.")
    link: str = Field(description="The absolute URL link for the opportunity.")
    location: str = Field(description="The City and full State name, or 'United States' if not found.")
    description: str = Field(description="A medium-length description of the work.")
    work_type: str = Field(description="The category or type of work (e.g., 'Environmental', 'Education').")
class Opportunities(BaseModel):
    opportunities: List[Opportunity] = Field(..., description="A list of opportunities.")

ai_key = os.environ["GEMINI_KEY"]
client = genai.Client(api_key=ai_key)

def call_gemini(html_data: str):
    system_prompt = (
        "You are an HTML parser. Analyze the following HTML content and extract opportunities, return **AS MUCH AS POSSIBLE** "
        "Extract the name, link , location (as City & full state name, defaulting to 'United States' if not found), "
        "a medium-length description and type of work."
    )

    # **Structured Output Configuration**
# 2. Define the Configuration (JSON Mode & System Prompt)
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,  # <-- Use this parameter!
        response_mime_type="application/json",
            response_schema= Opportunities, 
    )
    contents  = "What volunteer opportunities are there? Respond only with the JSON object following the schema. " + html_data

    
    # **The core API call**
    response = client.models.generate_content(
        model="gemini-2.5-flash", # A powerful and fast model for structured extraction
        contents=contents,
        config=config
    )
    
    # The response.text will contain the strict JSON string
    return response.text

  
def accept_link_to_scrape(url):
    load_dotenv() #load key from .env file
    HTML = getHTML(url)
    if HTML == None:
        logging.error("Failed to get HTML @" + url)
        return 
    result = call_gemini(HTML)
    if result == None:
        logging.error("AI response.")
    with open("app/response.json", "w") as file:
        file.write(result)



def load_json_to_db(url):
    with open("app/response.json", 'r') as f:
        data = json.load(f)  # Parse JSON → Python list/dict
    opportunities = data.get("opportunities", [])
    for entry in opportunities:
        # Create a Scrape object for each JSON record
        new_record = Scrape(
            name=entry.get('name'),
            link="".join(urljoin(url, entry.get('link'))),
            location=entry.get('location'),
            description=entry.get('description')
        )
        db.session.add(new_record)
    
    db.session.commit()
 
