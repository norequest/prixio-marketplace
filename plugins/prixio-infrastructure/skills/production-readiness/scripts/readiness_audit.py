#!/usr/bin/env python3
"""
Production Readiness Audit Script for Prixio LLC Services.

Runs automated production readiness checks against Lotify and Courio services.
Produces a scored report (0-100) with P0/P1/P2 categorized findings.

Usage:
    python3 readiness_audit.py --app courio-api --level thorough
    python3 readiness_audit.py --app lotify-web --level basic
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class Priority(Enum):
    P0 = "P0 (Critical)"
    P1 = "P1 (High)"
    P2 = "P2 (Medium)"


class Category(Enum):
    RELIABILITY = "Reliability"
    SECURITY = "Security"
    OBSERVABILITY = "Observability"
    PERFORMANCE = "Performance"
    BACKUP = "Backup & Recovery"
    BUILD = "Build & Deploy"
    SEO = "SEO & Accessibility"
    MOBILE = "Mobile"


@dataclass
class Finding:
    priority: Priority
    category: Category
    title: str
    detail: str
    passed: bool = False


@dataclass
class AuditReport:
    app: str
    level: str
    findings: list[Finding] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    @property
    def score(self) -> int:
        if not self.findings:
            return 0
        passed = sum(1 for f in self.findings if f.passed)
        return round((passed / len(self.findings)) * 100)

    def print_report(self) -> None:
        duration = self.end_time - self.start_time
        total = len(self.findings)
        passed = sum(1 for f in self.findings if f.passed)
        failed = total - passed

        print()
        print("=" * 72)
        print(f"  PRODUCTION READINESS AUDIT — {self.app.upper()}")
        print(f"  Level: {self.level} | Duration: {duration:.1f}s")
        print("=" * 72)
        print()

        # Group failures by priority
        for prio in Priority:
            failures = [f for f in self.findings if not f.passed and f.priority == prio]
            if not failures:
                continue
            print(f"  {prio.value} — {len(failures)} issue(s)")
            print(f"  {'-' * 50}")
            for f in failures:
                print(f"    [{f.category.value}] {f.title}")
                print(f"      -> {f.detail}")
            print()

        # Passed checks
        passed_findings = [f for f in self.findings if f.passed]
        if passed_findings:
            print(f"  PASSED — {len(passed_findings)} check(s)")
            print(f"  {'-' * 50}")
            for f in passed_findings:
                print(f"    [OK] [{f.category.value}] {f.title}")
            print()

        # Score
        score = self.score
        grade = "PASS" if score >= 70 else "FAIL"
        bar_filled = score // 2
        bar_empty = 50 - bar_filled
        bar = f"[{'#' * bar_filled}{'.' * bar_empty}]"

        print("=" * 72)
        print(f"  SCORE: {score}/100  {bar}  {grade}")
        print(f"  Total: {total} | Passed: {passed} | Failed: {failed}")
        print("=" * 72)
        print()


# ---------------------------------------------------------------------------
# App configurations
# ---------------------------------------------------------------------------

APP_CONFIGS = {
    "lotify-api": {
        "type": "fastify",
        "base_url": os.environ.get("LOTIFY_API_URL", "http://localhost:3001"),
        "project_dir": os.environ.get("LOTIFY_API_DIR", os.path.expanduser("~/Desktop/lotify/apps/api")),
    },
    "courio-api": {
        "type": "fastify",
        "base_url": os.environ.get("COURIO_API_URL", "http://localhost:3002"),
        "project_dir": os.environ.get("COURIO_API_DIR", os.path.expanduser("~/Desktop/courio/courio/apps/api")),
    },
    "lotify-web": {
        "type": "nextjs",
        "base_url": os.environ.get("LOTIFY_WEB_URL", "http://localhost:3000"),
        "project_dir": os.environ.get("LOTIFY_WEB_DIR", os.path.expanduser("~/Desktop/lotify/apps/web")),
    },
    "courio-admin": {
        "type": "nextjs",
        "base_url": os.environ.get("COURIO_ADMIN_URL", "http://localhost:3003"),
        "project_dir": os.environ.get("COURIO_ADMIN_DIR", os.path.expanduser("~/Desktop/courio/courio/apps/admin")),
    },
    "courier-app": {
        "type": "expo",
        "project_dir": os.environ.get("COURIER_APP_DIR", os.path.expanduser("~/Desktop/courio/courio/apps/courier")),
    },
    "consumer-app": {
        "type": "expo",
        "project_dir": os.environ.get("CONSUMER_APP_DIR", os.path.expanduser("~/Desktop/courio/courio/apps/consumer")),
    },
}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def http_get(url: str, timeout: int = 10) -> tuple[Optional[int], dict, Optional[str]]:
    """Perform an HTTP GET. Returns (status_code, headers_dict, body) or (None, {}, None) on error."""
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            headers = {k.lower(): v for k, v in resp.getheaders()}
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, headers, body
    except urllib.error.HTTPError as e:
        headers = {k.lower(): v for k, v in e.headers.items()} if e.headers else {}
        body = e.read().decode("utf-8", errors="replace") if e.fp else None
        return e.code, headers, body
    except Exception:
        return None, {}, None


def file_contains(filepath: str, needle: str) -> bool:
    """Check whether a file contains a substring (case-insensitive)."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return needle.lower() in f.read().lower()
    except FileNotFoundError:
        return False


