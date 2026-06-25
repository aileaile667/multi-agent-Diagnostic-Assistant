"""Tests for clinical pipeline routing guards."""

from src.graph.clinical_pipeline import MAX_DIAGNOSIS_RETRIES, _route_after_diagnosis
from src.graph.state import ClinicalState


def test_diagnosis_route_retries_intake_when_more_info_requested():
    state = ClinicalState(
        raw_input="patient narrative",
        diagnosis={"primary_diagnosis": {"disease_name": "Pneumonia"}},
        needs_more_info=True,
        diagnosis_retry_count=MAX_DIAGNOSIS_RETRIES,
    )

    assert _route_after_diagnosis(state) == "intake"


def test_diagnosis_route_stops_retrying_after_max_attempts():
    state = ClinicalState(
        raw_input="patient narrative",
        diagnosis={"primary_diagnosis": {"disease_name": "Pneumonia"}},
        needs_more_info=True,
        diagnosis_retry_count=MAX_DIAGNOSIS_RETRIES + 1,
    )

    assert _route_after_diagnosis(state) == "treatment"


def test_diagnosis_route_continues_when_no_more_info_needed():
    state = ClinicalState(
        raw_input="patient narrative",
        diagnosis={"primary_diagnosis": {"disease_name": "Pneumonia"}},
        needs_more_info=False,
        diagnosis_retry_count=0,
    )

    assert _route_after_diagnosis(state) == "treatment"
