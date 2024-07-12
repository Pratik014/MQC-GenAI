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


def clean_quiz_json(quiz_str):
    """
    Clean the quiz JSON string to remove any extraneous data and ensure it's valid JSON.
    """
    try:
        # Find the starting point of the actual JSON data
        start_index = quiz_str.find('{')
        end_index = quiz_str.rfind('}') + 1

        # Extract the JSON part of the string
        clean_str = quiz_str[start_index:end_index]

        # Validate and return the cleaned JSON string
        json.loads(clean_str)  # This will raise an error if the string is not valid JSON
        return clean_str
    except json.JSONDecodeError as e:
        logging.error(f"Error in clean_quiz_json: {str(e)}")
        traceback.print_exception(type(e), e, e.__traceback__)
        return None

def get_table_data(quiz_str):
    try:
        # Clean the quiz string to extract valid JSON
        clean_quiz_str = clean_quiz_json(quiz_str)
        if clean_quiz_str is None:
            raise ValueError("Invalid quiz JSON format")

        quiz_dict = json.loads(clean_quiz_str)
        quiz_table_data = []

        for key, value in quiz_dict.items():
            mcq = value["mcq"]
            options = " || ".join(
                [f"{option} -> {option_value}" for option, option_value in value["options"].items()]
            )
            correct = value["correct"]
            quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})

        return quiz_table_data
    except Exception as e:
        logging.error(f"Error in get_table_data: {str(e)}")
        traceback.print_exception(type(e), e, e.__traceback__)
        return None

def validate_quiz_format(quiz_str):
    try:
        # Clean the quiz string to extract valid JSON
        clean_quiz_str = clean_quiz_json(quiz_str)
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

