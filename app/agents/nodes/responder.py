import logfire
from app.agents.state import AgentState
from app.config import settings
from langchain_groq import ChatGroq


llm=ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model=settings.GROQ_MODEL,
    temperature=0.1
)

def generate_node(state:AgentState):
    """
    Synthesizes a response using both Documentation Context AND Conversation History.
    """
    query=state['current_query']
    history_str=""
    
    for msg in state['messages'][::-1]:
        role="User" if msg['role']=="user" else "Assistant"
        history_str+=f"{role}:{msg['content']}\n"
        
    user_msg = state["messages"][-1]["content"] if state["messages"] else ""
    
    if query=="CONVERSATIONAL":
        logfire.info("Generating conversational response with history")
        prompt=f"""You are a friendly and helpful Enterprise AI Assistant.
        Answer the user's latest message using the CONVERSATION HISTORY below.
        
        
        Conversation History:
        {history_str}
        
        Latest Message:
        {user_msg}
        """
    
    #Technical RAG with context limit(Token Safety)
    else:
        logfire.info("Generating technical RAG response")
        max_context_chars=25000
        full_context=""
        
        for doc in state['documents']:
            if full_context+len(doc)<max_context_chars:
                full_context+=doc+ "\n\n"
            else:
                logfire.warning("Token Limit exceed according to GROQ limits")
                break
            
        prompt=f"""
            You are a Senior Technical Architect. 
            Answer the question using the TECHNICAL CONTEXT provided. 
           
            Technical Context:
            {full_context}
             
           Conversation History:
           {history_str}
           
           User Message:
           {user_msg}   
           """
           
    with logfire.span("LLM Synthesis is completed"):
        
        try:
            
            response=llm.invoke(prompt)
            
            logfire.info("Response synthesized successfully.")
            
            return{
                "final_answer":response.content,
                "status": "Response Generated",
                "messages":[{"role":"Assistant"},{"content":response.content}]
                
            }
        except Exception as e:
            logfire.warning("LLM Generation failed {e}")
            raise e
            

    
    