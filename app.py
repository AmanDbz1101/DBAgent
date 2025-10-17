"""
Streamlit UI for the Inventory Management System.
Provides a chat interface for interacting with the inventory database.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

# Import your existing modules
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

# Page configuration
st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your inventory management assistant. You can ask me to show items, add new items, update quantities, or delete items from your inventory. How can I help you today?"}
        ]
    
    if "workflow" not in st.session_state:
        # Build workflow graph once and store in session state
        st.session_state.workflow = build_workflow_graph(
            classify_task_fn=classify_task,
            run_qa_agent_fn=run_qa_agent,
            run_upsert_agent_fn=run_upsert_agent,
            run_delete_agent_fn=run_delete_agent,
            handle_error_fn=handle_error
        )

def get_chat_history(limit: int = 5) -> List[Dict[str, str]]:
    """Get the last few chat interactions for context."""
    try:
        if "workflow" not in st.session_state:
            return []
        
        config = {"configurable": {"thread_id": "main"}}
        # Get state history from the workflow
        history = st.session_state.workflow.get_state_history(config, limit=limit)
        
        chat_history = []
        for state_snapshot in history:
            if state_snapshot.values and "message" in state_snapshot.values:
                user_message = state_snapshot.values["message"]
                response = state_snapshot.values.get("final_response") or state_snapshot.values.get("response", "")
                
                if user_message and response:
                    chat_history.append({
                        "user": user_message,
                        "assistant": response
                    })
        
        # Return in chronological order (oldest first)
        return list(reversed(chat_history))
    except Exception as e:
        # If there's an error getting history, return empty list
        return []

def get_inventory_dataframe():
    """Get inventory data as a pandas DataFrame."""
    try:
        inventory_data = extract_inventory_data()
        if inventory_data:
            df = pd.DataFrame(inventory_data)
            # Reorder columns for better display
            column_order = ['item_name', 'quantity', 'description']
            existing_columns = [col for col in column_order if col in df.columns]
            other_columns = [col for col in df.columns if col not in column_order]
            df = df[existing_columns + other_columns]
            return df
        else:
            return pd.DataFrame(columns=['item_name', 'quantity', 'description'])
    except Exception as e:
        st.error(f"Error loading inventory data: {str(e)}")
        return pd.DataFrame(columns=['item_name', 'quantity', 'description'])

def process_user_message(user_input: str) -> Dict[str, Any]:
    """Process user message through the workflow and return the result."""
    try:
        # Get chat history for context
        chat_history = get_chat_history(limit=5)
        
        # Initialize agent state
        state = initialize_agent_state(user_input)
        # Add chat history to state
        state["chat_history"] = chat_history
        
        # Run the workflow
        config = {"configurable": {"thread_id": "main"}}
        result = st.session_state.workflow.invoke(state, config=config)

        return result
    except Exception as e:
        return {
            "error": str(e),
            "final_response": f"Sorry, I encountered an error: {str(e)}",
            "response": f"Sorry, I encountered an error: {str(e)}"
        }

def main():
    """Main Streamlit application."""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("📦 Inventory Management System")
    st.markdown("Ask me anything about your inventory! I can help you view, add, update, or delete items.")
    
    # Sidebar for inventory display
    with st.sidebar:
        st.header("� Current Inventory")
        
        # Refresh button
        if st.button("🔄 Refresh Inventory"):
            st.rerun()
        
        # Display inventory table
        try:
            df = get_inventory_dataframe()
            
            if not df.empty:
                # Display summary
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Items", len(df))
                with col2:
                    if 'quantity' in df.columns:
                        total_quantity = df['quantity'].sum() if df['quantity'].dtype in ['int64', 'float64'] else 0
                        st.metric("Total Qty", total_quantity)
                
                # Display table
                st.dataframe(
                    df,
                    width='stretch',
                    hide_index=True
                )
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    width='stretch'
                )
            else:
                st.info("📦 No items in inventory")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
        
        # Chat controls
        st.markdown("---")
        st.subheader("💬 Chat Controls")
        
        if st.session_state.messages:
            st.write(f"Messages: {len(st.session_state.messages)}")
            if st.button("🗑️ Clear Chat", width='stretch'):
                st.session_state.messages = [
                    {"role": "assistant", "content": "Hello! I'm your inventory management assistant. How can I help you today?"}
                ]
                st.rerun()
        
    
    # Main chat interface
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message about inventory..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Processing your request..."):
                # Process the message
                result = process_user_message(prompt)
                
                # Get response
                response = result.get("final_response") or result.get("response")
                
                if response:
                    st.markdown(response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    error_msg = "Sorry, I couldn't generate a response. Please try again."
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()