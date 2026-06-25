"""Optional Neo4j integration tests for the lightweight GraphRAG graph."""

import os

import pytest


@pytest.mark.skipif(
    os.getenv("RUN_NEO4J_TESTS") != "1",
    reason="Set RUN_NEO4J_TESTS=1 to run Neo4j integration tests.",
)
def test_seeded_neo4j_returns_pneumonia_candidate():
    from neo4j import GraphDatabase

    from scripts.seed_neo4j_kg import create_constraints, reset_graph, seed_graph
    from src.config.settings import get_settings
    from src.services.graphrag_service import GraphRAGService

    settings = get_settings()
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    try:
        driver.verify_connectivity()
        with driver.session() as session:
            reset_graph(session)
            create_constraints(session)
            seed_graph(session)

        service = GraphRAGService(use_neo4j=True)
        results = service.find_diseases_by_symptoms(["fever", "cough"])
        pneumonia = next(result for result in results if result["disease"] == "Pneumonia")
        assert pneumonia["icd10_code"] == "J18.9"
        assert pneumonia["symptom_match_count"] == 2
        assert pneumonia["source"] == "Neo4j GraphRAG"
        service.close()
    finally:
        driver.close()
