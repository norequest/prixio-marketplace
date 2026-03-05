#!/usr/bin/env python3
"""
Migration Validator for Prixio LLC Hosting Migrations

Validates that a migration target is healthy and ready to receive production traffic.
Performs connectivity, DNS, SSL, health, latency, and smoke test checks.

Usage:
    python3 migration_validator.py \
        --source railway \
        --target hetzner \
        --app courio-api \
        --source-url https://courio-api-production.up.railway.app \
        --target-url https://staging-api.courio.ge

    python3 migration_validator.py \
        --target hetzner \
        --app courio-api \
        --target-url https://api.courio.ge \
        --target-ip 159.69.XX.XX
"""

import argparse
import json
import socket
import ssl
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from urllib.error import URLError
from urllib.request import Request, urlopen


class Status(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


@dataclass
class CheckResult:
    name: str
    status: Status
    message: str
    duration_ms: Optional[float] = None
    details: Optional[dict] = None


@dataclass
class ValidationReport:
    source: str
    target: str
    app: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.status in (Status.PASS, Status.SKIP, Status.WARN) for c in self.checks)

    @property
    def summary(self) -> str:
        counts = {s: 0 for s in Status}
        for c in self.checks:
            counts[c.status] += 1
        parts = [f"{counts[s]} {s.value}" for s in Status if counts[s] > 0]
        return ", ".join(parts)


def check_target_reachable(target_url: str, target_ip: Optional[str] = None) -> CheckResult:
    """Check if the target server is reachable via ping or TCP connection."""
    name = "Target Reachable"

    host = target_ip
    if not host:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(target_url)
            host = parsed.hostname
        except Exception:
            return CheckResult(name, Status.FAIL, "Could not parse target URL")

    # Try TCP connection on port 443
    start = time.monotonic()
    try:
        sock = socket.create_connection((host, 443), timeout=10)
        sock.close()
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(name, Status.PASS, f"TCP connection to {host}:443 succeeded", elapsed)
    except (socket.timeout, socket.error) as e:
        # Try port 80 as fallback
        try:
            sock = socket.create_connection((host, 80), timeout=10)
            sock.close()
            elapsed = (time.monotonic() - start) * 1000
            return CheckResult(name, Status.WARN, f"TCP 443 failed but 80 succeeded on {host}", elapsed)
        except (socket.timeout, socket.error):
            elapsed = (time.monotonic() - start) * 1000
            return CheckResult(name, Status.FAIL, f"Cannot reach {host} on port 443 or 80: {e}", elapsed)


def check_dns_resolution(target_url: str, expected_ip: Optional[str] = None) -> CheckResult:
    """Check if DNS resolves correctly, optionally to an expected IP."""
    name = "DNS Resolution"

    try:
        from urllib.parse import urlparse
        parsed = urlparse(target_url)
        hostname = parsed.hostname
    except Exception:
        return CheckResult(name, Status.FAIL, "Could not parse target URL")

    start = time.monotonic()
    try:
        ips = socket.getaddrinfo(hostname, None, socket.AF_INET)
        resolved_ips = list(set(addr[4][0] for addr in ips))
        elapsed = (time.monotonic() - start) * 1000

        if not resolved_ips:
            return CheckResult(name, Status.FAIL, f"{hostname} resolved to no addresses", elapsed)

        if expected_ip and expected_ip not in resolved_ips:
            return CheckResult(
                name, Status.FAIL,
                f"{hostname} resolves to {resolved_ips}, expected {expected_ip}",
                elapsed,
                {"resolved": resolved_ips, "expected": expected_ip},
            )

        msg = f"{hostname} resolves to {resolved_ips}"
        if expected_ip:
            msg += f" (matches expected {expected_ip})"
        return CheckResult(name, Status.PASS, msg, elapsed, {"resolved": resolved_ips})

    except socket.gaierror as e:
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(name, Status.FAIL, f"DNS resolution failed for {hostname}: {e}", elapsed)


def check_ssl_certificate(target_url: str) -> CheckResult:
    """Check if the SSL certificate is valid."""
    name = "SSL Certificate"

    try:
        from urllib.parse import urlparse
        parsed = urlparse(target_url)
        hostname = parsed.hostname
        port = parsed.port or 443
    except Exception:
        return CheckResult(name, Status.FAIL, "Could not parse target URL")

    start = time.monotonic()
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                elapsed = (time.monotonic() - start) * 1000

                # Check expiry
                not_after = ssl.cert_time_to_seconds(cert["notAfter"])
                now = time.time()
                days_remaining = (not_after - now) / 86400

                # Check subject
                subject = dict(x[0] for x in cert.get("subject", ()))
                san = [entry[1] for entry in cert.get("subjectAltName", ())]

                details = {
                    "issuer": dict(x[0] for x in cert.get("issuer", ())),
                    "subject": subject,
                    "san": san,
                    "not_after": cert["notAfter"],
                    "days_remaining": round(days_remaining, 1),
                }

                if days_remaining < 7:
                    return CheckResult(name, Status.WARN, f"Certificate expires in {days_remaining:.0f} days", elapsed, details)
                if days_remaining < 0:
                    return CheckResult(name, Status.FAIL, "Certificate has expired", elapsed, details)

                return CheckResult(
                    name, Status.PASS,
                    f"Valid certificate, expires in {days_remaining:.0f} days",
                    elapsed, details,
                )

    except ssl.SSLError as e:
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(name, Status.FAIL, f"SSL error: {e}", elapsed)
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(name, Status.FAIL, f"Connection error: {e}", elapsed)


