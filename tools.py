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

def get_table_name() -> str:
    """Get the appropriate table name based on user type."""
    try:
        # Import here to avoid circular imports
        from auth import get_user_table_name
        return get_user_table_name()
    except ImportError:
        # Fallback to default table if auth module not available
        return DB_TABLE_NAME

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
    table_name = get_table_name()
    response = supabase.table(table_name).select("*").execute()
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
    Add or update an inventory item in the database.
    
    Args:
        input_data: UpsertInput containing item details
        
    Returns:
        InventoryResponse with success status and message
    """
    try:
        table_name = get_table_name()
        
        # Prepare item data
        item_data = {
            "item_name": input_data.item_name,
            "quantity": input_data.quantity,
            "description": input_data.description
        }
        
        # Check if item exists (commented out for now - upsert handles this)
        # existing = supabase.table(table_name).select("*").eq("item_name", input_data.item_name).execute()
        
        response = supabase.table(table_name).upsert(item_data).execute()
        
        if response and hasattr(response, 'data') and response.data:
            return InventoryResponse(
                success=True,
                message=f"Successfully upserted item '{input_data.item_name}' with quantity {input_data.quantity}",
                data=response.data
            )
        else:
            return InventoryResponse(
                success=False,
                message="Failed to upsert item - no data returned",
                data=[]
            )
    except Exception as e:
        return InventoryResponse(
            success=False,
            message=f"Error upserting item: {str(e)}",
            data=[]
        )

def delete_inventory_item(input_data: DeleteInput) -> InventoryResponse:
    """
    Delete an inventory item from the database.
    
    Args:
        input_data: DeleteInput containing item name to delete
        
    Returns:
        InventoryResponse with success status and message
    """
    try:
        table_name = get_table_name()
        
        # Check if item exists first
        existing = supabase.table(table_name).select("*").eq("item_name", input_data.item_name).execute()
        
        if not existing.data:
            return InventoryResponse(
                success=False,
                message=f"Item '{input_data.item_name}' not found in inventory",
                data=[]
            )
        
        response = supabase.table(table_name).delete().eq("item_name", input_data.item_name).execute()
        
        if response:
            return InventoryResponse(
                success=True,
                message=f"Successfully deleted item '{input_data.item_name}' from inventory",
                data=[]
            )
        else:
            return InventoryResponse(
                success=False,
                message=f"Failed to delete item '{input_data.item_name}'",
                data=[]
            )
    except Exception as e:
        return InventoryResponse(
            success=False,
            message=f"Error deleting item: {str(e)}",
            data=[]
        )


