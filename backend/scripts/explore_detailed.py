"""Deep exploration of all 3 datasets - run this to understand data before processing."""
import json
import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
from datasets import load_from_disk

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def separator(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def explore_csconda():
    separator("1. CSConDa - Vietnamese Customer Support QA")
    path = RAW_DIR / "csconda"
    if not path.exists():
        print("  NOT FOUND")
        return

    ds = load_from_disk(str(path))

    for split_name in ds:
        split = ds[split_name]
        print(f"\n  --- Split: {split_name} ({len(split)} rows) ---")
        print(f"  Columns: {split.column_names}")

        # Type distribution
        types = [row["type"] for row in split]
        type_counts = Counter(types)
        print(f"\n  Type distribution:")
        for t, c in type_counts.most_common():
            print(f"    {t}: {c} ({c/len(split)*100:.1f}%)")

        # Length stats
        q_lens = [len(row["question"]) for row in split]
        a_lens = [len(row["answer"]) for row in split]
        print(f"\n  Question length: min={min(q_lens)}, max={max(q_lens)}, avg={sum(q_lens)/len(q_lens):.0f}")
        print(f"  Answer length:   min={min(a_lens)}, max={max(a_lens)}, avg={sum(a_lens)/len(a_lens):.0f}")

        # Very short questions (potential noise)
        short_q = [row for row in split if len(row["question"].strip()) < 10]
        print(f"\n  Questions < 10 chars: {len(short_q)} ({len(short_q)/len(split)*100:.1f}%)")
        if short_q:
            print("  Examples:")
            for row in short_q[:5]:
                print(f"    Q: '{row['question']}' -> A: '{row['answer'][:80]}...'")

        # Very long answers (potential noise)
        long_a = [row for row in split if len(row["answer"]) > 1000]
        print(f"\n  Answers > 1000 chars: {len(long_a)} ({len(long_a)/len(split)*100:.1f}%)")

        # Random 10 samples
        import random
        random.seed(42)
        print(f"\n  --- 10 Random Samples ---")
        indices = random.sample(range(len(split)), min(10, len(split)))
        for i in indices:
            row = split[i]
            print(f"\n  [{i}] type={row['type']}")
            print(f"    Q: {row['question'][:150]}")
            print(f"    A: {row['answer'][:150]}")


def explore_ecommerce():
    separator("2. Vietnamese Ecommerce Multi-turn Chat")
    path = RAW_DIR / "ecommerce"
    if not path.exists():
        print("  NOT FOUND")
        return

    ds = load_from_disk(str(path))
    train = ds["train"]
    print(f"  Total: {len(train)} conversations")

    # Turn count distribution
    turn_counts = [len(row["conversations"]) for row in train]
    print(f"\n  Turns per conversation: min={min(turn_counts)}, max={max(turn_counts)}, avg={sum(turn_counts)/len(turn_counts):.1f}")
    turn_dist = Counter(turn_counts)
    print("  Turn count distribution:")
    for t in sorted(turn_dist.keys()):
        print(f"    {t} turns: {turn_dist[t]} conversations")

    # Topic detection (first human message keywords)
    first_messages = [row["conversations"][0]["value"].lower() for row in train if row["conversations"]]
    topics = Counter()
    topic_keywords = {
        "thoi_trang": ["áo", "váy", "quần", "đầm", "chân váy", "vest", "jacket", "blazer", "jean", "denim"],
        "my_pham": ["kem", "serum", "sữa rửa", "toner", "son", "mỹ phẩm", "skincare", "makeup"],
        "dien_tu": ["điện thoại", "laptop", "tai nghe", "loa", "camera", "pin", "tản nhiệt", "màn hình"],
        "thuc_pham": ["thực phẩm", "đồ ăn", "vitamin", "thực phẩm chức năng", "trà", "cà phê"],
        "gia_dung": ["nồi", "chảo", "máy giặt", "tủ lạnh", "quạt", "đèn"],
    }
    for msg in first_messages:
        found = False
        for topic, kws in topic_keywords.items():
            if any(kw in msg for kw in kws):
                topics[topic] += 1
                found = True
                break
        if not found:
            topics["other"] += 1

    print(f"\n  Topic distribution (by first message):")
    for topic, count in topics.most_common():
        print(f"    {topic}: {count} ({count/len(train)*100:.1f}%)")

    # Random 10
    import random
    random.seed(42)
    print(f"\n  --- 10 Random Conversations ---")
    indices = random.sample(range(len(train)), 10)
    for i in indices:
        row = train[i]
        convs = row["conversations"]
        print(f"\n  [{i}] {len(convs)} turns")
        for turn in convs[:4]:
            role = "USER" if turn["from"] == "human" else "ASST"
            print(f"    {role}: {turn['value'][:120]}")
        if len(convs) > 4:
            print(f"    ... ({len(convs) - 4} more turns)")


def explore_alpaca():
    separator("3. Vietnamese Multi-turn Chat Alpaca")
    path = RAW_DIR / "alpaca"
    if not path.exists():
        print("  NOT FOUND")
        return

    ds = load_from_disk(str(path))
    train = ds["train"]
    print(f"  Total: {len(train)} conversations")

    # Turn count
    turn_counts = [len(row["conversations"]) for row in train]
    print(f"\n  Turns per conversation: min={min(turn_counts)}, max={max(turn_counts)}, avg={sum(turn_counts)/len(turn_counts):.1f}")

    # Relevance check - how many are related to shopping/CSKH
    KEEP_KEYWORDS = [
        "sản phẩm", "mua", "bán", "giá", "size", "màu", "chất liệu", "vải",
        "đổi trả", "hoàn", "ship", "giao hàng", "vận chuyển", "đơn hàng",
        "thanh toán", "khuyến mãi", "giảm giá", "voucher", "mã",
        "áo", "váy", "quần", "đầm", "chân váy", "túi", "giày", "dép",
        "thời trang", "outfit", "phối đồ", "mặc",
        "khách hàng", "shop", "cửa hàng", "tư vấn", "hỗ trợ",
        "bảo hành", "bảo quản", "giặt", "ủi",
        "review", "đánh giá", "feedback", "phàn nàn", "khiếu nại",
        "mỹ phẩm", "kem", "serum", "son", "nước hoa",
    ]

    relevant = []
    irrelevant_samples = []
    for row in train:
        text = " ".join(t["value"].lower() for t in row["conversations"])
        if any(kw in text for kw in KEEP_KEYWORDS):
            relevant.append(row)
        elif len(irrelevant_samples) < 5:
            irrelevant_samples.append(row)

    print(f"\n  Relevant to shopping/CSKH: {len(relevant)} ({len(relevant)/len(train)*100:.1f}%)")
    print(f"  Irrelevant (will be filtered): {len(train) - len(relevant)} ({(len(train) - len(relevant))/len(train)*100:.1f}%)")

    # Show irrelevant samples to verify filter is correct
    print(f"\n  --- Irrelevant samples (should be filtered out) ---")
    for row in irrelevant_samples[:3]:
        first_msg = row["conversations"][0]["value"][:150]
        print(f"    '{first_msg}'")

    # Show relevant samples
    import random
    random.seed(42)
    print(f"\n  --- 10 Random RELEVANT Conversations ---")
    sample_relevant = random.sample(relevant, min(10, len(relevant)))
    for row in sample_relevant:
        convs = row["conversations"]
        print(f"\n  [{row['id']}] {len(convs)} turns")
        for turn in convs[:3]:
            role = "USER" if turn["from"] == "human" else "ASST"
            print(f"    {role}: {turn['value'][:120]}")
        if len(convs) > 3:
            print(f"    ... ({len(convs) - 3} more turns)")


def summary():
    separator("SUMMARY")
    print("""
  Dataset          | Rows    | Format          | Quality
  -----------------+---------+-----------------+---------
  CSConDa          | ~8,349  | QA single-turn  | Real CSKH from DooPage
  Ecommerce        | 1,482   | Multi-turn chat | E-commerce product Q&A
  Alpaca (filtered)| ~4-5K   | Multi-turn chat | General VN (filtered)
  -----------------+---------+-----------------+---------
  Total estimate   | ~14-15K |                 |

  Next steps:
  1. Review samples above - any quality issues?
  2. Decide: keep all CSConDa types or filter some?
  3. Run notebook 01 on Colab to convert + merge
  """)


if __name__ == "__main__":
    explore_csconda()
    explore_ecommerce()
    explore_alpaca()
    summary()
