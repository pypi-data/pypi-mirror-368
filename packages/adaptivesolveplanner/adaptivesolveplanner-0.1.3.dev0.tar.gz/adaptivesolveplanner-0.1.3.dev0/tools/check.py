import subprocess
import sys

def main() -> None:
    """Run lint, type-check, and tests in one command."""
    cmds = [
        ["ruff", "check", "."],
        ["mypy", "adaptive_solve_planner"],
        ["pytest"],
    ]
    for cmd in cmds:
        print(f"\n>> Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            sys.exit(result.returncode)

if __name__ == "__main__":
    main()
