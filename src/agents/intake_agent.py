"""
Intake Agent（接诊Agent） — 患者信息收集与整理。

职责：
  - 将原始患者描述解析为结构化的PatientInfo
  - 提取主诉、症状、病史
  - 将数据标准化为符合FHIR标准的格式
  - 验证关键字段的完整性
"""

from __future__ import annotations
import json
import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..config.settings import get_settings
from ..models.patient import PatientInfo

logger = structlog.get_logger(__name__)

INTAKE_SYSTEM_PROMPT = """You are an expert medical intake specialist. Your job is to extract structured patient information from the provided clinical narrative.

Extract the following fields as a JSON object:
{
  "name": "patient name or 'Unknown'",
  "age": <integer>,
  "gender": "male|female|other|unknown",
  "chief_complaint": "main reason for visit",
  "symptoms": [
    {"name": "symptom name", "duration_days": <int or null>, "severity": "mild|moderate|severe|critical", "description": "details"}
  ],
  "medical_history": ["list of past conditions"],
  "family_history": ["list of family conditions"],
  "allergies": [
    {"substance": "name", "reaction": "description", "severity": "mild|moderate|severe"}
  ],
  "current_medications": [
    {"name": "drug name", "dosage": "dose", "frequency": "how often"}
  ],
  "vital_signs": {
    "temperature": <float or null>,
    "heart_rate": <int or null>,
    "blood_pressure_systolic": <int or null>,
    "blood_pressure_diastolic": <int or null>,
    "respiratory_rate": <int or null>,
    "oxygen_saturation": <float or null>
  },
  "lab_results": [
    {"test_name": "name", "value": "result", "unit": "unit", "reference_range": "range", "is_abnormal": true/false}
  ]
}

Rules:
- If a field is not mentioned, use reasonable defaults or null.
- Age must be a positive integer. If unclear, estimate from context.
- Always identify the chief complaint even if not explicitly stated.
- Return ONLY valid JSON, no markdown fences."""


def intake_agent(state) -> dict:
    """
    LangGraph节点：将原始患者输入解析为结构化数据。
    读取：state.raw_input
    写入：state.patient_info，state.current_agent
    """
    logger.info("intake_agent.start", raw_input_len=len(state.raw_input or ""))

    raw = state.raw_input
    if not raw:
        return {
            "patient_info": None,
            "current_agent": "intake",
            "errors": state.errors + ["No raw input provided to Intake Agent"],
        }

    settings = get_settings()
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=0.1,
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )

    messages = [
        SystemMessage(content=INTAKE_SYSTEM_PROMPT),
        HumanMessage(content=f"Patient narrative:\n\n{raw}"),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        patient_data = json.loads(content)
        patient = PatientInfo(**patient_data)
        patient_dict = patient.model_dump(mode="json")

        logger.info("intake_agent.success", patient_name=patient.name)
        return {
            "patient_info": patient_dict,
            "current_agent": "intake",
        }
    except json.JSONDecodeError as e:
        logger.error("intake_agent.json_error", error=str(e))
        return {
            "patient_info": None,
            "current_agent": "intake",
            "errors": state.errors + [f"Intake JSON parse error: {e}"],
        }
    except Exception as e:
        logger.error("intake_agent.error", error=str(e))
        return {
            "patient_info": None,
            "current_agent": "intake",
            "errors": state.errors + [f"Intake error: {e}"],
        }
