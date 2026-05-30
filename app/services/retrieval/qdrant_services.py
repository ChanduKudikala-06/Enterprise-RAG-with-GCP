import logfire
from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import settings
from app.services.retrieval.embedding import get_embedding_model,embed_query,embed_texts

#Qdrant Client
client=QdrantClient(
    url=settings.QDRANT_HOST,
    api_key=settings.QDRANT_API_KEY
)

#Enterprise retrieveal with top 8 chunks
def search_enterprise_knowledge(query: str,limit: int=8):
    
    #query_points is the modern standard to fetch data from qdrant
    
    try:
        query_vector=embed_query(query)
        
        response=client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=query_vector,
            limit=limit,
            with_payload=True #It will stored metadata has JSON
        )
        
        
        results=[]
        for res in response.points:
            results.append(
                {
                    "content":res.payload.get("text",""),#return text content otherwise it will return as blank
                    "source":res.payload.get("source","Unknown"),
                    "score":res.score
                }
            )
        
    except Exception as e:
        logfire.error(f"Qudrant Search is failed {e}")
    