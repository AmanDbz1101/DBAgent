"""
This module contains the tools used by the agents to interact with the database.
"""

import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Constants
DB_TABLE_NAME = "Inventory"

# Tool input/output models
class UpsertInput(BaseModel):
    item_name: str = Field(..., description="Name of the inventory item")
    quantity: int = Field(..., description="Quantity of the inventory item")
    description: Optional[str] = Field(None, description="Description of the inventory item")

class DeleteInput(BaseModel):
    item_name: str = Field(..., description="Name of the inventory item to delete")

class InventoryResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result of the operation")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Data returned by the operation")

# Database functions
def extract_inventory_data() -> List[Dict[str, Any]]:
    """
    Fetch all data from the inventory table.
    
    Returns:
        List of inventory items as dictionaries
    """
    response = supabase.table(DB_TABLE_NAME).select("*").execute()
    if response and hasattr(response, 'data'):
        return response.data
    return []

def fetch_all_inventory() -> InventoryResponse:
    """
    Fetch all inventory items from the database.
    
    Returns:
        InventoryResponse with success status, message, and inventory data
    """
    try:
        data = extract_inventory_data()
        return InventoryResponse(
            success=True,
            message=f"Successfully retrieved {len(data)} inventory items",
            data=data
        )
    except Exception as e:
        return InventoryResponse(
            success=False,
            message=f"Error retrieving inventory data: {str(e)}",
            data=None
        )

def upsert_inventory_item(input_data: UpsertInput) -> InventoryResponse:
    """
    Add or update an item in the inventory.
    
    Args:
        input_data: UpsertInput containing item details
        
    Returns:
        InventoryResponse with success status and message
    """
    try:
        item_data = {
            "item_name": input_data.item_name,
            "quantity": input_data.quantity
        }
        
        if input_data.description:
            item_data["description"] = input_data.description
            
        # Check if item exists
        # existing = supabase.table(DB_TABLE_NAME).select("*").eq("item_name", input_data.item_name).execute()
        
        response = supabase.table(DB_TABLE_NAME).upsert(item_data).execute()
        
        # action = "updated" if existing and existing.data else "added"
        
        return InventoryResponse(
            success=True,
            message="Done",
            data=response.data if hasattr(response, 'data') else None
        )
    except Exception as e:
        return InventoryResponse(
            success=False,
            message=f"Error upserting inventory item: {str(e)}",
            data=None
        )

def delete_inventory_item(input_data: DeleteInput) -> InventoryResponse:
    """
    Delete an item from the inventory.
    
    Args:
        input_data: DeleteInput containing item name
        
    Returns:
        InventoryResponse with success status and message
    """
    try:
        # Check if item exists
        existing = supabase.table(DB_TABLE_NAME).select("*").eq("item_name", input_data.item_name).execute()
        
        if not existing or not existing.data:
            return InventoryResponse(
                success=False,
                message=f"Item '{input_data.item_name}' not found in inventory",
                data=None
            )
        
        response = supabase.table(DB_TABLE_NAME).delete().eq("item_name", input_data.item_name).execute()
        
        return InventoryResponse(
            success=True,
            message=f"Successfully deleted item '{input_data.item_name}' from inventory",
            data=response.data if hasattr(response, 'data') else None
        )
    except Exception as e:
        return InventoryResponse(
            success=False,
            message=f"Error deleting inventory item: {str(e)}",
            data=None
        )