def find_file(directory: str, filename: str) -> Optional[str]:
    """Recursively find a file by name under a directory."""
    for root, _dirs, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None


def find_files_with_extension(directory: str, ext: str, max_depth: int = 5) -> list[str]:
    """Find files with a given extension, up to max_depth."""
    results = []
    base_depth = directory.rstrip(os.sep).count(os.sep)
    for root, _dirs, files in os.walk(directory):
        current_depth = root.count(os.sep) - base_depth
        if current_depth > max_depth:
            continue
        for f in files:
            if f.endswith(ext):
                results.append(os.path.join(root, f))
    return results


# ---------------------------------------------------------------------------
# Fastify API checks
# ---------------------------------------------------------------------------

def audit_fastify(report: AuditReport, config: dict, thorough: bool) -> None:
    base_url = config["base_url"]
    project_dir = config["project_dir"]

    # --- Reliability ---

    # Health check endpoint
    status, _headers, body = http_get(f"{base_url}/health")
    report.add(Finding(
        priority=Priority.P0,
        category=Category.RELIABILITY,
        title="Health check endpoint (/health)",
        detail="GET /health should return 200" if status != 200 else "Returns 200 OK",
        passed=status == 200,
    ))

    # DB connectivity in health check
    db_check = body and ("database" in body.lower() or "db" in body.lower() or "postgres" in body.lower()) if body else False
    report.add(Finding(
        priority=Priority.P0,
        category=Category.RELIABILITY,
        title="Health check includes DB connectivity",
        detail="Health response should mention database status" if not db_check else "DB status included",
        passed=db_check,
    ))

    # Graceful shutdown
    has_graceful = False
    entry_candidates = ["server.ts", "server.js", "index.ts", "index.js", "app.ts", "app.js"]
    for candidate in entry_candidates:
        found = find_file(project_dir, candidate)
        if found and (file_contains(found, "SIGTERM") or file_contains(found, "gracefulShutdown") or file_contains(found, "close()")):
            has_graceful = True
            break
    report.add(Finding(
        priority=Priority.P0,
        category=Category.RELIABILITY,
        title="Graceful shutdown handler",
        detail="No SIGTERM handler or graceful shutdown found" if not has_graceful else "Shutdown handler present",
        passed=has_graceful,
    ))

    # Request timeout
    has_timeout = False
    for candidate in entry_candidates:
        found = find_file(project_dir, candidate)
        if found and (file_contains(found, "connectionTimeout") or file_contains(found, "requestTimeout") or file_contains(found, "timeout")):
            has_timeout = True
            break
    report.add(Finding(
        priority=Priority.P1,
        category=Category.RELIABILITY,
        title="Request timeout configuration",
        detail="No timeout configuration found in server entry" if not has_timeout else "Timeout configured",
        passed=has_timeout,
    ))

    # Error boundaries
    has_error_handler = False
    for candidate in entry_candidates:
        found = find_file(project_dir, candidate)
        if found and (file_contains(found, "setErrorHandler") or file_contains(found, "onError") or file_contains(found, "uncaughtException") or file_contains(found, "unhandledRejection")):
            has_error_handler = True
            break
    report.add(Finding(
        priority=Priority.P0,
        category=Category.RELIABILITY,
        title="Error boundaries (unhandled rejection handling)",
        detail="No error handler or uncaught exception handler found" if not has_error_handler else "Error handling present",
        passed=has_error_handler,
    ))

    # --- Security ---

    # Security headers (Helmet)
    status, headers, _body = http_get(f"{base_url}/health")
    has_helmet = headers.get("x-content-type-options") == "nosniff" or "helmet" in str(headers)
    pkg_json = find_file(project_dir, "package.json")
    if not has_helmet and pkg_json:
        has_helmet = file_contains(pkg_json, "@fastify/helmet") or file_contains(pkg_json, "fastify-helmet")
    report.add(Finding(
        priority=Priority.P0,
        category=Category.SECURITY,
        title="Helmet plugin (security headers)",
        detail="No security headers detected (X-Content-Type-Options: nosniff missing)" if not has_helmet else "Security headers present",
        passed=has_helmet,
    ))

    # CORS
    cors_ok = False
    if headers.get("access-control-allow-origin") and headers["access-control-allow-origin"] != "*":
        cors_ok = True
    elif pkg_json and (file_contains(pkg_json, "@fastify/cors") or file_contains(pkg_json, "fastify-cors")):
        # Check if origin is configured (not wildcard)
        cors_file = find_file(project_dir, "cors.ts") or find_file(project_dir, "cors.js")
        if cors_file and not file_contains(cors_file, "origin: '*'") and not file_contains(cors_file, 'origin: "*"'):
            cors_ok = True
        elif not cors_file:
            cors_ok = True  # assume configured if plugin is installed
    report.add(Finding(
        priority=Priority.P0,
        category=Category.SECURITY,
        title="CORS configured (specific origins, not wildcard)",
        detail="CORS not configured or using wildcard origin" if not cors_ok else "CORS properly configured",
        passed=cors_ok,
    ))

    # Rate limiting
    has_rate_limit = False
    if pkg_json:
        has_rate_limit = file_contains(pkg_json, "@fastify/rate-limit") or file_contains(pkg_json, "fastify-rate-limit")
    report.add(Finding(
        priority=Priority.P1,
        category=Category.SECURITY,
        title="Rate limiting per IP and per user",
        detail="@fastify/rate-limit not found in dependencies" if not has_rate_limit else "Rate limiting package installed",
        passed=has_rate_limit,
    ))

    # Request body size limits
    has_body_limit = False
    for candidate in entry_candidates:
        found = find_file(project_dir, candidate)
        if found and (file_contains(found, "bodyLimit") or file_contains(found, "body_limit")):
            has_body_limit = True
            break
    report.add(Finding(
        priority=Priority.P1,
        category=Category.SECURITY,
        title="Request body size limits",
        detail="No explicit bodyLimit configuration found" if not has_body_limit else "Body limit configured",
        passed=has_body_limit,
    ))

    # Input validation (Zod)
    has_zod = pkg_json and file_contains(pkg_json, "zod") if pkg_json else False
    report.add(Finding(
        priority=Priority.P0,
        category=Category.SECURITY,
        title="Input validation (Zod schemas)",
        detail="Zod not found in dependencies" if not has_zod else "Zod installed for schema validation",
        passed=has_zod,
    ))

    # Secrets in logs
    has_pino_redact = False
    ts_files = find_files_with_extension(project_dir, ".ts", max_depth=3)
    for f in ts_files:
        if file_contains(f, "redact") and (file_contains(f, "pino") or file_contains(f, "logger")):
            has_pino_redact = True
            break
    report.add(Finding(
        priority=Priority.P0,
        category=Category.SECURITY,
        title="No secrets in logs (pino redaction)",
        detail="No log redaction configuration found" if not has_pino_redact else "Log redaction configured",
        passed=has_pino_redact,
    ))

    # --- Observability ---

    # Structured logging
    has_pino = pkg_json and file_contains(pkg_json, "pino") if pkg_json else False
    report.add(Finding(
        priority=Priority.P1,
        category=Category.OBSERVABILITY,
        title="Structured JSON logging (pino)",
        detail="Pino logger not found in dependencies" if not has_pino else "Pino installed",
        passed=has_pino,
    ))

    # Request ID propagation
    has_request_id = False
    for f in ts_files[:20]:
        if file_contains(f, "requestId") or file_contains(f, "request-id") or file_contains(f, "x-request-id"):
            has_request_id = True
            break
    report.add(Finding(
        priority=Priority.P1,
        category=Category.OBSERVABILITY,
        title="Request ID propagation",
        detail="No request ID propagation found" if not has_request_id else "Request ID handling found",
        passed=has_request_id,
    ))

    # Sentry
    has_sentry = pkg_json and file_contains(pkg_json, "sentry") if pkg_json else False
    report.add(Finding(
        priority=Priority.P1,
        category=Category.OBSERVABILITY,
        title="Error tracking (Sentry)",
        detail="Sentry not found in dependencies" if not has_sentry else "Sentry installed",
        passed=has_sentry,
    ))

    # --- Performance ---

    # Compression
    has_compression = False
    if headers.get("content-encoding") in ("gzip", "br", "deflate"):
        has_compression = True
    elif pkg_json and (file_contains(pkg_json, "@fastify/compress") or file_contains(pkg_json, "fastify-compress")):
        has_compression = True
    report.add(Finding(
        priority=Priority.P2,
        category=Category.PERFORMANCE,
        title="Response compression (gzip/brotli)",
        detail="No compression detected in responses or dependencies" if not has_compression else "Compression configured",
        passed=has_compression,
    ))

    # Thorough-only checks
    if thorough:
        # Response time check
        if status == 200:
            start = time.time()
            for _ in range(5):
                http_get(f"{base_url}/health")
            avg_ms = ((time.time() - start) / 5) * 1000
            report.add(Finding(
                priority=Priority.P2,
                category=Category.PERFORMANCE,
                title=f"Health endpoint response time (avg: {avg_ms:.0f}ms)",
                detail=f"Average response time is {avg_ms:.0f}ms (target: < 200ms)" if avg_ms > 200 else f"Good: {avg_ms:.0f}ms average",
                passed=avg_ms <= 200,
            ))

        # HSTS header
        has_hsts = "strict-transport-security" in headers
        report.add(Finding(
            priority=Priority.P1,
            category=Category.SECURITY,
            title="HSTS header (Strict-Transport-Security)",
            detail="HSTS header not present" if not has_hsts else "HSTS enabled",
            passed=has_hsts,
        ))

        # X-Frame-Options
        has_xfo = "x-frame-options" in headers
        report.add(Finding(
            priority=Priority.P2,
            category=Category.SECURITY,
            title="X-Frame-Options header",
            detail="X-Frame-Options not set" if not has_xfo else "Frame protection enabled",
            passed=has_xfo,
        ))


