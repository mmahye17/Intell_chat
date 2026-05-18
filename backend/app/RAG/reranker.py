from typing import Sequence

from langchain_core.documents import BaseDocumentCompressor, Document
from openai import OpenAI

from backend.app.config.Global_config import LLM_API_KEY, RERANK_MODEL
from backend.app.config.logger_config import logger

_rerank_client = OpenAI(
    api_key=LLM_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-api/v1",
)


class DashScopeReranker(BaseDocumentCompressor):
    """DashScope Rerank 重排序，适配 LangChain ContextualCompressionRetriever"""
    top_n: int = 3

    def compress_documents(
        self, documents: Sequence[Document], query: str, **kwargs
    ) -> Sequence[Document]:
        if not documents or len(documents) <= self.top_n:
            return list(documents)

        try:
            resp = _rerank_client.post(
                "/reranks",
                body={
                    "model": RERANK_MODEL,
                    "query": query,
                    "documents": [d.page_content for d in documents],
                    "top_n": self.top_n,
                },
                cast_to=object,
            )
            results = resp["results"]
        except Exception as e:
            logger.warning(f"Rerank API 调用失败: {e}")
            return list(documents)[: self.top_n]

        compressed = []
        for r in sorted(results, key=lambda x: x["relevance_score"], reverse=True):
            doc = documents[r["index"]]
            doc.metadata["relevance_score"] = round(r["relevance_score"], 4)
            compressed.append(doc)
        return compressed
