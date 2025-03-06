import json

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticToolsParser, JsonOutputToolsParser, JsonOutputKeyToolsParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from pydantic import BaseModel, Field
from typing import List,Optional, Literal, Set

from reservation_schema import ReservationData

from dotenv import load_dotenv
from icecream import ic
    

def create_extraction_agent():

    load_dotenv()
    
    functions = [ReservationData]

    #llm = ChatOllama(model="qwen2.5", temperature = 0)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature = 0)

    llm_with_functions = llm.bind_tools(functions)

    system_prompt = """You are an expert extraction algorithm. Your mission is to extract
                    the following:
                    - name: name of the person who made the reservation
                    - n_guests: number of guests of the reservation
                    Take into account your input will be a full conversation o part of it,
                    but the context always will be about a reservation
                    Conversation will be in Spanish.
                    Only extract relevant information from the text 
                    If you do not know the value of an attribute asked to extract, 
                    return null for the attribute's value."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
         ("user", "{input}"),
        ])
    
    extraction_chain = prompt | llm_with_functions | JsonOutputKeyToolsParser(key_name="ReservationData")
    
    
    return extraction_chain


def execute_extractor(request:str):
    load_dotenv()
    agent = create_extraction_agent()
    
    result = agent.invoke({"input":request})
    
    ic(result)
    return result

def main():

    while True:
        request = input("Detalla tu reserva: ")
        result = execute_extractor(request)
        print(result)


if __name__ == "__main__":
    main()


