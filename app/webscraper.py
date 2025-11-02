import requests
from bs4 import BeautifulSoup
import logging
from openai import OpenAI
import os
from dotenv import load_dotenv

# ---------- html ---------- \
#TODO: add a url based off a list of urls.txt 
DEFAULT_URL = "https://www.cityoftulsa.org/serve-tulsans/volunteers/find-an-opportunity/"
def getHTML():
    response = requests.get(DEFAULT_URL)
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
                                    "description": {
                                        "type": "string",
                                        "description": "location followed by a short description"
                                    }
                                },
                                "required": ["name", "link", "description"],
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
if __name__ == "__main__":
    load_dotenv()  # Add this at the start of your script
    result = call_openai(getHTML())
    if result == None:
        logging.error(msg)
    with open("response.json", "w") as file:
        file.write(result)

