from bs4 import BeautifulSoup
import logfire

def parse_html(file_path:str):
    #Parses HTML files

    with logfire.span("HTML Parsing",filename=file_path):

        try:
            with open(file_path,"r",encoding='utf-8',errors='ignore') as file:
                content=file.read()

            Soup=BeautifulSoup(content,'html.parser')

            #Removing tags
            for script in Soup(["script", "style", "meta", "noscript"]):
                script.decompose()

             # 2. Extract Text
            text = Soup.get_text(separator="\n")
            
            # 3. Clean Whitespace (Collapse multiple newlines)
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_clean = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text_clean
        except Exception as e:
            logfire.error(f"HTML Parse is failed:{e}")
            raise e
