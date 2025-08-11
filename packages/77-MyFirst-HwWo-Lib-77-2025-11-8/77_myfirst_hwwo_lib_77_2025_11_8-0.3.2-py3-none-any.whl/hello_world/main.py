import os
from dotenv import load_dotenv
load_dotenv()
# Import classes from sibling modules (package-style)
from .decompose import DecomposeQuestion, QuestionFilter
from .chunk_extractor import ChunkExtaction
from .reranker import ReRanker
from .final_llm import final_query

base_url = "http://localhost:9018/v1"
model = "ibnzterrell/Meta-Llama-3.3-70B-Instruct-AWQ-INT4"

def main():
    user_question = """
    explain Plancks Quantum Hypothesis.
    """


    print("\n--- Processing your question, please wait... ---")

    # Decomposition
    decomposer = DecomposeQuestion(model=model, base_url=base_url)
    print("\n--- Generating Sub-questions ---")
    sub_questions = decomposer.decompose_function(user_question)
    # print("Generated Sub-questions:\n", sub_questions)

    # Filter sub-questions
    question_filter = QuestionFilter(model=model, base_url=base_url)
    print("\n--- Filtering Sub-questions ---")
    filtered_questions = question_filter.filter_subquestions_function(user_question, sub_questions)
    print("Filtered Top 5 Sub-questions:\n", filtered_questions)

    # Sub-questions chunk extractors
    ChunkExtactorInstance = ChunkExtaction()
    print("\n--- Embedding Sub-questions and Extracting Chunks ---")
    filtered_questions_chunks = ChunkExtactorInstance.chunker_function(filtered_questions)
    print("\n--- Chunks Found ---")

    # Chunk re-ranking
    Ranker = ReRanker()
    print("\n--- Re Ranking ---")
    final_ranked_list = Ranker.reranker_function(filtered_questions_chunks)
    print("\n--- Re Ranking Done ---")

    # Feed to LLM
    llm_caller = final_query(model=model, base_url=base_url)
    print("\n--- Querying LLM --- \n")
    FinalAnswers = llm_caller.caller_function(final_ranked_list)
    print(FinalAnswers)

    # for i, answer in enumerate(FinalAnswers):
    #     print("\n -------------- \nans " , i , " : " , answer, "\n -------------- \n" )
    print("ALL DONE, WOHOO")

if __name__ == "__main__":
    main()
