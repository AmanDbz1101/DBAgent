"""
Main entry point for the inventory management system.
"""

import os
import argparse
from colorama import Fore, Style, init
from dotenv import load_dotenv

from agent import (
    initialize_agent_state,
    classify_task,
    run_qa_agent,
    run_upsert_agent,
    run_delete_agent,
    handle_error
)
from graph import build_workflow_graph
from tools import extract_inventory_data

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

def print_header():
    """Print the application header."""
    header = """
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║             INVENTORY MANAGEMENT SYSTEM           ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """
    print(Fore.CYAN + header)

def print_help():
    """Print help information."""
    help_text = """
    Commands:
    ---------
    - Type your question or command about inventory
    - Examples:
        "How many laptops do we have?"
        "Add 5 new monitors to the inventory"
        "Delete HDMI cables from inventory"
    - Type 'exit', 'quit', or 'q' to exit
    - Type 'help' to see this help information
    """
    print(Fore.YELLOW + help_text)

def print_inventory():
    """Print the current inventory."""
    inventory = extract_inventory_data()
    
    if not inventory:
        print(Fore.YELLOW + "\nInventory is empty.")
        return
    
    print(Fore.YELLOW + f"\nCurrent Inventory ({len(inventory)} items):")
    print(Fore.YELLOW + "-" * 80)
    print(Fore.YELLOW + f"{'ID':<5} {'Item Name':<20} {'Quantity':<10} {'Description':<40}")
    print(Fore.YELLOW + "-" * 80)
    
    for item in inventory:
        item_id = item.get("id", "N/A")
        item_name = item.get("item_name", "N/A")
        quantity = item.get("quantity", 0)
        description = item.get("description", "")
        print(Fore.WHITE + f"{item_id:<5} {item_name:<20} {quantity:<10} {description:<40}")
    
    print(Fore.YELLOW + "-" * 80)

def main():
    """Main function."""
    # Print header
    print_header()
    
    # Print help
    print_help()
    
    # Build workflow graph
    workflow = build_workflow_graph(
        classify_task_fn=classify_task,
        run_qa_agent_fn=run_qa_agent,
        run_upsert_agent_fn=run_upsert_agent,
        run_delete_agent_fn=run_delete_agent,
        handle_error_fn=handle_error
    )
    
    # Main loop
    while True:
        # Print current inventory
        print_inventory()
        
        # Get user input
        user_input = input(Fore.GREEN + "\n> ")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "q"]:
            print(Fore.CYAN + "Goodbye!")
            break
        
        # Check for help command
        if user_input.lower() == "help":
            print_help()
            continue
        
        # Process the user input
        print(Fore.CYAN + "Processing...")
        
        try:
            # Initialize agent state
            state = initialize_agent_state(user_input)
            
            # Run the workflow
            result = workflow.invoke(state)
            
            # Print the result
            if result.get("error"):
                print(Fore.RED + f"Error: {result['error']}")
            
            # Get the response from either final_response or response field
            response = result.get("final_response") or result.get("response")
            if response:
                print(Fore.GREEN + f"Response: {response}")
            else:
                print(Fore.YELLOW + "No response was generated.")
        except Exception as e:
            print(Fore.RED + f"Error processing request: {str(e)}")

if __name__ == "__main__":
    main()