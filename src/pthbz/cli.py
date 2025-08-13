from __future__ import annotations
import argparse
import sys
from .client import PthBzClient
from .utils import extract_code_from_url, build_qr_url

def _cmd_shorten(args: argparse.Namespace) -> int:
    client = PthBzClient(base_url=args.base, timeout=args.timeout)
    try:
        res = client.shorten(args.url)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        client.close()

    print("short_url_301:   ", res.short_url_301)
    print("short_url_js:    ", res.short_url_js, "  (interstitial anti-bot)")
    print("qr_301_png_url:  ", res.qr_301_png_url)
    print("qr_js_png_url:   ", res.qr_js_png_url)
    return 0

def _cmd_qr(args: argparse.Namespace) -> int:
    code = args.code or extract_code_from_url(args.url or "")
    if not code:
        print("Error: CODE was not provided and cannot be extracted.", file=sys.stderr)
        return 1
    try:
        url = build_qr_url(args.base, code, interstitial=args.interstitial, px=args.px)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(url)
    return 0

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pthbz",
        description="CLI for pth.bz — create short links, interstitial (anti-bot), and QR PNG URLs."
    )
    parser.add_argument("--base", default="https://pth.bz", help="Service base URL (default: https://pth.bz)")
    parser.add_argument("--timeout", default=10.0, type=float, help="Request timeout in seconds (default: 10.0).")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_short = sub.add_parser("shorten", help="Create a short link")
    p_short.add_argument("url", help="Long URL to shorten")
    p_short.set_defaults(func=_cmd_shorten)

    p_qr = sub.add_parser("qr", help="Build a QR PNG URL from CODE or a short link")
    p_qr.add_argument("--url", help="Short link to extract CODE from (alternative to --code)")
    p_qr.add_argument("--code", help="Short link CODE")
    p_qr.add_argument("--interstitial", action="store_true", help="Build QR for the interstitial (anti-bot) variant")
    p_qr.add_argument("--px", type=int, help="PNG size in pixels (200–2048)")
    p_qr.set_defaults(func=_cmd_qr)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
