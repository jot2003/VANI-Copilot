"""Build FAISS index from knowledge base documents in app/data/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.chunker import TextChunker
from app.services.retriever import Retriever


def main():
    data_dir = Path(__file__).resolve().parent.parent / "app" / "data"
    txt_files = list(data_dir.glob("*.txt"))

    if not txt_files:
        print(f"No .txt files found in {data_dir}")
        return

    chunker = TextChunker()
    all_chunks: list[dict] = []

    for txt_file in txt_files:
        chunks = chunker.chunk_file(txt_file)
        all_chunks.extend(chunks)
        print(f"  {txt_file.name}: {len(chunks)} chunks")

    print(f"\nTotal chunks: {len(all_chunks)}")

    retriever = Retriever.get_instance()
    retriever.build_index(all_chunks)
    print(f"FAISS index saved to {retriever.index}")


if __name__ == "__main__":
    main()
