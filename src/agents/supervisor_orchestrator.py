"""SupervisorOrchestrator.

Orchestrates multi-agent biomedical queries across:
- TranslationalGenomicsAgent (DisGeNET / MONDO)
- AnatomyExpressionAgent (Bgee / UBERON)
- PharmacologyTargetAgent (DrugCentral / Structures)

Manages conversational session history and synthesizes cross-domain translational intelligence.
Zero emoji characters in all outputs.
"""

from __future__ import annotations

import time
from typing import Any
import pandas as pd
from src.tools.db_tool import ReadOnlyDatabaseTool
from src.tools.query_analyzer import QueryAnalyzer
from src.agents.translational_genomics_agent import TranslationalGenomicsAgent
from src.agents.anatomy_expression_agent import AnatomyExpressionAgent
from src.agents.pharmacology_target_agent import PharmacologyTargetAgent


class SupervisorOrchestrator:
    """Central supervisor orchestrator routing queries and synthesizing multi-agent findings."""

    def __init__(self, db_tool: ReadOnlyDatabaseTool | None = None):
        self.db_tool = db_tool or ReadOnlyDatabaseTool()
        self.analyzer = QueryAnalyzer()

        # Initialize specialized domain agents
        self.genomics_agent = TranslationalGenomicsAgent(db_tool=self.db_tool)
        self.anatomy_agent = AnatomyExpressionAgent(db_tool=self.db_tool)
        self.pharmacology_agent = PharmacologyTargetAgent(db_tool=self.db_tool)

        # In-memory session history
        self.session_history: list[dict[str, Any]] = []

    def route_and_execute(self, query: str) -> dict[str, Any]:
        """Classify intent, route query to specialist agents, and synthesize findings."""
        start_time = time.perf_counter()
        analysis = self.analyzer.analyze(query)
        intent = analysis["primary_intent"]
        entities = analysis["entities"]

        agent_traces: list[dict[str, Any]] = []
        synthesized_sections: list[str] = []
        data_tables: dict[str, pd.DataFrame] = {}

        # ---------------------------------------------------------------------
        # Route 1: Single Agent - Translational Genomics
        # ---------------------------------------------------------------------
        if intent == "TRANSLATIONAL_GENOMICS":
            trace = self.genomics_agent.run(query, context={"entities": entities})
            agent_traces.append(trace)
            if not trace["data"].empty:
                data_tables["disgenet_associations"] = trace["data"]
            if not trace["mondo_data"].empty:
                data_tables["mondo_ontology"] = trace["mondo_data"]
            synthesized_sections.append(f"### Translational Genomics Evaluation\n{trace['summary']}")

        # ---------------------------------------------------------------------
        # Route 2: Single Agent - Anatomy & Tissue Expression
        # ---------------------------------------------------------------------
        elif intent == "ANATOMY_EXPRESSION":
            trace = self.anatomy_agent.run(query, context={"entities": entities})
            agent_traces.append(trace)
            if not trace["data"].empty:
                data_tables["bgee_expression"] = trace["data"]
            if not trace["uberon_data"].empty:
                data_tables["uberon_ontology"] = trace["uberon_data"]
            synthesized_sections.append(f"### Anatomical Expression Profile\n{trace['summary']}")

        # ---------------------------------------------------------------------
        # Route 3: Single Agent - Pharmacology & Drug Targets
        # ---------------------------------------------------------------------
        elif intent == "PHARMACOLOGY_TARGET":
            trace = self.pharmacology_agent.run(query, context={"entities": entities})
            agent_traces.append(trace)
            if not trace["data"].empty:
                data_tables["drugcentral_targets"] = trace["data"]
            synthesized_sections.append(f"### Pharmacology & Target Mechanism Report\n{trace['summary']}")

        # ---------------------------------------------------------------------
        # Route 4: Multi-Agent Translational Orchestration
        # ---------------------------------------------------------------------
        else:
            # Step 1: Query disease genomics (DisGeNET)
            g_trace = self.genomics_agent.run(query, context={"entities": entities})
            agent_traces.append(g_trace)
            if not g_trace["data"].empty:
                data_tables["disgenet_associations"] = g_trace["data"]
            if not g_trace["mondo_data"].empty:
                data_tables["mondo_ontology"] = g_trace["mondo_data"]

            candidate_genes = g_trace.get("candidate_genes", [])
            if not candidate_genes and entities["genes"]:
                candidate_genes = entities["genes"]

            # Step 2: Query drug mechanisms for candidate genes (DrugCentral)
            ph_trace = self.pharmacology_agent.run(
                query,
                context={"entities": entities, "candidate_genes": candidate_genes[:8]}
            )
            agent_traces.append(ph_trace)
            if not ph_trace["data"].empty:
                data_tables["drugcentral_targets"] = ph_trace["data"]

            # Step 3: Query anatomical tissue expression (Bgee)
            an_trace = self.anatomy_agent.run(
                query,
                context={"entities": entities, "candidate_genes": candidate_genes[:8]}
            )
            agent_traces.append(an_trace)
            if not an_trace["data"].empty:
                data_tables["bgee_expression"] = an_trace["data"]
            if not an_trace["uberon_data"].empty:
                data_tables["uberon_ontology"] = an_trace["uberon_data"]

            # Synthesis
            synthesized_sections.append("### Cross-Domain Multi-Agent Translational Discovery")
            synthesized_sections.append(
                f"1. **Genomic Variant Landscape (DisGeNET)**: {g_trace['summary']}"
            )
            synthesized_sections.append(
                f"2. **Therapeutic Targeting & Mechanisms (DrugCentral)**: {ph_trace['summary']}"
            )
            synthesized_sections.append(
                f"3. **Anatomical Expression Validation (Bgee)**: {an_trace['summary']}"
            )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        final_report = "\n\n".join(synthesized_sections)

        result_payload = {
            "query": query,
            "intent": intent,
            "entities": entities,
            "elapsed_ms": round(elapsed_ms, 2),
            "final_report": final_report,
            "agent_traces": agent_traces,
            "data_tables": data_tables,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        }

        # Save to session history
        self.session_history.append(result_payload)
        return result_payload

    def get_history(self) -> list[dict[str, Any]]:
        """Return full conversational session history."""
        return self.session_history

    def clear_history(self) -> None:
        """Clear session history."""
        self.session_history.clear()
