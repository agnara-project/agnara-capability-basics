---
name: documentation
description: Standards and synchronization rules for maintaining Agnara capability documentation.
---

# Documentation Skill

Use this skill when reading, authoring, or updating documentation in **Agnara Historical Reference Application #004 (`agnara-capability-basics`)**.

---

## 1. Separation of Responsibilities

Documentation in this repository strictly enforces distinct roles:

- **`README.md`:** Primary entry point for human developers. Explains educational goals, quick start, runnable demonstration, capability tour, and historical context.
- **`AGENTS.md`:** Primary operational manual for AI agents. Defines technical invariants, command palettes, negative constraints, GitFlow rules, and Definition of Done.
- **`ARCHITECTURE.md`:** Architectural deep dive into capability-first design, the two-phase registry lifecycle (ADR 0005), and metadata ontology.
- **`docs/capability-lifecycle.md`:** Specification of declaration, compilation freeze, and registry querying.
- **`docs/public-api-boundary.md`:** Documented catalog of supported vs unsupported APIs in `0.1.0a3`.
- **`CHANGELOG.md`:** Historical release ledger following Keep a Changelog.
- **Code & Docstrings:** Single source of truth for technical domain contracts and parameter semantics.

---

## 2. Synchronization Rules

When modifying capabilities, models, or metadata, ensure complete synchronization across:

1. **Code Contracts:** Update signatures and docstrings in `domain.py` and `catalog.py`.
2. **Pedagogical Walkthrough:** Update `app.py` output steps if observable behavior changes.
3. **Human Documentation:** Update snippets and tables in `README.md` and `docs/`.
4. **Agent Guidance:** Update constraints and API inventories in `AGENTS.md`.
5. **Ledger:** Record notable modifications under `[Unreleased]` in `CHANGELOG.md`.

---

## 3. Style & Integrity Invariants

- **No Placeholder Text:** Never commit `TODO`, `TBD`, or placeholder sections.
- **No Speculative Claims:** Only document features verifiably working in `agnara==0.1.0a3`.
- **No Duplicate Redundancy:** Do not copy whole sections between `README.md` and `AGENTS.md`; reference by markdown links instead.
- **Canonical URLs:**
  - Reference Application: `https://github.com/agnara-project/agnara-capability-basics`
  - Agnara Core: `https://github.com/Blandskron/agnara`