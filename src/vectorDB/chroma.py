from uuid import uuid4
from typing import List, Dict, Any
from langchain_chroma import Chroma as ch
from ..llm.model import embedding_model
from langchain_core.documents import Document
from ..constants import SUMMARY_TYPE


class ChromaDBManager:
    def __init__(self, collection_name: str, persist_directory: str = "./chroma_db"):
        """
        Initialize the ChromaDB manager with the collection name and persist directory.

        Args:
            collection_name (str): The name of the collection.
            persist_directory (str): Directory where Chroma DB is persisted.
        """
        # Initialize OpenAI embeddings and Chroma vector store
        self.embeddings = embedding_model
        self.db = ch(collection_name=collection_name,
                     embedding_function=self.embeddings,
                     persist_directory=persist_directory)
        self.retriever = self.db.as_retriever()

    async def add_documents(self, documents: List[str], metadata: dict, has_summary: bool = False):
        """
        Add documents to Chroma DB with their corresponding metadata and embeddings.

        Args:
            documents (List[str]): List of document texts to be added to the collection.
            metadata (List[Dict[str, Any]]): Metadata corresponding to each document.
            ids (List[str]): List of unique document IDs.
        """
        documents_to_insert = []
        documents_length = len(documents)
        for index, document in enumerate(documents):
            if has_summary and index == documents_length - 1:
                metadata.update({"type": SUMMARY_TYPE})
            documents_to_insert.append(Document(
                page_content=document if isinstance(
                    document, str) else document.page_content,
                metadata=metadata
            ))
        uuids = [str(uuid4()) for _ in range(len(documents))]
        self.db.add_documents(documents=documents_to_insert, ids=uuids)

        print(f"Added {len(uuids)} documents to Chroma DB.")

    def query(self, query: str, filter_query: Any = None, n_results: int = 5):
        """
        Query the Chroma DB to retrieve documents similar to the input query.

        Args:
            query (str): The query string to search for in the Chroma DB.
            n_results (int): Number of results to return.

        Returns:
            List[str]: List of most similar documents based on the query.
        """
        results = self.db.similarity_search(
            query,
            k=n_results,
            filter=filter_query,
        )

        return results
