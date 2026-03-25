"""Download 3 Vietnamese datasets from HuggingFace to data/raw/ for local exploration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def download_all():
    from datasets import load_dataset

    raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    datasets_config = [
        {
            "name": "csconda",
            "path": "ura-hcmut/Vietnamese-Customer-Support-QA",
            "description": "CSConDa - 9,849 QA pairs from DooPage (real Vietnamese CSKH)",
        },
        {
            "name": "ecommerce",
            "path": "5CD-AI/Vietnamese-Ecommerce-Multi-turn-Chat",
            "description": "Vietnamese E-commerce Multi-turn Chat - 1,482 conversations",
        },
        {
            "name": "alpaca",
            "path": "5CD-AI/Vietnamese-Multi-turn-Chat-Alpaca",
            "description": "Vietnamese Multi-turn Chat Alpaca - 12,697 conversations",
        },
    ]

    for ds_config in datasets_config:
        name = ds_config["name"]
        hf_path = ds_config["path"]
        desc = ds_config["description"]

        print(f"\n{'='*60}")
        print(f"Downloading: {desc}")
        print(f"HuggingFace: {hf_path}")
        print(f"{'='*60}")

        try:
            ds = load_dataset(hf_path)
            save_path = raw_dir / name
            ds.save_to_disk(str(save_path))
            print(f"Saved to: {save_path}")

            for split_name, split_data in ds.items():
                print(f"  Split '{split_name}': {len(split_data)} rows")
                print(f"  Columns: {split_data.column_names}")
                print(f"  Sample (first row):")
                sample = split_data[0]
                for key, value in sample.items():
                    val_str = str(value)
                    if len(val_str) > 100:
                        val_str = val_str[:100] + "..."
                    print(f"    {key}: {val_str}")

        except Exception as e:
            print(f"ERROR downloading {name}: {e}")
            print("You may need to accept the dataset agreement on HuggingFace first.")
            print(f"Visit: https://huggingface.co/datasets/{hf_path}")

    print(f"\n{'='*60}")
    print("Done! Explore the datasets in data/raw/")
    print("='*60")


if __name__ == "__main__":
    download_all()
