"""Tests for query_manager module."""
import pytest
from pathlib import Path
from sportsipy_dashboard.utils.query_manager import QueryManager, SavedQuery


@pytest.fixture
def tmp_queries_file(tmp_path):
    return tmp_path / "queries.json"


@pytest.fixture
def qm(tmp_queries_file):
    return QueryManager(queries_file=tmp_queries_file)


def test_save_and_load(qm):
    q = SavedQuery(name="Test Query", sport="mlb", season=2023)
    qm.save_query(q)
    queries = qm.load_queries()
    assert len(queries) == 1
    assert queries[0].name == "Test Query"


def test_get_query(qm):
    q = SavedQuery(name="My Query", sport="nba")
    qm.save_query(q)
    result = qm.get_query(q.id)
    assert result is not None
    assert result.name == "My Query"


def test_delete_query(qm):
    q = SavedQuery(name="To Delete", sport="nfl")
    qm.save_query(q)
    deleted = qm.delete_query(q.id)
    assert deleted is True
    assert qm.get_query(q.id) is None


def test_delete_nonexistent(qm):
    assert qm.delete_query("nonexistent-id") is False


def test_update_query(qm):
    q = SavedQuery(name="Original", sport="nhl")
    qm.save_query(q)
    q.name = "Updated"
    qm.update_query(q)
    result = qm.get_query(q.id)
    assert result.name == "Updated"


def test_multiple_queries(qm):
    for i in range(5):
        qm.save_query(SavedQuery(name=f"Query {i}", sport="mlb"))
    queries = qm.load_queries()
    assert len(queries) == 5


def test_empty_storage(qm):
    queries = qm.load_queries()
    assert queries == []
