import io
import logfire
from pypdf import PdfReader,PdfWriter
from google.cloud import documentai
from app.config import settings

client=documentai.DocumentProcessorServiceClient()
MAX_PAGES_PER_REQUEST=15#By default google document ai accepts only 15pages pdf per request, so we need to split our large pdfs

def parse_pdf(file_path:str):
    #parses PDF files using Google Document AI

    with logfire.span("PDFPARSING",filename=file_path):
        try:
                #Reading PDF and getting total pages
                reader=PdfReader(file_path)
                total_pages=len(reader.pages)
                logfire.info(f"Total pages in PDF:{total_pages}")

                name=client.processor_path(
                    settings.GCP_PROJECT_ID,
                    settings.GCP_DOC_AI_LOCATION,
                    settings.GCP_DOC_AI_PROCESSOR_ID
                )

                
                full_text=""
                #If size is less than 15 pages process directly else split into chunks

                if total_pages<=MAX_PAGES_PER_REQUEST:
                    with open(file_path,"rb") as f:
                        image_content=f.read()
                    full_text=process_document_chunk(image_content,name)
                else:
                    logfire.info(f"PDF has more than {MAX_PAGES_PER_REQUEST} pages splitting into chunks")
                    
                    for i in range(0,total_pages,MAX_PAGES_PER_REQUEST):
                        pdf_writer=PdfWriter()
                        chunk_end=min(i+MAX_PAGES_PER_REQUEST,total_pages)
                        for page_num in range(i,chunk_end):
                            pdf_writer.add_page(reader.pages[page_num])
                        
                        #Write chunks to bytes
                        with io.BytesIO() as bytes_stream:
                            pdf_writer.write(bytes_stream)
                            chunk_bytes=bytes_stream.getvalue()
                        with logfire.span(f"Processing pages {i+1} to {chunk_end}"):
                            chunk_text=process_document_chunk(chunk_bytes, name)
                            full_text+=chunk_text + "\n" #Adding newnline after each chunk
                            
                        if not full_text.strip():#if full text is empty after processing
                            logfire.warning(f"No Text in Document")
                        else:
                            logfire.info(f"Document AI is fully parsed and text is extracted")
                    
                #Helper function to process document by google cloud docuemnt ai
                def process_document_chunk(image_content:bytes,name:str) ->str:
                    raw_document=documentai.RawDocument(
                          content=image_content,
                          mime_type="application/pdf"
                          )
                    request=documentai.ProcessRequest(
                         name=name,
                         raw_document=raw_document
                    )

                    result=client.process_document(request=request)

                    return result.document.text
        

        #Split the PDF into chunks of 15 pages
        except Exception as e:
            logfire.error(f"PDF Parsing failed: {e}")
            raise e
        
