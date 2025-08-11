from sentence_transformers import CrossEncoder
from typing import List, Tuple

# TO DO - add print/log to check
class ReRanker():

    def __init__(self): 
        self.cross_encoder_model = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def reranker_function(self,filtered_questions_chunks):
        reranker = CrossEncoder(self.cross_encoder_model)

        for result_item in filtered_questions_chunks:
            self.index = result_item["index"]
            self.question = result_item["question"]
            #self.chunks = results["search_results"]

            all_chunks = []
            all_chunks.extend(result_item["search_results"])
            indiv_chunks = list(set(all_chunks))

            query_chunk_pairs = [[self.question, chunk] for chunk in indiv_chunks]
            scores = reranker.predict(query_chunk_pairs)
            scored_chunks = list(zip(indiv_chunks, scores))
            scored_chunks.sort(key=lambda x: x[1], reverse=True)

            final_ranked_list =[]
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

        """
        # print ranked chunks (rank, score)
        print("\nRERANKED CHUNKS")
        for rank, (chunk, score) in enumerate(scored_chunks, start=1):
            preview = chunk.replace("\n", " ")[:20]  # shorten long passages
            print(f"{rank:>2}. {score:.4f} | {preview}")
        print(" rareank print over\n")

        """
