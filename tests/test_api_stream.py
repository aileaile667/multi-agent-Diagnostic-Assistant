"""Tests for the clinical analysis SSE protocol."""

from src.api import routes
from src.api.routes import AnalyzeRequest, iter_analyze_events


class FakePipeline:
    def __init__(self, chunks=None, error=None):
        self.chunks = chunks or []
        self.error = error

    def stream(self, *_args, **_kwargs):
        if self.error:
            raise self.error
        yield from self.chunks


def test_iter_analyze_events_emits_stage_order_and_done(monkeypatch):
    chunks = [
        {"intake": {"patient_info": {"name": "John Doe"}, "errors": []}},
        {
            "diagnosis": {
                "diagnosis": {
                    "primary_diagnosis": {
                        "disease_name": "Pneumonia",
                        "confidence": 0.86,
                    }
                },
                "errors": [],
            }
        },
        {"treatment": {"treatment_plan": {"warnings": []}, "errors": []}},
        {"coding": {"coding_result": {"primary_icd10": {"code": "J18.9"}}, "errors": []}},
        {"audit": {"audit_result": {"hipaa_compliant": True}, "errors": []}},
    ]
    monkeypatch.setattr(routes, "get_pipeline", lambda: FakePipeline(chunks=chunks))

    req = AnalyzeRequest(patient_description="Patient has fever and cough.", thread_id="t-1")
    events = list(iter_analyze_events(req))

    completed_stages = [
        event["stage"] for event in events if event["status"] == "completed"
    ]
    assert completed_stages == [
        "intake",
        "diagnosis",
        "treatment",
        "coding",
        "audit",
        "done",
    ]
    assert events[-1]["payload"]["patient_info"]["name"] == "John Doe"
    assert events[-1]["payload"]["coding_result"]["primary_icd10"]["code"] == "J18.9"


def test_iter_analyze_events_emits_error_event(monkeypatch):
    monkeypatch.setattr(
        routes,
        "get_pipeline",
        lambda: FakePipeline(error=RuntimeError("boom")),
    )

    req = AnalyzeRequest(patient_description="Patient has fever and cough.", thread_id="t-err")
    events = list(iter_analyze_events(req))

    assert events == [
        {
            "thread_id": "t-err",
            "stage": "error",
            "status": "failed",
            "payload": {},
            "errors": ["Pipeline error: boom"],
        }
    ]
