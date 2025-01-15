import os
from typing import Any, Dict, List, Optional, Union

from langchain_core.documents import Document
from pymongo import MongoClient, collection


class DocumentStorage:
    def __init__(
        self,
        host: str,
        port: int,
        db_name: str,
        raw_collection_name: str,
        processed_collection_name: str,
    ) -> None:
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.raw_collection = self.db[raw_collection_name]
        self.processed_collection = self.db[processed_collection_name]

    def get_raw_document(self, source_name: str) -> Optional[str]:
        return self._get_document_by_name_and_collection(
            source_name, self.raw_collection
        )

    def get_processed_document(self, source_name: str) -> Optional[str]:
        return self._get_document_by_name_and_collection(
            source_name, self.processed_collection
        )

    def get_raw_documents(self) -> List[str]:
        return list(self.raw_collection.find({}))

    def get_processed_documents(self) -> List[str]:
        return list(self.processed_collection.find({}))

    def _get_document_by_name_and_collection(
        self, source_name: str, collection: collection.Collection
    ) -> Optional[str]:
        result = collection.find_one({"name": source_name})
        return result

    def set_raw_document(self, source_name: str, document: str) -> None:
        self._set_document_by_collection(
            self, source_name, document, self.raw_collection
        )
        return None

    def set_processed_document(self, source_name: str, document: str) -> None:
        self._set_document_by_collection(
            self, source_name, document, self.processed_collection
        )
        return None

    def _set_document_by_collection(
        self,
        source_name: str,
        document: str,
        collection: collection.Collection,
    ) -> None:
        collection.update_one(
            {"name": source_name}, document, {"upsert": True}
        )
        return None


class ChunkStorage:
    def __init__(
        self, host: str, port: int, db_name: str, collection_name: str
    ) -> None:
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_chunk(self, chunk_id: str) -> Optional[Document]:
        doc_obj = self.collection.find_one({"chunk_id": chunk_id})
        return Document(**doc_obj) if doc_obj else doc_obj

    def set_chunk(self, chunk_id: str, chunk: Document) -> None:
        self.collection.insert_one(
            {"chunk_id": chunk_id, **chunk.model_dump(mode="python")}
        )
        return None


class MetricStorage:
    def __init__(
        self, host: str, port: int, db_name: str, collection_name: str
    ) -> None:
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def set_metric(self, metric: Dict[str, Any]) -> None:
        existing_metric = self.collection.find_one({"name": metric["name"]})
        if existing_metric:
            self.collection.update_one(
                {"source_name": metric["source_name"]},
                {"$set": metric},
                upsert=False,
            )
        else:
            self.collection.insert_one(metric)
        return None

    def get_metric_by_source_name(
        self, source_name: str
    ) -> Optional[Dict[str, Any]]:
        metric = self.collection.find_one({"source_name": source_name})
        return metric


def initialize_storage(
    storage_type: str,
) -> Union[DocumentStorage, ChunkStorage, MetricStorage]:
    if storage_type == "document":
        return DocumentStorage(
            os.getenv("MongoHost"),
            int(os.getenv("MongoPort")),
            os.getenv("DBName"),
            os.getenv("RawDocumentCollectionName"),
            os.getenv("ProcessedDocumentCollectionName"),
        )
    elif storage_type == "chunk":
        return ChunkStorage(
            os.getenv("MongoHost"),
            int(os.getenv("MongoPort")),
            os.getenv("DBName"),
            os.getenv("ChunkCollectionName"),
        )
    elif storage_type == "metric":
        return MetricStorage(
            os.getenv("MongoHost"),
            int(os.getenv("MongoPort")),
            os.getenv("DBName"),
            os.getenv("MetricsCollectionName"),
        )
    else:
        raise ValueError("This storage type doesn't exists!")
