"""
Agents (Orchestrators)
======================

Orchestrators coordinate multiple Skills to accomplish higher-level business operations.

Constraints (from Constitution & ADR-001):
- ❌ NO FastAPI imports
- ❌ NO HTTP request/response handling
- ✅ ONLY: Skills, domain models, primitives
- ✅ Coordinate multiple skills
- ✅ Must be testable WITHOUT FastAPI
"""
