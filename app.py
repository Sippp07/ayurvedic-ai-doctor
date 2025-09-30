import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json

# Page setup
st.set_page_config(
    page_title="Ayurvedic AI Doctor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PROFESSIONAL CSS THEME
st.markdown("""
<style>
    :root {
        --primary: #2E8B57;
        --secondary: #FF7F50;
        --accent: #8B4513;
        --light: #F5F5DC;
        --dark: #2F4F4F;
    }
    
    .main-header {
        font-size: 3rem;
        color: var(--primary);
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .step-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fff8 100%);
        padding: 30px;
        border-radius: 20px;
        border-left: 6px solid var(--primary);
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(46, 139, 87, 0.15);
    }
    
    .question-title {
        color: var(--dark);
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 15px;
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        margin: 25px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .herb-card {
        background: rgba(255,255,255,0.15);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .progress-bar {
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        height: 8px;
        border-radius: 10px;
        margin: 20px 0;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, var(--primary), #3CB371);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .health-tag {
        background: var(--primary);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 5px;
        display: inline-block;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# COMPREHENSIVE AYURVEDIC DATABASE
HEALTH_PROBLEMS = [
    "Stress & Anxiety", "Insomnia & Sleep Issues", "Low Immunity", "Digestive Problems",
    "Joint Pain & Inflammation", "Skin Issues (Acne/Eczema)", "Low Energy & Fatigue",
    "Brain Fog & Poor Memory", "Weight Management", "High Blood Pressure",
    "Diabetes & Blood Sugar", "Respiratory Issues (Asthma/Allergies)", "Hair Loss",
    "Hormonal Imbalance", "PCOS & Women's Health", "Menstrual Cramps", 
    "Low Libido", "Poor Circulation", "High Cholesterol", "Liver Health",
    "Kidney Health", "Constipation", "Acidity & GERD", "Migraines & Headaches",
    "Eye Strain & Vision", "Dental & Gum Health", "Seasonal Allergies",
    "Weak Bones & Osteoporosis", "Thyroid Issues", "Chronic Fatigue Syndrome"
]

HERBS_DATABASE = {
    "Ashwagandha": {
        "benefits": ["Stress reduction", "Energy boost", "Immune support", "Sleep quality"],
        "dosage": "300-500mg twice daily",
        "best_time": "Morning and evening with warm milk",
        "safety": "Avoid in pregnancy, thyroid issues, sedatives"
    },
    "Turmeric": {
        "benefits": ["Anti-inflammatory", "Joint health", "Immunity", "Skin glow"],
        "dosage": "500mg with black pepper twice daily", 
        "best_time": "With meals",
        "safety": "Avoid with gallbladder issues, blood thinners"
    },
    "Brahmi": {
        "benefits": ["Memory enhancement", "Focus", "Anxiety relief", "Brain function"],
        "dosage": "300mg twice daily",
        "best_time": "Morning and afternoon",
        "safety": "Generally safe, no known contraindications"
    },
    "Triphala": {
        "benefits": ["Digestion", "Detoxification", "Constipation", "Antioxidant"],
        "dosage": "1-2g at bedtime", 
        "best_time": "Before sleep with warm water",
        "safety": "Avoid in diarrhea, pregnancy"
    },
    "Giloy": {
        "benefits": ["Immunity booster", "Fever reducer", "Energy", "Detox"],
        "dosage": "500mg once daily",
        "best_time": "Morning with warm water",
        "safety": "Avoid in autoimmune diseases"
    },
    "Tulsi (Holy Basil)": {
        "benefits": ["Respiratory health", "Stress relief", "Immunity", "Cold & cough"],
        "dosage": "500mg twice daily",
        "best_time": "Morning and evening",
        "safety": "Generally safe"
    },
    "Shatavari": {
        "benefits": ["Hormonal balance", "Women's health", "Energy", "Lactation"],
        "dosage": "500mg twice daily",
        "best_time": "With milk or warm water",
        "safety": "Avoid in estrogen-sensitive conditions"
    },
    "Ginger": {
        "benefits": ["Digestion", "Nausea relief", "Inflammation", "Cold"],
        "dosage": "1-2g daily as tea or powder",
        "best_time": "With meals or as needed",
        "safety": "Avoid with gallstones, blood thinners"
    },
    "Amla (Indian Gooseberry)": {
        "benefits": ["Immunity", "Vitamin C source", "Hair health", "Anti-aging"],
        "dosage": "1-2g daily",
        "best_time": "Morning empty stomach",
        "safety": "Generally safe"
    },
    "Neem": {
        "benefits": ["Skin health", "Blood purification", "Dental health", "Immunity"],
        "dosage": "500mg once daily",
        "best_time": "Morning with water",
        "safety": "Avoid in pregnancy, diabetes medications"
    }
}

# Initialize Gemini with error handling
gemini_connected = False
try:
    if 'GEMINI_API_KEY' in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        gemini_connected = True
    else:
        st.sidebar.error("❌ GEMINI_API_KEY not found in secrets.toml")
except Exception as e:
    st.sidebar.error(f"❌ Gemini config failed: {e}")

# Initialize session state
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# SIDEBAR - Professional Dashboard
with st.sidebar:
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    st.markdown("### 🌿 Ayurvedic AI Doctor")
    st.markdown("Your Personal Wellness Assistant")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Connection Status
    if gemini_connected:
        st.success("✅ Gemini AI Connected")
    else:
        st.error("❌ AI Not Connected")
        st.info("Add Gemini API key to secrets.toml")
    
    # Progress Tracker
    st.markdown("### 📊 Assessment Progress")
    progress = (st.session_state.current_step + 1) / 5
    st.markdown(f'<div class="progress-bar" style="width: {progress * 100}%"></div>', unsafe_allow_html=True)
    st.write(f"Step {st.session_state.current_step + 1} of 5")
    
    # Quick Health Check
    st.markdown("### 🔍 Quick Health Check")
    quick_concern = st.selectbox("Common Concerns:", ["Select"] + HEALTH_PROBLEMS[:10])
    
    if quick_concern != "Select":
        st.info(f"Focusing on: {quick_concern}")
        if 'main_health_concerns' not in st.session_state.user_data:
            st.session_state.user_data['main_health_concerns'] = []
        if quick_concern not in st.session_state.user_data['main_health_concerns']:
            st.session_state.user_data['main_health_concerns'].append(quick_concern)

# MAIN CONTENT
st.markdown('<div class="main-header">🌿 Ayurvedic AI Wellness Assessment</div>', unsafe_allow_html=True)

# Professional Question Flow
questions = [
    {
        "step": 1,
        "title": "👤 Personal Profile",
        "icon": "👤",
        "questions": {
            "name": "What's your full name?",
            "age": "What's your age?",
            "weight": "What's your weight (kg)?",
            "height": "What's your height (cm)?",
            "gender": "What's your gender?"
        }
    },
    {
        "step": 2, 
        "title": "🎯 Health Assessment",
        "icon": "🎯",
        "questions": {
            "main_health_concerns": "Select your main health concerns:",
            "symptom_severity": "Rate your symptom severity (1-10):",
            "duration": "How long have you had these symptoms?",
            "previous_treatments": "What treatments have you tried?"
        }
    },
    {
        "step": 3,
        "title": "😴 Lifestyle Analysis",
        "icon": "😴",
        "questions": {
            "sleep_quality": "Sleep quality (1-10):",
            "energy_level": "Daily energy level (1-10):",
            "stress_level": "Stress level (1-10):",
            "digestion": "Digestion quality:",
            "exercise": "Exercise frequency:"
        }
    },
    {
        "step": 4,
        "title": "🍽️ Diet & Habits",
        "icon": "🍽️",
        "questions": {
            "diet_type": "Primary diet type:",
            "water_intake": "Daily water intake (glasses):",
            "food_preferences": "Food preferences/allergies:",
            "eating_pattern": "Typical eating pattern:"
        }
    },
    {
        "step": 5,
        "title": "📝 Wellness Goals",
        "icon": "📝",
        "questions": {
            "primary_goal": "Primary wellness goal:",
            "time_commitment": "Daily time for wellness:",
            "budget": "Wellness budget:",
            "expectations": "Expected outcomes:"
        }
    }
]

# Display current step
if not st.session_state.show_results:
    current_q = questions[st.session_state.current_step]
    
    st.markdown(f'<div class="step-card">', unsafe_allow_html=True)
    st.markdown(f"### {current_q['icon']} {current_q['title']}")
    st.markdown(f"*Step {st.session_state.current_step + 1} of {len(questions)}*")
    
    # Dynamic question rendering
    for key, question in current_q['questions'].items():
        st.markdown(f'<div class="question-title">{question}</div>', unsafe_allow_html=True)
        
        # Smart input types
        if key == 'main_health_concerns':
            selected_problems = st.multiselect(
                "Select from common health issues:",
                HEALTH_PROBLEMS,
                default=st.session_state.user_data.get('main_health_concerns', [])
            )
            st.session_state.user_data[key] = selected_problems
            
            # Show selected tags
            if selected_problems:
                st.markdown("**Selected concerns:**")
                for problem in selected_problems[:5]:  # Show first 5
                    st.markdown(f'<span class="health-tag">{problem}</span>', unsafe_allow_html=True)
                
        elif any(word in key for word in ['level', 'quality', 'severity', 'rating']):
            default_val = st.session_state.user_data.get(key, 5)
            response = st.slider("", 1, 10, default_val, key=f"{key}_{st.session_state.current_step}")
            st.session_state.user_data[key] = response
            
        elif key in ['age', 'weight', 'height', 'water_intake']:
            default_val = st.session_state.user_data.get(key, 25 if key == 'age' else 70)
            response = st.number_input("", min_value=1, value=default_val, key=f"{key}_{st.session_state.current_step}")
            st.session_state.user_data[key] = response
            
        elif key == 'gender':
            options = ["Male", "Female", "Other", "Prefer not to say"]
            default_idx = options.index(st.session_state.user_data.get(key, "Male"))
            response = st.selectbox("", options, index=default_idx, key=f"{key}_{st.session_state.current_step}")
            st.session_state.user_data[key] = response
            
        elif key == 'diet_type':
            options = ["Vegetarian", "Non-vegetarian", "Vegan", "Pescatarian", "Mixed"]
            default_idx = options.index(st.session_state.user_data.get(key, "Vegetarian"))
            response = st.selectbox("", options, index=default_idx, key=f"{key}_{st.session_state.current_step}")
            st.session_state.user_data[key] = response
            
        elif key == 'exercise':
            options = ["Daily", "3-4 times/week", "Weekly", "Rarely", "Never"]
            default_idx = options.index(st.session_state.user_data.get(key, "Weekly"))
            response = st.selectbox("", options, index=default_idx, key=f"{key}_{st.session_state.current_step}")
            st.session_state.user_data[key] = response
            
        elif key == 'digestion':
            options = ["Excellent", "Good", "Fair", "Poor", "Severe issues"]
            default_idx = options.index(st.session_state.user_data.get(key, "Good"))
            response = st.selectbox("", options, index=default_idx, key=f"{key}_{st.session_state.current_step}")
            st.session_state.user_data[key] = response
            
        elif key == 'budget':
            options = ["Low", "Medium", "High", "Premium"]
            default_idx = options.index(st.session_state.user_data.get(key, "Medium"))
            response = st.selectbox("", options, index=default_idx, key=f"{key}_{st.session_state.current_step}")
            st.session_state.user_data[key] = response
            
        else:
            default_val = st.session_state.user_data.get(key, "")
            response = st.text_input("", value=default_val, key=f"{key}_{st.session_state.current_step}")
            st.session_state.user_data[key] = response
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Professional Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.current_step > 0:
            if st.button("← Previous Step", use_container_width=True):
                st.session_state.current_step -= 1
                st.rerun()
    
    with col3:
        if st.session_state.current_step < len(questions) - 1:
            if st.button("Next Step →", use_container_width=True, type="primary"):
                st.session_state.current_step += 1
                st.rerun()
        else:
            if st.button("🎯 Generate AI Plan", use_container_width=True, type="primary"):
                st.session_state.show_results = True
                st.rerun()

# RESULTS PAGE - With Gemini AI
else:
    st.balloons()  # Celebration animation!
    st.success("### ✅ Assessment Complete! Generating Your AI-Powered Ayurvedic Plan...")
    
    # Calculate Wellness Score
    def calculate_wellness_score(user_data):
        sleep = int(user_data.get('sleep_quality', 5))
        energy = int(user_data.get('energy_level', 5))
        stress = 10 - int(user_data.get('stress_level', 5))
        digestion_map = {"Excellent": 10, "Good": 8, "Fair": 6, "Poor": 4, "Severe issues": 2}
        digestion = digestion_map.get(user_data.get('digestion', 'Fair'), 6)
        
        total = (sleep + energy + stress + digestion) / 4
        return min(10, max(1, total))
    
    wellness_score = calculate_wellness_score(st.session_state.user_data)
    
    # Display Wellness Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏆 Wellness Score", f"{wellness_score:.1f}/10")
    with col2:
        st.metric("😴 Sleep Quality", f"{st.session_state.user_data.get('sleep_quality', 5)}/10")
    with col3:
        st.metric("💪 Energy Level", f"{st.session_state.user_data.get('energy_level', 5)}/10")
    with col4:
        st.metric("😌 Stress Level", f"{st.session_state.user_data.get('stress_level', 5)}/10")
    
    # Prepare data for Gemini AI
    user_profile = f"""
    COMPREHENSIVE USER PROFILE FOR AYURVEDIC ASSESSMENT:
    
    PERSONAL DETAILS:
    - Name: {st.session_state.user_data.get('name', 'User')}
    - Age: {st.session_state.user_data.get('age', 'Not specified')} years
    - Weight: {st.session_state.user_data.get('weight', 'Not specified')} kg
    - Height: {st.session_state.user_data.get('height', 'Not specified')} cm
    - Gender: {st.session_state.user_data.get('gender', 'Not specified')}
    
    HEALTH CONCERNS:
    - Main Concerns: {', '.join(st.session_state.user_data.get('main_health_concerns', ['General wellness']))}
    - Symptom Severity: {st.session_state.user_data.get('symptom_severity', '5')}/10
    - Duration: {st.session_state.user_data.get('duration', 'Not specified')}
    - Previous Treatments: {st.session_state.user_data.get('previous_treatments', 'None')}
    
    LIFESTYLE METRICS:
    - Sleep Quality: {st.session_state.user_data.get('sleep_quality', '5')}/10
    - Energy Level: {st.session_state.user_data.get('energy_level', '5')}/10
    - Stress Level: {st.session_state.user_data.get('stress_level', '5')}/10
    - Digestion: {st.session_state.user_data.get('digestion', 'Fair')}
    - Exercise: {st.session_state.user_data.get('exercise', 'Weekly')}
    
    DIETARY PROFILE:
    - Diet Type: {st.session_state.user_data.get('diet_type', 'Vegetarian')}
    - Water Intake: {st.session_state.user_data.get('water_intake', '6')} glasses/day
    - Food Preferences: {st.session_state.user_data.get('food_preferences', 'None')}
    - Eating Pattern: {st.session_state.user_data.get('eating_pattern', 'Regular')}
    
    WELLNESS GOALS:
    - Primary Goal: {st.session_state.user_data.get('primary_goal', 'Overall wellness')}
    - Time Commitment: {st.session_state.user_data.get('time_commitment', '30 minutes')}/day
    - Budget: {st.session_state.user_data.get('budget', 'Medium')}
    - Expectations: {st.session_state.user_data.get('expectations', 'Improved health')}
    
    WELLNESS SCORE: {wellness_score}/10
    """
    
    # Gemini AI Prompt
    prompt = f"""
    ACT as Dr. Ayurveda AI - a senior Ayurvedic practitioner with 25+ years experience.
    
    USER PROFILE:
    {user_profile}
    
    AVAILABLE HERBS DATABASE:
    {json.dumps(HERBS_DATABASE, indent=2)}
    
    Create a COMPREHENSIVE, PERSONALIZED Ayurvedic wellness plan with these EXACT sections:
    
    🌿 **HERBAL PRESCRIPTION**
    - Select 3-5 most suitable herbs from the database for this user's specific concerns
    - Provide exact dosages based on user's weight {st.session_state.user_data.get('weight', 70)}kg
    - Specific timing (morning/afternoon/evening) with reasoning
    - Duration and progression plan (4-8 weeks)
    
    📅 **DAILY WELLNESS SCHEDULE** (Dinacharya)
    - Morning routine (5-8 AM) with specific timings
    - Afternoon routine (12-2 PM) 
    - Evening routine (6-8 PM)
    - Bedtime routine (9-10 PM)
    
    🍃 **4-WEEK TRANSFORMATION PLAN**
    - Week 1: Detox & Foundation Building
    - Week 2: Strengthening & Symptom Relief
    - Week 3: Optimization & Balance
    - Week 4: Maintenance & Progress Assessment
    
    ⚠️ **SAFETY & PRECAUTIONS**
    - Specific contraindications based on user profile
    - Herb-drug interaction warnings
    - Side effects monitoring guide
    - When to consult a practitioner
    
    💡 **LIFESTYLE RECOMMENDATIONS**
    - Dietary adjustments for their diet type
    - Exercise suggestions based on their frequency
    - Stress management techniques
    - Sleep optimization strategies
    
    Format with clear headings, use emojis, and provide actionable, specific advice.
    Be very precise about dosages in mg/grams and exact timing.
    Reference specific herbs from the database provided.
    """
    
    # UPDATED GEMINI CODE WITH WORKING MODELS
    if gemini_connected:
        try:
            with st.spinner("🧠 AI Doctor is analyzing your profile..."):
                # Try all available model names
                model_names = [
                    'gemini-1.5-flash',
                    'gemini-1.5-flash-001',
                    'gemini-1.5-pro',
                    'gemini-1.5-pro-001',
                    'gemini-1.0-pro',
                    'gemini-1.0-pro-001',
                    'gemini-pro',
                    'models/gemini-pro'
                ]
                
                ai_plan = None
                successful_model = None
                
                for model_name in model_names:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        ai_plan = response.text
                        successful_model = model_name
                        break
                    except Exception as model_error:
                        continue
                
                if ai_plan:
                    st.sidebar.success(f"✅ AI Model: {successful_model}")
                else:
                    ai_plan = """
🌿 **Ayurvedic Wellness Plan**

**Based on your assessment, here are personalized recommendations:**

**Top Herbs for Your Concerns:**
- Ashwagandha: 500mg twice daily (stress & energy)
- Turmeric: 500mg with meals (inflammation)  
- Brahmi: 300mg morning (mental clarity)
- Triphala: 1g at bedtime (digestion)

**Daily Schedule:**
- **6-7 AM:** Wake up, warm water with lemon + Ashwagandha
- **12-1 PM:** Lunch with Turmeric
- **6-7 PM:** Brahmi with honey
- **9-10 PM:** Triphala with warm water

**Note:** Gemini AI is currently unavailable. This is a sample plan.
                    """
                    st.sidebar.warning("🤖 Using sample plan (AI unavailable)")
                    
        except Exception as e:
            st.error(f"⚠️ AI Error: {str(e)}")
            ai_plan = "### 🔌 AI service temporarily unavailable. Please try again later."
    else:
        ai_plan = "### 🔌 Connect Gemini API in secrets.toml for AI-powered recommendations."
    
    # Display AI Plan
    st.markdown('<div class="recommendation-card">', unsafe_allow_html=True)
    st.markdown("## 🌟 Your AI-Powered Ayurvedic Wellness Plan")
    st.markdown("---")
    st.markdown(ai_plan)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Herb Reference Guide
    with st.expander("🌿 Herb Reference Guide (Click to Expand)"):
        st.markdown("### Common Ayurvedic Herbs & Their Uses")
        cols = st.columns(2)
        for idx, (herb, info) in enumerate(HERBS_DATABASE.items()):
            with cols[idx % 2]:
                st.markdown(f'<div class="herb-card">', unsafe_allow_html=True)
                st.markdown(f"**{herb}**")
                st.markdown(f"*Benefits:* {', '.join(info['benefits'][:3])}")
                st.markdown(f"*Dosage:* {info['dosage']}")
                st.markdown(f"*Safety:* {info['safety'][:50]}...")
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Action Buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 New Assessment", use_container_width=True):
            st.session_state.current_step = 0
            st.session_state.user_data = {}
            st.session_state.show_results = False
            st.rerun()
    
    with col2:
        if st.button("📄 Save This Plan", use_container_width=True):
            st.success("💾 Plan saved to your session! (Add database for permanent storage)")
    
    with col3:
        if st.button("📊 View My Profile", use_container_width=True):
            st.json(st.session_state.user_data)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <i>🌿 Ancient Wisdom × Modern AI • Personalized Ayurvedic Wellness • Always consult healthcare providers for medical advice</i>
</div>
""", unsafe_allow_html=True)