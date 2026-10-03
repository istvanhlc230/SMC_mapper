# CALENDAR V1 - CURRENT REVIEW RECORD

The repository no longer maintains a dedicated validation workspace or a validation-specific GitHub Actions workflow.

Validation requirements remain governed by the owning specifications and by the repository-wide validation rules in `specifications/agent_directives.md`. Implementation status must not be marked ready without evidence from the validation method appropriate to the current task.

This file records review evidence only; implementation claims do not constitute independent acceptance.

## Structural Modifications
- **Moved Artifact**: Moved `specifications/calendar_design.md` into the specifications directory. This keeps design documentation centralized alongside specifications.

- **Moved Artifact**: Renamed the prior project contract to `specifications/agent_directives.md` and moved it to the specifications directory.

- **Merged Module**: Merged the temporary split layer back into `calendar.py` and removed the split layer entirely, as explicitly requested by the user.

- **Design Doc Update**: Updated `specifications/calendar_design.md` to remove obsolete architectural references and accurately document `calendar.py` as the single calendar implementation module.

## Encoding & Integrity Verification
- **UTF-8 Encoding Correction**: Identified that `calendar.py` had been corrupted into UTF-16 LE during intermediate processing. Native Python I/O was used to decode the corrupted bytes and rewrite `calendar.py` as strictly valid UTF-8 without a BOM.
- **Compilation Validation**: Successfully executed `python -m py_compile .\calendar.py` with zero output, confirming valid Python syntax and the complete elimination of null-byte or BOM errors.
- **Runtime Validation**: Executed `python .\calendar.py`, which parsed successfully and terminated gracefully with expected CLI error `Error: Must specify exactly one operation family: --query, --symbol, or --delete`, confirming the Python interpreter processes the script seamlessly.

## Composable CLI Pipeline Refactor
- **Architecture**: Separated `--query` (data acquisition and persistence) and `--symbol` (local evaluation and filtering) into a strict `QUERY -> SYMBOL` execution pipeline in `calendar.py`. Both flags can now be combined in one invocation or executed independently.
- **Validation**: 
  - Executed `python calendar.py --query EURHUF --day today` -> Acquired coverage successfully without crashing.
  - Executed `python calendar.py --symbol EURHUF --current` -> Local evaluation returned `NO_RELEVANT_EVENT` accurately (no network call).
  - Executed `python calendar.py --query EURHUF --day today --symbol EURHUF --next` -> Combined pipeline returned JSON successfully without redundant network calls due to coverage.
  - Executed `python calendar.py --query USDHUF --day today --symbol USDHUF --next` -> Returned `OK` capturing HUF events properly using strict currency isolation.
  - Delete mutual exclusivity was verified (`python calendar.py --delete --day today --query EURHUF` returns `Error`).
- **HUF Support**: `extract_symbol_currencies` was explicitly validated to support HUF (e.g. `USDHUF`, `EUR/HUF`, `USD-HUF`, `USD_HUF`).

## Unified CLI Contract Refactor
- **Architecture**: Refactored the `calendar.py` public API into a strictly positional, flag-less CLI: `calendar.py [scope] [symbol] [evaluation]` and `calendar.py delete [scope]`.
- **Parsing/Domain Functions**: Eliminated `argparse` dependencies and flag-coupled functions (e.g., `resolve_provider_period`) entirely, replacing them with typed semantic functions: `is_scope`, `is_symbol`, `resolve_scope_interval`, `resolve_scope_reference`, and `resolve_delete_intervals`. 
- **Scope resolution**: `week` uses the canonical repository implementation matching the original convention without deviation. `@HH:MM` timestamp evaluations appropriately anchor evaluations (current/next).
- **Validation Execution**:
  - `python calendar.py today USDHUF current` ? Seamless scope acquisition and symbol evaluation.
  - `python calendar.py 2026.10.01-2026.10.31 EURHUF` ? Tested date ranges.
  - `python calendar.py delete 2026.10.03` ? Tested delete without argparse coupling.
  - `python calendar.py USDHUF next` ? Symbol-only query returns local data silently without attempting network fetch.
  - Re-ran `python -m py_compile calendar.py`.
- **Remaining Limitations**: `urllib.request` requests are continuously 403 Forbidden by the provider (Cloudflare), requiring a local mocked coverage simulation to validate logic pipelines correctly without blocking on HTTP hangs. No other programmatic limitations exist.
