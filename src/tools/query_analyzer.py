"""Biomedical Query Analyzer and Entity Extractor.

Extracts biological entities (genes, diseases, tissues, drugs) and classifies query intent.
Zero emoji characters in all output strings.
"""

from __future__ import annotations

import re
from typing import Any


class QueryAnalyzer:
    """Extracts entities and classifies biomedical query intents."""

    # Common gene symbols regex (2-8 uppercase letters/numbers)
    GENE_PATTERN = re.compile(r"\b([A-Z][A-Z0-9]{1,7})\b")

    # Intent routing keywords
    GENOMICS_KEYWORDS = {
        "disease", "variant", "disgenet", "mutation", "cancer", "carcinoma",
        "tumor", "syndrome", "association", "gda", "pathology", "mondo",
        "glioblastoma", "leukemia", "lymphoma", "melanoma", "alzheimer"
    }

    ANATOMY_KEYWORDS = {
        "tissue", "anatomy", "bgee", "expression", "express", "uberon",
        "organ", "brain", "liver", "lung", "heart", "kidney", "colon",
        "epithelium", "cortex", "muscle", "blood", "spleen", "stomach"
    }

    PHARMACOLOGY_KEYWORDS = {
        "drug", "compound", "molecule", "target", "mechanism", "moa",
        "pharmacology", "drugcentral", "inhibitor", "antagonist", "agonist",
        "blocker", "ic50", "ki", "smiles", "therapy", "treatment"
    }

    def analyze(self, query: str) -> dict[str, Any]:
        """Analyze a biomedical query for entities and routing intent."""
        q_lower = query.lower()
        q_clean = re.sub(r"[^\w\s-]", " ", query)
        words = set(q_lower.split())

        # Match possible gene symbols
        potential_genes = [
            m for m in self.GENE_PATTERN.findall(query)
            if m not in {"AND", "OR", "NOT", "THE", "FOR", "IN", "OF", "WITH", "TAB", "WHAT", "FIND", "SHOW", "LIST"}
        ]

        # Calculate keyword match scores
        genomics_score = len(words.intersection(self.GENOMICS_KEYWORDS))
        anatomy_score = len(words.intersection(self.ANATOMY_KEYWORDS))
        pharma_score = len(words.intersection(self.PHARMACOLOGY_KEYWORDS))

        # Check for specific disease entities
        disease_hints = []
        for d in ["glioblastoma", "breast cancer", "lung cancer", "melanoma", "leukemia",
                  "colorectal", "alzheimer", "parkinson", "schizophrenia", "diabetes",
                  "cardiomyopathy", "carcinoma", "neoplasm", "adenocarcinoma"]:
            if d in q_lower:
                disease_hints.append(d)
                genomics_score += 2

        # Check for specific tissue entities
        tissue_hints = []
        for t in ["brain", "liver", "lung", "heart", "kidney", "colon", "pancreas",
                  "cerebral cortex", "colonic epithelium", "blood", "skin", "muscle"]:
            if t in q_lower:
                tissue_hints.append(t)
                anatomy_score += 2

        # Check for specific drug entities
        drug_hints = []
        for dr in ["osimertinib", "erlotinib", "gefitinib", "imatinib", "aspirin",
                   "metformin", "doxorubicin", "paclitaxel", "trastuzumab", "vemurafenib"]:
            if dr in q_lower:
                drug_hints.append(dr)
                pharma_score += 2

        # Determine orchestration strategy
        active_domains = sum(1 for s in [genomics_score, anatomy_score, pharma_score] if s > 0)
        is_multi_agent = active_domains >= 2 or ("drugs targeting genes" in q_lower) or ("and check" in q_lower)

        if is_multi_agent:
            primary_intent = "MULTI_AGENT_ORCHESTRATION"
        elif genomics_score >= max(anatomy_score, pharma_score, 1):
            primary_intent = "TRANSLATIONAL_GENOMICS"
        elif anatomy_score >= max(genomics_score, pharma_score, 1):
            primary_intent = "ANATOMY_EXPRESSION"
        elif pharma_score >= max(genomics_score, anatomy_score, 1):
            primary_intent = "PHARMACOLOGY_TARGET"
        else:
            primary_intent = "MULTI_AGENT_ORCHESTRATION"

        return {
            "query": query,
            "primary_intent": primary_intent,
            "is_multi_agent": is_multi_agent,
            "scores": {
                "genomics": genomics_score,
                "anatomy": anatomy_score,
                "pharmacology": pharma_score,
            },
            "entities": {
                "genes": potential_genes,
                "diseases": disease_hints,
                "tissues": tissue_hints,
                "drugs": drug_hints,
            },
        }
