import fitz  # PyMuPDF
from pathlib import Path
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import FAISS

# ------------ Configuration ------------
CHUNK_SIZE = 350
CHUNK_OVERLAP = 50
EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"
INDEX_PATH = "faiss_index"
PDF_DIR = Path("data")   # PDF folder in same directory in data folder


class SentenceTransformerEmbeddings(Embeddings):
    """LangChain-compatible wrapper for SentenceTransformer embeddings."""
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name, device="cpu")

    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text):
        return self.model.encode(text).tolist()


def get_text_splitter():
    """Creates and returns a text splitter with global settings."""
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]
    )


def get_pdf_paths(directory: Path = PDF_DIR):
    """Returns all PDF file paths from the target directory."""
    pdf_files = list(directory.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {directory}")
    return pdf_files


def build_faiss_index():
    """Main pipeline: Reads PDFs → Chunks text → Embeds → Saves FAISS index."""
    print("Step 1: Initializing embedding model...")
    embedding_model = SentenceTransformerEmbeddings(EMBEDDING_MODEL_NAME)

    print("Step 2: Preparing text splitter...")
    splitter = get_text_splitter()

    print(f"Step 3: Scanning for PDF files in '{PDF_DIR}'...")
    pdf_paths = get_pdf_paths()
    print(f"  → Found {len(pdf_paths)} PDF files.")

    print("Step 4: Extracting text from PDFs...")
    page_texts = []
    for pdf_path in pdf_paths:
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text and text.strip():
                    page_texts.append((text, page_num + 1, pdf_path.name))
        except Exception as e:
            raise RuntimeError(f"Error reading {pdf_path}: {e}")
    print(f"  → Extracted text from {len(page_texts)} pages.")

    if not page_texts:
        raise ValueError("No extractable text found.")

    print("Step 5: Splitting text into chunks...")
    chunks_with_metadata = []
    for text, page_num, filename in page_texts:
        page_chunks = splitter.split_text(text)
        for chunk in page_chunks:
            if chunk.strip():
                chunks_with_metadata.append({
                    "content": chunk,
                    "metadata": {"page": page_num, "filename": filename}
                })
    print(f"  → Created {len(chunks_with_metadata)} chunks.")

    if not chunks_with_metadata:
        raise ValueError("No valid chunks created.")

    print("Step 6: Converting chunks to Document objects...")
    documents = [
        Document(page_content=chunk["content"], metadata=chunk["metadata"])
        for chunk in chunks_with_metadata
    ]

    print("Step 7: Building FAISS index...")
    library = FAISS.from_documents(documents=documents, embedding=embedding_model)

    print(f"Step 8: Saving FAISS index to '{INDEX_PATH}'...")
    library.save_local(INDEX_PATH)
    print("FAISS index creation complete.")


# Auto-run if executed directly
build_faiss_index()
