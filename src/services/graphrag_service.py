"""
GraphRAG service — Medical knowledge graph retrieval.

Integrates with Neo4j to provide:
  - Symptom-to-disease relationship queries
  - Disease-to-treatment pathway lookups
  - Multi-hop reasoning across medical ontologies (UMLS, SNOMED, ICD)
  - Evidence retrieval for clinical decision support
"""

from __future__ import annotations
from typing import Optional
import structlog

from ..config.settings import get_settings

logger = structlog.get_logger(__name__)


class _AwaitableNone:
    def __await__(self):
        if False:
            yield None
        return None


class _AwaitableList(list):
    def __await__(self):
        if False:
            yield None
        return self


# Pre-built knowledge base for demonstration (offline mode)
SYMPTOM_DISEASE_MAP = {
    "fever": ["Influenza", "Pneumonia", "COVID-19", "Sepsis", "Malaria", "UTI"],
    "cough": ["Pneumonia", "Bronchitis", "Asthma", "COPD", "Lung Cancer", "COVID-19"],
    "headache": ["Migraine", "Tension Headache", "Meningitis", "Hypertension", "Brain Tumor"],
    "chest_pain": ["Acute MI", "Angina", "Pulmonary Embolism", "Pneumothorax", "GERD"],
    "abdominal_pain": ["Appendicitis", "Cholecystitis", "Pancreatitis", "Peptic Ulcer", "IBS"],
    "shortness_of_breath": ["Asthma", "COPD", "Heart Failure", "Pneumonia", "Pulmonary Embolism"],
    "fatigue": ["Anemia", "Hypothyroidism", "Depression", "Diabetes", "Heart Failure"],
    "nausea": ["Gastroenteritis", "Pregnancy", "Appendicitis", "Migraine", "Hepatitis"],
    "dizziness": ["BPPV", "Hypotension", "Anemia", "Stroke", "Arrhythmia"],
    "joint_pain": ["Rheumatoid Arthritis", "Osteoarthritis", "Gout", "SLE", "Lyme Disease"],
}

DISEASE_ICD10_MAP = {
    "Pneumonia": {"code": "J18.9", "desc": "Pneumonia, unspecified organism"},
    "Influenza": {"code": "J11.1", "desc": "Influenza with other respiratory manifestations"},
    "COVID-19": {"code": "U07.1", "desc": "COVID-19, virus identified"},
    "Acute MI": {"code": "I21.9", "desc": "Acute myocardial infarction, unspecified"},
    "Asthma": {"code": "J45.909", "desc": "Unspecified asthma, uncomplicated"},
    "Type 2 Diabetes": {"code": "E11.9", "desc": "Type 2 diabetes mellitus without complications"},
    "Hypertension": {"code": "I10", "desc": "Essential (primary) hypertension"},
    "Heart Failure": {"code": "I50.9", "desc": "Heart failure, unspecified"},
    "COPD": {"code": "J44.1", "desc": "COPD with acute exacerbation"},
    "Appendicitis": {"code": "K35.80", "desc": "Unspecified acute appendicitis"},
    "Migraine": {"code": "G43.909", "desc": "Migraine, unspecified, not intractable"},
    "Anemia": {"code": "D64.9", "desc": "Anemia, unspecified"},
    "UTI": {"code": "N39.0", "desc": "Urinary tract infection, site not specified"},
    "Depression": {"code": "F32.9", "desc": "Major depressive disorder, single episode, unspecified"},
    "Sepsis": {"code": "A41.9", "desc": "Sepsis, unspecified organism"},
}


