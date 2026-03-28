import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from src.utils.diagram_generator import extract_and_save_diagram

# Import system components
from src.graph.state import GraphState
from src.graph.nodes import architect_node, security_node, evaluator_node, route_to_next
from src.graph.nodes import mermaid_validator_node, route_after_architect


# Load environment variables
load_dotenv()
if not os.getenv("NOVITA_API_KEY"):
    raise ValueError("FATAL: NOVITA_API_KEY not found in .env file!")


def build_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("architect", architect_node)
    workflow.add_node("mermaid_validator", mermaid_validator_node)  # Mermaid validation node
    workflow.add_node("security", security_node)
    workflow.add_node("evaluator", evaluator_node)

    workflow.set_entry_point("architect")
    
    # Connect nodes
    workflow.add_edge("architect", "mermaid_validator")
    workflow.add_conditional_edges("mermaid_validator", route_after_architect)
    
    workflow.add_edge("security", "evaluator")
    workflow.add_conditional_edges("evaluator", route_to_next)

    return workflow.compile()

# ==========================================
# EXECUTE - Main execution with cost tracking
# ==========================================
if __name__ == "__main__":
    print("🔥 Starting AgentGraph Simulation (Clean Architecture)...")
    app = build_graph()
    
    initial_state = {
        "messages": [],
        "revision_count": 0,
        "feedback": "",
        "is_passed": False,
        "evaluation_score": 0.0,
        # Loop Prevention - Initialize history tracking fields
        "history_outputs": [],
        "history_scores": [],
        "history_feedback": [],
        "stop_reason": "",
        # Cost tracking - Design budget
        "estimated_cost_thb": 3.0,
        "cost_per_iteration_thb": 3.0,
        "total_cost_thb": 0.0
    }
    
    # Stream graph execution with detailed logs
    for output in app.stream(initial_state, stream_mode="updates"):
        for node_name, state_update in output.items():
            
            # Display agent messages
            if "messages" in state_update and len(state_update["messages"]) > 0:
                latest_msg = state_update["messages"][-1].content
                print(f"\n{'='*50}")
                print(f"📄 [OUTPUT FROM: {node_name.upper()}]")
                print(f"{'='*50}")
                print(f"{latest_msg}\n")
                
                # Extract and save diagrams if from architect
                if node_name == "architect":
                    current_round = state_update.get('revision_count', 0) + 1 
                    extract_and_save_diagram(latest_msg, current_round)
            
            # Display evaluator results
            if node_name == "evaluator":
                score = state_update.get('evaluation_score', 0.0)
                revision = state_update.get('revision_count', 0)
                print(f"\n[📊 Evaluation Summary - Round #{revision}]")
                print(f"Score: {score:.2f}/10.0")
                print(f"Feedback:\n{state_update.get('feedback')}")
                print(f"Passed: {state_update.get('is_passed')}")
    
    print(f"\n{'='*50}")
    print(f"✅ EXECUTION COMPLETE")
    print(f"{'='*50}")