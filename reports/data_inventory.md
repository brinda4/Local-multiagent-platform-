# Biomedical Data Sources Inventory Report

## Overview

This report provides an exact, disk-measured audit of the primary biomedical datasets ingested into the Translational Genomics & Anatomical Intelligence Platform.
In accordance with project requirements, the datasets replace legacy CTD/SIDER/Reactome combinations with five specialized resources derived from PrimeKG and reference ontologies.

| Metric | Value |
| :--- | :--- |
| Ingestion Timestamp | 2026-09-18 10:03:05 UTC |
| Total Datasets Ingested | 6 |
| Total Physical Disk Storage | 250.48 MB (262,650,999 bytes) |
| Maximum Permissible Storage Limit | 3.50 GB (3,758,096,384 bytes) |
| Storage Capacity Utilized | 6.99% |
| Total Biological Records Ingested | 10,630,787 |

---

## Dataset Manifest & Exact Disk Measurements

| Source | Domain | Disk Filename | Exact Disk Size | Record Count | SHA-256 Checksum |
| :--- | :--- | :--- | :--- | :--- | :--- |
| DrugCentral - Targets and Mechanisms | Pharmacology | `drugcentral_targets.tsv.gz` | 761.10 KB | 19,378 | `160d7b382799...` |
| DrugCentral - Chemical Structures | Pharmacology | `drugcentral_structures.smiles.tsv` | 1.04 MB | 4,099 | `5b81423a2ec1...` |
| UBERON Anatomical Structure Ontology | Anatomy Ontology | `uberon.obo` | 21.38 MB | 397,010 | `7f06d8e84420...` |
| MONDO Unified Disease Ontology | Disease Ontology | `mondo.obo` | 50.67 MB | 865,768 | `50c8367f9bd9...` |
| Bgee Anatomical Gene Expression | Expression | `bgee_human_expr.tsv.gz` | 165.97 MB | 9,261,153 | `42b4aae16980...` |
| DisGeNET Gene-Disease & Variant Associations | Translational Genomics | `disgenet_disease_associations.csv` | 10.68 MB | 83,379 | `81885fa1f579...` |

---

## Detailed Dataset Descriptions

### DrugCentral - Targets and Mechanisms
- **Domain Category**: Pharmacology
- **File on Disk**: `data/raw/drugcentral_targets.tsv.gz`
- **Exact Byte Size**: 779,363 bytes (761.10 KB)
- **Biological Records**: 19,378
- **Full SHA-256**: `160d7b3827997442def525d7499a82e12c3f97a96bc3b5bcaace1c6d12d48618`
- **Functional Utility**: Drug active ingredients, target genes, mechanism of action (MoA), and bioactivity metrics (IC50/Ki).

### DrugCentral - Chemical Structures
- **Domain Category**: Pharmacology
- **File on Disk**: `data/raw/drugcentral_structures.smiles.tsv`
- **Exact Byte Size**: 1,089,436 bytes (1.04 MB)
- **Biological Records**: 4,099
- **Full SHA-256**: `5b81423a2ec1e2766e9666ec4a172d5a5b47045ea2cc032d1ba06085956bc1fc`
- **Functional Utility**: Drug chemical structures with SMILES, InChI, InChIKey, INN names, and CAS registry numbers.

### UBERON Anatomical Structure Ontology
- **Domain Category**: Anatomy Ontology
- **File on Disk**: `data/raw/uberon.obo`
- **Exact Byte Size**: 22,414,082 bytes (21.38 MB)
- **Biological Records**: 397,010
- **Full SHA-256**: `7f06d8e8442008a67132a1599b652e86fe0c52d75c8d6bc5b0cc36a0031e6b3f`
- **Functional Utility**: Cross-species anatomical ontology standardizing tissues, organs, and physiological systems.

### MONDO Unified Disease Ontology
- **Domain Category**: Disease Ontology
- **File on Disk**: `data/raw/mondo.obo`
- **Exact Byte Size**: 53,134,854 bytes (50.67 MB)
- **Biological Records**: 865,768
- **Full SHA-256**: `50c8367f9bd9978321eedf84d4e2e79cb757efbed514c81effb00b9ad2e49994`
- **Functional Utility**: Comprehensive unified disease ontology harmonizing OMIM, Orphanet, NCIt, and ICD classifications.

### Bgee Anatomical Gene Expression
- **Domain Category**: Expression
- **File on Disk**: `data/raw/bgee_human_expr.tsv.gz`
- **Exact Byte Size**: 174,033,165 bytes (165.97 MB)
- **Biological Records**: 9,261,153
- **Full SHA-256**: `42b4aae16980219f4e9de4bca637bd7ff48585157e31eb94441a0bca5af12836`
- **Functional Utility**: Curated anatomical expression presence calls, gold quality ranks, and expression scores across human tissues.

### DisGeNET Gene-Disease & Variant Associations
- **Domain Category**: Translational Genomics
- **File on Disk**: `data/raw/disgenet_disease_associations.csv`
- **Exact Byte Size**: 11,200,099 bytes (10.68 MB)
- **Biological Records**: 83,379
- **Full SHA-256**: `81885fa1f57973fb02b45886ce3cbb825e002d2f7888f03a77d63f8d584bc1eb`
- **Functional Utility**: Curated gene-disease associations and variant scores linking MONDO diseases to target genes.

---

## Storage Compliance Verification

The total physical storage consumed by the raw dataset assets is **250.48 MB**, which is strictly below the ceiling of 3.50 GB.
Space optimization was achieved via streaming HTTP chunks, compression retention, and normalized relational indexing.
