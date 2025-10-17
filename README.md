# DBAgent - AI-Powered Inventory Management System

A sophisticated inventory management system featuring AI agents powered by LangGraph workflow orchestration, with both CLI and Streamlit web interfaces for natural language inventory operations.

## 🌟 Current Features

- 🤖 **AI Agent Workflow**: LangGraph-powered multi-agent system with task classification and specialized agents
- 📦 **Smart Inventory Operations**: Natural language processing for add/update/delete/query operations
- 💬 **Interactive Chat Interface**: Modern Streamlit web UI with real-time chat functionality
- 🧠 **Conversational Memory**: Persistent context awareness across chat sessions using LangGraph state history
- 🗃️ **Robust Database Integration**: Supabase backend with PostgreSQL for reliable data persistence
- 📊 **Live Dashboard**: Real-time inventory display with statistics and CSV export
- 🔍 **Advanced Monitoring**: Integrated LangSmith tracing for debugging and performance optimization
- 🎯 **Intelligent Task Routing**: Automatic classification of user intents to appropriate specialized agents

## 🚀 Setup & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the project root with the following format:

```env
# Supabase Database Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# Groq API Configuration  
GROQ_API_KEY=gsk_your_groq_api_key_here

# LangSmith Monitoring & Debugging (Optional but Recommended)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv2_pt_your_langsmith_api_key_here
LANGCHAIN_PROJECT=DBAgent

# Note: LangSmith integration helps with debugging agent workflows,
# monitoring performance, and optimizing prompt engineering
```

**⚠️ Important Notes:**
- Replace all placeholder values with your actual API keys and URLs
- Keep your `.env` file secure and never commit it to version control
- The LangSmith configuration is optional but highly recommended for development and debugging

### 3. Database Setup
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

