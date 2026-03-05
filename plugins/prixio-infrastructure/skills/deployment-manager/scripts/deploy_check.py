#!/usr/bin/env python3
"""
Pre-deployment validation script for Prixio LLC services.

Validates deployment readiness by checking environment variables, Dockerfile
syntax, health endpoints, git status, and migration state.

Usage:
    python3 deploy_check.py --app lotify-api --env production
    python3 deploy_check.py --app courio-api --env staging --skip-health
    python3 deploy_check.py --app lotify-web --env production --project-root /path/to/repo
"""

import argparse
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


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
    details: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------

APP_CONFIGS = {
    "lotify-api": {
        "type": "fastify",
        "port": 3001,
        "dockerfile": "Dockerfile.fastify",
        "path": "apps/lotify-api",
        "required_env": [
            "DATABASE_URL",
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
            "TBC_PAY_CLIENT_ID",
            "TBC_PAY_CLIENT_SECRET",
            "COURIO_API_URL",
            "COURIO_WEBHOOK_SECRET",
            "REDIS_URL",
        ],
    },
    "lotify-web": {
        "type": "nextjs",
        "port": 3000,
        "dockerfile": "Dockerfile.nextjs",
        "path": "apps/lotify-web",
        "required_env": [
            "NEXT_PUBLIC_SUPABASE_URL",
            "NEXT_PUBLIC_SUPABASE_ANON_KEY",
            "NEXT_PUBLIC_API_URL",
        ],
    },
    "lotify-admin": {
        "type": "nextjs",
        "port": 3000,
        "dockerfile": "Dockerfile.nextjs",
        "path": "apps/lotify-admin",
        "required_env": [
            "NEXT_PUBLIC_SUPABASE_URL",
            "NEXT_PUBLIC_SUPABASE_ANON_KEY",
            "NEXT_PUBLIC_API_URL",
        ],
    },
    "courio-api": {
        "type": "fastify",
        "port": 3001,
        "dockerfile": "Dockerfile.fastify",
        "path": "apps/courio-api",
        "required_env": [
            "DATABASE_URL",
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
            "LOTIFY_WEBHOOK_URL",
            "LOTIFY_WEBHOOK_SECRET",
            "REDIS_URL",
        ],
    },
    "courio-admin": {
        "type": "nextjs",
        "port": 3000,
        "dockerfile": "Dockerfile.nextjs",
        "path": "apps/courio-admin",
        "required_env": [
            "NEXT_PUBLIC_SUPABASE_URL",
            "NEXT_PUBLIC_SUPABASE_ANON_KEY",
            "NEXT_PUBLIC_API_URL",
        ],
    },
}

ENV_SPECIFIC_VARS = {
    "production": ["NODE_ENV"],
    "staging": ["NODE_ENV"],
    "dev": [],
}


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------


def check_env_vars(app_name: str, env: str, project_root: Path) -> CheckResult:
    """Check that all required environment variables are present."""
    config = APP_CONFIGS[app_name]
    required = config["required_env"] + ENV_SPECIFIC_VARS.get(env, [])
    missing = []
    present = []

    # Check current process environment
    for var in required:
        if os.environ.get(var):
            present.append(var)
        else:
            missing.append(var)

    # Also check for .env file existence
    env_file = project_root / config["path"] / ".env"
    env_example = project_root / config["path"] / ".env.example"

    details = []
    if present:
        details.append(f"Present: {', '.join(present)}")
    if missing:
        details.append(f"Missing: {', '.join(missing)}")
    if env_file.exists():
        details.append(f"Found .env file at {env_file}")
        if env == "production":
            details.append("WARNING: .env file should NOT be committed for production")
    if env_example.exists():
        details.append(f"Found .env.example at {env_example}")

    if missing:
        return CheckResult(
            name="Environment Variables",
            status=Status.FAIL,
            message=f"{len(missing)} required variable(s) not set in environment",
            details=details,
        )

    return CheckResult(
        name="Environment Variables",
        status=Status.PASS,
        message=f"All {len(required)} required variables present",
        details=details,
    )


