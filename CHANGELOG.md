# Changelog

All notable changes to `agnara-capability-basics` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-06

### Added
- Initial release of **Agnara Historical Reference Application #004: `agnara-capability-basics`**.
- Pinned to `agnara==0.1.0a3` on CPython >= 3.14.
- Core domain model for product catalog in `domain.py` (`Product`, `PriceBreakdown`, `InventoryStatus`).
- Four reference capabilities in `catalog.py`:
  - `get_product`: Single lookup with docstring description fallback and input validation.
  - `list_products`: Collection query with explicit name decoupling and optional filters.
  - `calculate_price`: Multi-parameter domain calculation with structured breakdown and business rules.
  - `check_warehouse_availability`: Asynchronous capability with non-blocking I/O simulation.
- Standalone interactive educational demonstration script in `app.py`.
- Comprehensive unit test suite in `tests/` covering execution, metadata, compilation, and error handling.
- Full architectural documentation in `ARCHITECTURE.md` and agent guidance in `AGENTS.md`.
- Educational documentation in `docs/` (`capability-lifecycle.md`, `public-api-boundary.md`) and agent-first skills in `.agents/skills/` (`agnara-capabilities`, `documentation`, `testing`).
- GitHub Actions continuous integration workflow and repository governance templates.