"""Tests for the Neo4j GraphRAG seed script helpers."""

from scripts.seed_neo4j_kg import build_seed_rows, create_constraints, reset_graph, seed_graph


class RecordingSession:
    def __init__(self):
        self.calls = []

    def run(self, cypher, **params):
        self.calls.append((cypher, params))
        if "count(n) AS total" in cypher:
            return RecordingResult(3)
        return RecordingResult(0)


class RecordingResult:
    def __init__(self, deleted):
        self.deleted = deleted

    def single(self):
        return {"total": self.deleted}

    def consume(self):
        return None


def test_build_seed_rows_contains_pneumonia_graph():
    symptoms, diseases, relation_and_icd_rows = build_seed_rows()
    relationships = [row for row in relation_and_icd_rows if "symptom" in row]
    icd10_codes = [row for row in relation_and_icd_rows if "code" in row]

    assert {"name": "fever"} in symptoms
    assert any(d["name"] == "Pneumonia" and d["icd10_code"] == "J18.9" for d in diseases)
    assert {"symptom": "cough", "disease": "Pneumonia"} in relationships
    assert any(code["code"] == "J18.9" for code in icd10_codes)


def test_seed_helpers_issue_expected_cypher():
    session = RecordingSession()

    deleted = reset_graph(session)
    create_constraints(session)
    counts = seed_graph(session)

    cypher_text = "\n".join(call[0] for call in session.calls)
    assert "DETACH DELETE n" in cypher_text
    assert deleted == 3
    assert "CREATE CONSTRAINT symptom_name IF NOT EXISTS" in cypher_text
    assert "CREATE CONSTRAINT disease_name IF NOT EXISTS" in cypher_text
    assert "CREATE CONSTRAINT icd10_code IF NOT EXISTS" in cypher_text
    assert "IS_SYMPTOM_OF" in cypher_text
    assert "CODED_AS" in cypher_text
    assert counts["symptoms"] > 0
    assert counts["diseases"] > 0
    assert counts["symptom_disease_relationships"] > 0