def check_health_endpoint(target_url: str, health_path: str = "/health") -> CheckResult:
    """Check if the health endpoint returns 200."""
    name = "Health Endpoint"

    url = target_url.rstrip("/") + health_path
    start = time.monotonic()
    try:
        req = Request(url, headers={"User-Agent": "PrixioMigrationValidator/1.0"})
        with urlopen(req, timeout=15) as response:
            elapsed = (time.monotonic() - start) * 1000
            status_code = response.status
            body = response.read().decode("utf-8", errors="replace")

            try:
                body_json = json.loads(body)
            except json.JSONDecodeError:
                body_json = None

            if status_code == 200:
                return CheckResult(
                    name, Status.PASS,
                    f"GET {health_path} returned 200",
                    elapsed,
                    {"status_code": status_code, "body": body_json or body[:500]},
                )
            else:
                return CheckResult(
                    name, Status.FAIL,
                    f"GET {health_path} returned {status_code}",
                    elapsed,
                    {"status_code": status_code, "body": body[:500]},
                )
    except URLError as e:
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(name, Status.FAIL, f"Request failed: {e}", elapsed)
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(name, Status.FAIL, f"Error: {e}", elapsed)


def check_response_time(target_url: str, health_path: str = "/health", threshold_ms: float = 500) -> CheckResult:
    """Check if response time is acceptable (< threshold)."""
    name = "Response Time"

    url = target_url.rstrip("/") + health_path
    times = []

    for i in range(3):
        start = time.monotonic()
        try:
            req = Request(url, headers={"User-Agent": "PrixioMigrationValidator/1.0"})
            with urlopen(req, timeout=15) as response:
                response.read()
                elapsed = (time.monotonic() - start) * 1000
                times.append(elapsed)
        except Exception:
            times.append(float("inf"))

    if not times or all(t == float("inf") for t in times):
        return CheckResult(name, Status.FAIL, "All requests failed")

    valid_times = [t for t in times if t != float("inf")]
    avg_time = sum(valid_times) / len(valid_times) if valid_times else float("inf")
    p95_time = sorted(valid_times)[int(len(valid_times) * 0.95)] if valid_times else float("inf")

    details = {
        "samples": len(valid_times),
        "avg_ms": round(avg_time, 1),
        "p95_ms": round(p95_time, 1),
        "threshold_ms": threshold_ms,
        "all_ms": [round(t, 1) for t in times],
    }

    if avg_time > threshold_ms:
        return CheckResult(
            name, Status.FAIL,
            f"Average response time {avg_time:.0f}ms exceeds threshold {threshold_ms:.0f}ms",
            avg_time, details,
        )
    elif avg_time > threshold_ms * 0.8:
        return CheckResult(
            name, Status.WARN,
            f"Average response time {avg_time:.0f}ms is close to threshold {threshold_ms:.0f}ms",
            avg_time, details,
        )
    else:
        return CheckResult(
            name, Status.PASS,
            f"Average response time {avg_time:.0f}ms (threshold: {threshold_ms:.0f}ms)",
            avg_time, details,
        )


