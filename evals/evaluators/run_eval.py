import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate

load_dotenv()

# 💡 Senior Trick: Manage path to import files from parent folders (src, main)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from main import build_graph



client = Client()
app = build_graph()

# ==========================================
# 1. Target Function (Candidate)
# ==========================================
def predict_architecture(inputs: dict):
    """
    This function receives 'problems' from the Dataset (e.g., requirements, budget)
    and sends them to our AgentGraph to generate answers.
    """
    initial_state = {
        "messages": [],
        "user_requirements": inputs.get("requirements", "Basic System"),
        "budget_context": inputs.get("budget", 5000.0),
        "revision_count": 0,
        "feedback": "",
        "is_passed": False,
        "evaluation_score": 0.0,
        "history_outputs": [],
        "history_scores": [],
        "history_feedback": [],
        "stop_reason": "",
    }
    
    # Invoke the graph - it will run until reaching END
    final_state = app.invoke(initial_state)
    
    # Return only the "results" we want evaluators to check
    return {
        "score": final_state.get("evaluation_score", 0.0),
        "is_passed": final_state.get("is_passed", False),
        "is_mermaid_valid": final_state.get("is_mermaid_valid", False),
        "revision_count": final_state.get("revision_count", 0)
    }

# ==========================================
# 2. Custom Evaluators (Examiners)
# ==========================================
def check_pass_status(run, example):
    """Evaluator #1: Check if the run completed with system passed (is_passed == True)"""
    result = run.outputs.get("is_passed", False)
    score = run.outputs.get("score", 0.0)
    return {
        "key": "System_Passed",  # Subject name
        "score": 1.0 if result else 0.0,  # 1.0 = pass, 0.0 = fail
        "comment": f"Final AI Score: {score}/10.0"
    }

def check_mermaid_syntax(run, example):
    """Evaluator #2: Check if Mermaid renders successfully 100%"""
    result = run.outputs.get("is_mermaid_valid", False)
    return {
        "key": "Valid_Mermaid",
        "score": 1.0 if result else 0.0
    }

def check_efficiency(run, example):
    """Evaluator #3: Check efficiency - if passes in one round, full score"""
    revisions = run.outputs.get("revision_count", 0)
    # If 1 revision = 1.0 | If 2 revisions = 0.5 | If 3 revisions = 0.33
    efficiency_score = 1.0 / max(1, revisions) 
    return {
        "key": "Revision_Efficiency",
        "score": efficiency_score,
        "comment": f"Took {revisions} iterations"
    }

# ==========================================
# 3. Execution (Open Exam)
# ==========================================
if __name__ == "__main__":
    print("🚀 Starting Automated Evaluation for AgentGraph...")
    
    # Dataset name on LangSmith that we need to create in advance
    DATASET_NAME = "AgentGraph-Test-Cases" 
    
    try:
        # Run the evaluation!
        experiment_results = evaluate(
            predict_architecture,       # Test target
            data=DATASET_NAME,          # Test dataset
            evaluators=[check_pass_status, check_mermaid_syntax, check_efficiency], # All 3 evaluators
            experiment_prefix="eval-llama3.3-", # Prefix in results table
            metadata={"version": "1.0", "framework": "langgraph"}
        )
        print("✅ Evaluation completed! Go check the detailed results on LangSmith UI.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"💡 Hint: Have you created the dataset '{DATASET_NAME}' in the LangSmith UI yet?")