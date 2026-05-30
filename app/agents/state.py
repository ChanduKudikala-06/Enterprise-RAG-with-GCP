from typing import List,TypedDict,Annotated

import operator

class AgentState(TypedDict):
    #Using Annotated with operator.add ensures that messages
    #are appended to the history rather than replaced
    #operator is reducer
    messages: Annotated[List[dict],operator.add] #list of messages
    current_query: str #current user query
    documents: List[str] #list of documents by retriever
    plan: str #it is technical/conversational
    status: List[str] #Current Status
    final_answer: str #final answer