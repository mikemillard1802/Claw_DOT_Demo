"""
Louisiana DOT Permitting Automation Demo
Streamlit web app for beta testing

Run: streamlit run dot_demo.py
"""
import streamlit as st
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="Louisiana DOT Permitting Demo",
    page_icon="🚦",
    layout="wide"
)

# Set API keys from secrets (cloud LLM only)
for key in ["GROQ_API_KEY"]:
    if key in st.secrets:
        os.environ[key] = st.secrets[key]

# Cloud LLM (Groq — fast, reliable for public deploy)
llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=0.1,
)

# Wrapped search tool
@tool("DuckDuckGo Search")
def duckduckgo_search(query: str) -> str:
    """Search the web for real-time signals."""
    return DuckDuckGoSearchRun().run(query)

# Demo data
PERMIT_TYPES = [
    "Overweight/Overdimensional Load Permit",
    "Utility Permit",
    "Driveway/Curb Cut Permit",
    "Right-of-Way Permit",
    "Construction Permit",
    "Event Permit"
]


st.title("🚦 Louisiana DOT Permitting Portal")
st.markdown("**AI-Powered Automated Permitting Demo**")

# Sidebar
with st.sidebar:
    st.header("About")
    st.info("""
    **eXodite AI - Opportunity Identifier Claw**
    
    This demo showcases the AI swarm solution for Louisiana DOT permitting automation.
    
    **Target:** 80% automation, 3-5 day processing
    """)
    
    st.header("Demo Mode")
    if GROK_API_KEY == "demo-mode":
        st.warning("Running in demo mode (no API key)")
    else:
        st.success("API Connected")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Apply", "📋 My Permits", "🔍 Track", "📊 Dashboard"])

# TAB 1: Apply for permit
with tab1:
    st.header("Apply for a Permit")
    
    with st.form("permit_application"):
        col1, col2 = st.columns(2)
        
        with col1:
            applicant_name = st.text_input("Company/Individual Name")
            contact_email = st.text_input("Email")
            permit_type = st.selectbox("Permit Type", PERMIT_TYPES)
            
        with col2:
            project_desc = st.text_area("Project Description", height=100)
            estimated_value = st.number_input("Project Value ($)", min_value=0, value=10000)
            
        submitted = st.form_submit_button("Submit Application", type="primary")
        
        if submitted:
            st.success(f"✅ Application submitted! Permits: {datetime.now().strftime('%Y%m%d%H%M%S')}")
            st.info("AI agents are now processing your application...")
            
            # Simulate AI processing
            with st.spinner("🤖 PermitIntakeAgent: Validating application..."):
                import time
                time.sleep(1)
            with st.spinner("🤖 ComplianceReviewAgent: Checking regulations..."):
                time.sleep(1)
            with st.spinner("🤖 RiskAssessmentAgent: Evaluating risks..."):
                time.sleep(1)
            with st.spinner("🤖 ApprovalOrchestrator: Routing for approval..."):
                time.sleep(1)
                
            st.success("🎉 Application Approved!")

# TAB 2: My Permits
with tab2:
    st.header("My Permits")
    
    # Demo permits
    demo_permits = [
        {"id": "LA-2026-00123", "type": "Utility Permit", "status": "Approved", "date": "2026-04-10"},
        {"id": "LA-2026-00124", "type": "Construction Permit", "status": "Under Review", "date": "2026-04-15"},
        {"id": "LA-2026-00125", "type": "Driveway Permit", "status": "Pending", "date": "2026-04-17"},
    ]
    
    for permit in demo_permits:
        with st.expander(f"{permit['id']} - {permit['type']}"):
            col1, col2 = st.columns(2)
            col1.write(f"**Status:** {permit['status']}")
            col2.write(f"**Submitted:** {permit['date']}")

# TAB 3: Track
with tab3:
    st.header("Track Application Status")
    
    search_id = st.text_input("Enter Permit ID", placeholder="LA-2026-00123")
    
    if st.button("Track"):
        if search_id:
            st.success(f"Found: {search_id}")
            st.markdown("""
            | Step | Status | Timestamp |
            |------|--------|-----------|
            | Application Received | ✅ | 2026-04-17 09:00 AM |
            | Data Validation | ✅ | 2026-04-17 09:01 AM |
            | Compliance Review | ✅ | 2026-04-17 09:05 AM |
            | Risk Assessment | 🔄 In Progress | - |
            | Final Approval | ⏳ Pending | - |
            """)

# TAB 4: Dashboard
with tab4:
    st.header("Performance Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Applications Processed", "1,247")
    col2.metric("Avg. Processing Time", "3.2 days")
    col3.metric("Automation Rate", "78%")
    col4.metric("Cost Savings", "$2.1M")
    
    st.subheader("Processing Trends")
    st.line_chart({
        "Applications": [120, 135, 142, 156, 168, 175],
        "Automated": [95, 108, 118, 130, 142, 152]
    })
    
    st.subheader("Agent Performance")
    st.progress(95, text="PermitIntakeAgent: 95%")
    st.progress(88, text="ComplianceReviewAgent: 88%")
    st.progress(92, text="RiskAssessmentAgent: 92%")
    st.progress(97, text="ApprovalOrchestrator: 97%")
    st.progress(100, text="AuditTrailAgent: 100%")

# Footer
st.markdown("---")
st.caption(f"eXodite AI Demo | {datetime.now().strftime('%Y-%m-%d')} | v1.0 Beta")
