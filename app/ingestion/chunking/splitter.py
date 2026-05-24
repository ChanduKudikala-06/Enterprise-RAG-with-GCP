from typing import List
import logfire

def chunk_text(text: str, chunk_size:int=1500) -> List[str]:
    
    #Split the text into specified chunk_size
    
    with logfire.span("Text Chunking",text_length=len(text)):
        
        if not text.strip():#Check text is empty or not
            return []
        
        paragraphs = text.split("\n\n")#Split text into paragraphs
        chunks=[]
        current_chunk=""
        
        for p in paragraphs:
            if len(current_chunk)+ len(p) < chunk_size:
                current_chunk += p +"\n\n"
            #If current chunk is more than chunk_size we will store current chunk in chunk slist
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                #We are storing current paragraph in current chunk
                current_chunk = p+"\n\n"
        #We are adding that current chunk to chunks list
        #So our old text and cuurrent paragraph will be added to chunks
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            
        valid_chunks=[c for c in chunks if c.strip()]
        logfire.info(f"Generated {len(valid_chunks)} chunks")
        return valid_chunks
                    