class GraphRAGService:
    """
    Medical knowledge graph retrieval service.

    In production, this connects to Neo4j and performs Cypher queries.
    For demo/testing, uses the built-in knowledge maps above.
    """

    def __init__(self, use_neo4j: bool = False):
        self.use_neo4j = use_neo4j
        self._driver = None

    def connect(self):
        if not self.use_neo4j or self._driver:
            return _AwaitableNone()

        try:
            from neo4j import GraphDatabase

            settings = get_settings()
            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            self._driver.verify_connectivity()
            logger.info("graphrag.neo4j_connected")
        except Exception as e:
            logger.warning("graphrag.neo4j_fallback", error=str(e))
            self.use_neo4j = False
            self._driver = None
        return _AwaitableNone()

    def find_diseases_by_symptoms(self, symptoms: list[str]) -> list[dict]:
        """Find candidate diseases given a list of symptom names."""
        normalized_symptoms = [_normalize_symptom(symptom) for symptom in symptoms if symptom]
        normalized_symptoms = [symptom for symptom in normalized_symptoms if symptom]

        if self.use_neo4j:
            try:
                self.connect()
                if self._driver:
                    results = self._find_diseases_by_symptoms_neo4j(normalized_symptoms)
                    if results:
                        return results
            except Exception as e:
                logger.warning("graphrag.neo4j_query_fallback", error=str(e))
                self.use_neo4j = False

        return self._find_diseases_by_symptoms_offline(normalized_symptoms)

    def _find_diseases_by_symptoms_offline(self, symptoms: list[str]) -> list[dict]:
        disease_scores: dict[str, int] = {}
        matched_symptoms: dict[str, list[str]] = {}
        for symptom in symptoms:
            for disease in SYMPTOM_DISEASE_MAP.get(symptom, []):
                disease_scores[disease] = disease_scores.get(disease, 0) + 1
                matched_symptoms.setdefault(disease, []).append(symptom)

        ranked = sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for disease, score in ranked:
            icd = DISEASE_ICD10_MAP.get(disease, {})
            symptoms_for_disease = matched_symptoms.get(disease, [])
            results.append({
                "disease": disease,
                "symptom_match_count": score,
                "icd10_code": icd.get("code", ""),
                "icd10_description": icd.get("desc", ""),
                "matching_symptoms": symptoms_for_disease,
                "evidence_paths": [
                    f"({symptom})-[:IS_SYMPTOM_OF]->({disease})"
                    for symptom in symptoms_for_disease
                ],
                "source": "Built-in GraphRAG fallback",
            })
        return results

    def _find_diseases_by_symptoms_neo4j(self, symptoms: list[str]) -> list[dict]:
        if not symptoms:
            return []

        cypher = """
        MATCH (s:Symptom)-[:IS_SYMPTOM_OF]->(d:Disease)
        WHERE s.name IN $symptoms
        OPTIONAL MATCH (d)-[:CODED_AS]->(icd:ICD10Code)
        WITH d, icd, collect(DISTINCT s.name) AS matching_symptoms
        RETURN d.name AS disease,
               size(matching_symptoms) AS symptom_match_count,
               coalesce(icd.code, d.icd10_code, "") AS icd10_code,
               coalesce(icd.description, d.icd10_description, "") AS icd10_description,
               matching_symptoms AS matching_symptoms
        ORDER BY symptom_match_count DESC, disease ASC
        LIMIT 20
        """
        rows = self.query_neo4j(cypher, {"symptoms": symptoms})
        results = []
        for row in rows:
            matching_symptoms = row.get("matching_symptoms") or []
            disease = row.get("disease", "")
            results.append({
                "disease": disease,
                "symptom_match_count": row.get("symptom_match_count", 0),
                "icd10_code": row.get("icd10_code", ""),
                "icd10_description": row.get("icd10_description", ""),
                "matching_symptoms": matching_symptoms,
                "evidence_paths": [
                    f"({symptom})-[:IS_SYMPTOM_OF]->({disease})"
                    for symptom in matching_symptoms
                ],
                "source": "Neo4j GraphRAG",
            })
        return results

    def get_icd10(self, disease_name: str) -> Optional[dict]:
        """Look up ICD-10 code for a disease name."""
        return DISEASE_ICD10_MAP.get(disease_name)

    def query_neo4j(self, cypher: str, params: dict = None) -> list[dict]:
        """Execute a Cypher query against Neo4j (production mode)."""
        if not self._driver:
            logger.warning("graphrag.neo4j_not_connected")
            return _AwaitableList()
        with self._driver.session() as session:
            result = session.run(cypher, params or {})
            return _AwaitableList(record.data() for record in result)

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None
        return _AwaitableNone()


_service: Optional[GraphRAGService] = None


def get_graphrag_service() -> GraphRAGService:
    global _service
    if _service is None:
        settings = get_settings()
        _service = GraphRAGService(use_neo4j=settings.graphrag_use_neo4j)
    return _service


def _normalize_symptom(symptom: str) -> str:
    return symptom.strip().lower().replace(" ", "_").replace("-", "_")
