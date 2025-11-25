# Web UI Guide

## 🚀 Quick Start

### Option 1: Run the UI directly (Windows)
```bash
python -m streamlit run app.py
```

### Option 2: Use the launcher script (Recommended)
```bash
python run_ui.py
```

### Option 3: Use batch file (Windows)
Double-click `START_UI.bat` or run:
```bash
START_UI.bat
```

The UI will open automatically in your web browser at `http://localhost:8501`

## 📱 Features

### 1. Meal Planning Tab
- **Input Form**: 
  - Number of days (1-14)
  - Budget in USD
  - Dietary restrictions (multi-select)
  - Cuisine preferences (multi-select)
  - Options for nutrition analysis and shopping list

- **Results Display**:
  - Meal plan summary
  - Meals organized by day (breakfast, lunch, dinner)
  - Nutrition analysis with metrics
  - Recommendations

### 2. Shopping List Tab
- **Organized Shopping List**:
  - Items grouped by store section (Produce, Dairy, Meat, Pantry, etc.)
  - Total item count
  - Cost estimates per item and total
  - Daily average cost

### 3. History & Preferences Tab
- **Session Information**: View current session details
- **Update Preferences**: Save favorite cuisines and budget preferences
- **Memory**: Preferences are saved and remembered across sessions

## 🎨 UI Features

- **Responsive Design**: Works on desktop and mobile
- **Interactive Forms**: Easy-to-use input fields
- **Real-time Updates**: Results appear instantly
- **Color-coded Sections**: Easy to navigate
- **Expandable Sections**: Organized information display

## 💡 Usage Tips

1. **First Time**: 
   - Enter a User ID (or use the default)
   - Click "Create New Session"
   - Fill out the meal planning form

2. **Generate Meal Plan**:
   - Select your preferences
   - Click "Generate Meal Plan"
   - Wait for results (may take 10-30 seconds)

3. **View Results**:
   - Check the "Meal Planning" tab for your meals
   - Switch to "Shopping List" tab for ingredients
   - Use "History & Preferences" to save preferences

4. **Save Preferences**:
   - Go to "History & Preferences" tab
   - Update your favorite cuisines and budget
   - Click "Save Preferences"
   - Future meal plans will remember these!

## 🔧 Troubleshooting

**UI won't start?**
```bash
pip install streamlit streamlit-option-menu
```

**Port already in use?**
```bash
streamlit run app.py --server.port 8502
```

**API Key not working?**
- Check your `.env` file
- Make sure `GEMINI_API_KEY` is set
- The app will work with mock data if no key is found

## 📸 Screenshots

The UI includes:
- Clean, modern interface
- Color-coded sections
- Interactive forms
- Real-time results
- Mobile-responsive design

## 🎯 Next Steps

1. Run `streamlit run app.py`
2. Open the browser to `http://localhost:8501`
3. Start planning your meals!