# ---------------------------------------------------------------------------
# Next.js checks
# ---------------------------------------------------------------------------

def audit_nextjs(report: AuditReport, config: dict, thorough: bool) -> None:
    base_url = config["base_url"]
    project_dir = config["project_dir"]

    # --- Build & Deploy ---

    # Standalone output
    next_config = find_file(project_dir, "next.config.ts") or find_file(project_dir, "next.config.js") or find_file(project_dir, "next.config.mjs")
    has_standalone = next_config and file_contains(next_config, "standalone") if next_config else False
    report.add(Finding(
        priority=Priority.P1,
        category=Category.BUILD,
        title="Standalone output mode for Docker",
        detail="No standalone output config found in next.config" if not has_standalone else "Standalone output configured",
        passed=has_standalone,
    ))

    # Image optimization
    has_image_opt = next_config and (file_contains(next_config, "images") or file_contains(next_config, "loader")) if next_config else False
    report.add(Finding(
        priority=Priority.P2,
        category=Category.PERFORMANCE,
        title="Image optimization configuration",
        detail="No image optimization config found" if not has_image_opt else "Image config present",
        passed=has_image_opt,
    ))

    # --- Security ---

    # CSP headers
    status, headers, body = http_get(base_url)
    has_csp = "content-security-policy" in headers
    report.add(Finding(
        priority=Priority.P1,
        category=Category.SECURITY,
        title="CSP headers configured",
        detail="Content-Security-Policy header not found" if not has_csp else "CSP header present",
        passed=has_csp,
    ))

    # Sensitive data in client bundles
    pkg_json = find_file(project_dir, "package.json")
    env_files = [f for f in [
        os.path.join(project_dir, ".env.production"),
        os.path.join(project_dir, ".env.local"),
        os.path.join(project_dir, ".env"),
    ] if os.path.exists(f)]
    has_exposed_secrets = False
    for env_file in env_files:
        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key = line.split("=", 1)[0].strip()
                        # NEXT_PUBLIC_ vars are exposed to client
                        if key.startswith("NEXT_PUBLIC_") and any(w in key.lower() for w in ["secret", "password", "private", "key"]):
                            has_exposed_secrets = True
        except Exception:
            pass
    report.add(Finding(
        priority=Priority.P0,
        category=Category.SECURITY,
        title="No sensitive data in NEXT_PUBLIC_ env vars",
        detail="Found NEXT_PUBLIC_ variable with sensitive-looking name" if has_exposed_secrets else "No obvious secrets exposed",
        passed=not has_exposed_secrets,
    ))

    # --- Performance ---

    # Bundle analysis capability
    has_analyzer = pkg_json and file_contains(pkg_json, "bundle-analyzer") if pkg_json else False
    report.add(Finding(
        priority=Priority.P2,
        category=Category.PERFORMANCE,
        title="Bundle size analysis tool available",
        detail="@next/bundle-analyzer not in dependencies" if not has_analyzer else "Bundle analyzer installed",
        passed=has_analyzer,
    ))

    # Font optimization
    ts_files = find_files_with_extension(project_dir, ".tsx", max_depth=4) + find_files_with_extension(project_dir, ".ts", max_depth=4)
    has_next_font = any(file_contains(f, "next/font") for f in ts_files[:30])
    report.add(Finding(
        priority=Priority.P2,
        category=Category.PERFORMANCE,
        title="Font optimization (next/font)",
        detail="No usage of next/font found" if not has_next_font else "next/font in use",
        passed=has_next_font,
    ))

    # --- SEO (only for lotify-web) ---

    is_consumer_facing = "lotify-web" in report.app
    if is_consumer_facing:
        # Sitemap
        sitemap_status, _, _ = http_get(f"{base_url}/sitemap.xml")
        report.add(Finding(
            priority=Priority.P2,
            category=Category.SEO,
            title="Sitemap generation",
            detail="GET /sitemap.xml did not return 200" if sitemap_status != 200 else "Sitemap accessible",
            passed=sitemap_status == 200,
        ))

        # Open Graph tags
        if body:
            has_og = 'og:title' in body or 'og:description' in body
            report.add(Finding(
                priority=Priority.P2,
                category=Category.SEO,
                title="Open Graph meta tags",
                detail="No og:title or og:description found in page HTML" if not has_og else "OG tags present",
                passed=has_og,
            ))

    # --- Error pages ---

    not_found_status, _, not_found_body = http_get(f"{base_url}/__nonexistent_path_for_audit__")
    has_custom_404 = not_found_status == 404 and not_found_body and len(not_found_body) > 100
    report.add(Finding(
        priority=Priority.P2,
        category=Category.RELIABILITY,
        title="Custom 404 page",
        detail="No custom 404 page detected" if not has_custom_404 else "Custom 404 page present",
        passed=has_custom_404,
    ))

    # Thorough-only checks
    if thorough:
        # Response time
        if status and status < 500:
            start = time.time()
            for _ in range(3):
                http_get(base_url)
            avg_ms = ((time.time() - start) / 3) * 1000
            report.add(Finding(
                priority=Priority.P2,
                category=Category.PERFORMANCE,
                title=f"Homepage response time (avg: {avg_ms:.0f}ms)",
                detail=f"Average: {avg_ms:.0f}ms (target: < 1000ms)" if avg_ms > 1000 else f"Good: {avg_ms:.0f}ms",
                passed=avg_ms <= 1000,
            ))

        # Dynamic imports usage
        has_dynamic = any(file_contains(f, "dynamic(") or file_contains(f, "React.lazy") for f in ts_files[:30])
        report.add(Finding(
            priority=Priority.P2,
            category=Category.PERFORMANCE,
            title="Code splitting / dynamic imports",
            detail="No dynamic() or React.lazy usage found" if not has_dynamic else "Dynamic imports in use",
            passed=has_dynamic,
        ))


