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

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# ============================================================
# Pollinations client (free)
# ============================================================

class PollinationsClientFree:
    BASE_URL = "https://image.pollinations.ai/prompt/"

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
        self.client = httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(600.0, connect=10.0),
            headers={
                "User-Agent": "poligen-free/1.0",
                "Accept": "image/*",
            },
        )

    def map_size(self, size: str) -> Tuple[int, int]:
        fmt = self.SIZE_MAP.get(size, "landscape")
        return self.FORMATS[fmt]

    async def generate_image_b64(
        self,
        prompt: str,
        size: str = "1920x1080",
        model: str = "flux",
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

client = PollinationsClientFree()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[poligen-free] Free Pollinations proxy started")
    yield
    await client.close()

app = FastAPI(
    title="Pollinations Free Image Proxy",
    lifespan=lifespan,
)

# ============================================================
# OpenAI-compatible image endpoint
# ============================================================

@app.post("/v1/images/generations")
async def image_generation(request: Request):
    body = await request.json()

    prompt = body.get("prompt")
    if not prompt:
        return JSONResponse(status_code=400, content={"error": "prompt required"})

    size = body.get("size", "1920x1080")
    model = body.get("model", "flux")
    n = int(body.get("n", 1))

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
    uvicorn.run(app, host="127.0.0.1", port=4290)
