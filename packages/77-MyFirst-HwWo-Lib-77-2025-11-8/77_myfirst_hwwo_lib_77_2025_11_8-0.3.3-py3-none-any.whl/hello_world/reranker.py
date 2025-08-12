from sentence_transformers import CrossEncoder
from typing import List, Tuple

# TO DO - add print/log to check
class ReRanker():
    """
    Reranks text chunks for each sub-question using a CrossEncoder.
    """
    def __init__(self): 
        self.cross_encoder_model = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def reranker_function(self,filtered_questions_chunks):
        """
        Reranks retrieved document chunks for each question using a CrossEncoder.

        Args:
            filtered_questions_chunks: List of dictionaries, each with 
            keys "index", "question", "search_results".

        Returns:
            List of dicts for each question, each with:
            - index: (int)
            - question: (str)
            - search_results: List[Tuple[str, float]] sorted by relevance
        """

        reranker = CrossEncoder(self.cross_encoder_model)
        final_ranked_list =[]

        for result_item in filtered_questions_chunks:
            self.index = result_item["index"]
            self.question = result_item["question"]
            #self.chunks = results["search_results"]

            all_chunks = []
            all_chunks.extend(result_item["search_results"])
            indiv_chunks = list(set(all_chunks))

            # Prepare query-chunk pairs
            query_chunk_pairs = [[self.question, chunk] for chunk in indiv_chunks]
            
            # Score each chunk for its relevance to the question
            scores = reranker.predict(query_chunk_pairs)
            scored_chunks = list(zip(indiv_chunks, scores))
            scored_chunks.sort(key=lambda x: x[1], reverse=True)
            
            result_item = {
                "index": self.index,
                "question": self.question,
                "search_results": scored_chunks
            }
            final_ranked_list.append(result_item)
            
        print("\n ------------------- \n")
        print("final_ranked_list for sub-q number: ",self.index, "is :",final_ranked_list)
        print("\n ------------------- \n")
        return final_ranked_list

