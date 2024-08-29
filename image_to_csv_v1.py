import pandas as pd
import openai
import ast

key = "" ## Your Key Here
openai.api_key = key
openai.models.list()

from openai import OpenAI
client = OpenAI(api_key = key)

import pytesseract
from pytesseract import Output
from PIL import Image
import os
import re
import easyocr

def extract_text_from_image(image_path):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path, detail=0)
    return " ".join(result)

def parse_tables_from_text(text):
    # Define a tool for GenAI to parse text into tables
    tools = [
        {
            "type": "function",
            "function": {
                "name": "parse_table",
                "description": "Parse the text into structured table format",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tables": {
                            "type": "array",
                            "description": "List of tables extracted from the text",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "heading": {"type": "string"},
                                    "rows": {
                                        "type": "array",
                                        "items": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    ]
    
    try:
        # Call OpenAI's API to parse the text
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Please parse the following text into structured tables:\n\n{text}"
                }
            ],
            functions=tools
        )
        parsed_tables = response.choices[0].message["function_call"]["arguments"]
        tables_dict = ast.literal_eval(parsed_tables)
        tables = {table['heading']: table['rows'] for table in tables_dict['tables']}
        return tables
    except Exception as e:
        print(f"Error parsing tables: {e}")
        return {}

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def save_tables_to_csv(tables, output_folder):
    for heading, table in tables.items():
        sanitized_heading = sanitize_filename(heading)
        df = pd.DataFrame(table)
        csv_filename = f"{sanitized_heading}.csv"
        df.to_csv(os.path.join(output_folder, csv_filename), index=False)

def process_image(image_path, output_folder):
    text = extract_text_from_image(image_path)
    tables = parse_tables_from_text(text)
    save_tables_to_csv(tables, output_folder)

def process_all_images(input_folder, output_folder):
    for image_filename in os.listdir(input_folder):
        if image_filename.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            image_path = os.path.join(input_folder, image_filename)
            process_image(image_path, output_folder)

def ensure_folder_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

input_folder = "C:/Users/shiva/Desktop/IITJ/Image to Excel/images"
output_folder = "C:/Users/shiva/Desktop/IITJ/Image to Excel/csvs"

ensure_folder_exists(output_folder)
process_all_images(input_folder, output_folder)