def check_dockerfile(app_name: str, project_root: Path) -> CheckResult:
    """Check that the Dockerfile exists and has valid basic syntax."""
    config = APP_CONFIGS[app_name]
    dockerfile_name = config["dockerfile"]
    details = []

    # Check in project root (monorepo pattern)
    dockerfile_path = project_root / dockerfile_name
    if not dockerfile_path.exists():
        # Also check in app directory
        dockerfile_path = project_root / config["path"] / "Dockerfile"
        if not dockerfile_path.exists():
            return CheckResult(
                name="Dockerfile",
                status=Status.FAIL,
                message=f"Dockerfile not found at {project_root / dockerfile_name} or {project_root / config['path'] / 'Dockerfile'}",
                details=[],
            )

    details.append(f"Found: {dockerfile_path}")

    content = dockerfile_path.read_text()
    lines = content.strip().splitlines()

    # Basic syntax validation
    has_from = False
    has_cmd_or_entrypoint = False
    has_expose = False
    stage_count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        upper = stripped.upper()
        if upper.startswith("FROM "):
            has_from = True
            stage_count += 1
        elif upper.startswith("CMD ") or upper.startswith("ENTRYPOINT "):
            has_cmd_or_entrypoint = True
        elif upper.startswith("EXPOSE "):
            has_expose = True

    issues = []
    if not has_from:
        issues.append("Missing FROM instruction")
    if not has_cmd_or_entrypoint:
        issues.append("Missing CMD or ENTRYPOINT instruction")
    if not has_expose:
        issues.append("Missing EXPOSE instruction (non-critical)")

    details.append(f"Build stages: {stage_count}")
    details.append(f"Total lines: {len(lines)}")

    if issues:
        critical = [i for i in issues if "EXPOSE" not in i]
        if critical:
            return CheckResult(
                name="Dockerfile",
                status=Status.FAIL,
                message=f"Dockerfile has syntax issues: {'; '.join(critical)}",
                details=details + issues,
            )
        return CheckResult(
            name="Dockerfile",
            status=Status.WARN,
            message="Dockerfile valid but has minor issues",
            details=details + issues,
        )

    return CheckResult(
        name="Dockerfile",
        status=Status.PASS,
        message=f"Dockerfile valid ({stage_count} stages, multi-stage: {'yes' if stage_count > 1 else 'no'})",
        details=details,
    )


def check_health_endpoint(app_name: str) -> CheckResult:
    """Check if the health endpoint responds."""
    config = APP_CONFIGS[app_name]
    port = config["port"]
    url = f"http://localhost:{port}/health"

    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.status
            body = response.read().decode("utf-8", errors="replace")

            if status_code == 200:
                return CheckResult(
                    name="Health Endpoint",
                    status=Status.PASS,
                    message=f"GET {url} returned 200",
                    details=[f"Response: {body[:200]}"],
                )
            else:
                return CheckResult(
                    name="Health Endpoint",
                    status=Status.FAIL,
                    message=f"GET {url} returned {status_code}",
                    details=[f"Response: {body[:200]}"],
                )
    except urllib.error.URLError as e:
        return CheckResult(
            name="Health Endpoint",
            status=Status.FAIL,
            message=f"Cannot reach {url}",
            details=[f"Error: {e.reason}"],
        )
    except Exception as e:
        return CheckResult(
            name="Health Endpoint",
            status=Status.FAIL,
            message=f"Cannot reach {url}",
            details=[f"Error: {str(e)}"],
        )


