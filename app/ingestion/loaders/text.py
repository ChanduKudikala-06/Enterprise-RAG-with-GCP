import logfire

def parse_text(file_path:str):
    #Parses plain text

    with logfire.span("Text Parsing ",filename=file_path):
        try:
            with open(file_path, 'r',encoding='utf-8',errors='ignore') as file:
                text=file.read()
                return text

        except Exception as e:
            logfire.error(f"Text Parse is failed:{e}")
            raise e