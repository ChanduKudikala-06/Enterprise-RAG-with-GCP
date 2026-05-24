import os
from dotenv import load_dotenv

#load environment variables from .env file
load_dotenv()

class Settings:

    #GCP COnfiguration

    GCP_PROJECT_ID=os.getenv("PROJECT_ID", "enterprise-rag06")
    LOCATION=os.getenv("LOCATION","us-central1")
    GCP_DOC_AI_LOCATION=os.getenv("GCP_DOC_AI_LOCATION","us")
    GCP_DOC_AI_PROCESSOR_ID=os.getenv("GCP_DOC_AI_PROCESSOR_ID","4b86620d867baedd")
    GCP_RAW_BUCKET=os.getenv("GCP_RAW_BUCKET","dmtxpress-rag-raw")
    GCP_PROCESSED_BUCKET=os.getenv("GCP_PROCESSED_BUCKET","dmtxpress-rag-processed")
    VPC_CONNECTOR=os.getenv("VPC_CONNECTOR","default")


    #Vecto DB (QDRANT)
    QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")
    QDRANT_HOST=os.getenv("QDRANT_HOST")
    QDRANT_COLLECTION=os.getenv("QDRANT_COLLECTION")

    #REASONING ENGINE (GROQ)
    GROQ_API_KEY=os.getenv("GROQ_API_KEY")
    GROQ_MODEL="llama-3.3-70b-versatile"



    #OBSERVABILITY

    LANGSMITH_TRACING=os.getenv("LANGSMITH_TRACING","true")
    LANGSMITH_API_KEY=os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT=os.getenv("LANGSMITH_PROJECT","enterprise-rag06")
    LANGSMITH_ENDPOINT=os.getenv("LANGSMITH_ENDPOINT","https://api.smith.langchain.com")


    #Apply Langchain environment variables for automatic tracing
    os.environ["LANGSMITH_TRACING"] = LANGSMITH_TRACING
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT
    os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT

settings = Settings()