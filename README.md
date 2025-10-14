# Inventory Management System

A complete inventory management system with both CLI and web interfaces, powered by AI agents for natural language interaction.

## Features

- 🤖 **AI-Powered Interface**: Natural language processing for inventory operations
- 📦 **Inventory Management**: Add, update, delete, and query inventory items
- 💬 **Chat Interface**: Web-based chatbot for easy interaction
- 🗃️ **Database Integration**: Supabase backend for reliable data storage
- 📊 **Real-time Updates**: Live inventory display and updates

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file with your credentials:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   GROQ_API_KEY=your_groq_api_key
   ```

3. **Database Setup**
   Make sure your Supabase database has an "Inventory" table with the following schema:
   ```sql
   CREATE TABLE public."Inventory" (
     created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
     item_name TEXT NOT NULL,
     quantity BIGINT NULL,
     description TEXT NULL,
     CONSTRAINT Inventory_pkey PRIMARY KEY (item_name),
     CONSTRAINT Inventory_item_name_key UNIQUE (item_name)
   ) TABLESPACE pg_default;
   ```

## Usage

### Web Interface (Recommended)

1. **Launch the Streamlit App**
   ```bash
   python run_streamlit.py
   ```
   Or directly:
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Access the Web Interface**
   Open your browser and go to `http://localhost:8501`

3. **Interact with the Chatbot**
   - Type natural language queries about your inventory
   - Use the example buttons for quick actions
   - View real-time inventory updates in the sidebar

### Command Line Interface

1. **Run the CLI Version**
   ```bash
   python main.py
   ```

2. **Use Natural Language Commands**
   - "Show me all laptops in stock"
   - "Add 5 new monitors to inventory"
   - "Delete keyboards from the system"
   - "How many items do we have?"

## Example Queries

### Fetching Information
- "How many laptops do we have?"
- "Show me all items in the inventory"
- "What's the total quantity of monitors?"
- "List all items with more than 10 in stock"

### Adding/Updating Items
- "Add 20 laptops to the inventory"
- "Update the mouse quantity to 15"
- "Create a new item called 'Headphones' with 25 in stock and description 'Wireless Bluetooth'"

### Deleting Items
- "Remove laptops from inventory"
- "Delete the item called 'old-keyboard'"
- "Remove sample items from the database"

## Web Interface Features

### Chat Interface
- 💬 **Real-time Chat**: Interactive conversation with the AI assistant
- 📝 **Chat History**: View previous interactions
- 🎯 **Example Queries**: Quick action buttons for common tasks
- ⚡ **Auto-refresh**: Real-time updates after operations

### Inventory Dashboard
- 📋 **Live Inventory Table**: Real-time view of all items
- 📊 **Statistics**: Total items and quantities
- 🔄 **Refresh Button**: Manual refresh option
- 📥 **CSV Export**: Download inventory data

### User Experience
- 🎨 **Clean UI**: Modern, responsive design
- ✅ **Status Indicators**: Clear success/error messaging
- 🔄 **Loading States**: Visual feedback during processing
- 📱 **Responsive**: Works on desktop and mobile

## Technical Architecture

### Components
- **Agent System**: AI-powered task classification and execution
- **Workflow Graph**: LangGraph-based state management
- **Database Layer**: Supabase integration with type safety
- **UI Layer**: Streamlit web interface with real-time updates

### AI Agents
1. **Task Classifier**: Determines user intent (fetch/upsert/delete)
2. **QA Agent**: Handles information retrieval queries
3. **Upsert Agent**: Manages adding/updating inventory items
4. **Delete Agent**: Handles item removal requests

## File Structure

```
DBAgent/
├── agent.py           # Core agent logic and state management
├── graph.py           # Workflow graph definition
├── tools.py           # Database interaction tools
├── prompt.py          # AI prompt templates
├── main.py            # CLI interface
├── streamlit_app.py   # Web interface
├── run_streamlit.py   # Streamlit launcher
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check that you're in the correct directory

2. **Database Connection Issues**
   - Verify your `.env` file has correct Supabase credentials
   - Check that your Supabase project is active
   - Ensure the "Inventory" table exists with correct schema

3. **API Key Issues**
   - Verify your GROQ_API_KEY is valid and active
   - Check for any rate limits or quota issues

4. **Streamlit Issues**
   - Try clearing browser cache
   - Restart the Streamlit server
   - Check terminal for error messages

### Getting Help

If you encounter issues:
1. Check the terminal output for error messages
2. Verify your environment variables are set correctly
3. Test the database connection independently
4. Check the Streamlit logs in the terminal

## Development

To extend or modify the system:
1. **Adding New Operations**: Extend the agent classes and update the workflow graph
2. **UI Modifications**: Edit `streamlit_app.py` for interface changes
3. **Database Changes**: Update the tools.py file and database schema
4. **Prompt Engineering**: Modify prompts in `prompt.py` for better AI responses

## License

This project is for educational and development purposes.
