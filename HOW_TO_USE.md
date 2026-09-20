# How to Use the Translational Genomics & Anatomical Intelligence Platform

This guide provides step-by-step instructions for running, querying, and managing the 100% local, offline-capable biomedical multi-agent platform.

---

## 1. Prerequisites and Environment Setup

The platform runs on any local workstation with Python 3.10+ (tested on Python 3.11 and 3.13) and `uv` package manager. No external cloud accounts or internet connections are required during standard runtime.

### Quick Setup with uv
Navigate to the project root directory and install dependencies:
```bash
cd translational_genomics_platform
uv sync
```

Alternatively, standard pip installation can be used:
```bash
pip install streamlit pandas altair plotly requests
```

---

## 2. Biomedical Data Pipeline

The platform uses five specialized biomedical datasets derived from PrimeKG and reference ontologies:
- **Bgee**: Anatomical tissue gene expression presence calls and gold-quality ranks.
- **DisGeNET**: Expert-curated gene-disease associations and calibrated variant confidence scores.
- **DrugCentral**: Active pharmaceutical ingredients, confirmed mechanisms of action (MoA), target proteins, and chemical structures.
- **MONDO**: Unified disease ontology and hierarchical disease classifications.
- **UBERON**: Cross-species anatomical structure ontology.

### Step 2.1: Space-Optimized Dataset Download
To download or refresh the raw datasets from official repositories (keeping total storage under 3.5 GB):
```bash
uv run python scripts/download_datasets.py
```
This script streams chunks in 64 KB increments, computes SHA-256 checksums, measures exact disk file sizes, and automatically generates:
- `reports/data_inventory.md`
- `reports/data_inventory.csv`

### Step 2.2: ETL and Database Population
To parse the raw datasets and construct the normalized relational database:
```bash
uv run python scripts/parse_and_prepare_data.py
```
This builds:
- `data/processed/translational_bio.db` (SQLite WAL mode with compound indexes)
- `data/processed/init_translational_db.sql` (MySQL 8.0 DDL export)
- `reports/mysql_schema_proposal.md` (Formal schema specification)

---

## 3. Launching the Web Dashboard (Streamlit)

The web interface features an **Emerald & Slate** theme (#059669 / #10B981) with top horizontal tabs and live database KPIs.

Launch the application:
```bash
uv run streamlit run app.py
```
Once started, open your web browser at:
`http://localhost:8501`

### Navigation Tabs Overview
1. **Tab 1: Anatomical Expression Explorer**
   - Query gene expression across 304 anatomical structures.
   - Filter by gene symbol (e.g., `EGFR`, `TP53`) or anatomical tissue (e.g., `brain`, `lung`, `liver`).
   - View interactive horizontal bar charts of expression scores.
   - 1-click CSV export of filtered expression calls.
2. **Tab 2: Gene-Disease DisGeNET Intelligence**
   - Search curated disease genomics across 80,411 records.
   - Filter by disease phenotype (e.g., `glioblastoma`, `breast cancer`) or gene symbol.
   - View scatter plots comparing Association Scores with Variant Impact Scores.
   - 1-click CSV export of genomic association tables.
3. **Tab 3: Pharmacology & Drug Mechanism Portal**
   - Search active pharmaceutical ingredients or target genes across 19,378 target interactions and 4,099 chemical structures.
   - Filter by Confirmed Mechanism of Action (MoA) and action type (Inhibitor, Antagonist, Agonist, Blocker).
   - View action type distribution donut charts and chemical identifiers (SMILES, InChIKey, CAS).
   - 1-click CSV export of pharmacology tables.
4. **Tab 4: Multi-Agent Query Suite**
   - Execute collaborative multi-agent queries orchestrated by `SupervisorOrchestrator`.
   - Access pre-configured research benchmarks or submit custom natural language research inquiries.
   - Review agent routing decisions, execution latencies, intermediate agent evidence tables, and synthesized translational reports.

---

## 4. Using the Interactive CLI Console (chat.py)

For headless or terminal-based research workflows, use `chat.py`.

### Interactive Shell
```bash
uv run python chat.py
```
Inside the shell, enter queries directly or use built-in commands:
- `demo`: Runs the pre-configured glioblastoma multi-agent benchmark query.
- `history`: Displays past queries executed in the current session.
- `clear`: Clears session memory.
- `exit`: Quits the interactive shell.

### Non-Interactive Single Query Execution
```bash
uv run python chat.py --query "Find drugs targeting genes associated with glioblastoma and check their tissue expression in the brain"
```

---

## 5. Security and Read-Only Safety Protocol

The platform enforces strict read-only execution safety via `src/tools/db_tool.py`:
- Database connections use SQLite URI mode `?mode=ro`, preventing physical file modifications at the operating system level.
- Queries are lexically validated before execution; only `SELECT`, `EXPLAIN`, and `WITH` statements are permitted.
- Any attempt to execute `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `REPLACE`, or `PRAGMA` raises a `DatabaseSecurityError`.
- Multiple semicolon-delimited statements are strictly blocked to prevent stacked SQL injection attacks.

---

## 6. MySQL Database Migration

To deploy the platform onto a standalone MySQL 8.0+ server:
1. Verify MySQL server is active.
2. Execute the included DDL script:
   ```bash
   mysql -u <username> -p < data/processed/init_translational_db.sql
   ```
3. Load data tables from `data/processed/translational_bio.db` using standard database export tools or the Python migration helper in `src/tools/db_tool.py`.
