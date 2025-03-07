from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
from icecream import ic
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate

from extraction_agent import execute_extractor
from reservation_schema import * 

class State(TypedDict):
    messages: Annotated[list, add_messages]
    asking: bool
    reservation_data: ReservationData

    def __init__(self,asking=False):
        self.asking = asking




def router_node(state: State):
    """
    Router node that will extract the data from the user input and store it in the state,
    if we are not in the asking mode. If we are in the asking mode, we will wait for the user
    to answer the previous question. 

    Args:
        state (State): State of the conversation
    """
    print("router_node")
    ic(state)

    # Initialize reservation_data_status with an empty class if it doesn't exist
    reservation_data_status = state.get("reservation_data", ReservationData())
    ic(reservation_data_status)

    # If we are not in the asking mode, extract data from the user's message
    if not state["asking"]:
        extracted_data = execute_extractor(state["messages"][-1].content)
        ic(extracted_data)

        # Fill the new reservation_data with the extracted data
        if extracted_data:
            assign_if_default(reservation_data_status,extracted_data[0])
            ic(reservation_data_status)

            #for key, value in extracted_data[0].items():
                # TODO: Validate each attribute (e.g., name format, phone number length)
                #ic(key)
                #ic(value)
                #setattr(reservation_data_status, key, value)
                #ic(reservation_data_status)

        # Check if all fields are filled and proceed accordingly
        if all_fields_filled(reservation_data_status):
            return {
                "reservation_data": reservation_data_status,
                "messages": [AIMessage(content="Reserva realizada con éxito")]
            }
    
    # Return the updated state
    return {"reservation_data": reservation_data_status}

def ask_question(state:State):
    print("ask_question")
    ic(state)

    # Find the first field of the reservation_data that is not filled
    field_to_fill_description = first_field_not_filled(state["reservation_data"])
    ic(field_to_fill_description)

    # Call a model to find the right question to ask to the user to fill the field
    system_prompt = """You have to generate a question to ask a user for a specific item regarding to a reservation
                    You will receive the the descriptiom of the item and you have to genearte the question.
                    Be very polite and clear in your question: start with terms like "Por favor" or "Podría decirme" or "Disculpe"
                    JUST generate the question, nothing else
                    Question MUST be in Spanish."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
         ("user", "{item}"),
        ])
    
    chain = prompt | llm
    result = chain.invoke({"item":field_to_fill_description})
    ic(result.content)
    
    return {"messages":[AIMessage(content=result.content)],"asking":True}

def check_data(state:State):
    print("check_data")
    ic(state)
    #TODO: is better to add another node (Confirmation node) to confirm the reservation, once
    # all the data is filled
    if state["asking"] or all_fields_filled(state["reservation_data"]) == True:
        return END     
    else:
        return "ask_question"
    
ic.disable()

memory = MemorySaver()

llm = ChatOllama(model="llama3.1:8b", temperature = 0.7)

graph_builder = StateGraph(State)
graph_builder.add_node("router", router_node)
graph_builder.add_node("ask_question", ask_question)

graph_builder.add_edge(START, "router")
graph_builder.add_conditional_edges("router", check_data)
graph_builder.add_edge("ask_question", "router")

graph = graph_builder.compile(checkpointer=memory)

config = {"configurable":{"thread_id": 1}}

with open("graph.png","wb") as file:
     #file.write(graph.get_graph().draw_mermaid_png())
     file.close()

while True:
    user_input = input("User: ")
    print("graph_invoke")
    state = graph.invoke({"messages": [user_input], "asking":False},
             config,
             stream_mode="values")
    ic(state)
    print("Assistant: ",state["messages"][-1].content)

    


