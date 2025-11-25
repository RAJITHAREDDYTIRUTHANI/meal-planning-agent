# Meal Planning & Shopping Assistant Agent

An intelligent AI agent system that helps users plan meals, find recipes, and generate optimized shopping lists based on dietary preferences, budget constraints, and nutritional goals.

## 🎯 Problem Statement

Meal planning is a time-consuming task that many people struggle with. It requires:
- Researching recipes that match dietary preferences
- Balancing nutritional needs
- Managing grocery shopping efficiently
- Avoiding food waste
- Staying within budget

This agent automates and streamlines the entire meal planning and shopping process, saving users hours each week while helping them make healthier, more cost-effective food choices.

## 🏗️ Architecture

The system uses a **multi-agent architecture** with specialized agents working together:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Orchestrator Agent (Main)                      │
│  - Coordinates workflow                                     │
│  - Manages session state                                    │
│  - Handles user preferences                                 │
└──────┬──────────────┬──────────────┬───────────────────────┘
       │              │              │
       ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Meal      │ │   Recipe    │ │  Shopping   │
│  Planner    │ │   Finder    │ │   List      │
│   Agent     │ │   Agent     │ │  Generator  │
│             │ │             │ │   Agent     │
└─────────────┘ └─────────────┘ └─────────────┘
```

### Agent Responsibilities

1. **Orchestrator Agent**: Main coordinator that manages the workflow, maintains session state, and remembers user preferences
2. **Meal Planner Agent**: Suggests meal plans based on dietary restrictions, preferences, and nutritional goals
3. **Recipe Finder Agent**: Searches for and retrieves recipes from various sources
4. **Shopping List Generator Agent**: Creates optimized shopping lists, groups items by category, and estimates costs

## ✨ Key Features

### Multi-Agent System
- **Sequential Agents**: Meal planning → Recipe finding → Shopping list generation
- **Parallel Agents**: Can search multiple recipe sources simultaneously
- **LLM-Powered**: All agents use Gemini for intelligent decision-making

### Custom Tools
- **Recipe Search Tool**: Searches recipe databases and APIs
- **Nutrition Analysis Tool**: Analyzes nutritional content of meals
- **Shopping List Optimizer**: Groups items by store section and optimizes for efficiency
- **Budget Calculator**: Estimates costs and suggests budget-friendly alternatives

### Sessions & Memory
- **InMemorySessionService**: Tracks user sessions and conversation context
- **Memory Bank**: Stores long-term preferences:
  - Dietary restrictions (vegetarian, vegan, gluten-free, etc.)
  - Favorite cuisines and recipes
  - Budget constraints
  - Past meal plans
  - Shopping history

### Observability
- **Logging**: Comprehensive logging of agent decisions and actions
- **Tracing**: End-to-end tracing of agent workflows
- **Metrics**: Performance metrics (response time, success rate, etc.)

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9 or higher
- Google Cloud account (for Gemini API)
- (Optional) Spoonacular API key for recipe data

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Kagg_compe
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys:
# GEMINI_API_KEY=your_gemini_api_key
# SPOONACULAR_API_KEY=your_spoonacular_key (optional)
```

4. Run the agent:

**Option A: Web UI (Recommended)**
```bash
python -m streamlit run app.py
```
Or use the launcher: `python run_ui.py`

The UI will open automatically in your browser at `http://localhost:8501`

**Option B: Command Line**
```bash
python main.py
```

## 📖 Usage Examples

### Basic Meal Planning
```python
from agents.orchestrator import OrchestratorAgent

# Initialize the orchestrator agent
agent = OrchestratorAgent()

# Create a session for a user
session_id = agent.create_session(
    user_id="user123",
    initial_preferences={"dietary_restriction": "vegetarian"}
)

# Plan meals for the week
response = agent.plan_meals(
    session_id=session_id,
    days=7,
    dietary_restrictions=["vegetarian"],
    budget=100,
    preferences=["Italian", "Mexican"],
    include_nutrition=True,
    include_shopping_list=True
)

# Access results
print(response["meal_plan"])
print(response["shopping_list"])
print(response["nutrition"])
```

### Using Memory Across Sessions
```python
# First session - set preferences
session_id1 = agent.create_session(user_id="user123")
agent.update_preferences(session_id1, {
    "favorite_cuisines": ["Mexican", "Thai"],
    "budget": 80.0
})

# Plan meals (preferences are remembered)
result1 = agent.plan_meals(session_id=session_id1, days=3)

# Second session - preferences persist in memory bank
session_id2 = agent.create_session(user_id="user123")
result2 = agent.plan_meals(session_id=session_id2, days=3)
# Agent remembers preferences from previous sessions!
```

### Running the Demo

**Web UI (Easiest)**
```bash
streamlit run app.py
```
Then use the interactive web interface to:
- Enter your preferences
- Generate meal plans
- View shopping lists
- Save preferences

**Command Line**
```bash
# Run the main demo
python main.py

# Run example usage scenarios
python example_usage.py
```

## 🏆 Capstone Requirements Met

This project demonstrates **at least 3 key concepts** required for the capstone:

### ✅ Multi-Agent System
- **Orchestrator Agent**: Main coordinator using LLM (Gemini) for workflow management
- **Meal Planner Agent**: LLM-powered agent for generating meal plans
- **Recipe Finder Agent**: LLM-powered agent for finding recipes
- **Shopping List Agent**: LLM-powered agent for generating shopping lists
- **Sequential Workflow**: Meal planning → Recipe finding → Shopping list generation
- **Parallel Capability**: Can search multiple recipe sources simultaneously

