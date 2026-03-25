"""Explore downloaded datasets - print samples for human inspection."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from datasets import load_from_disk


def explore_dataset(name: str, path: Path) -> None:
    print(f"\n{'='*70}")
    print(f"  DATASET: {name}")
    print(f"  Path: {path}")
    print(f"{'='*70}")

    if not path.exists():
        print(f"  [SKIPPED] Not found at {path}")
        print(f"  You may need to accept the agreement on HuggingFace first.")
        return

    ds = load_from_disk(str(path))
    for split_name, split_data in ds.items():
        print(f"\n  Split: {split_name}")
        print(f"  Rows: {len(split_data)}")
        print(f"  Columns: {split_data.column_names}")
        print(f"  Column types: {split_data.features}")

        print(f"\n  --- First 5 samples ---")
        for i in range(min(5, len(split_data))):
            print(f"\n  [Sample {i}]")
            sample = split_data[i]
            for key, value in sample.items():
                val_str = json.dumps(value, ensure_ascii=False, indent=4) if isinstance(value, (list, dict)) else str(value)
                if len(val_str) > 500:
                    val_str = val_str[:500] + "... (truncated)"
                print(f"    {key}: {val_str}")

        lengths = []
        for row in split_data:
            for key, val in row.items():
                if isinstance(val, str):
                    lengths.append(len(val))
                elif isinstance(val, list):
                    lengths.append(len(val))

        if lengths:
            print(f"\n  --- Stats ---")
            print(f"  Min length: {min(lengths)}")
            print(f"  Max length: {max(lengths)}")
            print(f"  Avg length: {sum(lengths)/len(lengths):.1f}")

    print()


def main():
    raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"

    datasets_to_explore = [
        ("CSConDa (Vietnamese Customer Support QA)", raw_dir / "csconda"),
        ("Vietnamese Ecommerce Multi-turn Chat", raw_dir / "ecommerce"),
        ("Vietnamese Multi-turn Chat Alpaca", raw_dir / "alpaca"),
    ]

    for name, path in datasets_to_explore:
        explore_dataset(name, path)

    print("\n" + "="*70)
    print("  EXPLORATION COMPLETE")
    print("  Review the samples above carefully before writing converters.")
    print("="*70)


if __name__ == "__main__":
    main()
