import os
import PyPDF2
import json
import traceback
from src.GenAI.logger import logging

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfFileReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            logging.error("Error reading the PDF file")
            raise Exception("Error reading the PDF file")
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        logging.error("Unsupported file format. Only PDF and text files are supported.")
        raise Exception("Unsupported file format. Only PDF and text files are supported.")



def clean_quiz_data(quiz_data):
    try:
        # Ensure quiz_data is a string
        if isinstance(quiz_data, list):
            quiz_data = "".join(quiz_data)  # Convert list to string

        # Find the start of JSON data
        start_index = quiz_data.find('{')
        if start_index == -1:
            raise ValueError("JSON object not found in the string.")
        
        # Extract JSON data
        quiz_json_str = quiz_data[start_index:]
        
        # Strip any trailing comments or non-JSON content
        quiz_json_str = quiz_json_str.split('\n\n')[0].strip()
        
        # Load JSON to validate its format
        quiz_json = json.loads(quiz_json_str)
        
        # Process each MCQ from the JSON
        mcq_list = []
        for key, value in quiz_json.items():
            mcq = {
                "mcq": value["mcq"],
                "options": value["options"],
                "correct": value["correct"]
            }
            mcq_list.append(mcq)
        
        return mcq_list
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding quiz JSON: {e}")
    except Exception as e:
        raise ValueError(f"Error processing quiz data: {str(e)}")


def get_table_data(quiz_data):
    try:
        # Convert quiz_data to a JSON string if it's a list of dictionaries
        if isinstance(quiz_data, list):
            quiz_str = json.dumps(quiz_data)
        elif isinstance(quiz_data, str):
            quiz_str = quiz_data  # Already a JSON-formatted string
        else:
            raise ValueError("Invalid input format. Expected string or list of dictionaries.")
        
        # Parse the quiz_str as JSON
        quiz_dict = json.loads(quiz_str)

        quiz_table_data = []
        
        # Iterate over the quiz dictionary and extract the required information
        for item in quiz_dict:
            mcq = item["mcq"]
            options = " || ".join(
                [f"{option} -> {option_value}" for option, option_value in item["options"].items()]
            )
            correct = item["correct"]
            quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})
        
        return quiz_table_data
    
    except Exception as e:
        logging.error(f"Error in get_table_data: {str(e)}")
        traceback.print_exc()
        return None

    


def validate_quiz_format(quiz_str):
    try:
        # Clean the quiz string to extract valid JSON
        clean_quiz_str = clean_quiz_data(quiz_str)
        if clean_quiz_str is None:
            raise ValueError("Invalid quiz JSON format")

        quiz_dict = json.loads(clean_quiz_str)

        for key, value in quiz_dict.items():
            if not all(k in value for k in ("mcq", "options", "correct")):
                raise ValueError(f"Quiz item {key} is missing required fields.")
            if not isinstance(value["options"], dict) or not all(isinstance(opt, str) for opt in value["options"].keys()):
                raise ValueError(f"Options in quiz item {key} are not in the correct format.")
        return True
    except (json.JSONDecodeError, ValueError) as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False
