"""LangChain tools for the CSKH agent.

Each tool handles a specific intent:
- RAGTool: FAQ, policies, product info (knowledge base retrieval)
- OrderTrackingTool: order status lookup (mock — ready for real API)
- ProductSearchTool: product catalog search
- HumanHandoffTool: escalate to human agent
"""

import json
import random
from datetime import datetime, timedelta

from langchain_core.tools import tool

from app.services.retriever import Retriever


@tool
def search_knowledge_base(query: str) -> str:
    """Search the store's knowledge base for FAQ, policies, shipping info, sizing guides,
    return/exchange policies, payment methods, and general store information.
    Use this when the customer asks about store policies, product details, or general questions."""
    retriever = Retriever.get_instance()
    results = retriever.search(query, top_k=5)

    if not results:
        return "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."

    chunks = []
    for r in results:
        chunks.append(f"[{r['source_file']}] {r['content']}")
    return "\n\n---\n\n".join(chunks)


@tool
def track_order(order_id: str) -> str:
    """Look up order status by order ID. Use when customer asks about their order,
    shipping status, or delivery time. The order ID usually starts with 'VN' or '#'."""
    # Mock data — in production, this calls the OMS/shipping API
    mock_orders = {
        "VN12345": {
            "status": "Đang giao hàng",
            "carrier": "GHN Express",
            "tracking": "GHN789456123",
            "estimated_delivery": (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y"),
            "items": "Áo croptop trắng x1, Quần jean ống rộng x1",
        },
        "VN67890": {
            "status": "Đã giao thành công",
            "carrier": "J&T Express",
            "delivered_at": (datetime.now() - timedelta(days=2)).strftime("%d/%m/%Y %H:%M"),
            "items": "Váy midi xếp ly đen x1",
        },
    }

    clean_id = order_id.strip().upper().replace("#", "")

    if clean_id in mock_orders:
        order = mock_orders[clean_id]
        return json.dumps(order, ensure_ascii=False)

    # Simulate random order for any other ID
    statuses = ["Đang xử lý", "Đã lấy hàng", "Đang giao hàng", "Đã giao thành công"]
    return json.dumps({
        "order_id": clean_id,
        "status": random.choice(statuses),
        "carrier": random.choice(["GHN Express", "J&T Express", "Viettel Post"]),
        "estimated_delivery": (datetime.now() + timedelta(days=random.randint(1, 3))).strftime("%d/%m/%Y"),
        "note": "Dữ liệu mô phỏng — tích hợp API OMS thực tế trong production.",
    }, ensure_ascii=False)


@tool
def search_products(query: str) -> str:
    """Search the product catalog for specific items, categories, prices, sizes, or availability.
    Use when customer asks about specific products, wants recommendations, or asks about stock."""
    retriever = Retriever.get_instance()
    results = retriever.search(query, top_k=5)

    product_results = [r for r in results if "products" in r.get("source_file", "").lower()]

    if not product_results:
        product_results = results[:3]

    if not product_results:
        return "Không tìm thấy sản phẩm phù hợp."

    chunks = []
    for r in product_results:
        chunks.append(r["content"])
    return "\n\n---\n\n".join(chunks)


@tool
def request_human_handoff(reason: str) -> str:
    """Escalate the conversation to a human agent. Use this when:
    - The customer is frustrated or angry
    - The question is too complex for AI to handle
    - The customer explicitly asks to speak with a human
    - The topic involves sensitive issues (complaints, refunds over policy)"""
    return json.dumps({
        "handoff": True,
        "reason": reason,
        "contact": {
            "hotline": "1900-xxxx",
            "zalo": "0xxx-xxx-xxx",
            "email": "support@vanistore.vn",
            "hours": "8:00 - 22:00 hàng ngày",
        },
        "message": f"Dạ em chuyển chị/anh sang bộ phận hỗ trợ trực tiếp nha ạ. Lý do: {reason}",
    }, ensure_ascii=False)


ALL_TOOLS = [
    search_knowledge_base,
    track_order,
    search_products,
    request_human_handoff,
]