### ✅ Custom Tools
- **RecipeSearchTool**: Custom tool for searching recipe databases/APIs
- **NutritionAnalysisTool**: Custom tool for analyzing nutritional content
- **ShoppingOptimizerTool**: Custom tool for optimizing and organizing shopping lists
- All tools integrate with the agent system and provide structured outputs

### ✅ Sessions & Memory
- **InMemorySessionService**: Manages user sessions and conversation context
- **Memory Bank**: Long-term storage of:
  - User preferences (dietary restrictions, cuisine preferences, budget)
  - Meal history (past meal plans with feedback)
  - Shopping history
- **Context Engineering**: Agents use memory to personalize recommendations

### ✅ Observability
- **Logging**: Comprehensive logging using Python's logging module
  - Logs agent decisions, tool usage, and errors
  - Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- **Tracing**: Custom tracing system for tracking:
  - Agent operation spans
  - Tool execution traces
  - End-to-end workflow tracing
- **Metrics**: Tracks performance metrics (response times, success rates)

### ✅ LLM-Powered Agents
- All agents use **Google Gemini** (gemini-pro) for intelligent decision-making
- Agents use LLMs for:
  - Generating meal plans based on preferences
  - Creating optimized search queries
  - Selecting best recipes from candidates
  - Extracting and normalizing ingredients  

## 📁 Project Structure

```
Kagg_compe/
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py      # Main orchestrator agent
│   ├── meal_planner.py      # Meal planning agent
│   ├── recipe_finder.py     # Recipe search agent
│   └── shopping_list.py     # Shopping list generator
├── tools/
│   ├── __init__.py
│   ├── recipe_search.py     # Recipe search tool
│   ├── nutrition.py         # Nutrition analysis tool
│   └── shopping_optimizer.py # Shopping list optimization
├── memory/
│   ├── __init__.py
│   ├── session_service.py   # Session management
│   └── memory_bank.py       # Long-term memory
├── observability/
│   ├── __init__.py
│   ├── logger.py            # Logging setup
│   └── tracer.py            # Tracing setup
├── main.py                  # Command-line entry point
├── app.py                   # Streamlit web UI
├── run_ui.py                # UI launcher script
├── requirements.txt
├── .env.example
├── README.md
└── UI_README.md             # UI-specific documentation
```

## 🔄 Workflow

The agent follows this sequential workflow:

1. **User Request**: User provides preferences, dietary restrictions, budget, and number of days
2. **Session Creation**: Orchestrator creates/retrieves session and loads user context from memory
3. **Meal Planning**: Meal Planner Agent uses LLM to generate meal plan
4. **Recipe Finding**: Recipe Finder Agent searches for recipes using custom RecipeSearchTool
5. **Shopping List Generation**: Shopping List Agent extracts ingredients and optimizes list
6. **Nutrition Analysis**: (Optional) Nutrition tool analyzes meal nutritional content
7. **Memory Update**: Results saved to memory bank for future personalization
8. **Response**: Complete meal plan with recipes, shopping list, and nutrition returned

## 🎥 Demo

[Link to YouTube video demo - to be added]

## 🧪 Testing

Run the example usage to see the agent in action:

```bash
python example_usage.py
```

This will demonstrate:
- Basic meal planning
- Memory persistence across sessions
- Nutrition-focused planning
- Budget-conscious planning

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required for full functionality
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - for enhanced recipe data
SPOONACULAR_API_KEY=your_spoonacular_api_key_here

# Observability
LOG_LEVEL=INFO
ENABLE_TRACING=true
```

### Getting API Keys

1. **Gemini API Key**: 
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add to `.env` file

2. **Spoonacular API Key** (Optional):
   - Visit [Spoonacular API](https://spoonacular.com/food-api)
   - Sign up for free tier (150 points/day)
   - Add to `.env` file

## 📊 Architecture Details

### Agent Communication Flow

```
User Request
    ↓
Orchestrator Agent
    ├─→ Loads user context from Memory Bank
    ├─→ Creates/retrieves session
    ↓
Sequential Agent Execution:
    ├─→ Meal Planner Agent (LLM)
    │   └─→ Generates meal plan
    ├─→ Recipe Finder Agent (LLM + Tool)
    │   ├─→ Uses RecipeSearchTool
    │   └─→ Selects best recipes
    ├─→ Shopping List Agent (LLM + Tool)
    │   ├─→ Extracts ingredients
    │   └─→ Uses ShoppingOptimizerTool
    └─→ Nutrition Tool (Optional)
        └─→ Analyzes nutritional content
    ↓
Results saved to Memory Bank
    ↓
Response to User
```

### Memory Architecture

- **Session Memory**: Short-term context (conversation state, current preferences)
- **Memory Bank**: Long-term storage (persistent preferences, meal history)
- **Context Compaction**: Memory Bank limits history to last 50 entries per user

## 🚀 Deployment

The agent can be deployed using:

- **Agent Engine**: Google Cloud Agent Engine (for production deployment)
- **Cloud Run**: Containerized deployment
- **Local**: Run directly with `python main.py`

For deployment instructions, see the deployment section in the code comments.

## 📝 License

MIT License

## 👥 Authors

[Your name/team name]

## 🙏 Acknowledgments

- Built for the 5-Day AI Agents Intensive Course with Google (Nov 10-14, 2025)
- Uses Google Gemini API for LLM capabilities
- Inspired by the need to simplify meal planning and grocery shopping

