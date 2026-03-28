import streamlit as st
import streamlit.components.v1 as components
import os
import re
from dotenv import load_dotenv

# ==========================================
# SETUP: Load Environment Variables
# ==========================================
load_dotenv()
if not os.getenv("NOVITA_API_KEY"):
    st.error("🚨 NOVITA_API_KEY not found in .env file!")
    st.stop()

# Import graph system
from main import build_graph

# ==========================================
# UI SETUP: Configure Streamlit page
# ==========================================
st.set_page_config(page_title="AgentGraph Consultant", layout="wide", page_icon="🔥")
st.title("AgentGraph: AI Architecture Consultant")
st.markdown("Multi-Agent system for real-time architecture design and security evaluation")

# ==========================================
# SIDEBAR: Configuration & User Input
# ==========================================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # System Requirements Input
    st.markdown("**📝 Define System Requirements:**")
    user_req = st.text_area(
        "Enter system details", 
        value="Design a RAG (Retrieval-Augmented Generation) chatbot system for a corporate environment supporting 1,000 concurrent users with monthly cost estimation in Thai Baht",
        height=150
    )
    
    st.markdown("---")
    
    # System Design Budget - Reference only for architect
    st.markdown("**💰 Monthly Operating Budget (THB):**")
    st.markdown("*Reference budget for architect to consider when designing the system*")
    user_monthly_budget_thb = st.number_input(
        "Enter your monthly operating budget in Thai Baht (฿)",
        min_value=0.0,
        value=5000.0,
        step=1000.0,
        help="This budget is passed to architect to design cost-effective solutions. Not deducted from iterations."
    )
    
    st.info(
        f"**Budget Information:**\n\n"
        f"• Architect will design system for: ฿{user_monthly_budget_thb:.2f}/month\n"
        f"• System design iterations: Unlimited (no cost per iteration)\n"
        f"• Focus: Cost-effective, practical solutions within budget"
    )
    
    st.markdown("---")
    
    # Execute Button
    start_btn = st.button("🚀 Start Simulation", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("**Agents in System:**")
    st.markdown("- 🏗️ **Architect**: Design system, estimate costs, create diagrams")
    st.markdown("- 🛡️ **Security**: Identify vulnerabilities and propose mitigations")
    st.markdown("- ⚖️ **Evaluator**: Score architecture (target >= 9.5/10)")

# ==========================================
# EXECUTION: Main logic when start button is clicked
# ==========================================
if start_btn:
    app_graph = build_graph()
    
    # Initialize state - pass budget to architect but no cost tracking per iteration
    initial_state = {
        "messages": [],
        "user_requirements": user_req,
        "revision_count": 0,
        "feedback": "",
        "is_passed": False,
        "evaluation_score": 0.0,
        "is_mermaid_valid": True,
        # Loop Prevention - History tracking fields
        "history_outputs": [],
        "history_scores": [],
        "history_feedback": [],
        "stop_reason": "",
        # Budget context (for architect reference only - no cost deduction)
        "budget_context": user_monthly_budget_thb
    }
    
    # Create container for chat-like UI display
    chat_container = st.container()
    
    # Track iterations (no cost tracking)
    iterations_completed = 0
    
    with st.spinner("🧠 Agents starting... Designing your system"):
        # Stream graph updates in real-time
        for output in app_graph.stream(initial_state, stream_mode="updates"):
            for node_name, state_update in output.items():
                
                # Display agent messages
                if "messages" in state_update and len(state_update["messages"]) > 0:
                    latest_msg = state_update["messages"][-1].content
                    
                    # Architect Node
                    if node_name == "architect":
                        iterations_completed += 1
                        
                        with chat_container.chat_message("assistant", avatar="🏗️"):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown("**[Architect] System Design:**")
                            with col2:
                                st.metric("Iteration", f"#{iterations_completed}", label_visibility="collapsed")
                            
                            # Display message safely (prevent Streamlit from rendering Mermaid)
                            safe_msg = latest_msg.replace("```mermaid", "```text")
                            st.markdown(safe_msg)
                            
                            # Extract and render Mermaid diagrams
                            matches = re.findall(r"```mermaid\n(.*?)\n```", latest_msg, re.DOTALL)
                            if matches:
                                st.info(f"🎨 Rendering {len(matches)} architecture diagram(s)")
                                for idx, m_code in enumerate(matches):
                                    html_code = f"""
                                    <div id="graph-{idx}" style="display: flex; justify-content: center; background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 10px;">
                                        <div class="mermaid" style="display:none;">
                                            {m_code}
                                        </div>
                                    </div>
                                    <script type="module">
                                        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                                        mermaid.initialize({{ startOnLoad: false, theme: 'default', securityLevel: 'loose' }});
                                        
                                        async function renderGraph() {{
                                            const container = document.getElementById('graph-{idx}');
                                            const codeElement = container.querySelector('.mermaid');
                                            const code = codeElement.textContent.trim();
                                            
                                            try {{
                                                const {{ svg }} = await mermaid.render('mermaid-svg-{idx}', code);
                                                container.innerHTML = svg;
                                            }} catch (error) {{
                                                console.error('Mermaid render error:', error);
                                                container.innerHTML = '<div style="color: red; text-align: center; padding: 20px;">⚠️ Diagram code has syntax errors but system continues<br><small>(' + error.message + ')</small></div>';
                                            }}
                                        }}
                                        renderGraph();
                                    </script>
                                    """
                                    components.html(html_code, height=550, scrolling=True)
                    
                    # Security Node
                    elif node_name == "security":
                        with chat_container.chat_message("assistant", avatar="🛡️"):
                            st.markdown("**[Security] Vulnerability Assessment:**")
                            st.markdown(latest_msg)

                # Evaluator Node
                if node_name == "evaluator":
                    with chat_container.chat_message("assistant", avatar="⚖️"):
                        score = state_update.get('evaluation_score', 0)
                        
                        # Display score
                        st.subheader(f"📊 Evaluation Score: {score:.2f}/10.0")
                        
                        st.write("**Feedback:**")
                        feedback = state_update.get('feedback', '')
                        if feedback:
                            st.error(feedback)
                        
                        # Check if passed evaluation
                        is_passed = state_update.get('is_passed', False)
                        if is_passed:
                            st.success("✅ System PASSED evaluation! Architecture approved!")
                            st.balloons()
                        else:
                            st.warning("🔄 Score below 9.5. Returning to Architect for design revision...")
    
    # Final Summary
    st.markdown("---")
    st.subheader("📋 Design Summary")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Iterations", iterations_completed)
    with col2:
        st.metric("Budget Reference", f"฿{user_monthly_budget_thb:.0f}/month")
    
    st.write(f"**Design completed** with {iterations_completed} architecture iteration(s)")
    st.write(f"**Budget used as reference:** ฿{user_monthly_budget_thb:.2f}/month for cost-conscious design")
