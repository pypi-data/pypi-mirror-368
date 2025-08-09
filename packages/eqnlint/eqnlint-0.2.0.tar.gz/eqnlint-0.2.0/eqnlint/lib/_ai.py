# lib/_ai.py
import os
import json
import asyncio
import httpx
from ._budget import RateLimiter
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    def __init__(self, model, rate=0.5, max_tokens=1200):
        self.model = model
        self.rate = RateLimiter(rate)
        self.max_tokens = max_tokens

    async def complete(self, system, user, fewshot=None):
        await self.rate.wait_async()
        if self.model.startswith("ollama:"):
            return await self._ollama(system, user, fewshot)
        else:
            return await self._openai(system, user, fewshot)

    async def _openai(self, system, user, fewshot):
        import openai
        client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        msgs = [{"role": "system", "content": system}]
        if fewshot:
            msgs += fewshot
        msgs.append({"role": "user", "content": user})
        
        try:
            resp = await client.chat.completions.create(
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
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream("POST", url, json=data) as response:
                    if response.status_code != 200:
                        raise RuntimeError(f"Ollama error: {response.status_code} {await response.aread()}")

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
        except Exception as e:
            print(f"[ERROR] Ollama call failed: {type(e).__name__}: {e}")
            return "[ERROR] Failed to get response from Ollama."

# Ensure RateLimiter has an async version
if not hasattr(RateLimiter, 'wait_async'):
    import time
    class RateLimiter:
        def __init__(self, rate):
            self.interval = 1.0 / rate
            self.last_called = None

        def wait(self):
            now = time.time()
            if self.last_called:
                elapsed = now - self.last_called
                if elapsed < self.interval:
                    time.sleep(self.interval - elapsed)
            self.last_called = time.time()

        async def wait_async(self):
            now = asyncio.get_event_loop().time()
            if self.last_called:
                elapsed = now - self.last_called
                if elapsed < self.interval:
                    await asyncio.sleep(self.interval - elapsed)
            self.last_called = asyncio.get_event_loop().time()
