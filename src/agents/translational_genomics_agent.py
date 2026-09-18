"""TranslationalGenomicsAgent.

Specialized agent handling DisGeNET gene-disease associations, variant scores,
and MONDO disease ontology classifications.
Zero emoji characters in all outputs.
"""

from __future__ import annotations

import time
from typing import Any
import pandas as pd
from src.agents.base_agent import BaseAgent
from src.tools.db_tool import ReadOnlyDatabaseTool


class TranslationalGenomicsAgent(BaseAgent):
    """Handles DisGeNET gene-disease variant scoring and MONDO ontology mappings."""

    def __init__(self, db_tool: ReadOnlyDatabaseTool | None = None):
        super().__init__(
            name="TranslationalGenomicsAgent",
            role="Translational Genomics and Disease Variant Specialist",
            description="Queries DisGeNET curated associations, variant confidence scores, and MONDO classifications.",
            db_tool=db_tool
        )

    def search_by_disease(self, disease_query: str, limit: int = 15) -> dict[str, Any]:
        """Search DisGeNET for genes associated with a disease query."""
        sql = """
        SELECT gene_symbol, disease_name, association_score, variant_score,
               evidence_count, evidence_level, disease_category, disease_id
        FROM disgenet_associations
        WHERE disease_name LIKE ?
        ORDER BY association_score DESC, variant_score DESC
        LIMIT ?;
        """
        param = f"%{disease_query.strip()}%"
        res = self.db_tool.execute_query(sql, (param, limit))
        return res

    def search_by_gene(self, gene_symbol: str, limit: int = 15) -> dict[str, Any]:
        """Search DisGeNET for diseases associated with a gene symbol."""
        sql = """
        SELECT gene_symbol, disease_name, association_score, variant_score,
               evidence_count, evidence_level, disease_category, disease_id
        FROM disgenet_associations
        WHERE gene_symbol = ? OR gene_symbol LIKE ?
        ORDER BY association_score DESC
        LIMIT ?;
        """
        g_clean = gene_symbol.strip().upper()
        res = self.db_tool.execute_query(sql, (g_clean, f"%{g_clean}%", limit))
        return res

    def lookup_mondo_definition(self, disease_term: str) -> dict[str, Any]:
        """Lookup disease definition from MONDO ontology."""
        sql = """
        SELECT mondo_id, disease_name, definition, parent_ids
        FROM mondo_ontology
        WHERE disease_name LIKE ?
        LIMIT 5;
        """
        param = f"%{disease_term.strip()}%"
        res = self.db_tool.execute_query(sql, (param,))
        return res

    def run(self, query: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Analyze disease genomics query and return structured evidence."""
        start_time = time.perf_counter()
        context = context or {}
        entities = context.get("entities", {})
        
        genes = entities.get("genes", [])
        diseases = entities.get("diseases", [])

        # Fallback entity extraction if not pre-populated
        if not genes and not diseases:
            q_clean = query.strip()
            # If uppercase word exists, treat as gene
            words = q_clean.split()
            for w in words:
                w_strip = w.strip("?,.:;\"'")
                if w_strip.isupper() and 2 <= len(w_strip) <= 8:
                    genes.append(w_strip)
            if not genes:
                diseases.append(q_clean)

        primary_df = pd.DataFrame()
        mondo_df = pd.DataFrame()
        summary_lines = []
        
        if diseases:
            target_disease = diseases[0]
            self.log_step("search_by_disease", {"disease": target_disease})
            res = self.search_by_disease(target_disease, limit=20)
            if res["success"]:
                primary_df = res["data"]
            
            # Also get MONDO definitions
            m_res = self.lookup_mondo_definition(target_disease)
            if m_res["success"]:
                mondo_df = m_res["data"]
                
            summary_lines.append(f"Identified disease target: '{target_disease}'.")
            if not primary_df.empty:
                top_genes = primary_df["gene_symbol"].head(5).tolist()
                summary_lines.append(
                    f"DisGeNET curated query identified {len(primary_df)} associated genes. Top candidates: {', '.join(top_genes)}."
                )
            else:
                summary_lines.append(f"No direct DisGeNET associations found for '{target_disease}'.")
                
        elif genes:
            target_gene = genes[0]
            self.log_step("search_by_gene", {"gene": target_gene})
            res = self.search_by_gene(target_gene, limit=20)
            if res["success"]:
                primary_df = res["data"]
            summary_lines.append(f"Identified gene target: '{target_gene}'.")
            if not primary_df.empty:
                top_diseases = primary_df["disease_name"].head(5).tolist()
                summary_lines.append(
                    f"DisGeNET query identified {len(primary_df)} disease associations for {target_gene}. Key phenotypes: {'; '.join(top_diseases)}."
                )
            else:
                summary_lines.append(f"No direct DisGeNET associations found for '{target_gene}'.")
        else:
            # Broad search
            res = self.search_by_disease(query, limit=20)
            if res["success"] and not res["data"].empty:
                primary_df = res["data"]
                summary_lines.append(f"General query '{query}' matched {len(primary_df)} DisGeNET associations.")
            else:
                summary_lines.append(f"Unable to resolve disease or gene entity for query: '{query}'.")

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        return {
            "agent": self.name,
            "success": True,
            "query": query,
            "elapsed_ms": round(elapsed_ms, 2),
            "summary": " ".join(summary_lines),
            "data": primary_df,
            "mondo_data": mondo_df,
            "candidate_genes": primary_df["gene_symbol"].unique().tolist() if not primary_df.empty else [],
            "candidate_diseases": primary_df["disease_name"].unique().tolist() if not primary_df.empty else [],
        }
