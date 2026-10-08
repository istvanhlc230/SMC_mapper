"""Root Market Data CLI entry point."""
from __future__ import annotations
from MARKET_DATA.cli import main as _cli_main

def main(argv=None) -> int:
    """Delegate CLI parsing and execution to the Market Data package."""
    return _cli_main(argv)

if __name__ == "__main__":
    raise SystemExit(main())
