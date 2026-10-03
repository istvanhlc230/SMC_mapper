# Test workspace

This directory is the repository-wide working directory for Python tests.

Development rule:

- The active developer agent creates new test files here.
- Test execution targets this directory.
- No new Python test files should be created in the repository root or in a separate `tests/` directory unless a specification explicitly requires a different location.
- Production source files do not belong here.
