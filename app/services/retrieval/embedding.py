from vertexai.language_models import TextEmbeddingModel

model=None
BATCH_SIZE=50

def get_embedding_model():
    global model
    
    if model is None:
        model= TextEmbeddingModel.from_pretrained("textembedding-004")
    return model

def embed_query(query:str):
    #Embeds a user-provided query string using the stable Vertex AI API for text embedding
    model=get_embedding_model()
    embedding=model.get_embeddings([query])
    return embedding[0].values

def embed_texts(texts: list[str]):
    #Embeds list of texts in batches
    model=get_embedding_model()
    all_embeddings=[]
    
    #Ex:- i=0 texts=200 batch_size=50
    #batch_texts=texts[0:50]
    #next i=50 batch_texts=texts[50:100] and so on until we process all texts in batches
    for i in range(0,len(texts),BATCH_SIZE):
        batch_texts=texts[i:i+BATCH_SIZE]
        batch_embeddings=model.get_embeddings(batch_texts)
        all_embeddings.extend([e.values for e in batch_embeddings])
        
        
    return all_embeddings
    