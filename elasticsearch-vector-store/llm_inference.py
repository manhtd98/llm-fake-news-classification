import logging
import os
import json
from langchain.cache import SQLiteCache

from langchain.chains import RetrievalQA
from config import CONFIG, PROMPT_TEMPLATE, SUMMARIZE_PROMPT_TEMPLATE

from document_embedding import ElasticVectorClient

from langchain_community.llms import LlamaCpp
from langchain_elasticsearch import ElasticsearchStore
from text_clean import text_processing
from datetime import datetime


class LLM_QA_INFERENCE:
    def __init__(
        self,
    ):
        self.llm = LlamaCpp(
            model_path=CONFIG.LLM_MODEL_ID,
            n_gpu_layers=CONFIG.n_gpu_layers,
            n_batch=CONFIG.n_batch,
            f16_kv=True,
            verbose=True,  # Verbose is required to pass to the callback manager
            n_ctx=CONFIG.N_CTX,
            temperature=1,
        )
        es_client = ElasticVectorClient(
            elastic_endpoint=CONFIG.ELS_ENDPOINT,
            index_name=CONFIG.ELS_INDEXNAME,
            username=CONFIG.ELS_USERNAME,
            password=CONFIG.ELS_PASSWORD,
            embedding_model=CONFIG.EMBEDDING_MODEL_ID,
        )

        elastic_vector_search = ElasticsearchStore(
            # es_connection=es_client.elastic_client,
            embedding=es_client.embedding_model,
            es_url=es_client.elastic_host,
            index_name=es_client.index_name,
            distance_strategy=CONFIG.distance_strategy,
            strategy=ElasticsearchStore.ApproxRetrievalStrategy(
                hybrid=True,
            ),
        )
        self.ELASTIC_QUERY_QA = ElasticsearchStore(
            # es_connection=es_client.elastic_client,
            embedding=es_client.embedding_model,
            es_url=es_client.elastic_host,
            index_name=es_client.qa_index,
            distance_strategy=CONFIG.distance_strategy,
            strategy=ElasticsearchStore.ExactRetrievalStrategy(),
        )

        self.LLM_QA_CHAIN = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=elastic_vector_search.as_retriever(
                search_kwargs={"k": CONFIG.top_k}
            ),
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": PROMPT_TEMPLATE,
                "verbose": True,
            },
        )
        self.SQL_CACHING_TTL = SQLiteCache(
            database_path=f"logs/{datetime.now().strftime('%Y-%m-%d')}.langchain.db"
        )
        # self.memory = ConversationBufferMemory(
        #     memory_key="chat_history",
        #     # chat_memory=chat_history,  # this is your persistence strategy subclass of `BaseChatMessageHistory`
        #     output_key="answer",
        #     return_messages=True,
        # )
        self.history_path = "./history"
        self.max_token = 5
        self.create_folder_if_not_exists(self.history_path)

    @staticmethod
    def create_folder_if_not_exists(folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logging.info(f"Folder created: {folder_path}")
        else:
            logging.info(f"Folder already exists: {folder_path}")

    def load_memory(self, session_id: str):
        if os.path.exists(f"{self.history_path}/{session_id}.json"):
            with open(f"{self.history_path}/{session_id}.json", "r+") as f:
                retrieve_from_db = json.load(f)
            return retrieve_from_db
        else:
            return []

    def save_json(self, data, conversation_id) -> str:
        # Write the data to the JSON file
        path = f"{self.history_path}/{conversation_id}.json"
        with open(path, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def __call__(self, prompt_input, session_id: str = "default"):
        use_history = False
        if use_history:
            history_prompt_json = self.load_memory(session_id=session_id)
            history_prompt_json = history_prompt_json[: self.max_token]
        input_prompt = text_processing(prompt_input)
        caching_prompt = self.SQL_CACHING_TTL.lookup(input_prompt, CONFIG.LLM_MODEL_ID)
        if caching_prompt is not None:
            datetime_str, response = caching_prompt
            datetime_str = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - datetime_str).total_seconds() < 60 * 60:
                logging.info(f"Using caching for request: {input_prompt}")
                return response, set([])

        # Hugging Face Login
        docs = []
        logging.info("STEP 1: ELASTICSEARCH.similarity_search_with_score")
        similar_score_qa = self.ELASTIC_QUERY_QA.similarity_search_with_score(
            input_prompt, topk=1, search_kwargs={"score_threshold": CONFIG.QA_THRESHOLD}
        )
        # logging.info(similar_score_qa)
        for doc, score in similar_score_qa:
            if score > CONFIG.QA_THRESHOLD:
                response = doc.metadata["answer"]
                docs.append(doc.metadata["source"])
                return response, set(docs)

        logging.info("STEP 2: RetrievalQA.from_chain_type")
        if use_history:
            history_prompt = "\n".join(history_prompt_json)
            input_prompt = self.llm(
                SUMMARIZE_PROMPT_TEMPLATE.format(
                    history=history_prompt, question=input_prompt
                )
            )
        # query = f"## Câu hỏi:\n{input_prompt}"
        result = self.LLM_QA_CHAIN(input_prompt)
        response = result["result"].split("##")[0]
        self.SQL_CACHING_TTL.update(
            input_prompt,
            CONFIG.LLM_MODEL_ID,
            [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), response],
        )
        logging.info(response)

        for doc in result["source_documents"]:
            docs.append(doc.metadata["source"])
        if use_history:
            history_prompt_json.append(prompt_input)
            self.save_json(history_prompt_json, conversation_id=session_id)
        return response, set(docs)
