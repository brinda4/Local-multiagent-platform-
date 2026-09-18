"""PharmacologyTargetAgent.

Specialized agent handling DrugCentral active ingredients, target mechanisms,
pharmacological actions (inhibitors, agonists, antagonists), and chemical structures.
Zero emoji characters in all outputs.
"""

from __future__ import annotations

import time
from typing import Any
import pandas as pd
from src.agents.base_agent import BaseAgent
from src.tools.db_tool import ReadOnlyDatabaseTool


class PharmacologyTargetAgent(BaseAgent):
    """Handles DrugCentral drug mechanism queries, target mappings, and bioactivities."""

    def __init__(self, db_tool: ReadOnlyDatabaseTool | None = None):
        super().__init__(
            name="PharmacologyTargetAgent",
            role="Pharmacology and Drug Mechanism Specialist",
            description="Queries DrugCentral target interactions, mechanisms of action (MoA), and bioactivities.",
            db_tool=db_tool
        )

    def search_drugs_by_gene(self, gene_symbol: str, limit: int = 25) -> dict[str, Any]:
        """Query pharmaceutical agents targeting a specific gene product."""
        sql = """
        SELECT t.drug_name, t.gene_symbol, t.target_name, t.target_class,
               t.action_type, t.moa, t.act_type, t.act_value, t.act_unit,
               s.smiles, s.inchikey
        FROM drugcentral_targets t
        LEFT JOIN drugcentral_structures s ON t.struct_id = s.struct_id
        WHERE t.gene_symbol = ?
        ORDER BY t.moa DESC, t.act_value ASC
        LIMIT ?;
        """
        res = self.db_tool.execute_query(sql, (gene_symbol.strip().upper(), limit))
        return res

    def search_drugs_by_genes(self, gene_symbols: list[str], limit: int = 30) -> dict[str, Any]:
        """Query pharmaceutical agents targeting any gene within a list of candidates."""
        if not gene_symbols:
            return {"success": False, "data": pd.DataFrame(), "row_count": 0}

        placeholders = ",".join(["?"] * len(gene_symbols))
        params = [g.strip().upper() for g in gene_symbols] + [limit]

        sql = f"""
        SELECT t.drug_name, t.gene_symbol, t.target_name, t.target_class,
               t.action_type, t.moa, t.act_type, t.act_value, t.act_unit,
               s.smiles, s.inchikey
        FROM drugcentral_targets t
        LEFT JOIN drugcentral_structures s ON t.struct_id = s.struct_id
        WHERE t.gene_symbol IN ({placeholders})
        ORDER BY t.moa DESC, t.act_value ASC
        LIMIT ?;
        """
        res = self.db_tool.execute_query(sql, tuple(params))
        return res

    def search_profile_by_drug(self, drug_name: str, limit: int = 20) -> dict[str, Any]:
        """Query full pharmacological profile for a specific active ingredient."""
        sql = """
        SELECT t.drug_name, t.gene_symbol, t.target_name, t.target_class,
               t.action_type, t.moa, t.act_type, t.act_value, t.act_unit,
               s.smiles, s.inchikey, s.cas_rn
        FROM drugcentral_targets t
        LEFT JOIN drugcentral_structures s ON t.struct_id = s.struct_id
        WHERE t.drug_name LIKE ?
        ORDER BY t.moa DESC
        LIMIT ?;
        """
        res = self.db_tool.execute_query(sql, (f"%{drug_name.strip().lower()}%", limit))
        return res

    def run(self, query: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Analyze pharmacology query and return structured drug-target mechanism evidence."""
        start_time = time.perf_counter()
        context = context or {}
        entities = context.get("entities", {})
        prior_genes = context.get("candidate_genes", [])

        genes = entities.get("genes", []) or prior_genes
        drugs = entities.get("drugs", [])

        primary_df = pd.DataFrame()
        summary_lines = []

        if drugs:
            target_drug = drugs[0]
            self.log_step("search_profile_by_drug", {"drug": target_drug})
            res = self.search_profile_by_drug(target_drug, limit=25)
            if res["success"]:
                primary_df = res["data"]
            summary_lines.append(f"Investigated pharmacological profile for active ingredient '{target_drug}'.")
            if not primary_df.empty:
                targets = primary_df["gene_symbol"].dropna().unique().tolist()
                actions = primary_df["action_type"].dropna().unique().tolist()
                summary_lines.append(
                    f"DrugCentral records {len(primary_df)} target interactions. Primary genes: {', '.join(targets[:5])}. Modalities: {', '.join(actions[:4])}."
                )
            else:
                summary_lines.append(f"No specific target interactions recorded for '{target_drug}'.")

        elif genes:
            self.log_step("search_drugs_by_genes", {"genes": genes[:10]})
            res = self.search_drugs_by_genes(genes[:10], limit=30)
            if res["success"]:
                primary_df = res["data"]
            summary_lines.append(
                f"Identified pharmaceutical interventions targeting candidate genes: {', '.join(genes[:5])}."
            )
            if not primary_df.empty:
                moa_count = int(primary_df["moa"].sum())
                top_drugs = primary_df["drug_name"].unique().tolist()[:6]
                summary_lines.append(
                    f"Identified {len(primary_df)} drug-target records ({moa_count} confirmed clinical MoA). Candidate compounds: {', '.join(top_drugs)}."
                )
            else:
                summary_lines.append("No active ingredients found in DrugCentral for the candidate gene set.")
        else:
            # Broad search
            res = self.search_profile_by_drug(query, limit=20)
            if res["success"] and not res["data"].empty:
                primary_df = res["data"]
                summary_lines.append(f"Matched {len(primary_df)} pharmacological records for query '{query}'.")
            else:
                summary_lines.append(f"Unable to resolve drug or target gene entity for query: '{query}'.")

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "agent": self.name,
            "success": True,
            "query": query,
            "elapsed_ms": round(elapsed_ms, 2),
            "summary": " ".join(summary_lines),
            "data": primary_df,
            "identified_drugs": primary_df["drug_name"].unique().tolist() if not primary_df.empty else [],
            "targeted_genes": primary_df["gene_symbol"].unique().tolist() if not primary_df.empty else [],
        }
