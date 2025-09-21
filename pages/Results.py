import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict
import os

# --- HELPER FUNCTIONS ---
def build_learning_roadmap(missing_skills: List[str]) -> List[Dict]:
    roadmap = []
    for skill in missing_skills:
        roadmap.append({
            "skill": skill,
            "sequence": [
                {"title": f"Foundations of {skill}", "type": "course", "duration_weeks": 2},
                {"title": f"Intermediate {skill} (hands-on)", "type": "course", "duration_weeks": 4},
                {"title": f"Project: Build a {skill} project", "type": "project", "duration_weeks": 3}
            ]
        })
    return roadmap

st.set_page_config(page_title="Career Results", layout="wide")

if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    st.warning("Please login to access this page.")
    st.stop()

profile_data = st.session_state['users'][st.session_state['username']]['profile']

if not profile_data:
    st.warning("Please submit your profile on the 'Profile Form' page first.")
    st.stop()

# Add logo and product name at the top of this page
logo_col, title_col = st.columns([1, 6])
with logo_col:
    st.image("Logo.png", use_container_width=False, width=80)
with title_col:
    st.markdown('<h1 class="app-title">CareerEdge</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Your personalized career assistant</p>', unsafe_allow_html=True)

st.markdown(f'<h1 class="app-title">Career Path & Roadmap</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="app-subtitle">Your personalized insights are ready to explore.</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Career Recommendations", "Learning Roadmap", "Progress Tracker"])

with tab1:
    st.markdown(f'<h2 class="section-title">Career Recommendations</h2>', unsafe_allow_html=True)
    for r in profile_data['recs']:
        st.markdown(f'<div class="career-card">', unsafe_allow_html=True)
        st.markdown(f"<h3>{r['role']}</h3>", unsafe_allow_html=True)
        st.write(f"**Why it fits:** {r['description']}")
        st.write("**Missing skills:**")
        st.markdown(f'<div class="skill-tags">', unsafe_allow_html=True)
        for skill in r.get('missing_skills', []):
            st.markdown(f'<span class="skill-tag missing-skill">{skill}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("**Recommended resources:**")
        for skill, reslist in r['resources'].items():
            st.markdown(f"**{skill.capitalize()}:**", unsafe_allow_html=True)
            for item in reslist[:3]:
                if ":" in item:
                    title, link = item.split(":", 1)
                    st.markdown(f"- <a href='{link.strip()}' target='_blank' class='resource-link'>{title.strip()}</a>", unsafe_allow_html=True)
                else:
                    st.markdown(f"- {item}")
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown(f'<h2 class="section-title">Learning Roadmap</h2>', unsafe_allow_html=True)
    roadmap = build_learning_roadmap(profile_data['all_missing'])
    for step in roadmap:
        st.markdown(f"<h4>{step['skill']}</h4>", unsafe_allow_html=True)
        for seq in step['sequence']:
            st.write(f"- **{seq['title']}** — {seq['type']}, est. {seq['duration_weeks']} weeks")
    
with tab3:
    st.markdown(f'<h2 class="section-title">Progress Tracker</h2>', unsafe_allow_html=True)
    
    if 'progress' not in st.session_state:
        st.session_state['progress'] = {}
    
    all_skills = profile_data['user_skills'] + profile_data['all_missing']
    
    for skill in all_skills:
        if skill not in st.session_state['progress']:
            st.session_state['progress'][skill] = False
    
    progress_df = pd.DataFrame([
        {'Skill': s.capitalize(), 'Status': 'Completed' if st.session_state['progress'][s] else 'Pending'}
        for s in st.session_state['progress'].keys()
    ])
    
    completed_count = len(progress_df[progress_df['Status'] == 'Completed'])
    total_count = len(progress_df)
    
    col_chart, col_bar = st.columns(2)
    with col_chart:
        fig = px.pie(progress_df, names='Status', title='Overall Progress', 
                     color='Status', color_discrete_map={'Completed': '#6a1b9a', 'Pending': '#e0e0e0'})
        fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#fff', width=2)))
        st.plotly_chart(fig, use_container_width=True)
    
    with col_bar:
        status_counts = progress_df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig_bar = px.bar(status_counts, x='Status', y='Count', color='Status', title='Skills Breakdown',
                         color_discrete_map={'Completed': '#6a1b9a', 'Pending': '#e0e0e0'})
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.write(f"**Progress:** {completed_count} / {total_count} skills completed.")
    
    st.write("Mark your skills as completed below:")
    for skill in st.session_state['progress'].keys():
        st.session_state['progress'][skill] = st.checkbox(f"**Completed:** {skill.capitalize()}", value=st.session_state['progress'][skill], key=f"checkbox_{skill}")
            
    st.success("Analysis complete — use the roadmap and resources to plan your next 3 months.")