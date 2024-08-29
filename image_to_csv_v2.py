import openai
import os
import ast
import pandas as pd
from PIL import Image

# Set your OpenAI API key
openai.api_key = "" ## Your Key Here

def resize_image(image_path, output_path, max_width=1000):
    with Image.open(image_path) as img:
        img.thumbnail((max_width, img.height))
        img.save(output_path)

def extract_text_and_tables_from_image(image_path):
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    # Use the OpenAI API to process the image and extract the tables
    response = openai.ChatCompletion.create(
        model="chatgpt-4o-latest",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts table data from images."},
            {"role": "user", "content": "Please extract the headings and corresponding table data from this image."},
            {"role": "user", "content": str(image_bytes)},  # Sending image as a binary string (this needs adjustment)
        ]
    )

    # Extract the structured data from the response
    structured_data = response.choices[0].message['content']
    return structured_data

def save_tables_to_csv_from_structured_data(structured_data, output_folder):
    tables_dict = ast.literal_eval(structured_data)

    # Save each table to a CSV file named after its heading
    for heading, table in tables_dict.items():
        df = pd.DataFrame(table)
        csv_filename = f"{heading}.csv"
        df.to_csv(os.path.join(output_folder, csv_filename), index=False)

def process_image_with_genai(image_path, output_folder):
    structured_data = extract_text_and_tables_from_image(image_path)
    save_tables_to_csv_from_structured_data(structured_data, output_folder)

def process_all_images_in_folder(input_folder, resized_folder, output_folder,  max_width=1000):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(resized_folder):
        os.makedirs(resized_folder)

    # Resize images and save them to the resized_folder
    for image_filename in os.listdir(input_folder):
        if image_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            image_path = os.path.join(input_folder, image_filename)
            resized_image_path = os.path.join(resized_folder, image_filename)
            resize_image(image_path, resized_image_path, max_width=max_width)
    
    # Process the resized images with OpenAI API and save CSVs
    for image_filename in os.listdir(resized_folder):
        if image_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            resized_image_path = os.path.join(resized_folder, image_filename)
            process_image_with_genai(resized_image_path, output_folder)

def ensure_folder_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

input_folder = "C:/Users/shiva/Desktop/IITJ/Image to Excel/images"
resized_folder = "C:/Users/shiva/Desktop/IITJ/Image to Excel/processed_images"
output_folder = "C:/Users/shiva/Desktop/IITJ/Image to Excel/csvs"

process_all_images_in_folder(input_folder, resized_folder, output_folder)
