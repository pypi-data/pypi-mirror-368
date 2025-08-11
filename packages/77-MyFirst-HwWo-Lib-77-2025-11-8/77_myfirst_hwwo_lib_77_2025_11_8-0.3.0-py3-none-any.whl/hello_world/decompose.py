from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings
from openai import OpenAI
from google.genai import types, errors
import os
from dotenv import load_dotenv
load_dotenv()

class DecomposeQuestion:

    def __init__(self, base_url, model):
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def decompose_function(self, orignal_query):
        # Prompt
        prompt_template = """
        Your task is to analyse the providing question then raise atomic sub-questions for the knowledge that can help you answer the question better.
        Think in different ways and raise as many diverse questions as possible. The user will provide the base question. 
        Do not answer the question, just raise sub-questions. Do not decompose if the question is simple enough
        """

        # API call
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt_template},
                    {"role": "user", "content": orignal_query},
                ]
            )
            #print( "Response : \n ",response.choices[0].message.content, "Response over \n")
            return response.choices[0].message.content
        except errors.APIError as e:
            print(e.code)
            print(e.message)


class QuestionFilter:

    def __init__(self, base_url, model):
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def filter_subquestions_function(self, orignal_query, subquestions):
        #  Prompt
        prompt_template = """
        You will receive an original question and a list of sub-questions.
        Your tasks:
        1. Compare each sub-question to the original question for relevance.
        2. Select only the sub-questions that are directly useful to answer the original question.
        3. Return 5 sub-questions as a numbered list. Do not repeat, elaborate, or answer.
        IMPORTANT - If the orignal question is simple enough, select even lesser sub-questions.

        Output Format:
        Example output:
        [
        {"q_number": 1, "q": "First selected sub-question"},
        {"q_number": 2, "q": "Second selected sub-question"}
        ]
        """

        # API call
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt_template},
                    {"role": "user", "content": f"Original question: {orignal_query}\nSub-questions:\n{subquestions}"},
                ]
            )
            #print("Response \n",response.choices[0].message.content,  "Response over \n")
            return response.choices[0].message.content
        except errors.APIError as e:
            print(e.code)
            print(e.message)