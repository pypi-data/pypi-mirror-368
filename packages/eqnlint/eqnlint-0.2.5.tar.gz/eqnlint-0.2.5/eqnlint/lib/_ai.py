# lib/_ai.py
import os
import json
import asyncio
import contextlib
import inspect
import httpx
from dotenv import load_dotenv
from ._budget import RateLimiter

load_dotenv()

class AIClient:
    def __init__(self, model, rate=0.5, max_tokens=1200):
        self.model = model
        self.rate = RateLimiter(rate)
        self.max_tokens = max_tokens
        self._openai_client = None  # persistent async client

    async def _ensure_openai_client(self):
        if self._openai_client is None:
            import openai
            # Create once; reuse for all calls
            self._openai_client = openai.AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )


    async def aclose(self):
        """
        Best-effort teardown of the persistent OpenAI async client.

        - Works whether the client exposes .aclose() (some libs) or .close() (OpenAI AsyncOpenAI).
        - Awaits the method if it's async (coroutine function or returns an awaitable).
        - No-ops safely if there's no running loop or it's already closed.
        - Yields control once so httpx/anyio can finish background cleanup.
        """
        client = self._openai_client
        self._openai_client = None  # drop reference early
        if not client:
            return

        # If there's no running loop (e.g., interpreter shutdown), bail quietly.
        try:
            loop = asyncio.get_running_loop()
            if loop.is_closed():
                return
        except RuntimeError:
            return

        # Prefer async aclose(), otherwise use close(), awaiting when needed.
        try:
            meth = getattr(client, "aclose", None) or getattr(client, "close", None)
            if not meth:
                return

            with contextlib.suppress(RuntimeError):
                if inspect.iscoroutinefunction(meth):
                    await meth()
                else:
                    result = meth()
                    if inspect.isawaitable(result):
                        await result
        except asyncio.CancelledError:
            raise
        except Exception:
            # Ignore shutdown noise
            pass

        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.sleep(0)

    async def complete(self, system, user, fewshot=None):
        await self.rate.wait_async()
        if self.model.startswith("ollama:"):
            return await self._ollama(system, user, fewshot)
        else:
            return await self._openai(system, user, fewshot)

    async def _openai(self, system, user, fewshot):
        await self._ensure_openai_client()
        msgs = [{"role": "system", "content": system}]
        if fewshot:
            msgs += fewshot
        msgs.append({"role": "user", "content": user})

        try:
            resp = await self._openai_client.chat.completions.create(
                model=self.model,
                messages=msgs,
                temperature=0,
                max_tokens=self.max_tokens
            )
            content = resp.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content.removeprefix("```json").removesuffix("```").strip()
            elif content.startswith("```"):
                content = content.removeprefix("```").removesuffix("```").strip()
            return content
        except asyncio.CancelledError:
            # Graceful cancel (e.g., Ctrl-C) without noisy tracebacks
            raise
        except Exception as e:
            print(f"[ERROR] OpenAI call failed: {type(e).__name__}: {e}")
            return "[ERROR] Failed to get response from OpenAI."

    async def _ollama(self, system, user, fewshot):
        prompt = system + "\n"
        if fewshot:
            for msg in fewshot:
                prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        prompt += f"User: {user}\n"

        url = "http://localhost:11434/api/generate"
        data = {
            "model": self.model.removeprefix("ollama:"),
            "prompt": prompt,
            "stream": True,
        }

        try:
            # This client is scoped to the call and closed before return.
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream("POST", url, json=data) as response:
                    if response.status_code != 200:
                        body = await response.aread()
                        raise RuntimeError(f"Ollama error: {response.status_code} {body!r}")
                    reply = ""
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            json_chunk = json.loads(line)
                            reply += json_chunk.get("response", "")
                        except Exception as ex:
                            print(f"[ERROR] Streaming: {type(ex).__name__}: {ex}")
                    return reply.strip()
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"[ERROR] Ollama call failed: {type(e).__name__}: {e}")
            return "[ERROR] Failed to get response from Ollama."