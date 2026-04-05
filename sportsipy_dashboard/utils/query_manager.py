"""Manage saved queries using a local JSON file store."""
import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

QUERIES_FILE = Path.home() / ".sportsipy_dashboard" / "queries.json"


@dataclass
class SavedQuery:
    """A saved query configuration."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    sport: str = ""
    season: Optional[int] = None
    filters: list[dict] = field(default_factory=list)
    columns: list[str] = field(default_factory=list)
    sort_by: list[dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    code_actions: list[dict] = field(default_factory=list)


class QueryManager:
    """Manages saving, loading, and deleting queries from a local JSON store."""

    def __init__(self, queries_file: Path = QUERIES_FILE) -> None:
        """Initialize the QueryManager.

        Args:
            queries_file: Path to the JSON file used for persistence.
        """
        self.queries_file = queries_file
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Create the storage directory and file if they don't exist."""
        self.queries_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.queries_file.exists():
            self.queries_file.write_text(json.dumps([]))
            logger.debug("Created new queries store at %s", self.queries_file)

    def _read_all(self) -> list[dict]:
        """Read raw query dicts from disk."""
        try:
            return json.loads(self.queries_file.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to read queries file: %s", exc)
            return []

    def _write_all(self, queries: list[dict]) -> None:
        """Write raw query dicts to disk."""
        self.queries_file.write_text(json.dumps(queries, indent=2))

    def save_query(self, query: SavedQuery) -> SavedQuery:
        """Persist a new query.

        Args:
            query: SavedQuery to store.

        Returns:
            The saved query (with populated id/timestamps).
        """
        queries = self._read_all()
        queries.append(asdict(query))
        self._write_all(queries)
        logger.info("Saved query '%s' (id=%s)", query.name, query.id)
        return query

    def load_queries(self) -> list[SavedQuery]:
        """Load all saved queries.

        Returns:
            List of SavedQuery objects.
        """
        raw = self._read_all()
        result = []
        for item in raw:
            try:
                result.append(SavedQuery(**item))
            except TypeError as exc:
                logger.warning("Skipping malformed query record: %s", exc)
        return result

    def get_query(self, query_id: str) -> Optional[SavedQuery]:
        """Retrieve a single query by ID.

        Args:
            query_id: The UUID string of the query.

        Returns:
            SavedQuery if found, else None.
        """
        for q in self.load_queries():
            if q.id == query_id:
                return q
        return None

    def delete_query(self, query_id: str) -> bool:
        """Delete a query by ID.

        Args:
            query_id: The UUID string of the query to delete.

        Returns:
            True if deleted, False if not found.
        """
        queries = self._read_all()
        original_len = len(queries)
        queries = [q for q in queries if q.get("id") != query_id]
        if len(queries) == original_len:
            logger.debug("Query id=%s not found for deletion", query_id)
            return False
        self._write_all(queries)
        logger.info("Deleted query id=%s", query_id)
        return True

    def update_query(self, query: SavedQuery) -> SavedQuery:
        """Update an existing query.

        Args:
            query: SavedQuery with updated fields (matched by id).

        Returns:
            The updated query.
        """
        query.updated_at = datetime.now().isoformat()
        queries = self._read_all()
        updated = False
        for i, q in enumerate(queries):
            if q.get("id") == query.id:
                queries[i] = asdict(query)
                updated = True
                break
        if not updated:
            logger.warning("Query id=%s not found for update; appending instead", query.id)
            queries.append(asdict(query))
        self._write_all(queries)
        logger.info("Updated query '%s' (id=%s)", query.name, query.id)
        return query
