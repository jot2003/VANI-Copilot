"""Download CSConDa dataset (gated, requires HF login)."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from datasets import load_dataset

print("Downloading CSConDa...")
ds = load_dataset("ura-hcmut/Vietnamese-Customer-Support-QA")
print(ds)

train = ds["train"]
print(f"Columns: {train.column_names}")
print(f"Train: {len(train)} rows")
print(f"Features: {train.features}")

ds.save_to_disk("data/raw/csconda")
print("Saved to data/raw/csconda")

print("\n--- First 3 samples ---")
for i in range(min(3, len(train))):
    row = train[i]
    print(f"\n[{i}]")
    for k, v in row.items():
        val = str(v)[:200]
        print(f"  {k}: {val}")