def check_smoke_test(source_url: Optional[str], target_url: str, health_path: str = "/health") -> CheckResult:
    """Compare basic responses from source and target."""
    name = "Smoke Test (Source vs Target)"

    if not source_url:
        return CheckResult(name, Status.SKIP, "No source URL provided, skipping comparison")

    try:
        headers = {"User-Agent": "PrixioMigrationValidator/1.0"}

        # Fetch from source
        req_source = Request(source_url.rstrip("/") + health_path, headers=headers)
        with urlopen(req_source, timeout=15) as resp:
            source_status = resp.status
            source_body = resp.read().decode("utf-8", errors="replace")

        # Fetch from target
        req_target = Request(target_url.rstrip("/") + health_path, headers=headers)
        with urlopen(req_target, timeout=15) as resp:
            target_status = resp.status
            target_body = resp.read().decode("utf-8", errors="replace")

        details = {
            "source_status": source_status,
            "target_status": target_status,
        }

        # Compare status codes
        if source_status != target_status:
            return CheckResult(
                name, Status.FAIL,
                f"Status mismatch: source={source_status}, target={target_status}",
                details=details,
            )

        # Compare response structure (for JSON responses)
        try:
            source_json = json.loads(source_body)
            target_json = json.loads(target_body)
            source_keys = set(source_json.keys()) if isinstance(source_json, dict) else set()
            target_keys = set(target_json.keys()) if isinstance(target_json, dict) else set()

            details["source_keys"] = sorted(source_keys)
            details["target_keys"] = sorted(target_keys)

            if source_keys != target_keys:
                missing = source_keys - target_keys
                extra = target_keys - source_keys
                details["missing_keys"] = sorted(missing)
                details["extra_keys"] = sorted(extra)
                return CheckResult(
                    name, Status.WARN,
                    f"Response structure differs: missing={missing}, extra={extra}",
                    details=details,
                )
        except (json.JSONDecodeError, AttributeError):
            # Non-JSON responses, just compare status
            pass

        return CheckResult(
            name, Status.PASS,
            "Source and target responses match",
            details=details,
        )

    except Exception as e:
        return CheckResult(name, Status.FAIL, f"Smoke test error: {e}")


def print_report(report: ValidationReport) -> None:
    """Print the validation report to stdout."""
    width = 72
    print("\n" + "=" * width)
    print("  PRIXIO MIGRATION VALIDATION REPORT")
    print("=" * width)
    print(f"  Timestamp : {report.timestamp}")
    print(f"  Source    : {report.source}")
    print(f"  Target    : {report.target}")
    print(f"  App       : {report.app}")
    print("-" * width)

    for check in report.checks:
        icon = {
            Status.PASS: "[PASS]",
            Status.FAIL: "[FAIL]",
            Status.WARN: "[WARN]",
            Status.SKIP: "[SKIP]",
        }[check.status]

        duration = f" ({check.duration_ms:.0f}ms)" if check.duration_ms is not None else ""
        print(f"  {icon} {check.name}{duration}")
        print(f"         {check.message}")

        if check.details:
            for key, value in check.details.items():
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, default=str)
                print(f"           {key}: {value}")
        print()

    print("-" * width)
    overall = "PASS -- Migration target is ready" if report.passed else "FAIL -- Migration target has issues"
    print(f"  RESULT: {overall}")
    print(f"  Summary: {report.summary}")
    print("=" * width + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Prixio hosting migration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --source railway --target hetzner --app courio-api \\
           --source-url https://courio-api-production.up.railway.app \\
           --target-url https://staging-api.courio.ge

  %(prog)s --target flyio --app courio-api \\
           --target-url https://courio-api-prod.fly.dev
        """,
    )
    parser.add_argument("--source", required=True, help="Source provider (e.g., railway, vercel, supabase)")
    parser.add_argument("--target", required=True, help="Target provider (e.g., hetzner, flyio, coolify)")
    parser.add_argument("--app", required=True, help="Application name (e.g., courio-api, lotify-web)")
    parser.add_argument("--source-url", default=None, help="Source URL for comparison (optional)")
    parser.add_argument("--target-url", required=True, help="Target URL to validate")
    parser.add_argument("--target-ip", default=None, help="Expected IP for DNS check (optional)")
    parser.add_argument("--health-path", default="/health", help="Health check path (default: /health)")
    parser.add_argument("--threshold-ms", type=float, default=500, help="Response time threshold in ms (default: 500)")
    parser.add_argument("--json", action="store_true", help="Output report as JSON")

    args = parser.parse_args()

    report = ValidationReport(
        source=args.source,
        target=args.target,
        app=args.app,
    )

    # Run all checks
    print(f"\nValidating migration: {args.source} -> {args.target} ({args.app})")
    print(f"Target: {args.target_url}\n")

    checks = [
        ("Checking target reachability...", lambda: check_target_reachable(args.target_url, args.target_ip)),
        ("Checking DNS resolution...", lambda: check_dns_resolution(args.target_url, args.target_ip)),
        ("Checking SSL certificate...", lambda: check_ssl_certificate(args.target_url)),
        ("Checking health endpoint...", lambda: check_health_endpoint(args.target_url, args.health_path)),
        ("Checking response time...", lambda: check_response_time(args.target_url, args.health_path, args.threshold_ms)),
        ("Running smoke test...", lambda: check_smoke_test(args.source_url, args.target_url, args.health_path)),
    ]

    for label, check_fn in checks:
        print(f"  {label}", end="", flush=True)
        result = check_fn()
        report.checks.append(result)
        print(f" {result.status.value}")

    if args.json:
        output = {
            "source": report.source,
            "target": report.target,
            "app": report.app,
            "timestamp": report.timestamp,
            "passed": report.passed,
            "summary": report.summary,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "duration_ms": c.duration_ms,
                    "details": c.details,
                }
                for c in report.checks
            ],
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print_report(report)

    sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
