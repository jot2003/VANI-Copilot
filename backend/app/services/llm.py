import json
from collections.abc import AsyncGenerator

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from app.core.config import settings

logger = structlog.get_logger()

_RETRYABLE = (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout)

_retry_policy = retry(
    retry=retry_if_exception_type(_RETRYABLE),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    before_sleep=before_sleep_log(logger, "WARNING"),
    reraise=True,
)


class LLMService:
    """Unified LLM interface: Ollama | Azure OpenAI | OpenAI | retrieval-only fallback."""

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        provider = settings.llm_provider

        if provider == "ollama":
            return await self._ollama_generate(system_prompt, user_prompt)
        if provider == "azure" and settings.azure_openai_api_key:
            return await self._azure_generate(system_prompt, user_prompt)
        if provider == "openai" and settings.openai_api_key:
            return await self._openai_generate(system_prompt, user_prompt)

        return self._retrieval_only_fallback(system_prompt, user_prompt)

    async def stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        provider = settings.llm_provider

        if provider == "ollama":
            async for token in self._ollama_stream(system_prompt, user_prompt):
                yield token
            return
        if provider == "azure" and settings.azure_openai_api_key:
            async for token in self._azure_stream(system_prompt, user_prompt):
                yield token
            return
        if provider == "openai" and settings.openai_api_key:
            async for token in self._openai_stream(system_prompt, user_prompt):
                yield token
            return

        fallback = self._retrieval_only_fallback(system_prompt, user_prompt)
        for word in fallback.split(" "):
            yield word + " "

    def _retrieval_only_fallback(self, system_prompt: str, user_prompt: str) -> str:
        logger.info("llm_fallback_retrieval_only")
        lines = system_prompt.split("\n")
        context_lines = []
        capture = False
        for line in lines:
            if "---" in line:
                capture = not capture
                continue
            if capture:
                context_lines.append(line.strip())
        context = "\n".join(l for l in context_lines if l)
        if not context:
            return (
                "[Demo Mode] Chưa có LLM được cấu hình. "
                "Hãy set AZURE_OPENAI_API_KEY hoặc cài Ollama để kích hoạt AI.\n\n"
                "Dưới đây là thông tin tìm được từ Knowledge Base:\n\n"
                + "\n".join(lines[3:10])
            )
        return (
            "[Demo Mode — RAG Retrieval Only]\n\n"
            "Thông tin tìm được từ Knowledge Base:\n\n"
            + context
        )

    # --- Ollama ---

    @_retry_policy
    async def _ollama_generate(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{settings.ollama_base_url}/api/chat"
        payload = {
            "model": settings.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()["message"]["content"]

    async def _ollama_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        url = f"{settings.ollama_base_url}/api/chat"
        payload = {
            "model": settings.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            async with client.stream("POST", url, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    token = data.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if data.get("done"):
                        break

    # --- Azure OpenAI ---

    @_retry_policy
    async def _azure_generate(self, system_prompt: str, user_prompt: str) -> str:
        url = (
            f"{settings.azure_openai_endpoint.rstrip('/')}"
            f"/openai/deployments/{settings.azure_openai_deployment}"
            f"/chat/completions?api-version={settings.azure_openai_api_version}"
        )
        headers = {"api-key": settings.azure_openai_api_key}
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def _azure_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        url = (
            f"{settings.azure_openai_endpoint.rstrip('/')}"
            f"/openai/deployments/{settings.azure_openai_deployment}"
            f"/chat/completions?api-version={settings.azure_openai_api_version}"
        )
        headers = {"api-key": settings.azure_openai_api_key}
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    data = json.loads(data_str)
                    delta = data["choices"][0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        yield token

    # --- OpenAI ---

    @_retry_policy
    async def _openai_generate(self, system_prompt: str, user_prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        payload = {
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def _openai_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        payload = {
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    data = json.loads(data_str)
                    delta = data["choices"][0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        yield token
