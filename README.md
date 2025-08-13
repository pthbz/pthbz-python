# pthbz — Python SDK for pth.bz

Official Python library for the **pth.bz** short link service.

- **301 redirect** — permanent redirect for SEO-safe migrations and clean sharing.
- **Interstitial (anti‑bot)** — an intermediate step to filter bots and hide the referrer.
- **QR PNG** — on-demand QR code images.
- **Sync and Async** clients with server-aligned URL validation.

Author: **Avel Kox**  
License: **MIT**

## Installation

```bash
pip install pthbz
```

## Quick start

```python
from pthbz import PthBzClient

client = PthBzClient(base_url="https://pth.bz")
res = client.shorten("https://example.com/landing?utm_source=newsletter")
print(res.short_url_301)   # https://pth.bz/AbC1234
print(res.short_url_js)    # https://pth.bz/i/AbC1234   (interstitial anti-bot)
print(res.qr_301_png_url)  # https://pth.bz/?qr=AbC1234
print(res.qr_js_png_url)   # https://pth.bz/?qi=AbC1234
client.close()
```

Async variant:

```python
import asyncio
from pthbz import AsyncPthBzClient

async def main():
    async with AsyncPthBzClient(base_url="https://pth.bz") as client:
        res = await client.shorten("https://example.com")
        print(res.short_url_301)

asyncio.run(main())
```

CLI:

```bash
# 1) Create a short link
pthbz shorten https://example.com

# 2) Build a QR PNG URL from a short link
pthbz --base https://pth.bz qr --url https://pth.bz/AbC1234 --px 640

# 3) Or with CODE directly
pthbz --base https://pth.bz qr --code AbC1234 --interstitial
```

## Notes

- Local URL validation mirrors server rules: only `http`/`https`, userinfo forbidden, `localhost` and IP allowed without a dot, other hosts must include at least one dot, IDN → punycode (via `idna`).