# ---------------------------------------------------------------------------
# Expo mobile app checks
# ---------------------------------------------------------------------------

def audit_expo(report: AuditReport, config: dict, thorough: bool) -> None:
    project_dir = config["project_dir"]

    # --- Build & Release ---

    # EAS config
    eas_json = os.path.join(project_dir, "eas.json")
    has_eas = os.path.exists(eas_json)
    report.add(Finding(
        priority=Priority.P0,
        category=Category.BUILD,
        title="EAS Build configuration (eas.json)",
        detail="eas.json not found in project root" if not has_eas else "eas.json present",
        passed=has_eas,
    ))

    # EAS profiles
    has_production_profile = False
    if has_eas:
        has_production_profile = file_contains(eas_json, "production")
    report.add(Finding(
        priority=Priority.P0,
        category=Category.BUILD,
        title="Production build profile in eas.json",
        detail="No 'production' profile found in eas.json" if not has_production_profile else "Production profile configured",
        passed=has_production_profile,
    ))

    # app.json / app.config.ts
    app_json = find_file(project_dir, "app.json") or find_file(project_dir, "app.config.ts") or find_file(project_dir, "app.config.js")
    has_app_config = app_json is not None
    report.add(Finding(
        priority=Priority.P0,
        category=Category.BUILD,
        title="App configuration file (app.json / app.config)",
        detail="No app.json or app.config found" if not has_app_config else f"Found: {os.path.basename(app_json)}",
        passed=has_app_config,
    ))

    # Version in app config
    has_version = app_json and file_contains(app_json, "version") if app_json else False
    report.add(Finding(
        priority=Priority.P1,
        category=Category.BUILD,
        title="Version numbering in app config",
        detail="No 'version' field found in app config" if not has_version else "Version field present",
        passed=has_version,
    ))

    # --- Security ---

    # Secure store usage
    pkg_json = find_file(project_dir, "package.json")
    has_secure_store = pkg_json and file_contains(pkg_json, "expo-secure-store") if pkg_json else False
    report.add(Finding(
        priority=Priority.P0,
        category=Category.SECURITY,
        title="Secure storage (expo-secure-store)",
        detail="expo-secure-store not in dependencies" if not has_secure_store else "SecureStore installed",
        passed=has_secure_store,
    ))

    # Hardcoded API keys check
    ts_files = find_files_with_extension(project_dir, ".ts", max_depth=4) + find_files_with_extension(project_dir, ".tsx", max_depth=4)
    has_hardcoded_keys = False
    suspicious_patterns = ["apikey", "api_key", "secret_key", "private_key"]
    for f in ts_files[:50]:
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read().lower()
                for pattern in suspicious_patterns:
                    # Look for hardcoded string assignments (not env references)
                    if pattern in content and ('= "' in content or "= '" in content):
                        # Rough heuristic — skip if it references env/constants
                        if "process.env" not in content and "constants" not in content and "expo-constants" not in content:
                            has_hardcoded_keys = True
                            break
        except Exception:
            pass
        if has_hardcoded_keys:
            break
    report.add(Finding(
        priority=Priority.P0,
        category=Category.SECURITY,
        title="No hardcoded API keys in source",
        detail="Possible hardcoded API key found in source files" if has_hardcoded_keys else "No obvious hardcoded keys",
        passed=not has_hardcoded_keys,
    ))

    # --- Push Notifications ---

    has_notifications = pkg_json and file_contains(pkg_json, "expo-notifications") if pkg_json else False
    report.add(Finding(
        priority=Priority.P1,
        category=Category.MOBILE,
        title="Push notifications (expo-notifications)",
        detail="expo-notifications not installed" if not has_notifications else "Notifications package installed",
        passed=has_notifications,
    ))

    # --- Performance ---

    # Hermes engine
    has_hermes = False
    if app_json and file_contains(app_json, "hermes"):
        has_hermes = True
    elif app_json and not file_contains(app_json, "jsEngine"):
        has_hermes = True  # Hermes is default in modern Expo
    report.add(Finding(
        priority=Priority.P2,
        category=Category.PERFORMANCE,
        title="Hermes engine enabled",
        detail="Hermes may not be configured" if not has_hermes else "Hermes enabled (default or explicit)",
        passed=has_hermes,
    ))

    # Crash reporting
    has_crash_reporting = pkg_json and (file_contains(pkg_json, "sentry") or file_contains(pkg_json, "crashlytics")) if pkg_json else False
    report.add(Finding(
        priority=Priority.P1,
        category=Category.OBSERVABILITY,
        title="Crash reporting (Sentry/Crashlytics)",
        detail="No crash reporting SDK found" if not has_crash_reporting else "Crash reporting installed",
        passed=has_crash_reporting,
    ))

    # Thorough-only: location services for courier app
    if thorough and "courier" in report.app:
        has_location = pkg_json and (file_contains(pkg_json, "expo-location") or file_contains(pkg_json, "expo-task-manager")) if pkg_json else False
        report.add(Finding(
            priority=Priority.P0,
            category=Category.MOBILE,
            title="Background location tracking configured",
            detail="expo-location or expo-task-manager not found" if not has_location else "Location packages installed",
            passed=has_location,
        ))

    if thorough:
        # Offline support indicators
        has_offline = False
        for f in ts_files[:30]:
            if file_contains(f, "netinfo") or file_contains(f, "offline") or file_contains(f, "network-state"):
                has_offline = True
                break
        if pkg_json and file_contains(pkg_json, "@react-native-community/netinfo"):
            has_offline = True
        report.add(Finding(
            priority=Priority.P2,
            category=Category.RELIABILITY,
            title="Offline support / network awareness",
            detail="No network status handling found" if not has_offline else "Network awareness implemented",
            passed=has_offline,
        ))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Production Readiness Audit for Prixio LLC services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 readiness_audit.py --app courio-api --level thorough
  python3 readiness_audit.py --app lotify-web --level basic
  python3 readiness_audit.py --app courier-app --level thorough

