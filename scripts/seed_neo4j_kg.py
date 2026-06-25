"""Seed the lightweight medical GraphRAG knowledge graph into Neo4j."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import get_settings
from src.services.graphrag_service import DISEASE_ICD10_MAP, SYMPTOM_DISEASE_MAP

EMPTY_PASSWORDS = {""}


def build_seed_rows() -> tuple[list[dict], list[dict], list[dict]]:
    symptoms = [{"name": name} for name in sorted(SYMPTOM_DISEASE_MAP)]

    diseases = []
    icd10_codes = {}
    for disease_names in SYMPTOM_DISEASE_MAP.values():
        for disease_name in disease_names:
            icd = DISEASE_ICD10_MAP.get(disease_name, {})
            diseases.append({
                "name": disease_name,
                "icd10_code": icd.get("code", ""),
                "icd10_description": icd.get("desc", ""),
            })
            if icd.get("code"):
                icd10_codes[icd["code"]] = {
                    "code": icd["code"],
                    "description": icd.get("desc", ""),
                }

    unique_diseases = {disease["name"]: disease for disease in diseases}
    relationships = [
        {"symptom": symptom, "disease": disease}
        for symptom, disease_names in SYMPTOM_DISEASE_MAP.items()
        for disease in disease_names
    ]
    return symptoms, list(unique_diseases.values()), relationships + list(icd10_codes.values())


def reset_graph(session, batch_size: int = 500) -> int:
    count_result = session.run("MATCH (n) RETURN count(n) AS total")
    total = count_result.single()["total"]
    if not total:
        return 0

    print(f"Deleting {total} existing Neo4j nodes in batches of {batch_size}...")
    session.run(
        f"""
        MATCH (n)
        CALL (n) {{
          DETACH DELETE n
        }} IN TRANSACTIONS OF {batch_size} ROWS
        """
    ).consume()
    print(f"Deleted {total} existing Neo4j nodes.")
    return total


def create_constraints(session) -> None:
    session.run(
        "CREATE CONSTRAINT symptom_name IF NOT EXISTS "
        "FOR (s:Symptom) REQUIRE s.name IS UNIQUE"
    )
    session.run(
        "CREATE CONSTRAINT disease_name IF NOT EXISTS "
        "FOR (d:Disease) REQUIRE d.name IS UNIQUE"
    )
    session.run(
        "CREATE CONSTRAINT icd10_code IF NOT EXISTS "
        "FOR (i:ICD10Code) REQUIRE i.code IS UNIQUE"
    )


def seed_graph(session) -> dict[str, int]:
    symptoms, diseases, relation_and_icd_rows = build_seed_rows()
    relationships = [row for row in relation_and_icd_rows if "symptom" in row]
    icd10_codes = [row for row in relation_and_icd_rows if "code" in row]

    session.run(
        """
        UNWIND $symptoms AS row
        MERGE (:Symptom {name: row.name})
        """,
        symptoms=symptoms,
    )
    session.run(
        """
        UNWIND $diseases AS row
        MERGE (d:Disease {name: row.name})
        SET d.icd10_code = row.icd10_code,
            d.icd10_description = row.icd10_description
        """,
        diseases=diseases,
    )
    session.run(
        """
        UNWIND $codes AS row
        MERGE (i:ICD10Code {code: row.code})
        SET i.description = row.description
        """,
        codes=icd10_codes,
    )
    session.run(
        """
        UNWIND $relationships AS row
        MATCH (s:Symptom {name: row.symptom})
        MATCH (d:Disease {name: row.disease})
        MERGE (s)-[:IS_SYMPTOM_OF]->(d)
        """,
        relationships=relationships,
    )
    session.run(
        """
        MATCH (d:Disease)
        WHERE d.icd10_code <> ""
        MATCH (i:ICD10Code {code: d.icd10_code})
        MERGE (d)-[:CODED_AS]->(i)
        """
    )

    return {
        "symptoms": len(symptoms),
        "diseases": len(diseases),
        "icd10_codes": len(icd10_codes),
        "symptom_disease_relationships": len(relationships),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="Clear existing graph data before seeding.")
    parser.add_argument("--reset-batch-size", type=int, default=500, help="Nodes to delete per reset batch.")
    parser.add_argument("--dry-run", action="store_true", help="Print seed counts without connecting to Neo4j.")
    parser.add_argument("--uri", help="Override NEO4J_URI from .env/settings.")
    parser.add_argument("--user", help="Override NEO4J_USER from .env/settings.")
    parser.add_argument("--password", help="Override NEO4J_PASSWORD from .env/settings.")
    args = parser.parse_args()

    symptoms, diseases, relation_and_icd_rows = build_seed_rows()
    relationships = [row for row in relation_and_icd_rows if "symptom" in row]
    icd10_codes = [row for row in relation_and_icd_rows if "code" in row]
    if args.dry_run:
        print(
            "Dry run: "
            f"{len(symptoms)} symptoms, {len(diseases)} diseases, "
            f"{len(icd10_codes)} ICD-10 codes, {len(relationships)} symptom-disease relationships."
        )
        return 0

    settings = get_settings()
    uri = args.uri or settings.neo4j_uri
    user = args.user or settings.neo4j_user
    password = args.password if args.password is not None else settings.neo4j_password
    if password in EMPTY_PASSWORDS:
        print(
            "Neo4j password is empty. "
            "Set NEO4J_PASSWORD in .env or pass --password explicitly.",
            file=sys.stderr,
        )
        print(
            "Example: python scripts\\seed_neo4j_kg.py --reset --password your-password-here",
            file=sys.stderr,
        )
        return 2

    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(
        uri,
        auth=(user, password),
        connection_timeout=10,
        connection_acquisition_timeout=10,
    )
    try:
        driver.verify_connectivity()
        with driver.session() as session:
            if args.reset:
                reset_graph(session, batch_size=args.reset_batch_size)
            create_constraints(session)
            counts = seed_graph(session)
        print(f"Seeded Neo4j GraphRAG knowledge graph: {counts}")
    except Exception as exc:
        print(f"Failed to seed Neo4j GraphRAG knowledge graph: {exc}", file=sys.stderr)
        return 1
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
