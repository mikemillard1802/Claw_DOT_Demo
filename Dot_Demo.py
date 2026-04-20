 """
   Louisiana DOT Permitting Automation Demo
   Enhanced Version with Human-in-the-Loop Checkpoints
   Run: streamlit run Dot_Demo.py
   """

   import streamlit as st
   import time
   from datetime import datetime, timedelta

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # LOUISIANA DOT BRANDING
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   LA_DOT_BLUE = "#004C97"
   LA_DOT_GOLD = "#F7C600"
   LA_DOT_RED = "#C8102E"

   st.set_page_config(
       page_title="Louisiana DOT | Permitting Portal",
       page_icon="🚦",
       layout="wide",
       initial_sidebar_state="expanded"
   )

   # Custom CSS
   st.markdown(f"""
   <style>
       .main {{ background-color: #f5f5f5; }}
       h1, h2, h3 {{ color: {LA_DOT_BLUE}; font-family: 'Arial', sans-serif; }}
       .stButton>button {{
           background-color: {LA_DOT_BLUE};
           color: white;
           border: 2px solid {LA_DOT_BLUE};
           font-weight: bold;
       }}
       .stButton>button:hover {{
           background-color: white;
           color: {LA_DOT_BLUE};
       }}
       .permit-card {{
           background: white;
           border-left: 4px solid {LA_DOT_BLUE};
           padding: 15px;
           margin: 10px 0;
           border-radius: 5px;
           box-shadow: 0 2px 5px rgba(0,0,0,0.1);
       }}
       .status-badge {{
           display: inline-block;
           padding: 5px 15px;
           border-radius: 20px;
           font-weight: bold;
           font-size: 0.9em;
       }}
   </style>
   """, unsafe_allow_html=True)

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # AGENT DEFINITIONS
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   AGENTS = {
       "orchestrator": {"name": "🧠 Orchestrator Agent", "role": "Central Coordination"},
       "intake": {"name": "📥 Intake Agent", "role": "Application Ingestion"},
       "compliance": {"name": "⚖️ Compliance Agent", "role": "Regulatory Review"},
       "risk": {"name": "💰 Risk Agent", "role": "Risk Analysis"},
       "approval": {"name": "✅ Approval Agent", "role": "Final Approval"},
       "audit": {"name": "📊 Audit Agent", "role": "Process Logging"}
   }

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # PERMIT TYPES
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   PERMIT_TYPES = [
       "Overweight/Overdimensional Load Permit",
       "Utility Permit",
       "Driveway/Curb Cut Permit",
       "Right-of-Way Permit",
       "Construction Permit",
       "Event Permit"
   ]

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # WORKFLOW STAGES
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   WORKFLOW_STAGES = [
       {"id": 1, "name": "INTAKE & VALIDATION", "agent": "intake", "duration": "0-2 hours",
        "hil_required": True, "hil_description": "Review application completeness"},
       {"id": 2, "name": "COMPLIANCE REVIEW", "agent": "compliance", "duration": "2-24 hours",
        "hil_required": True, "hil_description": "Verify regulatory compliance"},
       {"id": 3, "name": "RISK ASSESSMENT", "agent": "risk", "duration": "24-48 hours",
        "hil_required": True, "hil_description": "Evaluate financial and safety risks"},
       {"id": 4, "name": "FINAL APPROVAL", "agent": "approval", "duration": "48-72 hours",
        "hil_required": True, "hil_description": "Final sign-off and permit issuance"}
   ]

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # SESSION STATE
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   if 'permits' not in st.session_state:
       st.session_state.permits = []
   if 'workflow_stage' not in st.session_state:
       st.session_state.workflow_stage = 0
   if 'hil_approvals' not in st.session_state:
       st.session_state.hil_approvals = {}

   def generate_permit_id():
       return f"LA-{datetime.now().strftime('% Y')}-{int(time.time()) % 10000:05d}"

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # HEADER
   # ──────────────────────────────── ──────────────────────────────── ─────────────
 col1, col2 = st.columns([3, 1])
   with col1:
       st.title("🚦 Louisiana DOT Permitting Portal")
       st.markdown("**AI-Powered Automated Permitting System**")
   with col2:
       st.markdown("### Louisiana DOT")
       st.caption("Excellence in Transportation")

   st.markdown("---")

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # SIDEBAR
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   with st.sidebar:
       st.markdown("### About This Demo")
       st.info("""
       **eXodite AI - Claw Orchestrator**

       This demo showcases AI swarm automation for Louisiana DOT permitting.

       **Target:** 80% automation, 3-5 day processing
       **Status:** 🟢 Beta Demo Mode
       """)

       st.markdown("### Demo Controls")
       if st.button("🗑️ Clear All Data"):
           st.session_state.permits = []
           st.session_state.current_application = None
           st.session_state.workflow_stage = 0
           st.session_state.hil_approvals = {}
           st.rerun()

       st.markdown("---")
       st.caption(f"Session: {datetime.now().strftime('%Y-%m- %d %H:%M')}")

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # HELPER FUNCTIONS
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   def generate_permit_id():
       """Generate a unique permit ID."""
       return f"LA-{datetime.now().strftime('% Y')}-{int(time.time()) % 10000:05d}"

   def simulate_agent_processing(agent_ name, duration=1.5):
       """Simulate agent processing with a spinner."""
       with st.spinner(f"🤖 {agent_name} is working..."):
           time.sleep(duration)

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # MAIN TABS
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   tab1, tab2, tab3, tab4 = st.tabs(["📝 Apply", "📋 My Permits", "🔍 Track", "📊 Dashboard"])

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # TAB 1: APPLY
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   with tab1:
       st.header("Apply for a Permit")
       st.markdown("Complete the form below to initiate the AI-powered permitting workflow.")

       with st.form("permit_application"):
           st.subheader("1. Applicant Information")
           col1, col2 = st.columns(2)
           with col1:
               applicant_name = st.text_input("Company/Individual Name *", placeholder="e.g., Acme Construction LLC")
               contact_email = st.text_input("Email Address *", placeholder="name@example.com")
               phone = st.text_input("Phone Number", placeholder="(555) 123-4567")
           with col2:
               address = st.text_input("Street Address *", placeholder="123 Main St")
               city = st.text_input("City *", placeholder="Baton Rouge")
               zip_code = st.text_input("ZIP Code *", placeholder="70801")

           st.subheader("2. Permit Details")
           permit_type = st.selectbox("Permit Type *", PERMIT_TYPES)
           project_location = st.text_input("Project Location (Route/Parish) *", placeholder="I-10, Mile Marker 152")
           estimated_value = st.number_input("Estimated Project Value ($)", min_value=0, value=10000, step=1000)

           st.subheader("3. Project Description")
           project_desc = st.text_area("Describe the scope of work *", height=100, placeholder="Briefly describe the
 work to be performed...")

           st.subheader("4. Supporting Documents")
           uploaded_files = st.file_uploader("Upload drawings, maps, or insurance certs (Simulated)",
 accept_multiple_files=True)

           submitted = st.form_submit_button("Submit Application", type="primary", use_container_width=True)

           if submitted:
               if not applicant_name or not contact_email or not address or not city or not project_location or not
  project_desc = st.text_area(
       "Describe the scope of work *",
       height=100,
       placeholder="Briefly describe the work to be performed..."
   )

   st.subheader("4. Supporting Documents")
   uploaded_files = st.file_uploader(
       "Upload drawings, maps, or insurance certs (Simulated)",
       accept_multiple_files=True
   )

   submitted = st.form_submit_button("Submit Application", type="primary", use_container_width=True)

   if submitted:
       # Validation
       if not applicant_name or not contact_email or not address or not city or not project_location or not
 project_desc:
           st.error("❌ Please fill in all required fields marked with *.")
       else:
           # Create permit record
           permit_id = generate_permit_id()
           full_address = f"{address}, {city}, {zip_code}"

           st.session_state.current_application = {
               "id": permit_id,
               "type": permit_type,
               "applicant": applicant_name,
               "email": contact_email,
               "phone": phone,
               "address": full_address,
               "location": project_location,
               "value": estimated_value,
               "description": project_desc,
               "files": uploaded_files,
               "submitted_at": datetime.now(),
               "stage_index": 0,
               "status": "Stage 1: Intake",
               "hil_approvals": {}
           }

           # Add to session state
           st.session_state.permits.append( st.session_state.current_applica tion)
           st.session_state.hil_approvals = {}  # Reset HIL for new app

           st.success(f"✅ Application Submitted! Permit ID: **{permit_id}**")
           st.info("🚀 The AI Swarm is now processing your application. Proceed to the 'Track' tab to monitor
 progress.")

           # Simulate initial intake
           simulate_agent_processing("📥 Intake Agent", 2)

           # Advance to next stage
           st.session_state.workflow_stage = 1
           st.rerun()

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # TAB 2: MY PERMITS
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   with tab2:
       st.header("My Permits")

       if not st.session_state.permits:
           st.info("📭 No permits found. Submit an application in the 'Apply' tab.")
       else:
           for permit in reversed(st.session_state.permit s):
               with st.container():
                   st.markdown(
                       f"""
                       <div class="permit-card">
                           <h3>{permit['id']} - {permit['type']}</h3>
                           <p><strong>Applicant:</strong> {permit['applicant']}</p>
                           <p><strong>Status:</strong> <span class="status-badge" style="background-color: #e3f2fd;
 color: #0d47a1;">{permit['status']}</span></p>
                           <p><strong>Submitted:</strong> {permit['submitted_at'].strftime ('%Y-%m-%d %H:%M')}</p>
                       </div>
                       """,
                       unsafe_allow_html=True
                   )

                   # Expandable details
                   with st.expander("View Details & Workflow"):
                       st.write(f"**Location:** {permit['location']}")
                       st.write(f"**Value:** ${permit['value']:,.2f}")
                       st.write(f"**Description:** {permit['description']}")

                       # Show HIL status
                       st.markdown("**Human-in-the-Loop Checkpoints:**")
                       for i, stage in enumerate(WORKFLOW_STAGES):
                           stage_id = f"stage_{i}"
                           if stage_id in permit.get('hil_approvals', {}):
                               st.success(f"✅ Stage {i+1} ({stage['name']}) Approved by Human")
                           elif i <= permit.get('stage_index', 0):
                               st.warning(f"⏳ Stage {i+1} ({stage['name']}) Awaiting HIL Approval")
                           else:
                               st.info(f"⏪ Stage {i+1} ({stage['name']}) Pending")

   # ──────────────────────────────── ──────────────────────────────── ─────────────
  # TAB 3: TRACK (Interactive Workflow)
  # ──────────────────────────────── ──────────────────────────────── ─────────────
  with tab3:
       st.header("🔍 Track Application Status")
       if not st.session_state.permits:
           st.warning("📭 No active applications. Please apply first in the 'Apply' tab.")
       else:
           # Select permit to track
           permit_options = [p['id'] for p in st.session_state.permits]
           selected_id = st.selectbox("Select Permit ID", permit_options)

           # Find the selected permit data
           current_permit = next((p for p in st.session_state.permits if p['id'] == selected_id), None)

           if current_permit:
               st.markdown(f"### Tracking: {selected_id}")

               # Render the interactive workflow progress
               render_workflow_progress(
                   current_permit.get('stage_index' , 0),
                   current_permit.get('hil_approval s', {})
               )

               # Simulation Controls (For Demo Purposes)
               st.markdown("### 🎮 Demo Control Panel")
               st.caption("Use these controls to simulate the AI Agent processing and Human approvals.")

               current_idx = current_permit.get('stage_index' , 0)

               # Safe access to stage name and agent
               if current_idx < len(WORKFLOW_STAGES):
                   stage_name = WORKFLOW_STAGES[current_idx]['na me']
                   agent_name = WORKFLOW_STAGES[current_idx]['ag ent']

                   col_sim1, col_sim2 = st.columns(2)

                   with col_sim1:
                       if st.button(f"🤖 Simulate AI: {agent_name.title()}", use_container_width=True):
                           with st.spinner(f"Running {agent_name}..."):
                               time.sleep(2)  # Simulate work
                           st.success(f"✅ {stage_name} Complete. Awaiting Human Approval.")
                           st.rerun()

                   with col_sim2:
                       stage_key = f"stage_{current_idx}"
                       if st.button(f"✅ Human Approve Stage {current_idx+1}", use_container_width=True):
                           # Update HIL status
                           if 'hil_approvals' not in current_permit:
                               current_permit['hil_approvals'] = {}
                           current_permit['hil_approvals'][ stage_key] = True

                           # Advance workflow
                           if current_idx < len(WORKFLOW_STAGES) - 1:
                               current_permit['stage_index'] += 1
                               next_stage = WORKFLOW_STAGES[current_permit[' stage_index']]['name']
                               current_permit['status'] = f"Stage {current_permit['stage_index']+1}: {next_stage}"

                               # Final check
                               if current_permit['stage_index'] == len(WORKFLOW_STAGES) - 1:
                                   current_permit['status'] = "✅ PERMIT ISSUED"

                           st.success("Approval Recorded! Workflow advanced.")
                           st.rerun()
               else:
                   st.success("🎉 Workflow Complete! Permit has been issued.")

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # TAB 4: DASHBOARD (Metrics)
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   with tab4:
       st.header("📊 Performance Dashboard")

       # Calculate metrics from session data
       total_permits = len(st.session_state.permits)
       issued_permits = len([p for p in st.session_state.permits if 'ISSUED' in p.get('status', '')])
       automation_rate = 85  # Simulated target

       # Top Level Metrics
       col1, col2, col3, col4 = st.columns(4)
       col1.metric("Total Applications", total_permits)
       col2.metric("Permits Issued", issued_permits)
       col3.metric("Avg. Processing Time", "3.2 Days", "-12%")
       col4.metric("Automation Rate", f"{automation_rate}%", "Target: 80%")

       st.markdown("---")

       # Agent Performance Visualization
       st.subheader("🤖 Agent Swarm Performance")
       c1, c2 = st.columns(2)

       with c1:
           st.markdown("**Processing Speed by Agent**")
           st.progress(95, text="📥 Intake Agent: 95% Efficiency")
           st.progress(88, text="⚖️ Compliance Agent: 88% Efficiency")
           st.progress(92, text="💰 Risk Agent: 92% Efficiency")
           st.progress(97, text="✅ Approval Agent: 97% Efficiency")
           st.progress(100, text="📊 Audit Agent: 100% Accuracy")

       with c2:
           st.markdown("**Human-in-the-Loop Stats**")
           st.metric("HIL Interventions", "12", "Last 24h")
           st.metric("Avg. HIL Wait Time", "45 mins")
           st.metric("Escalation Rate", "3.2%", "Low Risk")

           st.markdown("---")
           st.subheader("💰 Cost Savings Estimate")
           st.info("""
           **Estimated Savings per Permit:** $150
           **Total Demo Savings:** $0.00 (Demo Mode)
           **Projected Annual Savings:** $1.5M (at 10k permits)
           """)

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # FOOTER
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   st.markdown("---")
   st.caption("© 2026 Louisiana Department of Transportation | Powered by eXodite AI & OpenClaw | v2.0 Beta")
   st.caption("Disclaimer: This is a demonstration environment. No real permits are issued.")
 ```

