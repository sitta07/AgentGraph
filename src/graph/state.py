from typing import Annotated, List, TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    revision_count: int
    feedback: str
    is_passed: bool
    evaluation_score: float
    is_mermaid_valid: bool  

class EvaluationRubric(BaseModel):
    """
    Schema สำหรับบังคับให้ Evaluator ตอบกลับเป็น JSON ที่มีโครงสร้างและขอบเขตข้อมูลที่ถูกต้อง
    """
    score: float = Field(
        ge=0.0, 
        le=10.0, 
        description="คะแนนตั้งแต่ 0.0 ถึง 10.0 ประเมินจากความปลอดภัยและสถาปัตยกรรมระบบ"
    )
    reasoning: str = Field(description="เหตุผลการให้คะแนนแบบสรุปย่อ")
    critique_points: List[str] = Field(description="รายการช่องโหว่หรือจุดที่ต้องแก้ไข (ถ้ามี)")
    is_passed: bool = Field(description="ผ่านเกณฑ์หรือไม่ (True เมื่อคะแนน >= 8.0)")