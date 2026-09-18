"""Interactive CLI Chat Interface for Multi-Agent Biomedical Platform.

Allows researchers to interactively query the local multi-agent system from the terminal.
Zero emoji characters in all output streams.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.supervisor_orchestrator import SupervisorOrchestrator


def print_banner():
    print("=" * 80)
    print("TRANSLATIONAL GENOMICS & ANATOMICAL INTELLIGENCE PLATFORM")
    print("Interactive Command Line Multi-Agent Interface")
    print("Datasets: Bgee, DisGeNET, DrugCentral, MONDO, UBERON")
    print("Strictly Local, Offline Relational Execution")
    print("=" * 80)
    print("Type your biomedical research query below.")
    print("Commands:")
    print("  'history' : View past session queries")
    print("  'clear'   : Clear session memory")
    print("  'demo'    : Run preconfigured multi-agent benchmark query")
    print("  'exit'    : Quit application")
    print("-" * 80)


def format_agent_output(result: dict):
    print("\n" + "=" * 80)
    print(f"QUERY: {result['query']}")
    print(f"INTENT: {result['intent']} | DURATION: {result['elapsed_ms']} ms | TIMESTAMP: {result['timestamp']}")
    print("-" * 80)
    print("SYNTHESIZED TRANSLATIONAL REPORT:\n")
    print(result["final_report"])
    print("\nEVIDENCE TABLES RETRIEVED:")
    
    for tbl_name, df in result["data_tables"].items():
        print(f"\n[Table: {tbl_name} - {len(df)} records]")
        if not df.empty:
            cols_to_show = df.columns[:6].tolist()
            sample_df = df[cols_to_show].head(5)
            print(sample_df.to_string(index=False))
        else:
            print("  (Empty dataset)")
            
    print("=" * 80 + "\n")


def run_interactive(orchestrator: SupervisorOrchestrator):
    print_banner()
    
    while True:
        try:
            query = input("biomed-agent> ").strip()
            if not query:
                continue
                
            cmd = query.lower()
            if cmd in ("exit", "quit", "q"):
                print("Exiting interactive biomedical shell.")
                break
            elif cmd == "history":
                hist = orchestrator.get_history()
                print(f"\nSession History ({len(hist)} queries recorded):")
                for i, h in enumerate(hist):
                    print(f"  [{i+1}] ({h['elapsed_ms']} ms) {h['query']}")
                print()
                continue
            elif cmd == "clear":
                orchestrator.clear_history()
                print("Session history cleared.\n")
                continue
            elif cmd == "demo":
                query = "Find drugs targeting genes associated with glioblastoma and check their tissue expression in the brain"
                print(f"Executing demonstration query: '{query}'")
                
            result = orchestrator.route_and_execute(query)
            format_agent_output(result)
            
        except (KeyboardInterrupt, EOFError):
            print("\nSession interrupted. Exiting.")
            break
        except Exception as e:
            print(f"\nError executing query: {e}\n")


def main():
    parser = argparse.ArgumentParser(description="Translational Genomics CLI Interface")
    parser.add_argument("--query", "-q", type=str, help="Single query to execute in non-interactive mode")
    args = parser.parse_args()
    
    orchestrator = SupervisorOrchestrator()
    
    if args.query:
        result = orchestrator.route_and_execute(args.query)
        format_agent_output(result)
    else:
        run_interactive(orchestrator)


if __name__ == "__main__":
    main()
