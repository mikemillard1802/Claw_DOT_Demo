"""Louisiana DOT Permitting Automation Demo
   Enhanced Version with Human-in-the-Loop Checkpoints
   Run: streamlit run dot_demo.py
"""
   import streamlit as st
   import time
   from datetime import datetime, timedelta
   import json

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

   # Custom CSS for Louisiana DOT branding
   st.markdown(f"""
   <style>
       .main {{
           background-color: #f5f5f5;
       }}
       .stApp {{
           background-color: #f5f5f5;
       }}
       h1, h2, h3 {{
           color: {LA_DOT_BLUE};
           font-family: 'Arial', sans-serif;
       }}
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
       .checkpoint-alert {{
           background-color: #fff3cd;
           border-left: 4px solid {LA_DOT_GOLD};
           padding: 15px;
           margin: 10px 0;
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
   # AGENT DEFINITIONS (5-Agent Swarm)
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   AGENTS = {
       "orchestrator": {
           "name": "🧠 Orchestrator Agent",
           "role": "Central Coordination & Human Escalation",
           "tools": ["exec", "message", "process", "browser"],
           "guardrails": ["Workflow state management", "Human checkpoint triggering", "Exception handling"]
       },
       "intake": {
           "name": "📥 Intake Agent",
           "role": "Permit Application Ingestion & Validation",
           "tools": ["read", "web_fetch", "message", "browser"],
           "guardrails": ["Rate limit: 100/hr", "Auto-reject after 3 cycles", "PII redaction"]
       },
       "compliance": {
           "name": "⚖️ Compliance Review Agent",
           "role": "Regulatory Compliance Verification",
           "tools": ["web_search", "read", "exec"],
           "guardrails": ["Flag high-impact for HIL", "Citation trail", "Rate limit: 50/hr"]
       },
       "risk": {
           "name": "💰 Risk Assessment Agent",
           "role": "Financial & Safety Risk Analysis",
           "tools": ["read", "exec", "message"],
           "guardrails": ["Complexity scoring", "Fee calculation", "Insurance validation"]
       },
       "approval": {
           "name": "✅ Approval Agent",
           "role": "Final Approval & Permit Issuance",
           "tools": ["message", "write", "exec", "browser"],
           "guardrails": ["2-of-3 for >$100K", "48h escalation", "Immutable permit ID"]
       },
       "audit": {
           "name": "📊 Audit Trail Agent",
           "role": "Process History & Logging",
           "tools": ["write", "read", "exec"],
           "guardrails": ["Write-only logs", "Daily backups", "7-year retention"]
       }
   }

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # PERMIT TYPES (Louisiana DOT Official)
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
   # WORKFLOW STAGES WITH HIL CHECKPOINTS
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   WORKFLOW_STAGES = [
       {
           "id": 1,
           "name": "INTAKE & VALIDATION",
           "agent": "intake",
           "duration": "0-2 hours",
           "hil_required": True,
           "hil_description": "Review application completeness and required documentation",
           "checks": ["Application completeness", "Required attachments", "Fee calculation", "Applicant verification"]
       },
       {
           "id": 2,
           "name": "COMPLIANCE REVIEW",
           "agent": "compliance",
           "duration": "2-24 hours",
           "hil_required": True,
           "hil_description": "Verify regulatory compliance and flag exceptions",
           "checks": ["LAC 70:V compliance", "Environmental screening", "Right-of-way validation", "Safety standards
 (AASHTO)"]
       },
       {
           "id": 3,
           "name": "RISK ASSESSMENT",
           "agent": "risk",
           "duration": "24-48 hours",
           "hil_required": True,
           "hil_description": "Evaluate financial and safety risks",
           "checks": ["Complexity scoring", "Fee schedule validation", "Insurance verification", "Bond requirements"]
       },
       {
           "id": 4,
           "name": "FINAL APPROVAL",
           "agent": "approval",
           "duration": "48-72 hours",
           "hil_required": True,
           "hil_description": "Final sign-off and permit issuance",
           "checks": ["Multi-level approval", "Digital signature", "Permit generation", "Stakeholder notification"]
       }
   ]

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # SESSION STATE INITIALIZATION
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   if 'permits' not in st.session_state:
       st.session_state.permits = []
   if 'current_application' not in st.session_state:
       st.session_state.current_application = None
   if 'workflow_stage' not in st.session_state:
       st.session_state.workflow_stage = 0
   if 'hil_approvals' not in st.session_state:
       st.session_state.hil_approvals = {}

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # HEADER WITH LOUISIANA DOT BRANDING
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   col1, col2 = st.columns([3, 1])
   with col1:
       st.title("🚦 Louisiana DOT Permitting Portal")
       st.markdown("**AI-Powered Automated Permitting System**")
   with col2:
       st.image("https://www.dotd.louisiana.gov/images/dotd-logo.png", width=150, use_column_width=False)

   st.markdown("---")

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # SIDEBAR
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   with st.sidebar:
       st.image("https://www.dotd.louisiana.gov/images/dotd-logo.png", width=200)
       st.markdown("### About This Demo")
       st.info("""
       **eXodite AI - Opportunity Identifier
 ```



 This everything expo?


 No, Mike! That was only the first 60% of the file! The message got cut off due to length limits. I need to provide you
 with the complete file in a different way.

 Let me give you the full, complete dot_demo.py file in my next message as a single code block you can copy entirely.
 It will include:

 1. ✅ All imports and branding
 2. ✅ Complete 5-agent definitions
 3. ✅ All 4 workflow stages with HIL checkpoints
 4. ✅ Full application form (matching LA DOT fields)
 5. ✅ Interactive HIL approval dialogs
 6. ✅ Permit tracking dashboard
 7. ✅ Agent performance metrics
 8. ✅ Complete footer and closing

 Stand by - sending the complete file in the next message! (I'll break it into 2-3 chunks if needed, but clearly marked
 so you know where to concatenate).

 Should I send it as:
 - Option A: One complete file (may span multiple messages, clearly marked)
 - Option B: Two files (dot_demo_part1.py + dot_demo_part2.py) you concatenate
 - Option C: Just the core logic file, and you modify the existing dot_demo.py manually?

 Which works best for you?


 Pick up here:

 ──────────────────────────────── ──────────────────────────────── ─────────────

 HEADER WITH LOUISIANA DOT BRANDING

 ──────────────────────────────── ──────────────────────────────── ─────────────

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🚦 Louisiana DOT Permitting Portal")
        st.markdown("AI-Powered Automated Permitting System")
    with col2:
        st.image("https://www.dotd.louisiana.gov/images/dotd-logo.png", width=150, use_column_width=False)

    st.markdown("---")

 ──────────────────────────────── ──────────────────────────────── ─────────────

 SIDEBAR

 ──────────────────────────────── ──────────────────────────────── ─────────────

     with st.sidebar:
       st.image("https://www.dotd.louisiana.gov/images/dotd-logo.png", width=200)
       st.markdown("### About This Demo")
       st.info("""
       **eXodite AI - Opportunity Identifier Claw**

       This demo showcases the AI swarm solution for Louisiana DOT permitting automation.

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

   def render_workflow_progress(current _stage_index, approvals):
       """Render the workflow progress bar with HIL checkpoints."""
       st.markdown("### 🔄 Workflow Status")

       for i, stage in enumerate(WORKFLOW_STAGES):
           is_current = i == current_stage_index
           is_completed = i < current_stage_index
           is_pending = i > current_stage_index

           # Determine status icon and color
           if is_completed:
               icon = "✅"
               color = "#28a745"
               status_text = "Completed"
           elif is_current:
               # Check if HIL approval is done for this stage
               stage_id = f"stage_{i}"
               if stage_id in approvals and approvals[stage_id]:
                   icon = "⏳"
                   color = "#17a2b8"
                   status_text = "Processing..."
               else:
                   icon = "🔴"
                   color = "#dc3545"
                   status_text = "Awaiting HIL Approval"
           else:
               icon = "⏪"
               color = "#6c757d"
               status_text = "Pending"

           # Render stage card
           with st.container():
               col1, col2 = st.columns([1, 4])
               with col1:
                   st.markdown(f"### {icon}")
               with col2:
                   st.markdown(f"**{stage['name']}* *")
                   st.markdown(f"*{stage['duration' ]} | Agent: {AGENTS[stage['agent']]['name']} *")
                   if is_current and stage_id not in approvals:
                       st.warning(f"**{stage['hil_descr iption']}**")
                       if st.button(f"✅ Approve Stage {i+1}", key=f"approve_{i}"):
                           st.session_state.hil_approvals[f "stage_{i}"] = True
                           st.rerun()
                   elif is_completed:
                       st.success(status_text)
                   elif is_current and stage_id in approvals:
                       st.info(status_text)
                   else:
                       st.markdown(f"*{status_text}*")
               st.markdown("---")

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # MAIN TABS
   # ──────────────────────────────── ──────────────────────────────── ─────────────
   tab1, tab2, tab3, tab4 = st.tabs(["📝 Apply", "📋 My Permits", "🔍 Track", "📊 Dashboard"])

   # ──────────────────────────────── ──────────────────────────────── ─────────────
   # TAB 1: APPLY (Authentic LA DOT Form)
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
                # Validation
            if not applicant_name or not contact_email or not address or not city or not project_location or not
 
 project_desc:
           st.error("❌ Please fill in all required fields marked with *.")
       else:
           # Create permit record
           permit_id = generate_permit_id()

           # ✅ FIX: Create the full address string first
           full_address = f"{address}, {city}, {zip_code}"

           st.session_state.current_application = {
               "id": permit_id,
               "type": permit_type,
               "applicant": applicant_name,
               "email": contact_email,
               "phone": phone,
               "address": full_address,       # ✅ Correctly uses the variable
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
                   st.markdown(f"""
                   <div class="permit-card">
                       <h3>{permit['id']} - {permit['type']}</h3>
                       <p><strong>Applicant:</strong> {permit['applicant']}</p>
                       <p><strong>Status:</strong> <span class="status-badge" style="background-color: #e3f2fd; color:
 #0d47a1;">{permit['status']}</span></p>
                       <p><strong>Submitted:</strong> {permit['submitted_at'].strftime ('%Y-%m-%d %H:%M')}</p>
                   </div>
                   """, unsafe_allow_html=True)

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

   
