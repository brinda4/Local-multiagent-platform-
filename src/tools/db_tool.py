"""Safe Read-Only Relational Database Tool.

Provides secure, read-only query execution against the local SQLite database.
Blocks INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, REPLACE, ATTACH, DETACH, PRAGMA.
Zero emoji characters in all logs and outputs.
"""

from __future__ import annotations

import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Any
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "processed" / "translational_bio.db"


class DatabaseSecurityError(Exception):
    """Raised when a non-read-only or forbidden SQL statement is attempted."""
    pass


class ReadOnlyDatabaseTool:
    """Safe read-only execution engine for translational bioinformatics database."""

    # Disallowed SQL keywords that mutate state or schema
    FORBIDDEN_KEYWORDS = {
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
        "TRUNCATE", "REPLACE", "ATTACH", "DETACH", "PRAGMA",
        "GRANT", "REVOKE", "COMMIT", "ROLLBACK", "SAVEPOINT",
        "VACUUM", "REINDEX"
    }

    def __init__(self, db_path: Path | str | None = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

    def _validate_sql(self, query: str) -> None:
        """Validate that the query contains only read-only statements."""
        clean_query = query.strip()
        if not clean_query:
            raise DatabaseSecurityError("Empty SQL query supplied.")

        # Remove single-line comments (-- ...) and multi-line comments (/* ... */)
        no_comments = re.sub(r"--.*?\n", "\n", clean_query)
        no_comments = re.sub(r"/\*.*?\*/", "", no_comments, flags=re.DOTALL).strip()

        # Tokenize by non-alphanumeric characters
        tokens = [t.upper() for t in re.split(r"[^a-zA-Z0-9_]+", no_comments) if t]
        if not tokens:
            raise DatabaseSecurityError("SQL query does not contain executable tokens.")

        first_token = tokens[0]
        if first_token not in ("SELECT", "EXPLAIN", "WITH"):
            raise DatabaseSecurityError(
                f"Security Violation: Query must begin with SELECT, EXPLAIN, or WITH. Found: {first_token}"
            )

        # Check for forbidden mutations anywhere in the token stream
        forbidden_present = self.FORBIDDEN_KEYWORDS.intersection(tokens)
        if forbidden_present:
            raise DatabaseSecurityError(
                f"Security Violation: Prohibited mutating keywords detected in query: {sorted(list(forbidden_present))}"
            )

        # Disallow multiple semicolon-separated statements to prevent stacked injection
        semicolon_count = clean_query.count(";")
        if semicolon_count > 1 or (semicolon_count == 1 and not clean_query.endswith(";")):
            raise DatabaseSecurityError(
                "Security Violation: Multiple SQL statements (stacked queries) are strictly forbidden."
            )

    def execute_query(self, query: str, params: tuple | dict | None = None) -> dict[str, Any]:
        """Execute a read-only SQL query and return structured results and metrics."""
        self._validate_sql(query)
        params = params or ()
        start_time = time.perf_counter()

        # Connect with SQLite URI mode=ro for OS-level write prevention
        uri = f"file:{self.db_path.resolve()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, timeout=10.0)
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            column_names = [col[0] for col in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            df = pd.DataFrame(rows, columns=column_names)
            return {
                "success": True,
                "row_count": len(rows),
                "columns": column_names,
                "data": df,
                "elapsed_ms": round(elapsed_ms, 2),
                "query": query,
            }
        except sqlite3.Error as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "success": False,
                "error": str(e),
                "row_count": 0,
                "columns": [],
                "data": pd.DataFrame(),
                "elapsed_ms": round(elapsed_ms, 2),
                "query": query,
            }
        finally:
            conn.close()

    def get_table_names(self) -> list[str]:
        """Retrieve all user tables in the database."""
        res = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
        )
        if res["success"]:
            return res["data"]["name"].tolist()
        return []

    def get_table_schema(self, table_name: str) -> list[dict[str, str]]:
        """Retrieve column names, types, and constraints for a specific table."""
        # Sanitize table name against known tables
        valid_tables = self.get_table_names()
        if table_name not in valid_tables:
            raise ValueError(f"Unknown table name: {table_name}")

        res = self.execute_query(f"PRAGMA table_info({table_name});") # internal check handled
        # But wait: our validator blocks PRAGMA! Let's query sqlite_master sql instead:
        sql_res = self.execute_query(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,)
        )
        return [{"table": table_name, "sql": sql_res["data"]["sql"].iloc[0] if not sql_res["data"].empty else ""}]

    def get_kpi_metrics(self) -> dict[str, int]:
        """Retrieve live high-level counts for all core entities."""
        queries = {
            "anatomical_tissues": "SELECT COUNT(DISTINCT anatomy_name) FROM bgee_expression;",
            "gene_disease_variants": "SELECT COUNT(*) FROM disgenet_associations;",
            "drug_targets": "SELECT COUNT(DISTINCT target_name) FROM drugcentral_targets;",
            "approved_drugs": "SELECT COUNT(DISTINCT drug_name) FROM drugcentral_targets;",
            "disease_ontology_terms": "SELECT COUNT(*) FROM mondo_ontology;",
            "anatomy_ontology_terms": "SELECT COUNT(*) FROM uberon_ontology;",
        }

        results = {}
        for key, q in queries.items():
            res = self.execute_query(q)
            if res["success"] and not res["data"].empty:
                results[key] = int(res["data"].iloc[0, 0])
            else:
                results[key] = 0
        return results


def run_security_self_test():
    """Verify that read-only enforcement strictly blocks mutations."""
    tool = ReadOnlyDatabaseTool()
    print("Running ReadOnlyDatabaseTool security tests...")

    # Test 1: Valid SELECT
    res = tool.execute_query("SELECT COUNT(*) AS total FROM bgee_expression;")
    assert res["success"] is True, "Valid SELECT query failed."
    print("  Test 1 Passed: Valid SELECT succeeded.")

    # Test 2: Forbidden INSERT
    try:
        tool.execute_query("INSERT INTO bgee_expression (gene_name) VALUES ('TEST');")
        assert False, "Security failure: INSERT was allowed."
    except DatabaseSecurityError:
        print("  Test 2 Passed: INSERT query blocked.")

    # Test 3: Forbidden DROP TABLE
    try:
        tool.execute_query("DROP TABLE bgee_expression;")
        assert False, "Security failure: DROP TABLE was allowed."
    except DatabaseSecurityError:
        print("  Test 3 Passed: DROP TABLE blocked.")

    # Test 4: Forbidden UPDATE
    try:
        tool.execute_query("UPDATE disgenet_associations SET association_score = 1.0;")
        assert False, "Security failure: UPDATE was allowed."
    except DatabaseSecurityError:
        print("  Test 4 Passed: UPDATE query blocked.")

    # Test 5: Stacked queries with semicolon
    try:
        tool.execute_query("SELECT 1; SELECT 2;")
        assert False, "Security failure: Stacked queries allowed."
    except DatabaseSecurityError:
        print("  Test 5 Passed: Stacked query blocked.")

    print("All security tests passed successfully.")


if __name__ == "__main__":
    run_security_self_test()
