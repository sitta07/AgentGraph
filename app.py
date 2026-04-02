import streamlit as st
import streamlit.components.v1 as components
import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.prompts import FINAL_SESSION_SUMMARY_PROMPT

# ==========================================
# CUSTOM CSS - High Contrast & Vibrant Dashboard
# ==========================================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {background-color: #f8fafc;}
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        color: #0f172a;
    }
    
    /* High Contrast Typography */
    h1 {font-weight: 700 !important; color: #0f172a !important; letter-spacing: -0.02em !important;}
    h2 {font-weight: 600 !important; color: #1e293b !important; margin-top: 1rem !important; margin-bottom: 0.75rem !important;}
    h3 {font-weight: 600 !important; color: #334155 !important;}
    
    p, li, .stMarkdown {color: #1e293b !important; font-size: 0.95rem !important; line-height: 1.6 !important;}
    
    /* Tighter Layout */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06);
    }
    
    /* Agent Container Styles with Color Coding */
    .architect-container {
        border-left: 4px solid #3b82f6 !important;
        background-color: #eff6ff !important;
    }
    
    .security-container {
        border-left: 4px solid #ef4444 !important;
        background-color: #fef2f2 !important;
    }
    
    .evaluator-container {
        border-left: 4px solid #8b5cf6 !important;
        background-color: #f5f3ff !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    /* Chat Message Styling */
    div[data-testid="stChatMessage"] {
        background-color: white;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06);
    }
    
    /* Better Blockquotes */
    blockquote {
        border-left: 3px solid #cbd5e1 !important;
        padding-left: 1rem !important;
        margin: 0.5rem 0 !important;
        color: #334155 !important;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetric"] {
        background: white;
        padding: 0.75rem;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
    }
    
    /* Success/Warning/Info boxes */
    .stSuccess, .stWarning, .stInfo {
        border-radius: 6px !important;
        padding: 0.75rem 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SETUP: Load Environment Variables
# ==========================================
load_dotenv()
if not os.getenv("NOVITA_API_KEY"):
    st.error("NOVITA_API_KEY not found in .env file!")
    st.stop()

from main import build_graph

# ==========================================
# UI SETUP: Configure Streamlit page
# ==========================================
st.set_page_config(
    page_title="AgentGraph",
    layout="wide",
    page_icon="◆",
    initial_sidebar_state="expanded"
)

# ==========================================
# SIDEBAR: Configuration & User Input
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    st.markdown("### 📝 System Requirements")
    user_req = st.text_area(
        "Define your system",
        value="Design a RAG chatbot system for a corporate environment supporting 1,000 concurrent users with monthly cost estimation in Thai Baht",
        height=120,
        label_visibility="collapsed",
        placeholder="Describe your system requirements..."
    )
    
    st.divider()
    
    st.markdown("### 💰 Monthly Budget (THB)")
    user_monthly_budget_thb = st.number_input(
        "Operating budget",
        min_value=0.0,
        value=float(os.getenv("DEFAULT_BUDGET_THB", 5000.0)),
        step=1000.0,
        label_visibility="collapsed",
        help="Reference budget for architect to design cost-effective solutions"
    )
    
    st.markdown(f"""
    <div style="background: #f5f5f5; border-radius: 8px; padding: 12px; font-size: 0.9rem; color: #555;">
        <strong>Budget Reference</strong><br>
        ฿{user_monthly_budget_thb:,.2f}/month<br>
        <span style="font-size: 0.8rem; color: #888;">Cost-effective design target</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    start_btn = st.button("▶ Start Design Session", type="primary", use_container_width=True)
    
    st.divider()
    
    st.markdown("### 🤖 Agents")
    agent_cols = st.columns(3)
    with agent_cols[0]:
        st.markdown("<div style='text-align: center;'><span style='font-size: 1.5rem;'>🏗️</span><br><small>Architect</small></div>", unsafe_allow_html=True)
    with agent_cols[1]:
        st.markdown("<div style='text-align: center;'><span style='font-size: 1.5rem;'>🛡️</span><br><small>Security</small></div>", unsafe_allow_html=True)
    with agent_cols[2]:
        st.markdown("<div style='text-align: center;'><span style='font-size: 1.5rem;'>⚖️</span><br><small>Evaluator</small></div>", unsafe_allow_html=True)

# ==========================================
# MAIN CONTENT AREA
# ==========================================

# Professional Empty State (shown before execution)
if not start_btn:
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; color: #666;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">◆</div>
        <h1 style="font-weight: 300; margin-bottom: 0.5rem;">AgentGraph</h1>
        <p style="font-size: 1.1rem; color: #888; max-width: 500px; margin: 0 auto;">
            AI-powered multi-agent system for real-time architecture design, 
            security evaluation, and cost optimization.
        </p>
        <div style="margin-top: 2rem; padding: 1.5rem; background: white; border-radius: 12px; display: inline-block; text-align: left;">
            <p style="margin: 0; color: #666; font-size: 0.9rem;">
                <strong>How it works:</strong><br><br>
                1. Define your system requirements and budget<br>
                2. Architect agent designs your system with Mermaid diagrams<br>
                3. Security agent identifies vulnerabilities<br>
                4. Evaluator scores the design (target: ≥9.5/10)<br>
                5. Iterate until approved or max revisions reached
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# EXECUTION: Main logic when start button is clicked
# ==========================================
if start_btn:
    # Header for active session
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.markdown("## Design Session Active")
    with col_header2:
        st.markdown(f"<div style='text-align: right; color: #888; font-size: 0.9rem;'>Budget: ฿{user_monthly_budget_thb:,.0f}/month</div>", unsafe_allow_html=True)
    
    st.divider()
    
    app_graph = build_graph()
    
    # Initialize state
    initial_state = {
        "messages": [],
        "user_requirements": user_req,
        "revision_count": 0,
        "feedback": "",
        "is_passed": False,
        "evaluation_score": 0.0,
        "is_mermaid_valid": True,
        "history_outputs": [],
        "history_scores": [],
        "history_feedback": [],
        "stop_reason": "",
        "budget_context": user_monthly_budget_thb
    }
    
    # Create container for chat-like UI display
    chat_container = st.container()
    
    # Track iterations
    iterations_completed = 0
    final_score = 0.0
    final_passed = False
    session_messages = []  # Collect all messages for final summary
    
    with st.spinner("Agents collaborating on your architecture..."):
        # Stream graph updates in real-time
        for output in app_graph.stream(initial_state, stream_mode="updates"):
            for node_name, state_update in output.items():
                
                # Display agent messages
                if "messages" in state_update and len(state_update["messages"]) > 0:
                    latest_msg = state_update["messages"][-1].content
                    session_messages.append(latest_msg)  # Collect for final summary
                    
                    # Architect Node
                    if node_name == "architect":
                        iterations_completed += 1
                        
                        with chat_container.chat_message("assistant", avatar="🏗️"):
                            with st.container(border=True):
                                st.markdown('<div class="architect-container">', unsafe_allow_html=True)
                                
                                # Header row with iteration number
                                header_cols = st.columns([4, 1])
                                with header_cols[0]:
                                    st.markdown("**Architect** — System Design")
                                with header_cols[1]:
                                    st.markdown(f"<div style='text-align: right; color: #3b82f6; font-size: 0.85rem; font-weight: 600;'>Iteration #{iterations_completed}</div>", unsafe_allow_html=True)
                                
                                # Architecture Description - fully visible
                                st.markdown("**Architecture Description**")
                                clean_text = re.sub(r"```mermaid.*?```", "", latest_msg, flags=re.DOTALL)
                                clean_text = re.sub(r"\n{3,}", "\n\n", clean_text.strip())
                                st.markdown(f"> {clean_text.replace(chr(10), chr(10)+'> ')}")
                                
                                st.write("")
                                
                                # Architecture Diagrams - fully visible
                                matches = re.findall(r"```mermaid\n(.*?)\n```", latest_msg, re.DOTALL)
                                if matches:
                                    st.markdown("**Architecture Diagram**")
                                    for idx, m_code in enumerate(matches):
                                        html_code = f"""
                                        <div id="graph-{iterations_completed}-{idx}" style="display: flex; justify-content: center; background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 10px;">
                                            <div class="mermaid" style="display:none;">
                                                {m_code}
                                            </div>
                                        </div>
                                        <script type="module">
                                            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                                            mermaid.initialize({{ startOnLoad: false, theme: 'default', securityLevel: 'strict' }});
                                            
                                            async function renderGraph() {{
                                                const container = document.getElementById('graph-{iterations_completed}-{idx}');
                                                const codeElement = container.querySelector('.mermaid');
                                                const code = codeElement.textContent.trim();
                                                
                                                try {{
                                                    const {{ svg }} = await mermaid.render('mermaid-svg-{iterations_completed}-{idx}', code);
                                                    container.innerHTML = svg;
                                                }} catch (error) {{
                                                    console.error('Mermaid render error:', error);
                                                    container.innerHTML = '<div style="color: #d73a49; text-align: center; padding: 20px;">Diagram syntax error — system continues<br><small>(' + error.message + ')</small></div>';
                                                }}
                                            }}
                                            renderGraph();
                                        </script>
                                        """
                                        components.html(html_code, height=550, scrolling=True)
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Security Node
                    elif node_name == "security":
                        with chat_container.chat_message("assistant", avatar="🛡️"):
                            with st.container(border=True):
                                st.markdown('<div class="security-container">', unsafe_allow_html=True)
                                
                                st.markdown("**Security** — Vulnerability Assessment")
                                
                                # Security Analysis - fully visible
                                st.markdown("**Security Analysis**")
                                st.markdown(f"> {latest_msg.replace(chr(10), chr(10)+'> ')}")
                                
                                st.markdown('</div>', unsafe_allow_html=True)

                # Evaluator Node
                if node_name == "evaluator":
                    score = state_update.get('evaluation_score', 0)
                    is_passed = state_update.get('is_passed', False)
                    feedback = state_update.get('feedback', '')
                    
                    final_score = score
                    final_passed = is_passed
                    
                    with chat_container.chat_message("assistant", avatar="⚖️"):
                        with st.container(border=True):
                            st.markdown('<div class="evaluator-container">', unsafe_allow_html=True)
                            
                            st.markdown("**Evaluator** — Design Review")
                            
                            # Score metrics in columns
                            metric_cols = st.columns(3)
                            with metric_cols[0]:
                                st.metric("Score", f"{score:.2f}/10.0", 
                                         delta="PASSED" if is_passed else "NEEDS WORK",
                                         delta_color="normal" if is_passed else "inverse")
                            with metric_cols[1]:
                                st.metric("Iteration", f"#{iterations_completed}/3")
                            with metric_cols[2]:
                                status = "Approved" if is_passed else "Revision"
                                st.metric("Status", status)
                            
                            # Feedback - fully visible
                            if feedback:
                                st.markdown("**Detailed Feedback**")
                                if is_passed:
                                    st.success(f"> {feedback.replace(chr(10), chr(10)+'> ')}")
                                else:
                                    st.warning(f"> {feedback.replace(chr(10), chr(10)+'> ')}")
                                st.write("")
                            
                            # Pass/fail notification
                            if is_passed:
                                st.success("Architecture approved! The design meets all criteria.")
                                st.balloons()
                            else:
                                st.info("Score below threshold. Returning to Architect for refinement...")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Generate and display final session flow summary
    with st.spinner("Generating detailed session summary..."):
        # Initialize LLM for summary generation
        summary_llm = ChatOpenAI(
            api_key=os.getenv("NOVITA_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL", "https://api.novita.ai/v3/openai"),
            model=os.getenv("MODEL_NAME", "meta-llama/llama-3.3-70b-instruct"),
            temperature=0.3
        )
        
        # Build conversation history text
        conversation_history = "\n\n".join([
            f"Message {i+1}:\n{msg}" for i, msg in enumerate(session_messages)
        ])
        
        # Call LLM with summary prompt
        summary_messages = [
            SystemMessage(content=FINAL_SESSION_SUMMARY_PROMPT),
            HumanMessage(content=f"CONVERSATION HISTORY:\n\n{conversation_history}")
        ]
        
        try:
            summary_response = summary_llm.invoke(summary_messages)
            final_summary = summary_response.content
        except Exception as e:
            final_summary = f"Could not generate detailed summary: {str(e)}"
    
    st.divider()
    
    # Display final summary - fully visible in clean container
    st.markdown("## 📋 Detailed Session Flow Summary")
    with st.container(border=True):
        st.markdown(final_summary)
    
    st.write("")
    st.divider()
    
    # Final Summary Section
    st.markdown("## 📋 Session Summary")
    
    summary_cols = st.columns(4)
    with summary_cols[0]:
        st.metric("Iterations", iterations_completed)
    with summary_cols[1]:
        st.metric("Final Score", f"{final_score:.2f}")
    with summary_cols[2]:
        status_text = "Approved" if final_passed else "Pending"
        st.metric("Status", status_text)
    with summary_cols[3]:
        st.metric("Budget Used", f"฿{user_monthly_budget_thb:,.0f}")
    
    st.markdown(f"""
    <div style="background: white; border-radius: 12px; padding: 1.5rem; margin-top: 1rem; border-left: 4px solid {'#28a745' if final_passed else '#ffc107'};">
        <strong style="color: {'#28a745' if final_passed else '#856404'};">
            {'✓ Design Approved' if final_passed else '⚠ Design Requires Additional Work'}
        </strong>
        <p style="margin: 0.5rem 0 0 0; color: #666;">
            Completed {iterations_completed} iteration(s) with a final score of {final_score:.2f}/10.0. 
            Budget reference: ฿{user_monthly_budget_thb:,.2f}/month.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("<div style='text-align: center; color: #888; font-size: 0.85rem;'>AgentGraph — Multi-Agent Architecture Design System</div>", unsafe_allow_html=True)
