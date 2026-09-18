"""AnatomyExpressionAgent.

Specialized agent handling Bgee anatomical gene expression lookups and
UBERON anatomical structure ontology classifications.
Zero emoji characters in all outputs.
"""

from __future__ import annotations

import time
from typing import Any
import pandas as pd
from src.agents.base_agent import BaseAgent
from src.tools.db_tool import ReadOnlyDatabaseTool


class AnatomyExpressionAgent(BaseAgent):
    """Handles Bgee anatomical tissue expression lookups and UBERON ontology mappings."""

    def __init__(self, db_tool: ReadOnlyDatabaseTool | None = None):
        super().__init__(
            name="AnatomyExpressionAgent",
            role="Anatomical Expression and Tissue Specificity Specialist",
            description="Queries Bgee curated expression scores, gold quality tissue calls, and UBERON anatomy.",
            db_tool=db_tool
        )

    def search_expression_by_gene(self, gene_symbol: str, limit: int = 20) -> dict[str, Any]:
        """Query anatomical tissues expressing the target gene."""
        sql = """
        SELECT gene_name, anatomy_name, anatomy_id, expression_score,
               expression_rank, expression_call, call_quality, fdr
        FROM bgee_expression
        WHERE gene_name = ?
        ORDER BY expression_score DESC, expression_rank ASC
        LIMIT ?;
        """
        res = self.db_tool.execute_query(sql, (gene_symbol.strip().upper(), limit))
        return res

    def search_expression_by_genes(self, gene_symbols: list[str], tissue_filter: str | None = None, limit: int = 25) -> dict[str, Any]:
        """Query expression for multiple genes, optionally filtered by anatomical structure."""
        if not gene_symbols:
            return {"success": False, "data": pd.DataFrame(), "row_count": 0}

        placeholders = ",".join(["?"] * len(gene_symbols))
        params = [g.strip().upper() for g in gene_symbols]

        if tissue_filter:
            sql = f"""
            SELECT gene_name, anatomy_name, anatomy_id, expression_score,
                   expression_rank, expression_call, call_quality
            FROM bgee_expression
            WHERE gene_name IN ({placeholders}) AND anatomy_name LIKE ?
            ORDER BY expression_score DESC
            LIMIT ?;
            """
            params.append(f"%{tissue_filter.strip()}%")
            params.append(limit)
        else:
            sql = f"""
            SELECT gene_name, anatomy_name, anatomy_id, expression_score,
                   expression_rank, expression_call, call_quality
            FROM bgee_expression
            WHERE gene_name IN ({placeholders})
            ORDER BY expression_score DESC
            LIMIT ?;
            """
            params.append(limit)

        res = self.db_tool.execute_query(sql, tuple(params))
        return res

    def search_genes_by_tissue(self, tissue_name: str, limit: int = 20) -> dict[str, Any]:
        """Query top expressed genes within a specific anatomical tissue."""
        sql = """
        SELECT gene_name, anatomy_name, anatomy_id, expression_score,
               expression_rank, expression_call, call_quality
        FROM bgee_expression
        WHERE anatomy_name LIKE ?
        ORDER BY expression_score DESC, expression_rank ASC
        LIMIT ?;
        """
        res = self.db_tool.execute_query(sql, (f"%{tissue_name.strip()}%", limit))
        return res

    def lookup_uberon_definition(self, tissue_term: str) -> dict[str, Any]:
        """Lookup anatomical entity definition from UBERON ontology."""
        sql = """
        SELECT uberon_id, anatomy_name, definition, parent_ids, part_of
        FROM uberon_ontology
        WHERE anatomy_name LIKE ?
        LIMIT 5;
        """
        res = self.db_tool.execute_query(sql, (f"%{tissue_term.strip()}%",))
        return res

    def run(self, query: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Analyze anatomical expression query and return structured tissue evidence."""
        start_time = time.perf_counter()
        context = context or {}
        entities = context.get("entities", {})
        prior_genes = context.get("candidate_genes", [])
        
        genes = entities.get("genes", []) or prior_genes
        tissues = entities.get("tissues", [])

        primary_df = pd.DataFrame()
        uberon_df = pd.DataFrame()
        summary_lines = []

        if genes and tissues:
            target_tissue = tissues[0]
            self.log_step("search_expression_by_genes_and_tissue", {"genes": genes[:5], "tissue": target_tissue})
            res = self.search_expression_by_genes(genes[:10], tissue_filter=target_tissue, limit=25)
            if res["success"]:
                primary_df = res["data"]
            
            u_res = self.lookup_uberon_definition(target_tissue)
            if u_res["success"]:
                uberon_df = u_res["data"]
                
            summary_lines.append(
                f"Evaluated expression of {len(genes)} target genes in anatomical tissue '{target_tissue}'."
            )
            if not primary_df.empty:
                top_hit = primary_df.iloc[0]
                summary_lines.append(
                    f"Highest expression observed for {top_hit['gene_name']} (score: {top_hit['expression_score']}, rank: {top_hit['expression_rank']})."
                )
            else:
                summary_lines.append(f"No specific expression entries recorded for these genes in '{target_tissue}'.")

        elif genes:
            target_gene = genes[0]
            self.log_step("search_expression_by_gene", {"gene": target_gene})
            res = self.search_expression_by_gene(target_gene, limit=25)
            if res["success"]:
                primary_df = res["data"]
            summary_lines.append(f"Queried anatomical tissue expression profile for gene '{target_gene}'.")
            if not primary_df.empty:
                top_tissues = primary_df["anatomy_name"].head(4).tolist()
                summary_lines.append(
                    f"Bgee gold quality calls indicate primary expression across: {', '.join(top_tissues)}."
                )
            else:
                summary_lines.append(f"No Bgee anatomical expression records found for '{target_gene}'.")

        elif tissues:
            target_tissue = tissues[0]
            self.log_step("search_genes_by_tissue", {"tissue": target_tissue})
            res = self.search_genes_by_tissue(target_tissue, limit=25)
            if res["success"]:
                primary_df = res["data"]
            u_res = self.lookup_uberon_definition(target_tissue)
            if u_res["success"]:
                uberon_df = u_res["data"]
            summary_lines.append(f"Queried top expressing genes in anatomical structure '{target_tissue}'.")
            if not primary_df.empty:
                top_genes = primary_df["gene_name"].head(5).tolist()
                summary_lines.append(f"Dominant expressing genes: {', '.join(top_genes)}.")
            else:
                summary_lines.append(f"No records found for anatomical structure '{target_tissue}'.")
        else:
            # Broad search
            res = self.search_genes_by_tissue(query, limit=20)
            if res["success"] and not res["data"].empty:
                primary_df = res["data"]
                summary_lines.append(f"Matched {len(primary_df)} expression entries for query '{query}'.")
            else:
                summary_lines.append(f"Unable to resolve anatomical structure or gene for query: '{query}'.")

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "agent": self.name,
            "success": True,
            "query": query,
            "elapsed_ms": round(elapsed_ms, 2),
            "summary": " ".join(summary_lines),
            "data": primary_df,
            "uberon_data": uberon_df,
            "expressed_tissues": primary_df["anatomy_name"].unique().tolist() if not primary_df.empty else [],
        }
