import streamlit as st
import json
import re
import google.generativeai as genai
import requests
from typing import List, Dict
from streamlit_lottie import st_lottie
import os

# --- HELPER FUNCTIONS ---
def normalize_skill(s: str) -> str:
    return s.strip().lower().replace("-", "_").replace(" ", "_")

def interpret_user_skills(skills_text: str) -> List[str]:
    if not skills_text:
        return []
    parts = [normalize_skill(s) for s in skills_text.replace('\n', ',').split(',') if s.strip()]
    return list(dict.fromkeys(parts))

def generate_career_recommendations(profile: dict) -> list:
    try:
        genai.configure(api_key=st.secrets["gemini_api_key"])
    except Exception as e:
        st.error("API key not found. Please set it in .streamlit/secrets.toml")
        return []
    
    prompt = f"""
    You are an AI-powered career advisor for students in India.
    Given the profile:
    Education: {profile['education']}
    Skills: {', '.join(profile['skills'])}
    Interests: {', '.join(profile['interests'])}
    Career Goal: {profile['career_goal']}
    
    Suggest the 3 most relevant career paths. For each, provide:
    - Role name
    - Why it fits this student
    - Missing skills they should learn
    - Example resources (courses, YouTube, GitHub links)

    Return ONLY valid JSON. Do not include explanations, markdown, or code fences.
    Format strictly as:
    [
      {{
        "role": "Role Name",
        "description": "Why this fits",
        "missing_skills": ["skill1", "skill2"],
        "resources": {{
            "skill1": ["title:link"],
            "skill2": ["title:link"]
        }}
      }}
    ]
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    try:
        raw_text = response.text.strip()
        clean_text = re.sub(r"^```json|```$", "", raw_text, flags=re.MULTILINE).strip()
        recommendations = json.loads(clean_text)
        return recommendations
    except Exception as e:
        st.error("⚠️ Could not parse Gemini response — fallback mode.")
        st.write("Raw Gemini output:", response.text)
        return []

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

st.set_page_config(page_title="Profile Form", layout="wide")

if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    st.warning("Please login to access this page.")
    st.stop()
else:
    # Add logo and product name at the top of this page
    logo_col, title_col = st.columns([1, 6])
    with logo_col:
        st.image("Logo.png", use_container_width=False, width=80)
    with title_col:
        st.markdown('<h1 class="app-title">CareerEdge</h1>', unsafe_allow_html=True)
        st.markdown('<p class="app-subtitle">Your personalized career assistant</p>', unsafe_allow_html=True)
    
    st.title("Profile Analysis")
    st.info("Please provide your details to get personalized recommendations.")

    with st.form(key='profile_form'):
        st.markdown('<h3>Step 1 — Tell us about yourself</h3>', unsafe_allow_html=True)
        
        user_profile = st.session_state['users'][st.session_state['username']]['profile']
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full name", value=user_profile.get('name', st.session_state['username'].split('@')[0].capitalize()))
            education_options = ["High School", "Undergraduate", "Postgraduate", "Diploma", "Other"]
            education_index = education_options.index(user_profile.get('education', 'Undergraduate'))
            education = st.selectbox("Highest education", education_options, index=education_index)
            current_year = st.text_input("Current year / specialization (optional)", value=user_profile.get('current_year', ''))
        
        with col2:
            skills_text = st.text_area("List your skills (comma separated). Example: Python, SQL, Machine Learning, HTML", value=", ".join(user_profile.get('user_skills', [])))
            interests = st.text_area("Your interests / topics you like (comma separated). Example: AI, Web, Climate", value=", ".join(user_profile.get('interests_list', [])))
            career_goal = st.text_input("Career goal / dream role (optional)", value=user_profile.get('career_goal', ''))

        submitted = st.form_submit_button("Analyze my profile")
        
    if submitted:
        with st.spinner('Analyzing your profile...'):
            lottie_loading_url = "https://assets8.lottiefiles.com/private_files/lf30_a9q2x37k.json"
            lottie_loading = load_lottieurl(lottie_loading_url)
            if lottie_loading:
                st_lottie(lottie_loading, height=200)

            user_skills = interpret_user_skills(skills_text)
            interests_list = [normalize_skill(x) for x in interests.replace('\n',',').split(',') if x.strip()]
            
            profile = {
                "education": education,
                "skills": user_skills,
                "interests": interests_list,
                "career_goal": career_goal
            }
            recs = generate_career_recommendations(profile)
            
            if recs:
                st.session_state['users'][st.session_state['username']]['profile'] = {
                    'name': name,
                    'education': education,
                    'current_year': current_year,
                    'user_skills': user_skills,
                    'interests_list': interests_list,
                    'career_goal': career_goal,
                    'recs': recs,
                    'all_missing': []
                }
                all_missing = []
                for r in recs:
                    for m in r.get('missing_skills', []):
                        if m not in all_missing:
                            all_missing.append(m)
                st.session_state['users'][st.session_state['username']]['profile']['all_missing'] = all_missing
                st.success("Analysis complete! Head over to the Results page to see your recommendations.")
            else:
                st.info("No recommendations. Please refine your profile or try again.")