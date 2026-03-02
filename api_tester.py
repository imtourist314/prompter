#!/usr/bin/env python3
"""Simple smoke tests for the Prompter API read endpoints.

This script tests GET requests against:
  /api/instructions/<area>/<file>

Examples:
  python api_tester.py --base-url http://localhost:3050 --area testing --file instructions.md
  python api_tester.py --base-url http://localhost:3050 --smoke

Exit codes:
  0  all tests passed
  1  one or more tests failed
  2  invalid arguments

Assumes the `requests` package is available.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests


DEFAULT_BASE_URL = os.environ.get("PROMPTER_BASE_URL", "http://localhost:3050").rstrip("/")
ALLOWED_AREAS = ("front-end", "back-end", "testing")
ALLOWED_FILES = ("instructions.md", "completed_instructions.md")


def normalize_area(area: str) -> str:
    a = area.strip().lower()
    aliases = {
        "frontend": "front-end",
        "front-end": "front-end",
        "front_end": "front-end",
        "fe": "front-end",
        "backend": "back-end",
        "back-end": "back-end",
        "back_end": "back-end",
        "be": "back-end",
        "testing": "testing",
        "test": "testing",
        "qa": "testing",
    }
    if a not in aliases:
        raise ValueError(f"Invalid area '{area}'. Expected one of: {', '.join(ALLOWED_AREAS)}")
    return aliases[a]


@dataclass
class TestResult:
    name: str
    ok: bool
    detail: str = ""


def _get_text(url: str, timeout_s: int) -> requests.Response:
    return requests.get(url, timeout=timeout_s)


def test_read(
    base_url: str,
    area: str,
    file: str,
    timeout_s: int,
    print_body: bool,
    max_chars: int,
) -> TestResult:
    url = f"{base_url}/api/instructions/{area}/{file}"
    name = f"GET {url}"

    try:
        resp = _get_text(url, timeout_s=timeout_s)
    except requests.RequestException as e:
        return TestResult(name=name, ok=False, detail=f"request failed: {e}")

    if resp.status_code != 200:
        return TestResult(name=name, ok=False, detail=f"expected 200, got {resp.status_code}: {resp.text[:200]}")

    ctype = resp.headers.get("content-type", "")
    if not ctype.startswith("text/markdown"):
        return TestResult(name=name, ok=False, detail=f"unexpected content-type: {ctype!r}")

    body = resp.text or ""
    if print_body:
        snippet = body if len(body) <= max_chars else (body[:max_chars] + "...<truncated>")
        # Print body as part of detail so it appears with the test output.
        return TestResult(name=name, ok=True, detail=f"{len(body)} bytes\n---\n{snippet}\n---")

    return TestResult(name=name, ok=True, detail=f"{len(body)} bytes")


def test_invalid_area(base_url: str, timeout_s: int) -> TestResult:
    url = f"{base_url}/api/instructions/not-a-real-area/instructions.md"
    name = f"GET invalid area -> 400 ({url})"

    try:
        resp = _get_text(url, timeout_s=timeout_s)
    except requests.RequestException as e:
        return TestResult(name=name, ok=False, detail=f"request failed: {e}")

    if resp.status_code != 400:
        return TestResult(name=name, ok=False, detail=f"expected 400, got {resp.status_code}: {resp.text[:200]}")

    # Server returns JSON: { error: "..." }
    ctype = resp.headers.get("content-type", "")
    if "application/json" not in ctype:
        return TestResult(name=name, ok=False, detail=f"expected JSON error, got content-type: {ctype!r}")

    return TestResult(name=name, ok=True, detail=resp.text.strip()[:200])


def test_invalid_file(base_url: str, timeout_s: int) -> TestResult:
    url = f"{base_url}/api/instructions/testing/not-allowed.md"
    name = f"GET invalid file -> 400 ({url})"

    try:
        resp = _get_text(url, timeout_s=timeout_s)
    except requests.RequestException as e:
        return TestResult(name=name, ok=False, detail=f"request failed: {e}")

    if resp.status_code != 400:
        return TestResult(name=name, ok=False, detail=f"expected 400, got {resp.status_code}: {resp.text[:200]}")

    ctype = resp.headers.get("content-type", "")
    if "application/json" not in ctype:
        return TestResult(name=name, ok=False, detail=f"expected JSON error, got content-type: {ctype!r}")

    return TestResult(name=name, ok=True, detail=resp.text.strip()[:200])


def run_tests(tests: Iterable[TestResult]) -> int:
    failed = 0
    for t in tests:
        status = "PASS" if t.ok else "FAIL"
        print(f"[{status}] {t.name}")
        if t.detail:
            for line in t.detail.splitlines():
                print(f"       {line}")
        if not t.ok:
            failed += 1

    if failed:
        print(f"\n{failed} test(s) failed")
        return 1

    print("\nAll tests passed")
    return 0


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Test Prompter API GET endpoints")
    p.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL}). Can also set PROMPTER_BASE_URL.",
    )
    p.add_argument(
        "--area",
        default=None,
        help="Area to fetch (front-end/back-end/testing). If omitted, use --smoke or --all.",
    )
    p.add_argument(
        "--file",
        default=None,
        help="Filename to fetch (instructions.md or completed_instructions.md). If omitted, use --smoke or --all.",
    )
    p.add_argument(
        "--all",
        action="store_true",
        help="Fetch both allowed files for the specified --area.",
    )
    p.add_argument(
        "--smoke",
        action="store_true",
        help="Run a small suite: read all areas/files + invalid area/file tests.",
    )
    p.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10).",
    )
    p.add_argument(
        "--print-body",
        action="store_true",
        help="Print response body (or a truncated snippet) for successful reads.",
    )
    p.add_argument(
        "--max-chars",
        type=int,
        default=1200,
        help="When using --print-body, maximum characters to print (default: 1200).",
    )
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    base_url = (args.base_url or "").rstrip("/")
    timeout_s = max(1, int(args.timeout))

    results: List[TestResult] = []

    try:
        if args.smoke:
            for area in ALLOWED_AREAS:
                for file in ALLOWED_FILES:
                    results.append(
                        test_read(
                            base_url,
                            area,
                            file,
                            timeout_s=timeout_s,
                            print_body=args.print_body,
                            max_chars=args.max_chars,
                        )
                    )
            results.append(test_invalid_area(base_url, timeout_s=timeout_s))
            results.append(test_invalid_file(base_url, timeout_s=timeout_s))
            return run_tests(results)

        if args.area and args.all:
            area = normalize_area(args.area)
            for file in ALLOWED_FILES:
                results.append(
                    test_read(
                        base_url,
                        area,
                        file,
                        timeout_s=timeout_s,
                        print_body=args.print_body,
                        max_chars=args.max_chars,
                    )
                )
            return run_tests(results)

        if args.area and args.file:
            area = normalize_area(args.area)
            if args.file not in ALLOWED_FILES:
                print(
                    f"Invalid --file '{args.file}'. Expected one of: {', '.join(ALLOWED_FILES)}",
                    file=sys.stderr,
                )
                return 2
            results.append(
                test_read(
                    base_url,
                    area,
                    args.file,
                    timeout_s=timeout_s,
                    print_body=args.print_body,
                    max_chars=args.max_chars,
                )
            )
            return run_tests(results)

        print("Nothing to do. Provide --smoke, or --area/--file, or --area --all.", file=sys.stderr)
        return 2

    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
