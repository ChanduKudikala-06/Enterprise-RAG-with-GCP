import os
import sys
import uuid
import json
import logfire
import vertexai

from typing import List
from google.cloud import storage
from qdrant_client import QdrantClient
from qdrant_client.http import models

#Import local modules

from app.config import settings
from app.services.retrieval.embedding import embed_texts
from app.ingestion.chunking.splitter import chunk_text
from app.ingestion.loaders.pdf import parse_pdf
from app.ingestion.loaders.text import parse_text
from app.ingestion.loaders.office import parse_office
from app.ingestion.loaders.html import parse_html

#Initalize Logfire with the Enterprise-ingestion service
logfire.configure(service_name="Enterprise-Ingestion")

#Initalize Vertex AI for embeddings
vertexai.init(project=settings.GCP_PROJECT_ID,location=settings.LOCATION)

#GCS Client
storage_client=storage.Client(project=settings.GCP_PROJECT_ID)

#Initialize Qdrant Client

qdrant_client=QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY
)

def upload_to_gcs(data,bucket_name:str,destination_blob_name:str,is_json:bool=False):
    
    #Uploads a file or JSON data to GCS
    with logfire.span("GCS Upload",bucket=bucket_name,blob=destination_blob_name):
        
        try:
            #Uploads data to Google Cloud Storage (GCS) bucket
            bucket=storage_client.bucket(bucket_name)
            blob=bucket.blob(destination_blob_name)#name of file inside the bucket
            if is_json:
                blob.upload_from_string(json.dumps(data),content_type="application/json")
                #data means filename 
            else:
                blob.upload_from_filename(data)#This method is used to upload a file from local to GCS
            logfire.info("Uploaded to bucket {bucket_name}") 
        except Exception as e:
            logfire.error(f"Error occurred while uploading to GCS: {e}")
            raise e
        
def process_file(file_path:str,filename:str,source_type:str,skip_raw_upload: bool = False):
    """
        Orchestrates the parsing, chunking, embedding, and indexing of a single file.
        
        Args:
            file_path: Local path to the file
            filename: Original name of the file
            source_type: 'true', 'noisy', etc.
            skip_raw_upload: Set to True if the file is ALREADY in GCS (prevents infinite loops)
    """
    with logfire.span("Processing file ",file=filename,source=source_type):
        
        try:
            #Upload Raw files to GCS
            #source_type->folder name
            raw_gcs_path=f"{source_type}/{filename}" #file name inside the bucket
            #filepath,bucketname from settings,gcs path
            upload_to_gcs(file_path,settings.RAW_BUCKET_NAME,raw_gcs_path)
            
            #Extract text based on extension
            #a.pdf->[a,pdf]->-1 pdf
            ext=filename.lower().split('.')[-1]
            
            if ext == 'pdf':
                full_text=parse_pdf(file_path)
            elif ext in ['html','htm']:
                full_text=parse_html(file_path)
                
            elif ext == 'txt':
                full_text=parse_text(file_path)
            elif ext in ['docx','pptx']:
                full_text=parse_office(file_path)
            else:
                logfire.warning(f"Unsupported file type: {ext}  for file {filename}")
                return
            
            if not full_text or not full_text.strip():
                logfire.warning(f"No text extracted from file {filename}")
                return
            
            #Chunk Text
            chunks=chunk_text(full_text)
            
            if not chunks:
                return
            
            #Upload Processed data to GCS
            processed_data={"file_name":filename,"chunks":chunks,"source_type":source_type} #Forming proceesed data as json
            processed_gcs_path=f"{source_type}/{filename}.json"
            upload_to_gcs(processed_data, settings.PROCESSED_BUCKET_NAME, processed_gcs_path, is_json=True)
            
            
        except Exception as e:
            logfire.error(f"Error processing file {filename}: {e}")
            raise e      
            


def run_universal_ingestion(base_dir: str, explicit_source_type: str = None, wipe: bool = False):
    """
    Automatically scans the directory for CLI usage.
    """
    with logfire.span("🌍 Universal Ingestion Started", base_directory=base_dir):
        # Ensure Collection Exists
        if not qdrant_client.collection_exists(settings.QDRANT_COLLECTION):
            qdrant_client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
            )
        
        # Scan for subfolders
        subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        
        if not subdirs:
            source_type = explicit_source_type or "general"
            process_directory(base_dir, source_type)
        else:
            for subdir in subdirs:
                source_type = "true" if "true" in subdir.lower() else "noisy" if "noisy" in subdir.lower() else subdir
                dir_path = os.path.join(base_dir, subdir)
                process_directory(dir_path, source_type)

def process_directory(dir_path: str, source_type: str):
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    for filename in files:
        file_path = os.path.join(dir_path, filename)
        # For CLI usage, we DO want to upload the local file to GCS
        process_file(file_path, filename, source_type, skip_raw_upload=False)
        
    
    
    
    