Supported apps:
  lotify-api, courio-api, lotify-web, courio-admin, courier-app, consumer-app

Environment variables (optional overrides):
  LOTIFY_API_URL, COURIO_API_URL, LOTIFY_WEB_URL, COURIO_ADMIN_URL
  LOTIFY_API_DIR, COURIO_API_DIR, LOTIFY_WEB_DIR, COURIO_ADMIN_DIR
  COURIER_APP_DIR, CONSUMER_APP_DIR
        """,
    )
    parser.add_argument(
        "--app",
        required=True,
        choices=list(APP_CONFIGS.keys()),
        help="Application to audit",
    )
    parser.add_argument(
        "--level",
        default="basic",
        choices=["basic", "thorough"],
        help="Audit depth level (default: basic)",
    )

    args = parser.parse_args()
    config = APP_CONFIGS[args.app]
    thorough = args.level == "thorough"

    report = AuditReport(app=args.app, level=args.level)
    report.start_time = time.time()

    # Verify project directory exists
    if not os.path.isdir(config["project_dir"]):
        print(f"WARNING: Project directory not found: {config['project_dir']}")
        print("Set the appropriate environment variable to override.")
        print("Proceeding with remote-only checks where possible...\n")

    app_type = config["type"]
    if app_type == "fastify":
        audit_fastify(report, config, thorough)
    elif app_type == "nextjs":
        audit_nextjs(report, config, thorough)
    elif app_type == "expo":
        audit_expo(report, config, thorough)
    else:
        print(f"Unknown app type: {app_type}")
        sys.exit(1)

    report.end_time = time.time()
    report.print_report()

    # Exit code: 0 if passing (>= 70), 1 otherwise
    sys.exit(0 if report.score >= 70 else 1)


if __name__ == "__main__":
    main()
