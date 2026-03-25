from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_api_key
from app.models.database import Document, get_session
from app.services.chunker import TextChunker
from app.services.retriever import Retriever

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(verify_api_key)])


class DocumentCreate(BaseModel):
    filename: str
    content: str
    category: str = "general"


class DocumentUpdate(BaseModel):
    content: str | None = None
    category: str | None = None


# --- Document CRUD ---


@router.get("/documents")
async def list_documents(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Document).order_by(Document.uploaded_at.desc()))
    docs = result.scalars().all()
    return {
        "documents": [
            {
                "id": d.id,
                "filename": d.filename,
                "category": d.category,
                "chunk_count": d.chunk_count,
                "content_preview": d.content[:200] + "..." if len(d.content) > 200 else d.content,
                "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
                "updated_at": d.updated_at.isoformat() if d.updated_at else None,
            }
            for d in docs
        ],
        "total": len(docs),
    }


@router.post("/documents")
async def create_document(doc: DocumentCreate, session: AsyncSession = Depends(get_session)):
    existing = await session.execute(select(Document).where(Document.filename == doc.filename))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Document '{doc.filename}' already exists. Use PUT to update.")

    db_doc = Document(filename=doc.filename, content=doc.content, category=doc.category)
    session.add(db_doc)
    await session.commit()
    await session.refresh(db_doc)

    # Write to disk + rebuild index
    await _sync_documents_to_disk(session)
    chunk_count = await _rebuild_index()
    db_doc.chunk_count = chunk_count.get(doc.filename, 0)
    await session.commit()

    return {"status": "ok", "id": db_doc.id, "filename": doc.filename}


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
):
    content = (await file.read()).decode("utf-8")
    filename = file.filename or "unnamed.txt"
    category = _guess_category(filename)

    existing = await session.execute(select(Document).where(Document.filename == filename))
    db_doc = existing.scalar_one_or_none()

    if db_doc:
        db_doc.content = content
        db_doc.category = category
    else:
        db_doc = Document(filename=filename, content=content, category=category)
        session.add(db_doc)

    await session.commit()
    await session.refresh(db_doc)

    await _sync_documents_to_disk(session)
    chunk_count = await _rebuild_index()
    db_doc.chunk_count = chunk_count.get(filename, 0)
    await session.commit()

    return {"status": "ok", "id": db_doc.id, "filename": filename, "size": len(content)}


@router.put("/documents/{doc_id}")
async def update_document(
    doc_id: int,
    update: DocumentUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Document).where(Document.id == doc_id))
    db_doc = result.scalar_one_or_none()
    if not db_doc:
        raise HTTPException(404, "Document not found")

    if update.content is not None:
        db_doc.content = update.content
    if update.category is not None:
        db_doc.category = update.category

    await session.commit()

    await _sync_documents_to_disk(session)
    chunk_count = await _rebuild_index()
    db_doc.chunk_count = chunk_count.get(db_doc.filename, 0)
    await session.commit()

    return {"status": "ok", "id": db_doc.id}


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Document).where(Document.id == doc_id))
    db_doc = result.scalar_one_or_none()
    if not db_doc:
        raise HTTPException(404, "Document not found")

    # Remove file from disk
    data_dir = Path("app/data")
    file_path = data_dir / db_doc.filename
    if file_path.exists():
        file_path.unlink()

    await session.execute(sa_delete(Document).where(Document.id == doc_id))
    await session.commit()

    await _rebuild_index()

    return {"status": "ok", "deleted": db_doc.filename}


@router.post("/rebuild-index")
async def rebuild_index():
    chunk_counts = await _rebuild_index()
    total = sum(chunk_counts.values())
    return {"status": "ok", "total_chunks": total, "per_file": chunk_counts}


@router.get("/chunks")
async def list_chunks():
    retriever = Retriever.get_instance()
    if not retriever.chunks:
        return {"chunks": [], "total": 0}

    return {
        "chunks": [
            {
                "content": c["content"][:200] + "..." if len(c["content"]) > 200 else c["content"],
                "source_file": c["source_file"],
                "chunk_index": c["chunk_index"],
            }
            for c in retriever.chunks
        ],
        "total": len(retriever.chunks),
    }


# --- Helpers ---


def _guess_category(filename: str) -> str:
    name = filename.lower()
    if "faq" in name:
        return "faq"
    if "polic" in name or "chinh-sach" in name:
        return "policies"
    if "product" in name or "san-pham" in name:
        return "products"
    return "general"


async def _sync_documents_to_disk(session: AsyncSession):
    """Write all documents from DB to app/data/ as .txt files."""
    data_dir = Path("app/data")
    data_dir.mkdir(parents=True, exist_ok=True)

    result = await session.execute(select(Document))
    docs = result.scalars().all()
    for doc in docs:
        (data_dir / doc.filename).write_text(doc.content, encoding="utf-8")


async def _rebuild_index() -> dict[str, int]:
    """Rebuild FAISS index from all .txt files in app/data/. Returns chunk count per file."""
    data_dir = Path("app/data")
    chunker = TextChunker()
    all_chunks: list[dict] = []
    chunk_counts: dict[str, int] = {}

    for txt_file in data_dir.glob("*.txt"):
        chunks = chunker.chunk_file(txt_file)
        all_chunks.extend(chunks)
        chunk_counts[txt_file.name] = len(chunks)

    retriever = Retriever.get_instance()
    retriever.build_index(all_chunks)

    return chunk_counts
