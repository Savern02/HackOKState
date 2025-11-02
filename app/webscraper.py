import requests
from bs4 import BeautifulSoup
import logging
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from .models import Scrape
from . import db
from urllib.parse import urljoin

# ---------- html ---------- \
#TODO: add a url based off a list of urls.txt 
def getHTML(url):
    response = requests.get(url)
    if response.status_code != 200:
        logging.error("Failed:", response.status_code)
        return
    html_data = response.text
    return html_data

# -------------soup--------------------------
# def parseHTML(html_data):
#     soup = BeautifulSoup(html_data, "html.parser")
#     return soup.body.get_text(separator="\n", strip=True)
# ------------------Open AI ---------------------------
ai_key = os.environ["OPEN_AI_KEY"]

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key= ai_key,

)
def call_openai(html_data: str):
    response = client.chat.completions.create(
    model="google/gemini-2.0-flash-lite-001",
    messages=[

            {"role": "system", "content": "You are an HTML parser. Analyze HTML content and extract links (links start with https:\\), locations, and descriptions."},
            { "role": "user", "content": html_data},
            { "role": "user", "content": "What volunteer opportunities are there? "},
     ],
   response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "html_parser",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "opportunities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "name of listing from the HTML"
                                    },
                                    "link": {
                                        "type": "string",
                                        "description": "link to the listing"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Give the full state name of the location only, default to United States if not found"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "Give a medium description"
                                    }
                                },
                                "required": ["name", "link",  "location", "description"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["opportunities"],
                    "additionalProperties": False
                }
            }
        }
    )
    print(len(response.choices))
    return response.choices[0].message.content


  
#TODO: Send parse JSON from each site and send it to database where it will be compiled 
def accept_link_to_scrape(url):
    load_dotenv() #load key from .env file
    result = call_openai(getHTML(url))
    if result == None:
        logging.error(msg)
    with open("response.json", "w") as file:
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

if __name__ == "__main__":
    load_json_to_db()