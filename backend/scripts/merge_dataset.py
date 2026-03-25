"""
Merge & validate datasets for fine-tuning.
Strategy 1: CSConDa (full, filter noise) + Ecommerce (full) + Alpaca (drop)

Output format (ChatML for Llama 3.1):
{"messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    ...
], "source": "csconda|ecommerce"}

Validation rules:
1. First message must be role=system
2. After system, messages must alternate: user -> assistant -> user -> assistant
3. No empty content
4. Must have at least 1 user + 1 assistant message
"""
import json
import random
import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
from datasets import load_from_disk

random.seed(42)

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = (
    "Bạn là nhân viên chăm sóc khách hàng của một shop thời trang nữ online. "
    "Trả lời thân thiện, lịch sự, xưng em gọi khách là chị/anh. "
    "Dùng emoji phù hợp. Trả lời ngắn gọn, đúng trọng tâm."
)

MIN_QUESTION_LEN = 15
MIN_ANSWER_LEN = 15


# ============================================================
# STEP 1: Convert each dataset independently
# ============================================================

def convert_csconda() -> list[dict]:
    """Convert CSConDa QA pairs. Filter noise (too short)."""
    path = RAW_DIR / "csconda"
    if not path.exists():
        print("[CSConDa] NOT FOUND - skipping")
        return []

    ds = load_from_disk(str(path))
    converted = []
    skipped_short = 0
    skipped_empty = 0

    for split_name in ["train", "test"]:
        if split_name not in ds:
            continue
        for row in ds[split_name]:
            question = row.get("question", "").strip()
            answer = row.get("answer", "").strip()

            if not question or not answer:
                skipped_empty += 1
                continue

            if len(question) < MIN_QUESTION_LEN and len(answer) < MIN_ANSWER_LEN:
                skipped_short += 1
                continue

            converted.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer},
                ],
                "source": "csconda",
            })

    print(f"[CSConDa] Converted: {len(converted)} | Skipped empty: {skipped_empty} | Skipped short: {skipped_short}")
    return converted


def convert_ecommerce() -> list[dict]:
    """Convert multi-turn conversations. Map human->user, gpt->assistant."""
    path = RAW_DIR / "ecommerce"
    if not path.exists():
        print("[Ecommerce] NOT FOUND - skipping")
        return []

    ds = load_from_disk(str(path))
    converted = []
    skipped_bad_role = 0
    skipped_empty = 0
    skipped_wrong_order = 0

    for row in ds["train"]:
        convs = row["conversations"]
        if not convs or len(convs) < 2:
            skipped_empty += 1
            continue

        role_map = {"human": "user", "gpt": "assistant"}
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        valid = True

        for turn in convs:
            role = role_map.get(turn["from"])
            if not role:
                skipped_bad_role += 1
                valid = False
                break

            content = turn["value"].strip()
            if not content:
                skipped_empty += 1
                valid = False
                break

            messages.append({"role": role, "content": content})

        if not valid:
            continue

        # Check alternating pattern: user, assistant, user, assistant...
        non_system = [m for m in messages if m["role"] != "system"]
        if len(non_system) < 2:
            skipped_empty += 1
            continue

        alternating = True
        for i, msg in enumerate(non_system):
            expected = "user" if i % 2 == 0 else "assistant"
            if msg["role"] != expected:
                alternating = False
                break

        if not alternating:
            skipped_wrong_order += 1
            continue

        converted.append({"messages": messages, "source": "ecommerce"})

    print(f"[Ecommerce] Converted: {len(converted)} | Bad role: {skipped_bad_role} | Empty: {skipped_empty} | Wrong order: {skipped_wrong_order}")
    return converted


# ============================================================
# STEP 2: Validate every single sample
# ============================================================

def validate_sample(sample: dict, idx: int) -> list[str]:
    """Return list of error strings. Empty = valid."""
    errors = []
    msgs = sample.get("messages", [])

    if not msgs:
        errors.append(f"[{idx}] No messages")
        return errors

    # Rule 1: First must be system
    if msgs[0]["role"] != "system":
        errors.append(f"[{idx}] First message is '{msgs[0]['role']}', expected 'system'")

    # Rule 2: Check all roles are valid
    for j, msg in enumerate(msgs):
        if msg["role"] not in ("system", "user", "assistant"):
            errors.append(f"[{idx}] Invalid role '{msg['role']}' at position {j}")

    # Rule 3: No empty content
    for j, msg in enumerate(msgs):
        if not msg.get("content", "").strip():
            errors.append(f"[{idx}] Empty content at position {j} (role={msg['role']})")

    # Rule 4: Alternating user/assistant after system
    non_system = [m for m in msgs if m["role"] != "system"]
    if len(non_system) < 2:
        errors.append(f"[{idx}] Only {len(non_system)} non-system messages (need >= 2)")
    else:
        for j, msg in enumerate(non_system):
            expected = "user" if j % 2 == 0 else "assistant"
            if msg["role"] != expected:
                errors.append(f"[{idx}] Position {j}: got '{msg['role']}', expected '{expected}'")
                break

    # Rule 5: Last non-system message should be assistant
    if non_system and non_system[-1]["role"] != "assistant":
        errors.append(f"[{idx}] Last message is '{non_system[-1]['role']}', expected 'assistant'")

    # Rule 6: Source field exists
    if "source" not in sample:
        errors.append(f"[{idx}] Missing 'source' field")

    return errors


