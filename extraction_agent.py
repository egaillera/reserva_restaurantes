import json

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticToolsParser, JsonOutputToolsParser, JsonOutputKeyToolsParser
from langchain_ollama import ChatOllama


from pydantic import BaseModel, Field
from typing import List,Optional, Literal, Set

from dotenv import load_dotenv


class Reservation(BaseModel):
    """Information about a resevation, including its main features"""
    name: str = Field(description="name of the person who made the reservation")
    phone: str = Field(description="phone number of the person who made the reservation")
    n_guests: int = Field(description="number of guests of the reservation")
    date: str = Field(description="date of the reservation")
    time: str = Field(description="time of the reservation")
    

def create_extraction_agent():

    load_dotenv()
    
    functions = [Reservation]

    llm = ChatOllama(model="llama3.1:8b", temperature = 0)

    llm_with_functions = llm.bind_tools(functions)

    system_prompt = "You are an expert extraction algorithm. \
                    Only extract relevant information from the text \
                    If you do not know the value of an attribute asked to extract, \
                    return null for the attribute's value."

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
         ("user", "{input}"),
        ])
    
    extraction_chain = prompt | llm_with_functions | JsonOutputKeyToolsParser(key_name="Reservation")
    
    return extraction_chain

def execute_extractor(request:str):
    load_dotenv()
    agent = create_extraction_agent()
    
    result = agent.invoke({"input":request})

    return result

def main():

    while True:
        request = input("Detalla tu reserva: ")
        result = execute_extractor(request)
        print(result)


if __name__ == "__main__":
    main()


