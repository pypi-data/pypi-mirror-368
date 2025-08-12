import json
from google.genai import errors
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings



class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name, device="cpu")
        
    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]
    
    def embed_query(self, text):
        return self.model.encode(text).tolist()
    

class ChunkExtraction:
    """
    Loads a FAISS vector database and provides semantic search
    for relevant document chunks from filtered sub-questions.
    """
    def __init__(self):
        try:
            embedding_model = SentenceTransformerEmbeddings("all-mpnet-base-v2")
            self.library = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)

        except  errors.APIError as e:
            print(e.code)
            print(e.message)


    def chunker_function(self, filtered_questions_json,k: int = 5 ):
        """
        Takes a list (or a JSON string representing a list) of filtered sub-questions.
        For each sub-question, retrieves top k most similar document chunks.

        Args:
            filtered_questions (str | list): List or JSON string of sub-question dicts.
            k (int): Number of chunks to return per question.

        Returns:
            List[dict]: Each result dict contains question info and retrieved chunks.
        """

        input_list = json.loads(filtered_questions_json)
        query_answers = []
        print("Number of input questions:", len(input_list))


        for i, item in enumerate(input_list):
            q_number = item.get("q_number")
            q = item.get("q")

            # 5 chunks for each q
            try:
                document_chunks = self.library.similarity_search(q, k=k)
                string_chunks = [doc.page_content for doc in document_chunks]
            except  errors.APIError as e:
                print(e.code)
                print(e.message)
                string_chunks = []

            result_item = {
                "index": i,
                "q_number": q_number,
                "question": q,
                "search_results": string_chunks
            }
            query_answers.append(result_item)

        return query_answers
