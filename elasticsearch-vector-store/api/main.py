from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from model import QueryDocument
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # noqa: E402

configure_logging()

app = FastAPI(openapi_url="/api/v1/tasks/openapi.json", docs_url="/api/v1/docs")
FastAPIInstrumentor.instrument_app(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
elastic_client = ElasticVectorClient(
    elastic_endpoint=CONFIG.ELS_ENDPOINT,
    index_name=CONFIG.ELS_INDEXNAME,
    bucket_name=CONFIG.GCP_BUCKET_NAME,
    username=CONFIG.ELS_USERNAME,
    password=CONFIG.ELS_PASSWORD,
    embedding_model=CONFIG.EMBEDDING_MODEL_ID,
)


@app.on_event("startup")
async def startup_event():
    logging.info("SUCCESS INIT RESTFUL API")


@app.get("/heatbeat")
async def heatbeat():
    logging.info("GET HEATBEAT")
    return {"status": True}


@app.get("/ping")
def read_root():
    return {"status": True}


@app.post("/query")
def query(query: QueryDocument):
    result = elastic_client.query_document(query.query, query.topk)
    return result