def validate_all(data: list[dict], name: str) -> list[dict]:
    """Validate and return only clean samples."""
    print(f"\n--- Validating {name}: {len(data)} samples ---")
    clean = []
    all_errors = []

    for i, sample in enumerate(data):
        errs = validate_sample(sample, i)
        if errs:
            all_errors.extend(errs)
        else:
            clean.append(sample)

    if all_errors:
        print(f"  ERRORS: {len(all_errors)} issues in {len(data) - len(clean)} samples")
        for e in all_errors[:10]:
            print(f"    {e}")
        if len(all_errors) > 10:
            print(f"    ... and {len(all_errors) - 10} more")
    else:
        print(f"  ALL VALID!")

    print(f"  Clean: {len(clean)} / {len(data)} ({len(clean)/len(data)*100:.1f}%)")
    return clean


# ============================================================
# STEP 3: Merge, shuffle, split
# ============================================================

def print_stats(data: list[dict], name: str):
    """Print dataset statistics."""
    print(f"\n--- Stats: {name} ({len(data)} samples) ---")

    sources = Counter(d["source"] for d in data)
    print(f"  Source distribution:")
    for src, cnt in sources.most_common():
        print(f"    {src}: {cnt} ({cnt/len(data)*100:.1f}%)")

    turn_counts = [len(d["messages"]) - 1 for d in data]  # exclude system
    print(f"  Turns: min={min(turn_counts)}, max={max(turn_counts)}, avg={sum(turn_counts)/len(turn_counts):.1f}")

    user_lens = []
    asst_lens = []
    for d in data:
        for m in d["messages"]:
            if m["role"] == "user":
                user_lens.append(len(m["content"]))
            elif m["role"] == "assistant":
                asst_lens.append(len(m["content"]))

    print(f"  User msg length: min={min(user_lens)}, max={max(user_lens)}, avg={sum(user_lens)/len(user_lens):.0f}")
    print(f"  Asst msg length: min={min(asst_lens)}, max={max(asst_lens)}, avg={sum(asst_lens)/len(asst_lens):.0f}")


def save_jsonl(data: list[dict], path: Path):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"  Saved: {path} ({len(data)} samples)")


def spot_check(data: list[dict], n: int = 5):
    """Print random samples for human verification."""
    print(f"\n--- Spot Check: {n} random samples ---")
    samples = random.sample(data, min(n, len(data)))
    for i, s in enumerate(samples):
        print(f"\n  [{i+1}] source={s['source']}")
        for m in s["messages"]:
            if m["role"] == "system":
                continue
            role = "USER" if m["role"] == "user" else "ASST"
            content = m["content"][:150]
            print(f"    {role}: {content}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("  DATASET MERGE PIPELINE")
    print("  Strategy: CSConDa (full) + Ecommerce (full) + Alpaca (DROPPED)")
    print("=" * 70)

    # Step 1: Convert
    print("\n[STEP 1] Converting datasets...")
    csconda = convert_csconda()
    ecommerce = convert_ecommerce()

    # Step 2: Validate independently
    print("\n[STEP 2] Validating...")
    csconda_clean = validate_all(csconda, "CSConDa")
    ecommerce_clean = validate_all(ecommerce, "Ecommerce")

    # Step 3: Merge
    print("\n[STEP 3] Merging...")
    all_data = csconda_clean + ecommerce_clean
    random.shuffle(all_data)
    print(f"  Total merged: {len(all_data)}")

    # Stats
    print_stats(all_data, "Merged Dataset")

    # Step 4: Split 80/10/10
    print("\n[STEP 4] Splitting train/val/test (80/10/10)...")
    n = len(all_data)
    train_end = int(n * 0.8)
    val_end = int(n * 0.9)

    train_data = all_data[:train_end]
    val_data = all_data[train_end:val_end]
    test_data = all_data[val_end:]

    print(f"  Train: {len(train_data)}")
    print(f"  Val:   {len(val_data)}")
    print(f"  Test:  {len(test_data)}")

    # Verify no source leakage in splits
    for name, split in [("Train", train_data), ("Val", val_data), ("Test", test_data)]:
        sources = Counter(d["source"] for d in split)
        dist = ", ".join(f"{s}: {c}" for s, c in sources.most_common())
        print(f"  {name} sources: {dist}")

    # Step 5: Save
    print("\n[STEP 5] Saving...")
    save_jsonl(train_data, OUTPUT_DIR / "train.jsonl")
    save_jsonl(val_data, OUTPUT_DIR / "val.jsonl")
    save_jsonl(test_data, OUTPUT_DIR / "test.jsonl")

    # Step 6: Spot check
    spot_check(train_data, 8)

    # Final validation: reload and re-validate
    print("\n[STEP 6] Final validation - reload from disk...")
    for fname in ["train.jsonl", "val.jsonl", "test.jsonl"]:
        fpath = OUTPUT_DIR / fname
        with open(fpath, "r", encoding="utf-8") as f:
            reloaded = [json.loads(line) for line in f]

        errors = []
        for i, sample in enumerate(reloaded):
            errs = validate_sample(sample, i)
            errors.extend(errs)

        if errors:
            print(f"  {fname}: {len(errors)} ERRORS FOUND!")
            for e in errors[:5]:
                print(f"    {e}")
        else:
            print(f"  {fname}: {len(reloaded)} samples - ALL VALID")

    print("\n" + "=" * 70)
    print("  DONE!")
    print(f"  Output: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
