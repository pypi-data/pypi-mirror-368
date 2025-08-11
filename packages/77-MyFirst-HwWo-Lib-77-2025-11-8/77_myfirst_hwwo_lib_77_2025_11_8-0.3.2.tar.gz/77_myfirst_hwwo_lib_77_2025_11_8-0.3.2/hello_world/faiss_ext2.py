import fitz  # PyMuPDF
from pathlib import Path
import glob
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import FAISS

print("STrting creation of FAISS index...")
# Embedding wrapper
class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name, device="cpu")

    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text):
        return self.model.encode(text).tolist()

embedding_model = SentenceTransformerEmbeddings("all-mpnet-base-v2")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=350,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " "]
)

pdf_dir = Path("D:\\Spanda\\ReRank&QDecomp\\data")
pdf_paths = glob.glob(str(pdf_dir / "*.pdf"))
print(f"# PDF files found: {len(pdf_paths)}")

if not pdf_paths:
    raise FileNotFoundError("No PDF files found in data folder.")

page_texts = []
for pdf_path in pdf_paths:
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            print(f"PDF: {pdf_path}, Page {page_num+1}, text_len: {len(text) if text else 0}")
            if text and text.strip():
                page_texts.append((text, page_num+1, Path(pdf_path).name))
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        #print("Tip: If you see 'module fitz has no attribute open', please install PyMuPDF: pip install --upgrade PyMuPDF")

print("Number of pages with extracted text:", len(page_texts))

if not page_texts:
    raise ValueError("No extractable text in PDFs. Are they scanned images? If yes, consider using OCR libraries like pytesseract.")

# Split text into chunks
chunks_with_metadata = []
for text, page_num, filename in page_texts:
    page_chunks = splitter.split_text(text)
    for chunk in page_chunks:
        if chunk.strip():
            chunks_with_metadata.append({
                "content": chunk,
                "metadata": {
                    "page": page_num,
                    "filename": filename
                }
            })

print("Number of non-empty chunks with metadata:", len(chunks_with_metadata))

if not chunks_with_metadata:
    raise ValueError("No text chunks created. Check chunking or input document content.")

documents = [
    Document(page_content=chunk["content"], metadata=chunk["metadata"])
    for chunk in chunks_with_metadata
]

print("Number of Document objects:", len(documents))

if not documents:
    raise ValueError("No Document objects created. Check chunk creation code.")

library = FAISS.from_documents(
    documents=documents,
    embedding=embedding_model
)

library.save_local("faiss_index")

print("FAISS index stored in 'faiss_index'")
