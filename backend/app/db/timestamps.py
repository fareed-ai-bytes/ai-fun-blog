from datetime import UTC, datetime


def utcnow() -> datetime:
    """Python-side timestamp (distinct per call, unlike Postgres now() within a transaction)."""
    return datetime.now(UTC)
