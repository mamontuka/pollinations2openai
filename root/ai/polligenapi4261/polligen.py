# Copyright (C) 2026 Oleh Mamont
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org>.


import random
import time
import base64
import asyncio
import httpx

from pathlib import Path
from typing import Dict, Tuple
from urllib.parse import quote
from contextlib import asynccontextmanager
from collections import deque
from datetime import datetime, timedelta

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# ============================================================
# API key loader (file-based, no env)
# ============================================================

def read_api_key(path: str) -> str | None:
    try:
        key = Path(path).read_text(encoding="utf-8").strip()
        return key if key else None
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"[poligen] Failed to read API key file: {e}")
        return None


# ============================================================
# Rate/Limits tracking
# ============================================================

TPD_LIMIT = 450  # limit per day
RPM_LIMIT = 5    # limit per minute

last_requests = deque()  # timestamps last queries (for RPM)
daily_count = 0
daily_reset = datetime.utcnow() + timedelta(days=1)


# ============================================================
# Pollinations client
# ============================================================

class PollinationsClient:
    BASE_URL = "https://gen.pollinations.ai/image/"
    API_KEY_PATH = "/root/ai/polligenapi4261/pollinations.key"

    FORMATS: Dict[str, Tuple[int, int]] = {
        "square": (1024, 1024),
        "landscape": (1920, 1080),
        "portrait": (1080, 1920),
        "landscape_large": (2560, 1440),
        "portrait_large": (1440, 2560),
    }

    SIZE_MAP = {
        "512x512": "square",
        "1024x1024": "square",
        "1920x1080": "landscape",
        "2560x1440": "landscape_large",
        "1080x1920": "portrait",
        "1440x2560": "portrait_large",
    }

    def __init__(self):
        self.api_key = read_api_key(self.API_KEY_PATH)

        headers = {
            "User-Agent": "poligen/1.0",
            "Accept": "image/*",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self.client = httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(600.0),
            headers=headers,
        )

    def map_size(self, size: str) -> Tuple[int, int]:
        fmt = self.SIZE_MAP.get(size, "landscape")
        return self.FORMATS[fmt]

    async def generate_image_b64(
        self,
        prompt: str,
        size: str = "1920x1080",
        model: str = "klein",
        enhance: bool = True,
        seed: int | None = None,
    ) -> str:
        width, height = self.map_size(size)

        if seed is None:
            seed = random.randint(0, 999999)

        nonce = random.randint(100000, 999999)
        safe_prompt = quote(f"{prompt}::{nonce}", safe="")
        url = f"{self.BASE_URL}{safe_prompt}"

        params = {
            "width": width,
            "height": height,
            "model": model,
            "nologo": "true",
            "enhance": str(enhance).lower(),
            "seed": seed,
            "t": int(time.time()),
        }

        resp = await self.client.get(url, params=params)
        resp.raise_for_status()

        return base64.b64encode(resp.content).decode("utf-8")

    async def close(self):
        await self.client.aclose()


# ============================================================
# FastAPI app
# ============================================================

client = PollinationsClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if client.api_key:
        print("[poligen] Pollinations API key loaded (paid mode)")
    else:
        print("[poligen] No API key found (free mode)")
    yield
    await client.close()

app = FastAPI(
    title="Pollinations OpenAI Image Proxy",
    lifespan=lifespan,
)

# ============================================================
# OpenAI-compatible image endpoint
# ============================================================

@app.post("/v1/images/generations")
async def image_generation(request: Request):
    global daily_count, daily_reset, last_requests

    body = await request.json()
    prompt = body.get("prompt")
    if not prompt:
        return JSONResponse(status_code=400, content={"error": "prompt required"})

    size = body.get("size", "1920x1080")
    model = body.get("model", "klein")
    n = int(body.get("n", 1))

    # --- limits ---
    now = datetime.utcnow()
    if now >= daily_reset:
        daily_count = 0
        daily_reset = now + timedelta(days=1)

    # check TPD
    if daily_count >= TPD_LIMIT:
        return JSONResponse(
            status_code=503,
            content={"error": "Daily limit exceeded"}
        )

    # check RPM
    while last_requests and (now - last_requests[0]).total_seconds() > 60:
        last_requests.popleft()

    if len(last_requests) >= RPM_LIMIT:
        return JSONResponse(
            status_code=503,
            content={"error": "Rate limit exceeded"}
        )

    # query registration
    last_requests.append(now)
    daily_count += 1

    # --- generation ---
    images = []
    for _ in range(max(1, n)):
        img_b64 = await client.generate_image_b64(
            prompt=prompt,
            size=size,
            model=model,
        )
        images.append({"b64_json": img_b64})

    return JSONResponse(
        content={
            "created": int(time.time()),
            "data": images,
        }
    )


# ============================================================
# Local run
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=4261)
