import os
import sys
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.GenAI.utils import read_file, get_table_data,  clean_quiz_data

import streamlit as st
from src.GenAI.MCQGenerator import generate_evaluate_chain
from src.GenAI.logger import logging

# Load environment variables
load_dotenv()

# Try importing the correct callback function
try:
    from langchain.callbacks import get_openai_callback
except ImportError:
    st.error("get_openai_callback is not available in the current LangChain version. Please check the documentation for the correct import.")
    get_openai_callback = None

# Load the JSON response file
with open('Response.json', 'r') as f:
    RESPONSE_JSON = json.load(f)

st.title("MCQ Creator Application with LangChain")

with st.form('user input'):
    uploaded_file = st.file_uploader('Upload PDF or TXT')

    mcq_count = st.number_input("Number of MCQs", min_value=3, max_value=10)

    subject = st.text_input("Insert Subject", max_chars=25)

    tone = st.text_input("Complexity Level of Question", max_chars=20, placeholder='simple')

    button = st.form_submit_button("Create MCQs")

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner('Loading...'):
            try:
                text = read_file(uploaded_file)

                if get_openai_callback:
                    with get_openai_callback() as cb:
                        response = generate_evaluate_chain(
                            {
                                "text": text,
                                "number": mcq_count,
                                "subject": subject,
                                "tone": tone,
                                "response_json": json.dumps(RESPONSE_JSON)
                            }
                        )
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error while generating MCQs")
            else:
                print(response)
                print(f"Total Tokens: {cb.total_tokens}")
                print(f"Prompt Tokens: {cb.prompt_tokens}")
                print(f"Completion Tokens: {cb.completion_tokens}")
                print(f"Total Cost (USD): {cb.total_cost}")

                if isinstance(response, dict):
                    quiz = response.get('quiz', None)
                    if quiz is not None:
                        clean_quiz_str = clean_quiz_data(quiz)
                        if clean_quiz_str:
                            table_data = get_table_data(clean_quiz_str)
                            if table_data:
                                df = pd.DataFrame(table_data)
                                df.index = df.index + 1
                                st.table(df)
                                st.text_area(label='Review', value=response['review'])
                            else:
                                st.error("Error in the table data format")
                        else:
                            st.error("Invalid quiz JSON format")
                else:
                    st.write(response)
