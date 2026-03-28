import streamlit as st
import streamlit.components.v1 as components
import os
import re
from dotenv import load_dotenv

load_dotenv()
if not os.getenv("NOVITA_API_KEY"):
    st.error("Error: ไม่พบ NOVITA_API_KEY ในไฟล์ .env")
    st.stop()

from main import build_graph

st.set_page_config(page_title="AgentGraph Simulation", layout="wide")
st.title("AgentGraph: Architecture Design Simulation")
st.markdown("ระบบ Multi-Agent สำหรับออกแบบและตรวจสอบ System Architecture")

with st.sidebar:
    st.header("Controls")
    start_btn = st.button("เริ่มการจำลอง", type="primary")
    st.markdown("---")
    st.markdown("**Agents:**")
    st.markdown("- **Architect**: ออกแบบและสร้าง Diagram (Mermaid)")
    st.markdown("- **Security**: ตรวจสอบช่องโหว่ (Vulnerability Assessment)")
    st.markdown("- **Evaluator**: ประเมินผล (เป้าหมาย >= 8.0/10)")

if start_btn:
    app_graph = build_graph()
    
    initial_state = {
        "messages": [],
        "revision_count": 0,
        "feedback": "",
        "is_passed": False,
        "evaluation_score": 0.0,
        "is_mermaid_valid": True  # 🚀 เพิ่มบรรทัดนี้
    }
    chat_container = st.container()
    
    with st.spinner("ระบบกำลังประมวลผล..."):
        for output in app_graph.stream(initial_state, stream_mode="updates"):
            for node_name, state_update in output.items():
                
                if "messages" in state_update and len(state_update["messages"]) > 0:
                    latest_msg = state_update["messages"][-1].content
                    
                    if node_name == "architect":
                        with chat_container.chat_message("assistant", avatar="🏗️"):
                            st.markdown("**[Architect] System Design:**")
                            st.markdown(latest_msg)
                            
                            matches = re.findall(r"```mermaid\n(.*?)\n```", latest_msg, re.DOTALL)
                            if matches:
                                for idx, m_code in enumerate(matches):
                                    html_code = f"""
                                    <div class="mermaid" style="display: flex; justify-content: center; background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 10px;">
                                        {m_code}
                                    </div>
                                    <script type="module">
                                        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                                        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
                                    </script>
                                    """
                                    components.html(html_code, height=450, scrolling=True)
                            
                    elif node_name == "security":
                        with chat_container.chat_message("human", avatar="🛡️"):
                            st.markdown("**[Security] Vulnerability Assessment:**")
                            st.markdown(latest_msg)

                if node_name == "evaluator":
                    with chat_container.chat_message("ai", avatar="⚖️"):
                        score = state_update.get('evaluation_score', 0)
                        st.subheader(f"Evaluation Score: {score}/10")
                        st.write("**Feedback:**")
                        st.error(state_update.get('feedback'))
                        
                        if state_update.get('is_passed'):
                            st.success("สถานะ: ผ่านเกณฑ์การประเมิน")
                        else:
                            st.warning("สถานะ: ไม่ผ่านเกณฑ์ กำลังส่งกลับเพื่อแก้ไข...")