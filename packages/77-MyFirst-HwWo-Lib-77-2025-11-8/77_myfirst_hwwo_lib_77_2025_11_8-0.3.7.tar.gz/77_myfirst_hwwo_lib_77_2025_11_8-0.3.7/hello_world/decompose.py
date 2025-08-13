from langchain_community.vectorstores import FAISS
from openai import OpenAI
from google.genai import errors

DECOMPOSE_PROMPT = (
    "Your task is to analyse the provided question, then raise atomic sub-questions "
    "for the knowledge that can help you answer the question better.\n\n"
    "Think in different ways and raise as many diverse questions as possible. "
    "The user will provide the base question.\n\n"
    "Do not answer the question, just raise sub-questions. "
    "Do not decompose if the question is simple enough."
)

FILTER_PROMPT = (
    "You will receive an original question and a list of sub-questions.\n"
    "Your tasks:\n"
    "1. Compare each sub-question to the original question for relevance.\n"
    "2. Select only the sub-questions that are directly useful to answer the original question.\n"
    "3. Return up to 5 sub-questions as a numbered list. Do not repeat, elaborate, or answer.\n"
    "IMPORTANT - If the original question is simple enough, select even fewer sub-questions.\n\n"
    "Output Format (MUST be valid JSON):\n"
    "[\n"
    '{"q_number": 1, "q": "First selected sub-question"},\n'
    '{"q_number": 2, "q": "Second selected sub-question"}'
    "\n]"
)

class DecomposeQuestion:
    """
    Uses an LLM (via OpenAI API) to break down a complex question
    into a set of atomic sub-questions.
    """

    def __init__(self, base_url, model):
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(base_url=self.base_url)

    def decompose_function(self, orignal_query):
        """
        Given an input question, generate atomic sub-questions via LLM.
        Returns:
            str: Raw string response from LLM (user may want to parse downstream).
        Raises:
            APIError: If LLM API call fails.
        """

        # API call
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": DECOMPOSE_PROMPT},
                    {"role": "user", "content": orignal_query},
                ]
            )
            output = response.choices[0].message.content
            return output
        except errors.APIError as e:
            print(e.code)
            print(e.message)


class QuestionFilter:
    """
    Filters the generated sub-questions to select the most relevant ones
    in relation to the original user question.
    """

    def __init__(self, base_url, model):
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(base_url=self.base_url)

    def filter_subquestions_function(self, original_query, subquestions):
        """
        Filters subquestions for relevance via LLM.
        Args:
            original_query (str): The user's original question.
            subquestions (str): Sub-questions to filter (typically comma-separated or JSON).
        Returns:
            str: Raw string response from LLM (machine-parseable numbered dicts, e.g. JSON).
        Raises:
            APIError: If LLM API call fails.
        """

        user_prompt = f"Original question: {original_query}\nSub-questions:\n{subquestions}"
        # API call
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": FILTER_PROMPT},
                    {"role": "user", "content": user_prompt},
                ]
            )
            #print("Response \n",response.choices[0].message.content,  "Response over \n")
            return response.choices[0].message.content
        except errors.APIError as e:
            print(e.code)
            print(e.message)