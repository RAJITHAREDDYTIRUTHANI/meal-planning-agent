"""
Streamlit Web UI for Meal Planning & Shopping Assistant
"""

import streamlit as st
import os
from dotenv import load_dotenv
from agents.orchestrator import OrchestratorAgent
from tools.email_service import EmailService
from tools.ordering_service import OrderingService
from observability.logger import setup_logger, get_logger

# Load environment variables
load_dotenv()

# Set up logging
setup_logger(level="INFO")
logger = get_logger("streamlit_app")

# Page configuration
st.set_page_config(
    page_title="Meal Planning & Shopping Assistant",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = OrchestratorAgent()
    st.session_state.session_id = None
    st.session_state.user_id = None
    st.session_state.meal_plan_result = None
    st.session_state.email_service = EmailService()
    st.session_state.ordering_service = OrderingService()

# Advanced Modern CSS Styling
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main Header with Gradient */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
        letter-spacing: -0.02em;
    }
    
    /* Sub Headers */
    .sub-header {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1a202c;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* Modern Cards */
    .meal-card {
        padding: 1.5rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        border: 1px solid #e2e8f0;
        margin: 0.75rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .meal-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }
    
    .meal-card strong {
        font-size: 1.1rem;
        color: #667eea;
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    /* Info Boxes */
    .info-box {
        padding: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-left: 4px solid #667eea;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    }
    
    .success-box {
        padding: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #48bb7815 0%, #38a16915 100%);
        border-left: 4px solid #48bb78;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(72, 187, 120, 0.1);
    }
    
    /* Day Header */
    .day-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2d3748;
        margin: 2rem 0 1rem 0;
        padding: 0.75rem 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Section Cards */
    .section-card {
        padding: 1.25rem;
        border-radius: 12px;
        background: white;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Metric Cards */
    .metric-card {
        padding: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f7fafc 0%, #ffffff 100%);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Form Inputs */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #2d3748;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
    </style>
""", unsafe_allow_html=True)

# Main header with modern design
st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <div class="main-header">🍽️ Meal Planning & Shopping Assistant</div>
        <p style="color: #718096; font-size: 1.1rem; margin-top: -1rem;">
            AI-Powered Meal Planning Made Simple
        </p>
    </div>
""", unsafe_allow_html=True)

# Sidebar for user preferences
with st.sidebar:
    st.header("⚙️ User Settings")
    
    # User ID input
    user_id = st.text_input(
        "User ID",
        value=st.session_state.user_id or "user_" + str(hash(st.session_state.get("user_id", "default")) % 10000),
        help="Enter a unique identifier for your profile"
    )
    st.session_state.user_id = user_id
    
    # Create/Reset session button
    if st.button("🔄 Create New Session", use_container_width=True):
        st.session_state.session_id = st.session_state.orchestrator.create_session(
            user_id=user_id,
            initial_preferences={}
        )
        st.session_state.meal_plan_result = None
        st.success("New session created!")
        st.rerun()
    
    st.divider()
    
    # API Key status
    st.subheader("🔑 API Status")
    if os.getenv("GEMINI_API_KEY"):
        st.success("✅ Gemini API Key Found")
    else:
        st.warning("⚠️ No API Key - Using Mock Data")
        st.info("Add GEMINI_API_KEY to .env file for full functionality")
    
    st.divider()
    
    # Instructions
    st.subheader("📖 How to Use")
    st.markdown("""
    1. Enter your preferences below
    2. Click "Generate Meal Plan"
    3. View your meal plan and shopping list
    4. Save or modify as needed
    """)

# Main content area
tab1, tab2, tab3 = st.tabs(["📋 Meal Planning", "🛒 Shopping List", "📊 History & Preferences"])

# Tab 1: Meal Planning
with tab1:
    st.markdown('<div class="sub-header">Create Your Meal Plan</div>', unsafe_allow_html=True)
    
    # Create session if not exists
    if not st.session_state.session_id:
        st.session_state.session_id = st.session_state.orchestrator.create_session(
            user_id=st.session_state.user_id
        )
    
    # User input form
    with st.form("meal_plan_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            days = st.number_input(
                "Number of Days",
                min_value=1,
                max_value=14,
                value=7,
                help="How many days would you like to plan meals for?"
            )
            
            budget = st.number_input(
                "Budget (USD)",
                min_value=0.0,
                max_value=1000.0,
                value=100.0,
                step=10.0,
                help="Your total budget for all meals"
            )
        
        with col2:
            dietary_restrictions = st.multiselect(
                "Dietary Restrictions",
                options=["vegetarian", "vegan", "gluten-free", "dairy-free", "nut-free", "keto", "paleo"],
                help="Select any dietary restrictions"
            )
            
            cuisine_preferences = st.multiselect(
                "Cuisine Preferences",
                options=["Italian", "Mexican", "Asian", "Indian", "Mediterranean", "American", "Thai", "Japanese", "French"],
                help="Select your favorite cuisines"
            )
        
        # Additional options
        col3, col4 = st.columns(2)
        with col3:
            include_nutrition = st.checkbox("Include Nutrition Analysis", value=True)
        with col4:
            include_shopping_list = st.checkbox("Generate Shopping List", value=True)
        
        # Submit button
        submitted = st.form_submit_button("🚀 Generate Meal Plan", use_container_width=True)
        
        if submitted:
            with st.spinner("Planning your meals... This may take a moment."):
                try:
                    result = st.session_state.orchestrator.plan_meals(
                        session_id=st.session_state.session_id,
                        days=int(days),
                        dietary_restrictions=dietary_restrictions if dietary_restrictions else None,
                        preferences=cuisine_preferences if cuisine_preferences else None,
                        budget=float(budget) if budget > 0 else None,
                        include_nutrition=include_nutrition,
                        include_shopping_list=include_shopping_list
                    )
                    
                    st.session_state.meal_plan_result = result
                    # Save to history
                    user_id = st.session_state.user_id
                    if user_id:
                        st.session_state.orchestrator.memory_bank.add_meal_history(
                            user_id=user_id,
                            meal_plan=result.get("meal_plan", {})
                        )
                    st.success("✅ Meal plan generated successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error generating meal plan: {str(e)}")
                    logger.error(f"Error in meal planning: {e}", exc_info=True)
    
    # Display results if available
    if st.session_state.meal_plan_result:
        result = st.session_state.meal_plan_result
        meal_plan = result.get("meal_plan", {})
        
        st.markdown('<div class="sub-header">Your Meal Plan</div>', unsafe_allow_html=True)
        
        # Summary with modern design
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; font-weight: 700; color: #667eea;">{meal_plan.get('days', 'N/A')}</div>
                <div style="color: #718096; margin-top: 0.5rem;">Days Planned</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; font-weight: 700; color: #667eea;">{len(meal_plan.get('meals', []))}</div>
                <div style="color: #718096; margin-top: 0.5rem;">Total Meals</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            meals_per_day = len(meal_plan.get('meals', [])) / meal_plan.get('days', 1) if meal_plan.get('days', 0) > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; font-weight: 700; color: #667eea;">{meals_per_day:.1f}</div>
                <div style="color: #718096; margin-top: 0.5rem;">Meals/Day</div>
            </div>
            """, unsafe_allow_html=True)
        
        if meal_plan.get('summary'):
            st.markdown(f"""
            <div class="info-box">
                <strong style="color: #2d3748; font-size: 1.1rem;">📋 Plan Summary</strong><br>
                <div style="color: #4a5568; margin-top: 0.75rem; line-height: 1.6;">
                    {meal_plan.get('summary', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Display meals by day
        meals = meal_plan.get("meals", [])
        if meals:
            # Group meals by day
            days_dict = {}
            for meal in meals:
                day = meal.get("day", 1)
                if day not in days_dict:
                    days_dict[day] = []
                days_dict[day].append(meal)
            
            # Display each day with modern cards
            for day in sorted(days_dict.keys()):
                st.markdown(f'<div class="day-header">📅 Day {day}</div>', unsafe_allow_html=True)
                day_meals = days_dict[day]
                
                cols = st.columns(3)
                meal_types = ["breakfast", "lunch", "dinner"]
                meal_icons = {"breakfast": "🌅", "lunch": "☀️", "dinner": "🌙"}
                
                for idx, meal_type in enumerate(meal_types):
                    with cols[idx]:
                        meal = next((m for m in day_meals if m.get("meal_type") == meal_type), None)
                        if meal:
                            icon = meal_icons.get(meal_type, "🍽️")
                            st.markdown(f"""
                            <div class="meal-card">
                                <strong>{icon} {meal_type.title()}</strong>
                                <div style="font-size: 1.1rem; font-weight: 600; color: #2d3748; margin: 0.75rem 0;">
                                    {meal.get('name', 'N/A')}
                                </div>
                                <div style="color: #718096; font-size: 0.9rem; line-height: 1.5;">
                                    {meal.get('description', '')}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="meal-card" style="opacity: 0.6;">
                                <strong>{meal_icons.get(meal_type, "🍽️")} {meal_type.title()}</strong>
                                <div style="color: #a0aec0; margin-top: 0.5rem;">No meal planned</div>
                            </div>
                            """, unsafe_allow_html=True)
        
        # Nutrition analysis with modern design
        if result.get("nutrition"):
            st.markdown('<div class="sub-header">📊 Nutrition Analysis</div>', unsafe_allow_html=True)
            nutrition = result["nutrition"]
            
            col1, col2, col3, col4 = st.columns(4)
            nutrition_data = [
                ("🔥 Calories", f"{nutrition.get('total_calories', 0):.0f}", "#f56565"),
                ("💪 Protein", f"{nutrition.get('total_protein_g', 0):.1f}g", "#4299e1"),
                ("🍞 Carbs", f"{nutrition.get('total_carbs_g', 0):.1f}g", "#48bb78"),
                ("🥑 Fat", f"{nutrition.get('total_fat_g', 0):.1f}g", "#ed8936")
            ]
            
            for idx, (label, value, color) in enumerate(nutrition_data):
                with [col1, col2, col3, col4][idx]:
                    st.markdown(f"""
                    <div class="metric-card" style="border-left: 4px solid {color};">
                        <div style="font-size: 1.75rem; font-weight: 700; color: {color};">{value}</div>
                        <div style="color: #718096; margin-top: 0.5rem; font-weight: 500;">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            if nutrition.get("recommendations"):
                st.markdown("### 💡 Recommendations")
                for rec in nutrition["recommendations"]:
                    st.markdown(f"""
                    <div class="info-box" style="margin: 0.75rem 0;">
                        <div style="color: #4a5568; line-height: 1.6;">{rec}</div>
                    </div>
                    """, unsafe_allow_html=True)

# Tab 2: Shopping List
with tab2:
    st.markdown('<div class="sub-header">Your Shopping List</div>', unsafe_allow_html=True)
    
    if st.session_state.meal_plan_result and st.session_state.meal_plan_result.get("shopping_list"):
        shopping_list = st.session_state.meal_plan_result["shopping_list"]
        
        # Summary with modern metrics
        total_items = shopping_list.get('total_items', 0)
        st.markdown(f"""
        <div class="metric-card" style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem; font-weight: 700; color: #667eea;">{total_items}</div>
            <div style="color: #718096; margin-top: 0.5rem; font-size: 1.1rem; font-weight: 500;">Total Items</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grouped by section with modern design
        if shopping_list.get("grouped_by_section"):
            st.markdown('<div class="sub-header">🛒 Items by Store Section</div>', unsafe_allow_html=True)
            
            section_icons = {
                "produce": "🥬", "dairy": "🥛", "meat": "🥩", "pantry": "🥫",
                "frozen": "🧊", "bakery": "🍞", "beverages": "🥤", "snacks": "🍿"
            }
            
            for section, items in shopping_list["grouped_by_section"].items():
                icon = section_icons.get(section.lower(), "📦")
                with st.expander(f"{icon} {section.upper()} ({len(items)} items)", expanded=True):
                    st.markdown(f"""
                    <div class="section-card">
                        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 0.75rem;">
                    """, unsafe_allow_html=True)
                    for item in items:
                        st.markdown(f"""
                        <div style="padding: 0.75rem; background: #f7fafc; border-radius: 8px; border-left: 3px solid #667eea;">
                            ✓ {item}
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Cost estimate with modern design
        if shopping_list.get("estimated_cost"):
            cost = shopping_list["estimated_cost"]
            st.markdown('<div class="sub-header">💰 Cost Estimate</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            total_cost = cost.get('total_estimate', 0)
            currency = cost.get('currency', 'USD')
            
            with col1:
                st.markdown(f"""
                <div class="metric-card" style="border-left: 4px solid #48bb78;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: #48bb78;">${total_cost:.2f}</div>
                    <div style="color: #718096; margin-top: 0.5rem; font-weight: 500;">Total Estimated Cost</div>
                    <div style="color: #a0aec0; font-size: 0.85rem; margin-top: 0.25rem;">{currency}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.session_state.meal_plan_result.get("meal_plan", {}).get("days"):
                    days = st.session_state.meal_plan_result["meal_plan"]["days"]
                    daily_avg = total_cost / days if days > 0 else 0
                    st.markdown(f"""
                    <div class="metric-card" style="border-left: 4px solid #667eea;">
                        <div style="font-size: 2.5rem; font-weight: 700; color: #667eea;">${daily_avg:.2f}</div>
                        <div style="color: #718096; margin-top: 0.5rem; font-weight: 500;">Daily Average</div>
                        <div style="color: #a0aec0; font-size: 0.85rem; margin-top: 0.25rem;">Per day</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            if cost.get("note"):
                st.info(f"ℹ️ {cost.get('note', '')}")
            
            # Item costs breakdown
            if cost.get("item_costs"):
                with st.expander("📋 View Detailed Item Costs", expanded=False):
                    item_costs = cost["item_costs"]
                    st.markdown("""
                    <div style="max-height: 400px; overflow-y: auto;">
                    """, unsafe_allow_html=True)
                    for item, price in sorted(item_costs.items(), key=lambda x: x[1], reverse=True):
                        st.markdown(f"""
                        <div style="padding: 0.75rem; margin: 0.5rem 0; background: #f7fafc; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 500; color: #2d3748;">{item}</span>
                            <span style="font-weight: 700; color: #48bb78;">${price:.2f}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
        
        # Email and Ordering Actions
        st.markdown('<div class="sub-header">📧 Share & Order</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📧 Send to Email")
            
            # Show email service status
            email_service = st.session_state.email_service
            email_service._check_configuration()  # Refresh config
            
            if email_service.enabled:
                st.success("✅ Email service configured and ready!")
            else:
                st.warning("⚠️ Email service not configured")
                with st.expander("📝 How to configure email", expanded=False):
                    st.markdown("""
                    **To enable email sending, add these to your `.env` file:**
                    
                    ```env
                    SENDER_EMAIL=your.email@gmail.com
                    SENDER_PASSWORD=your_app_password
                    SMTP_SERVER=smtp.gmail.com
                    SMTP_PORT=587
                    ```
                    
                    **For Gmail:**
                    1. Enable 2-Step Verification
                    2. Generate an App Password: https://myaccount.google.com/apppasswords
                    3. Use the 16-character app password (not your regular password)
                    
                    **After adding to .env:**
                    - Restart the Streamlit app (Ctrl+C and run again)
                    - The email service will automatically detect the configuration
                    """)
            
            with st.form("email_form"):
                email_address = st.text_input(
                    "Email Address",
                    placeholder="your.email@example.com",
                    help="Enter your email to receive the shopping list"
                )
                send_email = st.form_submit_button("📧 Send Shopping List", use_container_width=True, disabled=not email_service.enabled)
                
                if send_email:
                    if email_address and "@" in email_address:
                        with st.spinner("Sending email..."):
                            success = email_service.send_shopping_list(
                                recipient_email=email_address,
                                shopping_list=shopping_list,
                                meal_plan=st.session_state.meal_plan_result.get("meal_plan") if st.session_state.meal_plan_result else None
                            )
                            if success:
                                st.success(f"✅ Shopping list sent to {email_address}!")
                            else:
                                st.error("❌ Failed to send email. Please check your email configuration and try again.")
                    else:
                        st.error("Please enter a valid email address")
        
        with col2:
            st.markdown("### 🛒 Online Ordering")
            preferred_service = st.selectbox(
                "Preferred Service",
                options=["Instacart", "Amazon Fresh", "Walmart Grocery", "Kroger", "Target", "Whole Foods"],
                help="Select your preferred grocery delivery service"
            )
            
            if st.button("🛒 Generate Order Links", use_container_width=True):
                order_data = st.session_state.ordering_service.generate_order_links(
                    shopping_list=shopping_list,
                    preferred_service=preferred_service
                )
                
                st.success(f"✅ Order links generated for {preferred_service}!")
                
                with st.expander("🔗 Order Links", expanded=True):
                    for service_name, service_data in order_data["services"].items():
                        if service_data["available"]:
                            st.markdown(f"### {service_name}")
                            st.markdown(f"[🔍 Search Items]({service_data['search_url']})")
                            st.markdown(f"[🛒 Go to Cart]({service_data['cart_url']})")
                            st.divider()
        
        # Checkout Assistance
        st.markdown('<div class="sub-header">💳 Checkout Assistance</div>', unsafe_allow_html=True)
        
        budget = st.session_state.meal_plan_result.get("meal_plan", {}).get("budget") if st.session_state.meal_plan_result else None
        tips = st.session_state.ordering_service.get_checkout_tips(shopping_list, budget)
        
        for tip in tips:
            st.info(tip)
    else:
        st.info("👆 Generate a meal plan first to see your shopping list!")

# Tab 3: History & Preferences
with tab3:
    st.markdown('<div class="sub-header">Your Preferences & History</div>', unsafe_allow_html=True)
    
    if st.session_state.session_id:
        user_id = st.session_state.user_id
        memory_bank = st.session_state.orchestrator.memory_bank
        
        # Get user preferences from memory bank
        saved_preferences = memory_bank.get_preferences(user_id)
        
        # Display saved preferences
        if saved_preferences:
            st.markdown("### 💾 Saved Preferences")
            pref_cols = st.columns(3)
            
            with pref_cols[0]:
                if "favorite_cuisines" in saved_preferences:
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>Favorite Cuisines:</strong><br>
                        {', '.join(saved_preferences['favorite_cuisines']) if isinstance(saved_preferences['favorite_cuisines'], list) else saved_preferences['favorite_cuisines']}
                    </div>
                    """, unsafe_allow_html=True)
            
            with pref_cols[1]:
                if "budget" in saved_preferences:
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>Preferred Budget:</strong><br>
                        ${saved_preferences['budget']:.2f}
                    </div>
                    """, unsafe_allow_html=True)
            
            with pref_cols[2]:
                if "dietary_restriction" in saved_preferences:
                    restrictions = saved_preferences.get("dietary_restriction", [])
                    if isinstance(restrictions, str):
                        restrictions = [restrictions]
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>Dietary Restrictions:</strong><br>
                        {', '.join(restrictions) if restrictions else 'None'}
                    </div>
                    """, unsafe_allow_html=True)
        
        st.divider()
        
        # Update preferences form
        st.markdown("### ✏️ Update Preferences")
        with st.form("preferences_form"):
            new_preferences = {}
            
            col1, col2 = st.columns(2)
            
            with col1:
                favorite_cuisines = st.multiselect(
                    "Favorite Cuisines",
                    options=["Italian", "Mexican", "Asian", "Indian", "Mediterranean", "American", "Thai", "Japanese", "French"],
                    default=saved_preferences.get("favorite_cuisines", []) if saved_preferences.get("favorite_cuisines") else [],
                    help="Your favorite cuisines"
                )
                if favorite_cuisines:
                    new_preferences["favorite_cuisines"] = favorite_cuisines
                
                dietary_restrictions = st.multiselect(
                    "Dietary Restrictions",
                    options=["vegetarian", "vegan", "gluten-free", "dairy-free", "nut-free", "keto", "paleo"],
                    help="Your dietary restrictions"
                )
                if dietary_restrictions:
                    new_preferences["dietary_restriction"] = dietary_restrictions
            
            with col2:
                budget_pref = st.number_input(
                    "Preferred Budget (USD)",
                    min_value=0.0,
                    max_value=1000.0,
                    value=float(saved_preferences.get("budget", 100.0)) if saved_preferences.get("budget") else 100.0,
                    step=10.0,
                    help="Your preferred weekly budget"
                )
                if budget_pref:
                    new_preferences["budget"] = budget_pref
            
            if st.form_submit_button("💾 Save Preferences", use_container_width=True):
                if new_preferences:
                    st.session_state.orchestrator.update_preferences(
                        st.session_state.session_id,
                        new_preferences
                    )
                    st.success("✅ Preferences saved successfully!")
                    st.rerun()
                else:
                    st.warning("Please select at least one preference to save")
        
        st.divider()
        
        # Meal History
        st.markdown("### 📜 Meal History")
        meal_history = memory_bank.get_meal_history(user_id, limit=10)
        
        if meal_history:
            for idx, history_entry in enumerate(reversed(meal_history[-5:])):  # Show last 5
                # Handle date formatting
                if hasattr(history_entry.date, 'strftime'):
                    date_str = history_entry.date.strftime('%Y-%m-%d %H:%M')
                elif isinstance(history_entry.date, str):
                    date_str = history_entry.date[:16]  # First 16 chars
                else:
                    date_str = str(history_entry.date)[:16]
                
                with st.expander(f"📅 {date_str}", expanded=False):
                    meal_plan = history_entry.meal_plan
                    st.markdown(f"**Days:** {meal_plan.get('days', 'N/A')}")
                    st.markdown(f"**Total Meals:** {len(meal_plan.get('meals', []))}")
                    
                    if meal_plan.get('summary'):
                        st.markdown(f"**Summary:** {meal_plan.get('summary')}")
                    
                    if history_entry.feedback:
                        st.markdown(f"**Your Feedback:** {history_entry.feedback}")
                    else:
                        # Add feedback form
                        with st.form(f"feedback_form_{idx}"):
                            feedback = st.text_area("Add Feedback", placeholder="How was this meal plan? Any suggestions?")
                            if st.form_submit_button("💬 Save Feedback"):
                                if feedback:
                                    # Update feedback in memory bank
                                    history_entry.feedback = feedback
                                    # Save updated history
                                    memory_bank.meal_history[user_id][-len(meal_history)+idx].feedback = feedback
                                    memory_bank.save_to_disk()
                                    st.success("✅ Feedback saved!")
                                    st.rerun()
                    
                    # Show sample meals
                    meals = meal_plan.get('meals', [])[:6]  # First 6 meals
                    if meals:
                        st.markdown("**Sample Meals:**")
                        for meal in meals:
                            st.write(f"- Day {meal.get('day')} {meal.get('meal_type')}: {meal.get('name')}")
        else:
            st.info("No meal history yet. Generate a meal plan to see it here!")
        
        # Session info
        st.divider()
        st.markdown("### ℹ️ Session Information")
        session_info = st.session_state.orchestrator.get_session_info(st.session_state.session_id)
        if session_info:
            info_cols = st.columns(2)
            with info_cols[0]:
                st.metric("User ID", session_info.get("user_id", "N/A"))
            with info_cols[1]:
                st.metric("Session Created", session_info.get("created_at", "N/A")[:10] if session_info.get("created_at") else "N/A")
    else:
        st.info("👆 Create a session first to view preferences and history")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>Meal Planning & Shopping Assistant Agent | Built for AI Agents Capstone Project</p>
    <p>Powered by Google Gemini AI</p>
</div>
""", unsafe_allow_html=True)


