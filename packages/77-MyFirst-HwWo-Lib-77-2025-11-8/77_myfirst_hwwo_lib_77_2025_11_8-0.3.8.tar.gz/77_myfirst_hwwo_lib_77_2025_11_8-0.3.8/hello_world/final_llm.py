from openai import OpenAI
from google.genai import errors

class final_query():

    def __init__(self, base_url, model):
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(base_url=self.base_url)
        
    def caller_function(self,final_ranked_list):
        llm_answers = []
        for result_item in final_ranked_list:
            self.q = result_item["question"]
            self.rankedchunks = result_item["search_results"]

            formatted_context = "\n".join([f"{i+1}. {chunk}" for i, chunk in enumerate(self.rankedchunks)])
            prompt_template = """
            You are an assistant who answers questions. Find answers to the question. Answer as precisely as possible using the context provided.
            Task:
            1. Read the numbered context snippets for the question.
            2. Decide which snippet(s) fully answer the question.
            3. Copy or paraphrase only what is needed.
            context:{context}
            IMPORTANT - Answer strictly from these excerpts. If the answer is not present, say “Requested answer not found”.
            """
            prompt_filled = prompt_template.format(context=formatted_context)
            print("\n ---------------- \n", formatted_context,"\n ------------------ \n" )
            # API call
            try:
                response = self.client.chat.completions.create(
                    model= self.model,
                    messages=[
                        {"role": "system", "content": prompt_filled},
                        {"role": "user", "content": self.q},
                    ]
                )
                print(response.choices[0].message.content)
                llm_answers.append(response.choices[0].message.content)
            except errors.APIError as e:
                print(e.code)
                print(e.message)
        return llm_answers