def check_git_status(project_root: Path) -> CheckResult:
    """Check that the git working tree is clean."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return CheckResult(
                name="Git Status",
                status=Status.FAIL,
                message="Failed to run git status",
                details=[result.stderr.strip()],
            )

        output = result.stdout.strip()
        if not output:
            # Also check current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            branch = branch_result.stdout.strip()
            return CheckResult(
                name="Git Status",
                status=Status.PASS,
                message=f"Working tree clean (branch: {branch})",
                details=[],
            )

        changed_files = output.splitlines()
        return CheckResult(
            name="Git Status",
            status=Status.FAIL,
            message=f"{len(changed_files)} uncommitted change(s) detected",
            details=changed_files[:20],  # Show up to 20 files
        )

    except FileNotFoundError:
        return CheckResult(
            name="Git Status",
            status=Status.FAIL,
            message="git is not installed or not in PATH",
            details=[],
        )
    except subprocess.TimeoutExpired:
        return CheckResult(
            name="Git Status",
            status=Status.FAIL,
            message="git status timed out",
            details=[],
        )


def check_migrations(app_name: str, project_root: Path) -> CheckResult:
    """Check that database migrations are up to date."""
    config = APP_CONFIGS[app_name]

    # Only API apps have migrations
    if config["type"] != "fastify":
        return CheckResult(
            name="Migrations",
            status=Status.SKIP,
            message="Not applicable for frontend apps",
            details=[],
        )

    # Check for Supabase migrations directory
    migrations_dir = project_root / config["path"] / "supabase" / "migrations"
    if not migrations_dir.exists():
        # Also check project root
        migrations_dir = project_root / "supabase" / "migrations"

    if not migrations_dir.exists():
        return CheckResult(
            name="Migrations",
            status=Status.WARN,
            message="No migrations directory found",
            details=[
                f"Checked: {project_root / config['path'] / 'supabase' / 'migrations'}",
                f"Checked: {project_root / 'supabase' / 'migrations'}",
            ],
        )

    migration_files = sorted(migrations_dir.glob("*.sql"))
    if not migration_files:
        return CheckResult(
            name="Migrations",
            status=Status.WARN,
            message="Migrations directory exists but contains no .sql files",
            details=[str(migrations_dir)],
        )

    # Check if supabase CLI is available for a proper status check
    try:
        result = subprocess.run(
            ["supabase", "migration", "list"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            # Parse output for pending migrations
            output = result.stdout.strip()
            if "Not applied" in output or "PENDING" in output.upper():
                return CheckResult(
                    name="Migrations",
                    status=Status.FAIL,
                    message="Pending migrations detected",
                    details=output.splitlines()[:10],
                )
            return CheckResult(
                name="Migrations",
                status=Status.PASS,
                message=f"All {len(migration_files)} migration(s) applied",
                details=[f"Latest: {migration_files[-1].name}"],
            )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: just report migration file count
    return CheckResult(
        name="Migrations",
        status=Status.WARN,
        message=f"Found {len(migration_files)} migration file(s), but cannot verify applied status (supabase CLI not available)",
        details=[f"Latest: {migration_files[-1].name}"],
    )


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

COLORS = {
    Status.PASS: "\033[92m",  # Green
    Status.FAIL: "\033[91m",  # Red
    Status.WARN: "\033[93m",  # Yellow
    Status.SKIP: "\033[90m",  # Gray
}
RESET = "\033[0m"
BOLD = "\033[1m"


def print_result(result: CheckResult, use_color: bool = True) -> None:
    if use_color:
        color = COLORS[result.status]
        print(f"  {color}[{result.status.value:4s}]{RESET} {BOLD}{result.name}{RESET}: {result.message}")
    else:
        print(f"  [{result.status.value:4s}] {result.name}: {result.message}")

    for detail in result.details:
        prefix = "       "
        print(f"{prefix}{detail}")


def print_summary(results: list[CheckResult], app_name: str, env: str, use_color: bool = True) -> bool:
    passed = sum(1 for r in results if r.status == Status.PASS)
    failed = sum(1 for r in results if r.status == Status.FAIL)
    warned = sum(1 for r in results if r.status == Status.WARN)
    skipped = sum(1 for r in results if r.status == Status.SKIP)

    print()
    print(f"{'=' * 60}")
    print(f"  Deployment Readiness: {app_name} ({env})")
    print(f"{'=' * 60}")
    print()

    for result in results:
        print_result(result, use_color)
        print()

    print(f"{'─' * 60}")
    summary = f"  {passed} passed, {failed} failed, {warned} warnings, {skipped} skipped"

    if failed > 0:
        if use_color:
            print(f"  {COLORS[Status.FAIL]}RESULT: NOT READY FOR DEPLOYMENT{RESET}")
        else:
            print("  RESULT: NOT READY FOR DEPLOYMENT")
    else:
        if use_color:
            print(f"  {COLORS[Status.PASS]}RESULT: READY FOR DEPLOYMENT{RESET}")
        else:
            print("  RESULT: READY FOR DEPLOYMENT")

    print(summary)
    print(f"{'─' * 60}")
    print()

    return failed == 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate deployment readiness for Prixio services.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 deploy_check.py --app lotify-api --env production
  python3 deploy_check.py --app courio-api --env staging --skip-health
  python3 deploy_check.py --app lotify-web --env production --project-root /path/to/repo
        """,
    )
    parser.add_argument(
        "--app",
        required=True,
        choices=list(APP_CONFIGS.keys()),
        help="Application to validate",
    )
    parser.add_argument(
        "--env",
        required=True,
        choices=["dev", "staging", "production"],
        help="Target deployment environment",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Path to the monorepo root (defaults to current git repo root)",
    )
    parser.add_argument(
        "--skip-health",
        action="store_true",
        help="Skip health endpoint check (useful when service is not running locally)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    # Determine project root
    project_root = args.project_root
    if project_root is None:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                project_root = Path(result.stdout.strip())
            else:
                project_root = Path.cwd()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            project_root = Path.cwd()

    # Run checks
    results: list[CheckResult] = []

    results.append(check_env_vars(args.app, args.env, project_root))
    results.append(check_dockerfile(args.app, project_root))

    if args.skip_health:
        results.append(CheckResult(
            name="Health Endpoint",
            status=Status.SKIP,
            message="Skipped (--skip-health flag)",
            details=[],
        ))
    else:
        results.append(check_health_endpoint(args.app))

    results.append(check_git_status(project_root))
    results.append(check_migrations(args.app, project_root))

    # Output
    if args.json_output:
        output = {
            "app": args.app,
            "env": args.env,
            "project_root": str(project_root),
            "checks": [
                {
                    "name": r.name,
                    "status": r.status.value,
                    "message": r.message,
                    "details": r.details,
                }
                for r in results
            ],
            "ready": all(r.status != Status.FAIL for r in results),
        }
        print(json.dumps(output, indent=2))
        return 0 if output["ready"] else 1

    use_color = not args.no_color and sys.stdout.isatty()
    ready = print_summary(results, args.app, args.env, use_color)

    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
