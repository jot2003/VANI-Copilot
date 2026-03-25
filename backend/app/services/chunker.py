from pathlib import Path

from app.core.config import settings


class TextChunker:
    """Split documents into overlapping chunks with metadata."""

    def __init__(
        self,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", ", ", " "]

    def _split_text(self, text: str) -> list[str]:
        """Recursively split text using separators, maintaining chunk size."""
        chunks: list[str] = []
        current_chunk = ""

        paragraphs = text.split("\n\n")

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                if len(para) <= self.chunk_size:
                    current_chunk = para
                else:
                    sentences = para.replace(". ", ".\n").split("\n")
                    current_chunk = ""
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                            current_chunk = f"{current_chunk} {sentence}" if current_chunk else sentence
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._add_overlap(chunks)

        return chunks

    def _add_overlap(self, chunks: list[str]) -> list[str]:
        """Add overlap between consecutive chunks."""
        overlapped: list[str] = [chunks[0]]

        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-self.chunk_overlap :]
            overlap_text = prev_tail.split(" ", 1)[-1] if " " in prev_tail else prev_tail
            overlapped.append(f"{overlap_text} {chunks[i]}")

        return overlapped

    def chunk_file(self, file_path: Path) -> list[dict]:
        """Read a file and return chunks with metadata."""
        text = file_path.read_text(encoding="utf-8")
        raw_chunks = self._split_text(text)

        return [
            {
                "content": chunk,
                "source_file": file_path.name,
                "chunk_index": i,
            }
            for i, chunk in enumerate(raw_chunks)
            if chunk.strip()
        ]

    def chunk_text(self, text: str, source_name: str = "upload") -> list[dict]:
        """Chunk raw text string with metadata."""
        raw_chunks = self._split_text(text)

        return [
            {
                "content": chunk,
                "source_file": source_name,
                "chunk_index": i,
            }
            for i, chunk in enumerate(raw_chunks)
            if chunk.strip()
        ]
