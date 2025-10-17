"""
This module contains the agent state definitions and agent-related functions.
"""

import os
import json
from typing import Dict, List, Any, Optional, TypedDict, Union
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

from prompt import (
    get_task_classifier_prompt,
    get_qa_agent_prompt,
    get_upsert_agent_prompt,
    get_delete_agent_prompt
)
from tools import (
    UpsertInput,
    DeleteInput,
    extract_inventory_data,
    upsert_inventory_item,
    delete_inventory_item,
    # export_inventory_to_csv
)
from graph import TaskClassifier, UpsertState, DeleteState, QAState

# Load environment variables
load_dotenv()

# Initialize LLM
def get_llm(temperature=0):
    """Get a Groq LLM instance."""
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=temperature)

# Agent states
class AgentState(TypedDict):
    """The overall state of the agent workflow."""
    message: str
    inventory_data: List[Dict[str, Any]]
    chat_history: Optional[List[Dict[str, str]]]
    task: Optional[str]
    task_classifier: Optional[TaskClassifier]
    upsert_data: Optional[UpsertState]
    delete_data: Optional[DeleteState]
    qa_response: Optional[QAState]
    final_response: Optional[str]
    error: Optional[str]

# Agent functions
def format_inventory_as_string(inventory_data: List[Dict[str, Any]]) -> str:
    """Format inventory data as a readable string."""
    if not inventory_data:
        return "The inventory is empty."
    
    result = "INVENTORY DATA:\n"
    result += "|Item Name | Quantity | Description |\n"
    # result += "|-----------|---------:|-------------|\n"
    
    for item in inventory_data:
        item_name = item.get("item_name", "N/A")
        quantity = item.get("quantity", 0)
        description = item.get("description", "")
        result += f"{item_name} | {quantity} | {description} |\n"
    
    return result

def initialize_agent_state(message: str) -> AgentState:
    """Initialize the agent state with a user message."""
    inventory_data = extract_inventory_data()
    
    return AgentState(
        message=message,
        inventory_data=inventory_data,
        chat_history=None,  # Will be set by caller
        task=None,
        task_classifier=None,
        upsert_data=None,
        delete_data=None,
        qa_response=None,
        final_response=None,
        error=None
    )

def classify_task(state: AgentState) -> AgentState:
    """Classify the user's message into a task."""
    try:
        # Get formatted prompt
        prompt = get_task_classifier_prompt(state["message"])
        
        # Create LLM
        llm = get_llm()
        
        # Get structured output
        response = llm.with_structured_output(TaskClassifier).invoke(prompt)
        
        # Update state
        state["task_classifier"] = response
        state["task"] = response.task
        
        return state
    except Exception as e:
        state["error"] = f"Error in task classification: {str(e)}"
        return state

def run_qa_agent(state: AgentState) -> AgentState:
    """Run the QA agent to answer the user's question."""
    try:
        # Format inventory data as string
        inventory_str = format_inventory_as_string(state["inventory_data"])
        # Get chat history
        chat_history = state.get("chat_history", [])
        # Get formatted prompt
        prompt = get_qa_agent_prompt(state["message"], inventory_str, chat_history)
        
        # Create LLM
        # llm = get_llm(temperature=0.2)  # Slightly higher temperature for more natural responses
        llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2)
        # Create parser
        parser = StrOutputParser()
        
        # Create chain
        chain = llm | parser
        
        # Invoke chain
        response = chain.invoke(prompt)
        
        # Update state
        state["qa_response"] = QAState(
            output=response,
            inventory_context=inventory_str
        )
        # Set both response fields for compatibility
        state["final_response"] = response
        state["response"] = response
        
        return state
    except Exception as e:
        state["error"] = f"Error in QA agent: {str(e)}"
        state["final_response"] = f"Error in QA agent: {str(e)}"
        state["response"] = f"Error in QA agent: {str(e)}"
        return state

def run_upsert_agent(state: AgentState) -> AgentState:
    """Run the upsert agent to add or update inventory items."""
    try:
        # Format inventory data as string
        inventory_str = format_inventory_as_string(state["inventory_data"])
        # Get chat history
        chat_history = state.get("chat_history", [])
        
        # Get formatted prompt
        prompt = get_upsert_agent_prompt(state["message"], inventory_str, chat_history)
        
        # Create LLM
        llm = get_llm()
        
        # Get structured output
        response = llm.with_structured_output(UpsertState).invoke(prompt)
        
        # Update state
        state["upsert_data"] = response
        
        # Perform upsert
        upsert_result = upsert_inventory_item(UpsertInput(
            item_name=response.item_name,
            quantity=response.quantity,
            description=response.description
        ))
        
        # Update state with result
        if upsert_result.success:
            success_message = f"Successfully added/updated {response.item_name} with quantity {response.quantity}."
            state["final_response"] = success_message
            state["response"] = success_message
        else:
            state["error"] = upsert_result.message
            error_message = f"Error: {upsert_result.message}"
            state["final_response"] = error_message
            state["response"] = error_message
        
        return state
    except Exception as e:
        error_message = f"Error in upsert agent: {str(e)}"
        state["error"] = error_message
        state["final_response"] = error_message
        state["response"] = error_message
        return state

def run_delete_agent(state: AgentState) -> AgentState:
    """Run the delete agent to remove inventory items."""
    try:
        # Format inventory data as string
        inventory_str = format_inventory_as_string(state["inventory_data"])
        # Get chat history
        chat_history = state.get("chat_history", [])
        
        # Get formatted prompt
        prompt = get_delete_agent_prompt(state["message"], inventory_str, chat_history)
        
        # Create LLM
        llm = get_llm()
        
        # Get structured output
        response = llm.with_structured_output(DeleteState).invoke(prompt)
        
        # Update state
        state["delete_data"] = response
        
        # Perform delete
        delete_result = delete_inventory_item(DeleteInput(
            item_name=response.item_name
        ))
        
        # Update state with result
        if delete_result.success:
            success_message = f"Successfully deleted {response.item_name} from inventory."
            state["final_response"] = success_message
            state["response"] = success_message
        else:
            state["error"] = delete_result.message
            error_message = f"Error: {delete_result.message}"
            state["final_response"] = error_message
            state["response"] = error_message
        
        return state
    except Exception as e:
        error_message = f"Error in delete agent: {str(e)}"
        state["error"] = error_message
        state["final_response"] = error_message
        state["response"] = error_message
        return state


        
def handle_error(state: AgentState) -> AgentState:
    """Handle errors in the workflow."""
    # Check if there's already an error message
    if not state.get("error"):
        state["error"] = "I couldn't understand what you want to do. Please try again with a clearer query about fetching, updating, or deleting inventory items."
    
    # Set a user-friendly response in both fields for compatibility
    error_response = f"Sorry, I encountered an issue: {state['error']}. Please try again with a clearer query about inventory management."
    state["final_response"] = error_response
    state["response"] = error_response
    
    return state
