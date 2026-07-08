from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingest.mock_mes_socket import load_mock_mes_export
from app.llm.brief_prompt import build_mes_context_prompt


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile mock MES CSV exports into LLM context.")
    parser.add_argument("source", nargs="?", default="samples/mock_mes")
    parser.add_argument("--output", default="outputs/mock_mes_context.json")
    parser.add_argument("--prompt-output", help="Optional path for the LLM prompt text.")
    args = parser.parse_args()

    bundle = load_mock_mes_export(args.source)
    context = bundle.to_llm_context()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(context, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    if args.prompt_output:
        prompt_path = Path(args.prompt_output)
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(build_mes_context_prompt(context), encoding="utf-8")
        print(f"Wrote {prompt_path}")

    print(f"Wrote {output_path}")
    print(f"Tables: {bundle.table_counts}")
    print(f"Normalized jobs: {len(bundle.production_jobs)}")
    if bundle.warnings:
        print("Warnings:")
        for warning in bundle.warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
