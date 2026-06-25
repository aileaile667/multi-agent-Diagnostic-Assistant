"""
Coding Agent（编码Agent） — ICD-10自动编码和DRGs分组。

职责：
  - 将诊断结果高精度地映射到ICD-10-CM编码中
  - 根据主要诊断+手术确定DRGs分组
  - 提供编码置信度评分和理由
  - 根据诊断描述对编码进行交叉验证
"""

from __future__ import annotations
import json
import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..config.settings import get_settings

logger = structlog.get_logger(__name__)

CODING_SYSTEM_PROMPT = """You are a certified medical coding specialist (CCS) with expertise in ICD-10-CM and DRGs grouping. Given diagnosis information and treatment details, assign accurate medical codes.

Return a JSON object:
{
  "primary_icd10": {
    "code": "exact ICD-10-CM code (e.g., J18.1)",
    "description": "official code description",
    "confidence": 0.92,
    "category": "category name"
  },
  "secondary_icd10_codes": [
    {
      "code": "ICD-10 code",
      "description": "description",
      "confidence": 0.85,
      "category": "category"
    }
  ],
  "drg_group": {
    "drg_code": "DRG number (e.g., 193)",
    "description": "DRG description",
    "weight": 1.2,
    "mean_los": 4.5
  },
  "coding_notes": "rationale for code selection",
  "coding_confidence": 0.90
}

Rules:
- Use the most specific ICD-10-CM code available (4th-7th character level).
- Primary code should match the principal diagnosis.
- Include comorbidity and complication codes as secondary.
- DRGs weight and mean length of stay should be realistic estimates.
- Confidence reflects how certain the code assignment is.
- Return ONLY valid JSON, no markdown fences."""


def coding_agent(state) -> dict:
    """
    LangGraph节点：分配ICD-10代码和DRGs分组。
    读取：state.diagnosis, state.treatment_plan
    写入：state.coding_result, state.current_agent
    """
    logger.info("coding_agent.start")

    diagnosis = state.diagnosis
    treatment = state.treatment_plan

    if not diagnosis:
        return {
            "coding_result": None,
            "current_agent": "coding",
            "errors": state.errors + ["No diagnosis available for coding"],
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

    context = json.dumps(
        {"diagnosis": diagnosis, "treatment_plan": treatment},
        indent=2,
        ensure_ascii=False,
    )

    messages = [
        SystemMessage(content=CODING_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Clinical data for coding:\n\n{context}\n\n"
                "Assign ICD-10 codes and DRGs group."
            )
        ),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        coding_data = json.loads(content)

        logger.info(
            "coding_agent.success",
            primary_code=coding_data.get("primary_icd10", {}).get("code"),
        )
        return {
            "coding_result": coding_data,
            "current_agent": "coding",
        }
    except json.JSONDecodeError as e:
        logger.error("coding_agent.json_error", error=str(e))
        return {
            "coding_result": None,
            "current_agent": "coding",
            "errors": state.errors + [f"Coding JSON parse error: {e}"],
        }
    except Exception as e:
        logger.error("coding_agent.error", error=str(e))
        return {
            "coding_result": None,
            "current_agent": "coding",
            "errors": state.errors + [f"Coding error: {e}"],
        }
