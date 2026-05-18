import os
import tempfile
from pathlib import Path
from typing import Optional
import json

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_classic.retrievers import ContextualCompressionRetriever
from openai import OpenAI

from app.config.Global_config import (
    CHROMA_DB_DIR,EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE, EMBEDDING_KEY, EMBEDDING_URL,
)
from app.config.logger_config import logger
from app.RAG.reranker import DashScopeReranker

# ===== 客户端 =====

os.makedirs(CHROMA_DB_DIR, exist_ok=True)

_embed_client = OpenAI(api_key=EMBEDDING_KEY, base_url=EMBEDDING_URL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    all_embeddings = []
    for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[i : i + EMBEDDING_BATCH_SIZE]
        resp = _embed_client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        all_embeddings.extend([d.embedding for d in resp.data])
    return all_embeddings


class DashScopeEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return embed_texts(texts)

    def embed_query(self, text: str) -> list[float]:
        return embed_texts([text])[0]


_embeddings = DashScopeEmbeddings()

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],
)


def _collection_name(conv_id: int) -> str:
    return f"conversion_{conv_id}"


# ===== 文件加载 =====

_LOADERS = {
    ".txt": TextLoader,
    ".pdf": PyPDFLoader,
    ".csv": CSVLoader,
    ".html": UnstructuredHTMLLoader,
    ".htm": UnstructuredHTMLLoader,
    ".md": UnstructuredMarkdownLoader,
}


def load_documents(filename: str, content: bytes) -> list[Document]:
    ext = Path(filename).suffix.lower()

    if ext == ".json":

        data = json.loads(content.decode("utf-8"))
        if isinstance(data, list):
            docs = [Document(page_content=json.dumps(item, ensure_ascii=False)) for item in data]
        else:
            docs = [Document(page_content=json.dumps(data, ensure_ascii=False))]
        if not docs:
            raise ValueError("JSON 文件内容为空")
        return docs

    loader_cls = _LOADERS.get(ext)
    if loader_cls is None:
        raise ValueError(f"不支持的文件类型: {ext}")

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        docs = loader_cls(tmp_path, encoding="utf-8") if ext in (".txt", ".csv") else loader_cls(tmp_path)
        docs = docs.load() if hasattr(docs, 'load') else docs
    finally:
        os.remove(tmp_path)

    if not docs:
        raise ValueError("文件内容为空")
    return docs


# ===== 文本切片 =====

def split_documents(docs: list[Document]) -> list[Document]:
    return _splitter.split_documents(docs)


# ===== 向量存储 =====

def store_documents(conv_id: int, documents: list[Document]):
    print(documents)
    Chroma.from_documents(
        documents=documents,
        embedding=_embeddings,
        collection_name=_collection_name(conv_id),
        persist_directory=str(CHROMA_DB_DIR),
    )
    logger.info(f"ChromaDB 存入 {len(documents)} 个 chunk → {_collection_name(conv_id)}")


# ===== 检索 =====

def _get_vectorstore(conv_id: int) -> Optional[Chroma]:
    try:
        return Chroma(
            collection_name=_collection_name(conv_id),
            embedding_function=_embeddings,
            persist_directory=str(CHROMA_DB_DIR),
        )
    except Exception:
        return None


def get_retriever(conv_id: int, top_k: int = 5):
    vectorstore = _get_vectorstore(conv_id)
    if vectorstore is None:
        return None
    return vectorstore.as_retriever(search_kwargs={"k": top_k})


def retrieve_with_rerank(conv_id: int, query: str, top_k: int = 5, top_n: int = 3) -> list[dict]:
    retriever = get_retriever(conv_id, top_k)
    if retriever is None:
        return []

    reranker = DashScopeReranker(top_n=top_n)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=retriever,
    )

    try:
        compressed = compression_retriever.invoke(query)
    except Exception as e:
        logger.warning(f"Rerank 失败，退回向量检索: {e}")
        compressed = retriever.invoke(query)

    #调试
    logger.info(compressed)
    print("==========================================")
    print(doc for doc in compressed)

    return [
        {"content": doc.page_content, "score": doc.metadata.get("relevance_score", 0)}
        for doc in compressed
    ]


def delete_collection(conv_id: int):
    try:
        vectorstore = _get_vectorstore(conv_id)
        if vectorstore:
            vectorstore.delete_collection()
    except Exception:
        pass
