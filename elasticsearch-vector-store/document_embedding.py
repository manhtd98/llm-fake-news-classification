# import dotenv

# dotenv.load_dotenv()
import glob
import logging
from typing import Dict
from config import CONFIG, ResponseEnum
import os
import json

## for vector store
from elasticsearch import Elasticsearch
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_elasticsearch import ElasticsearchStore
from langchain.document_loaders import JSONLoader
from langchain.docstore.document import Document
from text_clean import text_processing_document
import pandas as pd


def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["source"] = record.get("metadata")
    return metadata


class ElasticVectorClient:
    def __init__(
        self,
        elastic_endpoint: str,
        index_name: str,
        embedding_model: str,
        username: str,
        password: str,
    ):
        logging.info(">> Elasticsearch connection setup!")
        self.elastic_host = f"http://{username}:{password}@{elastic_endpoint}:9200"
        self.elastic_client = Elasticsearch(
            [self.elastic_host], basic_auth=(username, password), http_compress=True
        )
        if not self.elastic_client.ping():
            raise ValueError("Connection failed")

        logging.info(f">> Prep. Huggingface embedding: {embedding_model} setup!")
        model_kwargs = {"device": "cpu"}
        encode_kwargs = {"normalize_embeddings": False}
        self.embedding_model = SentenceTransformerEmbeddings(
            model_name=embedding_model,
            cache_folder=CONFIG.cache_dir,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
        )

        self.index_name = index_name
        self.qa_index = CONFIG.ELS_INDEXNAME_QA
        self.r_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CONFIG.chunk_size,
            chunk_overlap=CONFIG.chunk_overlap,
            # separators=["\n\n",],
        )

        if os.getenv("DB_RELOAD", "FALSE") == "TRUE":
            self.elastic_client.indices.delete(index=self.index_name, ignore=[400, 404])
            self.elastic_client.indices.delete(index=self.qa_index, ignore=[400, 404])

        if not self.elastic_client.indices.exists(index=self.index_name):
            logging.info(
                f">> Elasticsearch index: {self.index_name} doesn't exist. Create new!"
            )
            for document in glob.glob(CONFIG.source_path):
                self.insert_document_embedding(document, self.index_name)

        if not self.elastic_client.indices.exists(index=self.qa_index):
            logging.info(
                f">> Elasticsearch index: {self.qa_index} doesn't exist. Create new!"
            )
            for document in glob.glob(CONFIG.qa_path):
                self.insert_document_qa(document, index_name=self.qa_index)

        logging.info(">> Elasticsearch retriever success set-up!")

    def insert_document_embedding(self, document_path: str, index_name: str) -> Dict:
        try:
            if "processed_" in document_path:
                return
            with open(document_path, "r") as f:
                json_file = json.load(f)
                processing_data = []
                for doc in json_file["document"]:
                    for subdoc in doc["subdocument"]:
                        processing_data.append(
                            {
                                "text": text_processing_document(subdoc["text"]),
                                "metadata": doc["tittle"] + " " + subdoc["metadata"],
                            }
                        )
            save_file = (
                "/".join(document_path.split("/")[:-1])
                + "/processed_"
                + document_path.split("/")[-1]
            )
            with open(save_file, "w+") as f:
                json.dump({"data": processing_data}, f)

            loader = JSONLoader(
                file_path=save_file,
                jq_schema=".data[]",
                content_key="text",
                text_content=False,
                metadata_func=metadata_func,
            )

            r_docs = loader.load()
            r_docs = self.r_splitter.split_documents(r_docs)
            logging.info(f"Create Document from path: {document_path}")
            _ = ElasticsearchStore.from_documents(
                r_docs,
                es_connection=self.elastic_client,
                embedding=self.embedding_model,
                index_name=index_name,
                distance_strategy=CONFIG.distance_strategy,
                strategy=ElasticsearchStore.ApproxRetrievalStrategy(
                    hybrid=True,
                ),
            )
            logging.info(
                f">> Success add: {len(r_docs)} documents to index: {index_name}"
            )

            return {"status": True, "code": ResponseEnum.SUCCESS}
        except Exception as exception:
            logging.error(str(exception) + document_path)
            return {"status": False, "code": ResponseEnum.EXCEPTION}

    def insert_document_qa(self, document_path: str, index_name: str) -> Dict:
        try:
            df = pd.read_excel(document_path, index_col=0)
            all_document = []
            for _, doc in df.iterrows():
                page_document = Document(
                    page_content=text_processing_document(doc[0]),
                    metadata={
                        "source": str(document_path).split("/")[-1],
                        "answer": doc[1],
                    },
                )
                all_document.append(page_document)
            logging.info(f"Create Document from path: {document_path}")
            _ = ElasticsearchStore.from_documents(
                all_document,
                es_connection=self.elastic_client,
                embedding=self.embedding_model,
                index_name=index_name,
                distance_strategy=CONFIG.distance_strategy,
                strategy=ElasticsearchStore.ExactRetrievalStrategy(),
            )
            logging.info(f">> Success add document to index: {index_name}")

            return {"status": True, "code": ResponseEnum.SUCCESS}
        except Exception as exception:
            logging.error(str(exception))
            return {"status": False, "code": ResponseEnum.EXCEPTION}


if __name__ == "__main__":
    es = ElasticVectorClient(
        elastic_endpoint=CONFIG.ELS_ENDPOINT,
        index_name=CONFIG.ELS_INDEXNAME,
        bucket_name=CONFIG.GCP_BUCKET_NAME,
        username=CONFIG.ELS_USERNAME,
        password=CONFIG.ELS_PASSWORD,
        embedding_model=CONFIG.EMBEDDING_MODEL_ID,
    )

    # es.elastic_client.indices.delete(index=es.index_name, ignore=[400, 404])
    es.insert_document_embedding("raw_jira_tickets/aeriseu/IOTA-16075.json")
    results = es.query_document("What's IOTA?")
    print(results)
