# Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Get API Key (Optional but Recommended)

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### Step 3: Configure Environment

```bash
# Copy the example file (if not already created)
# The .env file should already exist, just edit it

# Edit .env and add your key:
# GEMINI_API_KEY=your_key_here
```

### Step 4: Run the Application

**🎨 Option A: Web UI (Recommended - Easiest!)**

**Windows PowerShell/Command Prompt:**
```bash
python -m streamlit run app.py
```

**Or use the launcher script:**
```bash
python run_ui.py
```

**Or double-click:**
- `START_UI.bat` (Windows)
- `START_UI.ps1` (PowerShell)

The UI will automatically open in your browser at `http://localhost:8501`

**💻 Option B: Command Line**

```bash
python main.py
```

## 🎯 Using the Web UI

1. **Open the UI**: Run `streamlit run app.py`
2. **Enter Preferences**: 
   - Number of days (1-14)
   - Budget in USD
   - Dietary restrictions (select multiple)
   - Cuisine preferences (select multiple)
3. **Generate Meal Plan**: Click "Generate Meal Plan" button
4. **View Results**: 
   - See your meals in the "Meal Planning" tab
   - Check shopping list in the "Shopping List" tab
   - Manage preferences in "History & Preferences" tab

## 📋 Example Output

### Meal Plan
- Day 1: Breakfast, Lunch, Dinner
- Day 2: Breakfast, Lunch, Dinner
- ... and so on

### Shopping List
- **Produce**: Lettuce, Tomato, Onion...
- **Dairy**: Milk, Cheese, Yogurt...
- **Pantry**: Pasta, Rice, Olive Oil...
- **Total Cost**: $45.50

### Nutrition Analysis
- Total Calories: 1850
- Protein: 95g
- Carbs: 220g
- Fat: 65g

## 🧪 Try Different Scenarios

```bash
# Run example scenarios (command line)
python example_usage.py
```

This demonstrates:
- Basic meal planning
- Memory persistence
- Nutrition-focused planning
- Budget-conscious planning

## 🎨 Web UI Features

- ✅ Interactive forms for easy input
- ✅ Real-time meal plan generation
- ✅ Organized shopping lists by store section
- ✅ Nutrition analysis with metrics
- ✅ Cost estimates
- ✅ Preference saving and memory
- ✅ Mobile-responsive design

## 🔧 Troubleshooting

**UI won't start?**
```bash
pip install streamlit
streamlit run app.py
```

**No API key?** 
- The agent will use mock data for demonstration
- You'll still see the full workflow, just with sample data

**Port already in use?**
```bash
streamlit run app.py --server.port 8502
```

**Import errors?** 
- Make sure all dependencies are installed: `pip install -r requirements.txt`

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [UI_README.md](UI_README.md) for UI-specific features
- Check [SUBMISSION_SUMMARY.md](SUBMISSION_SUMMARY.md) for project overview
- Customize preferences in the UI
- Extend with additional features

## 💡 Tips

- **First Time**: Create a session in the sidebar
- **Save Preferences**: Use the "History & Preferences" tab to save your favorite cuisines
- **Budget Planning**: Set a budget to get cost estimates
- **Multiple Days**: Plan up to 14 days at once!