### 4. LangSmith Setup (Optional)
LangSmith was integrated to solve workflow debugging issues and optimize agent performance:
- Sign up at [LangSmith](https://smith.langchain.com/)
- Create a new project named "DBAgent" (or update `LANGCHAIN_PROJECT` in `.env`)
- Get your API key from the settings page
- This enables detailed tracing of agent decisions, execution paths, and performance metrics

## 🖥️ Usage

### Web Interface (Recommended)

1. **Launch the Streamlit Application**
   ```bash
   python app.py
   ```
   Or using Streamlit directly:
   ```bash
   streamlit run app.py
   ```

2. **Access the Interface**
   Open your browser and navigate to `http://localhost:8501`

3. **Interact with the AI Assistant**
   - Type natural language queries in the chat interface
   - View real-time inventory updates in the sidebar
   - Monitor agent workflows through LangSmith (if configured)

### Command Line Interface

1. **Run the CLI Version** (if available)
   ```bash
   python agent.py
   ```

2. **Use Natural Language Commands**
   - "Show me all laptops in stock"
   - "Add 5 new monitors to inventory"  
   - "Delete keyboards from the system"
   - "How many items do we have?"

## 💡 Example Queries

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

## 🏗️ Technical Architecture

### Core Components
- **LangGraph Workflow Engine**: Orchestrates multi-agent collaboration with state management
- **Specialized AI Agents**: Task classifier, QA agent, upsert agent, and delete agent
- **Supabase Integration**: PostgreSQL database with real-time capabilities
- **Streamlit Frontend**: Modern web interface with chat functionality
- **LangSmith Monitoring**: Comprehensive workflow tracing and debugging

### Agent Workflow System
1. **Task Classifier Agent**: Analyzes user input and routes to appropriate specialist
2. **QA Agent**: Handles information retrieval and inventory queries
3. **Upsert Agent**: Manages adding new items and updating existing inventory
4. **Delete Agent**: Processes item removal requests with validation
5. **Error Handler**: Graceful error management with user-friendly messages

### LangSmith Integration Benefits
- **Workflow Debugging**: Visual representation of agent decision paths
- **Performance Monitoring**: Track response times and success rates
- **Prompt Optimization**: Analyze and improve agent prompts based on real usage
- **Error Analysis**: Detailed logging of failures for continuous improvement

### 🧠 Memory & Persistence System

The system implements sophisticated conversation memory using LangGraph's built-in persistence capabilities, enabling contextual interactions across multiple exchanges.

#### **Memory Architecture**
- **InMemorySaver Checkpointer**: Maintains conversation state throughout the session
- **Thread-based Persistence**: Each conversation thread maintains independent state history
- **State History Tracking**: Automatically captures user messages and agent responses
- **Contextual Retrieval**: Agents access up to 5 previous interactions for context

#### **Implementation Details**
```python
# Workflow compilation with checkpointer
checkpointer = InMemorySaver()
workflow = StateGraph.compile(checkpointer=checkpointer)

# Thread-based conversation tracking
config = {"configurable": {"thread_id": "main"}}
history = workflow.get_state_history(config, limit=5)
```

## 📁 Project Structure

```
DBAgent/
├── agent.py              # Core agent logic and state management
├── app.py                # Streamlit web interface (main entry point)
├── graph.py              # LangGraph workflow definition and orchestration
├── tools.py              # Database interaction tools and utilities
├── prompt.py             # AI prompt templates and engineering
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not in repo)
└── README.md            # Project documentation
```

### Key Files Explained
- **`app.py`**: Main Streamlit application with chat interface and real-time inventory display
- **`agent.py`**: Contains all agent implementations and state management logic
- **`graph.py`**: Defines the LangGraph workflow that orchestrates agent interactions
- **`tools.py`**: Database operations and Supabase integration functions
- **`prompt.py`**: Carefully crafted prompts for each agent type, optimized through LangSmith analysis

## 🔧 Troubleshooting

### Common Issues & Solutions

1. **Environment Variable Errors**
   - Verify `.env` file exists and contains all required variables
   - Check API key validity and ensure no extra spaces/characters
   - Restart the application after updating environment variables

2. **Database Connection Issues**
   - Verify Supabase URL and key are correct in `.env`
   - Ensure Supabase project is active and accessible
   - Check that the "Inventory" table exists with the correct schema
   - Test connection using Supabase dashboard

3. **Agent Workflow Issues**
   - Check LangSmith traces for detailed execution logs
   - Verify GROQ API key is valid and has sufficient credits
   - Monitor agent classification accuracy in LangSmith dashboard
   - Review prompt effectiveness and adjust if needed

4. **Streamlit Interface Problems**
   - Clear browser cache and refresh the page
   - Restart the Streamlit server: `Ctrl+C` then `python app.py`
   - Check terminal for error messages and stack traces
   - Ensure all dependencies are installed correctly

### Using LangSmith for Debugging
1. **Access Tracing**: Visit your LangSmith project dashboard
2. **Analyze Failures**: Click on failed runs to see detailed execution paths
3. **Optimize Prompts**: Use feedback loops to improve agent responses
4. **Monitor Performance**: Track response times and success rates over time

### Getting Help
If issues persist:
1. Check LangSmith traces for detailed error information
2. Verify all environment variables are correctly configured
3. Test database connectivity independently
4. Review agent logs in the Streamlit terminal output
5. Ensure API quotas and rate limits are not exceeded

## 🛠️ Development & Debugging

### LangSmith for Issue Resolution
LangSmith was crucial in solving several development challenges:

1. **Agent Decision Debugging**: Visualized why agents were making incorrect classifications
2. **Prompt Engineering**: Iteratively improved prompts based on failure analysis
3. **Workflow Optimization**: Identified bottlenecks in the agent execution pipeline
4. **Error Pattern Recognition**: Discovered common failure modes and implemented preventive measures

### Development Workflow
1. **Adding New Features**: Extend agent classes and update the workflow graph in `graph.py`
2. **UI Modifications**: Edit `app.py` for interface improvements
3. **Database Changes**: Update `tools.py` and ensure schema compatibility
4. **Prompt Engineering**: Modify `prompt.py` templates and validate with LangSmith
5. **Memory Enhancement**: Update agent state schemas and context handling for improved persistence
6. **Debugging**: Use LangSmith traces to understand agent behavior and optimize performance

### Memory System Development
The conversational memory implementation demonstrates advanced LangGraph patterns:

- **State Schema Design**: `WorkflowState` and `AgentState` include `chat_history` fields
- **Context Retrieval**: `get_state_history()` with configurable limits for efficient memory usage  
- **Prompt Integration**: All agent prompts enhanced with contextual chat history formatting
- **Thread Management**: Persistent conversation threads using configurable thread IDs
- **Backward Compatibility**: Graceful handling when no chat history is available

### Monitoring & Analytics
- Access LangSmith dashboard to view real-time agent performance
- Analyze user interaction patterns and common query types
- Monitor system reliability and response time metrics
- Track prompt effectiveness and iteration improvements

## 📜 License

This project is for educational and development purposes.

---

## 🔄 Recent Updates

- ✅ **Conversational Memory Implementation**: Added persistent context awareness using LangGraph's `get_state_history()`
- ✅ **Enhanced Agent Context**: All agents now receive and process up to 5 previous chat interactions
- ✅ **Natural Reference Resolution**: Agents understand ambiguous references from conversation history
- ✅ **Integrated LangSmith**: Comprehensive workflow monitoring and debugging capabilities
- ✅ **Multi-agent Architecture**: LangGraph-powered robust task handling with specialized agents
- ✅ **Real-time Chat Interface**: Enhanced Streamlit UI with live inventory dashboard
- ✅ **Advanced Error Handling**: Sophisticated error management and user feedback systems
- ✅ **Prompt Optimization**: Iterative improvements through LangSmith analytics

**Note**: The memory persistence implementation enables truly conversational interactions, allowing users to have natural follow-up conversations without repeating context. LangSmith integration was crucial for debugging the agent workflows and optimizing the contextual prompt engineering.
