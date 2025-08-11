from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings
import json


class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name, device="cpu")
        
    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]
    
    def embed_query(self, text):
        return self.model.encode(text).tolist()
    

class ChunkExtaction:

    def __init__(self):
        embedding_model = SentenceTransformerEmbeddings("all-mpnet-base-v2")
        self.library = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)
    
    """
    def chunker_function(self, filtered_questions):  
        query_answers = []
        #iterate through 5 q
        print("Number of input questions:", len(filtered_questions))
        for i, q in enumerate(filtered_questions[:5]):
            # 5 chunks for each q
            document_chunks  = self.library.similarity_search(q, k=5)
            string_chunks = [doc.page_content for doc in document_chunks]   
            #dict def per q
            print("\n ------- len of string_chunks:" , len(string_chunks))
            result_item = {
                "index": i,
                "question": q,
                "search_results": string_chunks
            }
            query_answers.append(result_item)
        print("\n --------- len of query_answers:", len(query_answers))
        return query_answers

    """
    def chunker_function(self, filtered_questions_json):

        input_list = json.loads(filtered_questions_json)
        query_answers = []
        print("Number of input questions:", len(input_list))
        for i, item in enumerate(input_list):
            q_number = item.get("q_number")
            q = item.get("q")
            # 5 chunks for each q
            document_chunks  = self.library.similarity_search(q, k=5)
            string_chunks = [doc.page_content for doc in document_chunks]
            #print(f"\n ------- len of string_chunks for q_number {q_number}:", len(string_chunks))
            result_item = {
                "index": i,
                "q_number": q_number,
                "question": q,
                "search_results": string_chunks
            }
            query_answers.append(result_item)
        #print("\n --------- len of query_answers:", len(query_answers))
        return query_answers
