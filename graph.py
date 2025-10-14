"""
This module contains the workflow graph definition for the inventory management system.
"""

from langgraph.graph import StateGraph, END, START
from typing import Any, Dict, Optional, List, Callable, Literal, Union, TypedDict, Annotated
from typing_extensions import NotRequired
from langchain_groq import ChatGroq


from pydantic import BaseModel, Field
from langchain.schema import SystemMessage, HumanMessage

# Model definitions
class TaskClassifier(BaseModel):
    task: Literal["fetch", "upsert", "delete"] = Field(
        ..., description="Predicted task: one of 'fetch', 'upsert', or 'delete'"
    )
    confidence: Optional[float] = Field(None, description="Confidence score for the classification (0-1)")
    reasoning: Optional[str] = Field(None, description="Reasoning behind the classification decision")

class QAState(BaseModel):
    output: str = Field(..., description="LLM output response")
    inventory_context: Optional[str] = Field(None, description="Inventory data used for generating the response")
    query_type: Optional[str] = Field(None, description="Type of query (count, specific item, all items, etc.)")

class UpsertState(BaseModel):
    item_name: str = Field(..., description="Name of the inventory item")
    quantity: int = Field(..., description="Quantity of the inventory item")
    description: Optional[str] = Field(None, description="Description of the inventory item")
    
# class UpsertState(BaseModel):
#     items: List[UpsertItem] = Field(..., description="List of items to add or update")
#     operation_type: Optional[str] = Field("upsert", description="Operation type: 'insert' for new items, 'update' for existing items, or 'upsert' for either")

class DeleteState(BaseModel):
    item_name: str = Field(..., description="Name of the inventory item to delete")
    confirm: bool = Field(True, description="Confirmation to proceed with deletion")

# Define the state schema for the workflow
class WorkflowState(TypedDict):
    """The schema for the workflow state."""
    message: str
    inventory_data: List[Dict[str, Any]]
    task: NotRequired[Optional[str]]
    task_classifier: NotRequired[Optional[TaskClassifier]]
    upsert_data: NotRequired[Optional[UpsertState]]
    delete_data: NotRequired[Optional[DeleteState]]
    qa_response: NotRequired[Optional[QAState]]
    final_response: NotRequired[Optional[str]]
    response: NotRequired[Optional[str]]  # Added for compatibility
    error: NotRequired[Optional[str]]

# Graph functions
def task_router(state: Dict[str, Any]) -> str:
    """
    Route to the appropriate agent based on the task.
    
    Args:
        state: Agent state dictionary
        
    Returns:
        Name of the next node
    """
    task = state.get("task")
    
    if not task:
        return "handle_error"
    
    if task == "fetch":
        return "run_qa_agent"
    elif task == "upsert":
        return "run_upsert_agent"
    elif task == "delete":
        return "run_delete_agent"
    else:
        return "handle_error"

def handle_error_fn(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle error cases where task classification fails or returns an unrecognized task.
    
    Args:
        state: Agent state dictionary
        
    Returns:
        Updated state dictionary with error response
    """
    error_message = "I'm sorry, I couldn't understand what you want to do. Please try again with a clearer query about fetching, updating, or deleting inventory items."
    return {
        **state,
        "response": error_message,
        "final_response": error_message,  # Set both response and final_response
        "error": "Unrecognized task or query"
    }

def build_workflow_graph(
    classify_task_fn, 
    run_qa_agent_fn, 
    run_upsert_agent_fn, 
    run_delete_agent_fn,
    handle_error_fn=None
):
    """
    Build the workflow graph for the inventory management system.
    
    Args:
        classify_task_fn: Function to classify the task
        run_qa_agent_fn: Function to run the QA agent
        run_upsert_agent_fn: Function to run the upsert agent
        run_delete_agent_fn: Function to run the delete agent
        handle_error_fn: Function to handle errors (optional)
        
    Returns:
        Compiled StateGraph instance
    """
    # Create the graph with proper state schema
    workflow = StateGraph(name="inventory_agent", state_schema=WorkflowState)
    
    # Add nodes for main workflow
    workflow.add_node("classify_task", classify_task_fn)
    workflow.add_node("run_qa_agent", run_qa_agent_fn)
    workflow.add_node("run_upsert_agent", run_upsert_agent_fn)
    workflow.add_node("run_delete_agent", run_delete_agent_fn)
    
    # Add error handling node
    if handle_error_fn:
        workflow.add_node("handle_error", handle_error_fn)
    else:
        # If no custom error handler provided, use default
        workflow.add_node("handle_error", lambda state: {
            **state,
            "error": state.get("error", "Unknown error occurred"),
            "final_response": "Sorry, I couldn't process your request. Please try again with a clearer query.",
            "response": "Sorry, I couldn't process your request. Please try again with a clearer query."
        })
    
    # Add edges
    workflow.add_edge(START, "classify_task")
    
    workflow.add_conditional_edges(
        "classify_task",
        task_router,
        {
            "run_qa_agent": "run_qa_agent",
            "run_upsert_agent": "run_upsert_agent",
            "run_delete_agent": "run_delete_agent",
            "handle_error": "handle_error"
        }
    )
    
    # Connect agents directly to END
    workflow.add_edge("run_qa_agent", END)
    workflow.add_edge("run_upsert_agent", END)
    workflow.add_edge("run_delete_agent", END)
    workflow.add_edge("handle_error", END)
    
    # Compile the graph
    return workflow.compile()