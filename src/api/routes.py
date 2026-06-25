"""
API route definitions.

Endpoints:
  POST /api/v1/clinical/analyze   — Run full pipeline on raw patient text
  POST /api/v1/clinical/intake    — Run intake agent only
  GET  /api/v1/clinical/icd10     — Search ICD-10 codes
  GET  /api/v1/clinical/ddi       — Check drug interactions
"""

from __future__ import annotations
import json
from collections.abc import Iterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from ..graph.clinical_pipeline import get_pipeline
from ..services.icd10_service import search_icd10_by_text, lookup_icd10, get_drg_group
from ..services.drug_interaction import check_interactions

router = APIRouter(tags=["Clinical Decision"])


# ---- Request / Response models ----

class AnalyzeRequest(BaseModel):
    patient_description: str = Field(
        ...,
        min_length=10,
        description="Free-text patient narrative",
        examples=[
            "45-year-old male presenting with fever (39.2°C) for 3 days, "
            "productive cough with yellow sputum, and right-sided chest pain. "
            "History of type 2 diabetes and hypertension. "
            "Current medications: metformin 500mg BID, lisinopril 10mg daily. "
            "Allergies: penicillin (rash). "
            "Labs: WBC 15,000/μL, CRP 85 mg/L, chest X-ray shows right lower lobe infiltrate."
        ],
    )
    thread_id: str = Field(default="default", description="Conversation thread ID for checkpointing")


class AnalyzeResponse(BaseModel):
    patient_info: dict | None = None
    diagnosis: dict | None = None
    treatment_plan: dict | None = None
    coding_result: dict | None = None
    audit_result: dict | None = None
    errors: list[str] = Field(default_factory=list)


class ICD10SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Search text for ICD-10 codes")


class DDICheckRequest(BaseModel):
    new_drugs: list[str] = Field(..., min_length=1, description="Drugs to be prescribed")
    current_drugs: list[str] = Field(default_factory=list, description="Patient's current medications")


STAGE_PAYLOAD_KEYS = {
    "intake": "patient_info",
    "diagnosis": "diagnosis",
    "treatment": "treatment_plan",
    "coding": "coding_result",
    "audit": "audit_result",
}


def _sse_message(event: dict) -> str:
    return f"data: {json.dumps(event, default=str)}\n\n"


def _coerce_chunk_state(chunk: object) -> tuple[str | None, dict]:
    if not isinstance(chunk, dict) or not chunk:
        return None, {}

    for stage in STAGE_PAYLOAD_KEYS:
        if stage in chunk:
            value = chunk[stage]
            return stage, value if isinstance(value, dict) else {}

    return None, chunk


def iter_analyze_events(req: AnalyzeRequest) -> Iterator[dict]:
    """
    Yield Server-Sent Event payloads for the clinical pipeline.

    The compiled LangGraph stream emits one chunk per executed node. Each chunk
    is converted into the stable front-end protocol used by the Vue dashboard.
    """
    pipeline = get_pipeline()
    final_state: dict = {}

    try:
        for chunk in pipeline.stream(
            {"raw_input": req.patient_description},
            config={
                "configurable": {"thread_id": req.thread_id},
                "recursion_limit": 10,
            },
        ):
            stage, state = _coerce_chunk_state(chunk)
            if stage is None:
                continue

            yield {
                "thread_id": req.thread_id,
                "stage": stage,
                "status": "started",
                "payload": {},
                "errors": [],
            }

            final_state.update(state)
            payload_key = STAGE_PAYLOAD_KEYS[stage]
            yield {
                "thread_id": req.thread_id,
                "stage": stage,
                "status": "completed",
                "payload": {payload_key: state.get(payload_key)},
                "errors": state.get("errors", []),
            }

        yield {
            "thread_id": req.thread_id,
            "stage": "done",
            "status": "completed",
            "payload": AnalyzeResponse(
                patient_info=final_state.get("patient_info"),
                diagnosis=final_state.get("diagnosis"),
                treatment_plan=final_state.get("treatment_plan"),
                coding_result=final_state.get("coding_result"),
                audit_result=final_state.get("audit_result"),
                errors=final_state.get("errors", []),
            ).model_dump(),
            "errors": final_state.get("errors", []),
        }
    except Exception as e:
        yield {
            "thread_id": req.thread_id,
            "stage": "error",
            "status": "failed",
            "payload": {},
            "errors": [f"Pipeline error: {str(e)}"],
        }


def sse_analyze_messages(req: AnalyzeRequest) -> Iterator[str]:
    for event in iter_analyze_events(req):
        yield _sse_message(event)


# ---- Endpoints ----

@router.post("/clinical/analyze", response_model=AnalyzeResponse)
async def analyze_patient(req: AnalyzeRequest):
    """
    Run the full 5-agent clinical decision pipeline.

    1. Intake Agent → structured patient info
    2. Diagnosis Agent → differential diagnosis
    3. Treatment Agent → evidence-based treatment plan
    4. Coding Agent → ICD-10 codes + DRGs
    5. Audit Agent → HIPAA compliance report
    """
    pipeline = get_pipeline()

    try:
        result = await run_in_threadpool(
            pipeline.invoke,
            {"raw_input": req.patient_description},
            config={
                "configurable": {"thread_id": req.thread_id},
                "recursion_limit": 10,
            },
        )
        return AnalyzeResponse(
            patient_info=result.get("patient_info"),
            diagnosis=result.get("diagnosis"),
            treatment_plan=result.get("treatment_plan"),
            coding_result=result.get("coding_result"),
            audit_result=result.get("audit_result"),
            errors=result.get("errors", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.post("/clinical/analyze/stream")
async def stream_analyze_patient(req: AnalyzeRequest):
    """Stream pipeline progress and final results as Server-Sent Events."""
    return StreamingResponse(
        sse_analyze_messages(req),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/clinical/icd10/search")
async def search_icd10(req: ICD10SearchRequest):
    """Search ICD-10 codes by text description."""
    results = search_icd10_by_text(req.query)
    return {"query": req.query, "results": results, "count": len(results)}


@router.get("/clinical/icd10/{code}")
async def get_icd10(code: str):
    """Look up a specific ICD-10 code."""
    result = lookup_icd10(code)
    if not result:
        raise HTTPException(status_code=404, detail=f"ICD-10 code {code} not found")
    drg = get_drg_group(code)
    return {"icd10": result, "drg_group": drg}


@router.post("/clinical/ddi/check")
async def check_ddi(req: DDICheckRequest):
    """Check drug-drug interactions."""
    interactions = check_interactions(req.new_drugs, req.current_drugs)
    return {
        "new_drugs": req.new_drugs,
        "current_drugs": req.current_drugs,
        "interactions": interactions,
        "interaction_count": len(interactions),
        "has_major_interaction": any(i["severity"] in ("major", "contraindicated") for i in interactions),
    }
