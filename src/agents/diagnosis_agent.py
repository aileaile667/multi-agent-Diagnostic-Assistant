"""
 Diagnosis Agent（诊断Agent）——基于结构化患者数据的鉴别诊断。

职责：
  - 根据医学知识分析症状和实验室结果
  - 生成带有置信度评分的排序鉴别诊断列表
  - 为每个候选诊断提供证据链
  - 如果信息不充分，建议进行额外测试
  - 在可用时与GraphRAG知识图谱集成
"""

from __future__ import annotations
import json
import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..config.settings import get_settings
from ..services.graphrag_service import get_graphrag_service

logger = structlog.get_logger(__name__)

DIAGNOSIS_SYSTEM_PROMPT = """You are an expert diagnostician performing differential diagnosis. Given structured patient information, provide a comprehensive differential diagnosis.

Return a JSON object with this structure:
{
  "primary_diagnosis": {
    "disease_name": "most likely diagnosis",
    "icd10_hint": "approximate ICD-10 code (e.g., J18.9)",
    "confidence": 0.85,
    "evidence": ["supporting finding 1", "supporting finding 2"],
    "reasoning": "clinical reasoning explanation"
  },
  "differential_list": [
    {
      "disease_name": "alternative diagnosis",
      "icd10_hint": "ICD-10 code",
      "confidence": 0.6,
      "evidence": ["evidence 1"],
      "reasoning": "why this is considered"
    }
  ],
  "recommended_tests": ["test 1 to confirm/rule out", "test 2"],
  "clinical_notes": "overall clinical impression",
  "knowledge_sources": ["source 1", "source 2"],
  "needs_more_info": false
}

Rules:
- Confidence scores must be between 0 and 1.
- Provide at least 2-3 differential diagnoses.
- List evidence from the patient data that supports each diagnosis.
- If critical information is missing, set needs_more_info to true.
- Use standard medical terminology and ICD-10 code hints.
- Return ONLY valid JSON, no markdown fences."""


def _extract_symptom_names(patient_info: dict) -> list[str]:
    symptoms = patient_info.get("symptoms", [])
    names = []
    if isinstance(symptoms, list):
        for symptom in symptoms:
            if isinstance(symptom, str):
                names.append(symptom)
            elif isinstance(symptom, dict):
                value = symptom.get("name") or symptom.get("symptom") or symptom.get("description")
                if value:
                    names.append(str(value))
    return names


def _format_graphrag_context(candidates: list[dict]) -> str:
    if not candidates:
        return "No matching diseases were found in the lightweight GraphRAG knowledge graph."

    lines = []
    for candidate in candidates[:10]:
        matching = ", ".join(candidate.get("matching_symptoms") or [])
        paths = "; ".join(candidate.get("evidence_paths") or [])
        lines.append(
            "- {disease} (ICD-10: {icd10}, matched symptoms: {count}; symptoms: {symptoms}; evidence: {paths})".format(
                disease=candidate.get("disease", ""),
                icd10=candidate.get("icd10_code", "") or "unknown",
                count=candidate.get("symptom_match_count", 0),
                symptoms=matching or "none",
                paths=paths or "none",
            )
        )
    return "\n".join(lines)


def diagnosis_agent(state) -> dict:
    """
    LangGraph节点：根据患者信息生成鉴别诊断。
    Reads: state.patient_info
    Writes: state.diagnosis, state.needs_more_info, state.current_agent
    """
    logger.info("diagnosis_agent.start")

    patient_info = state.patient_info
    if not patient_info:
        return {
            "diagnosis": None,
            "needs_more_info": True,
            "diagnosis_retry_count": state.diagnosis_retry_count + 1,
            "current_agent": "diagnosis",
            "errors": state.errors + ["No patient info available for diagnosis"],
        }

    settings = get_settings()
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=0.2,
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )

    patient_summary = json.dumps(patient_info, indent=2, ensure_ascii=False)
    symptom_names = _extract_symptom_names(patient_info)
    graphrag_candidates = []
    graphrag_source = "Built-in GraphRAG fallback"
    try:
        graphrag = get_graphrag_service()
        graphrag_candidates = graphrag.find_diseases_by_symptoms(symptom_names)
        if graphrag_candidates:
            graphrag_source = graphrag_candidates[0].get("source", graphrag_source)
    except Exception as e:
        logger.warning("diagnosis_agent.graphrag_unavailable", error=str(e))

    graphrag_context = _format_graphrag_context(graphrag_candidates)

    messages = [
        SystemMessage(content=DIAGNOSIS_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Patient information:\n\n{patient_summary}\n\n"
                f"Lightweight GraphRAG candidate diseases:\n{graphrag_context}\n\n"
                "Use the GraphRAG candidates as supporting evidence when clinically appropriate, "
                "but do not limit the diagnosis to this list. Include the GraphRAG source in "
                f"knowledge_sources when used: {graphrag_source}.\n\n"
                "Provide your differential diagnosis."
            )
        ),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        diagnosis_data = json.loads(content)
        needs_more = diagnosis_data.pop("needs_more_info", False)
        diagnosis_retry_count = state.diagnosis_retry_count + 1 if needs_more else 0
        knowledge_sources = diagnosis_data.get("knowledge_sources")
        if not isinstance(knowledge_sources, list):
            knowledge_sources = [str(knowledge_sources)] if knowledge_sources else []
            diagnosis_data["knowledge_sources"] = knowledge_sources
        if graphrag_candidates and graphrag_source not in knowledge_sources:
            knowledge_sources.append(graphrag_source)

        logger.info(
            "diagnosis_agent.success",
            primary=diagnosis_data.get("primary_diagnosis", {}).get("disease_name"),
        )
        return {
            "diagnosis": diagnosis_data,
            "needs_more_info": needs_more,
            "diagnosis_retry_count": diagnosis_retry_count,
            "current_agent": "diagnosis",
        }
    except json.JSONDecodeError as e:
        logger.error("diagnosis_agent.json_error", error=str(e))
        return {
            "diagnosis": None,
            "needs_more_info": False,
            "current_agent": "diagnosis",
            "errors": state.errors + [f"Diagnosis JSON parse error: {e}"],
        }
    except Exception as e:
        logger.error("diagnosis_agent.error", error=str(e))
        return {
            "diagnosis": None,
            "needs_more_info": False,
            "current_agent": "diagnosis",
            "errors": state.errors + [f"Diagnosis error: {e}"],
        }
