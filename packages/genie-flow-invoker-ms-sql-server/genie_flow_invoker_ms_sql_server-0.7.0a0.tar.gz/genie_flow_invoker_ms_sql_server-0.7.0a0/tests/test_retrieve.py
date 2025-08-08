import pymssql

from conftest import MockMSSQLCursor, MockMSSQLConnection
from genie_flow_invoker.invoker.ms_sql_server.retrieve import Retriever


def test_retrieve_table_not_found(monkeypatch):

    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(
            exception=pymssql.OperationalError("table not found"),
        )
        return MockMSSQLConnection(cursor)

    monkeypatch.setattr(pymssql, "connect", connect)
    retriever = Retriever(
        "localhost",
        "some-user",
        "some-pass",
        "some-database",
        "tesy",
    )
    results = retriever.retrieve()

    assert results.error == "error OperationalError: ('table not found',)"
    assert results.results == []


def test_retrieve_all(monkeypatch):
    expected_results = [dict(aap=1, noot=2), dict(aap=3, noot=4)]

    def connect(*arg, **kwargs):
        cursor = MockMSSQLCursor(
            results={
                "SELECT * FROM tesy;": expected_results,
            }
        )
        return MockMSSQLConnection(cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    retriever = Retriever(
        "localhost",
        "some-user",
        "some-pass",
        "some-database",
        "tesy",
    )
    results = retriever.retrieve()

    assert results.error is None
    assert results.results == expected_results


def test_retrieve_top(monkeypatch):
    expected_results = [dict(aap=1, noot=2), dict(aap=3, noot=4)]

    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(
            results={
                "SELECT TOP 2 * FROM tesy;": expected_results,
            }
        )
        return MockMSSQLConnection(cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    retriever = Retriever(
        "localhost",
        "some-user",
        "some-pass",
        "some-database",
        "tesy",
        top=2,
    )
    results = retriever.retrieve()

    assert results.error is None
    assert results.results == expected_results


def test_retrieve_order(monkeypatch):
    expected_results = [dict(aap=1, noot=2), dict(aap=3, noot=4)]

    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(
            results={
                "SELECT * FROM tesy ORDER BY aap, noot DESC;": expected_results,
            }
        )
        return MockMSSQLConnection(cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    retriever = Retriever(
        "localhost",
        "some-user",
        "some-pass",
        "some-database",
        "tesy",
        sort_order=["aap", "-noot"],
    )
    results = retriever.retrieve()

    assert results.error is None
    assert results.results == expected_results


def test_retrieve_top_and_order(monkeypatch):
    expected_results = [dict(aap=1, noot=2), dict(aap=3, noot=4)]

    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(
            results={
                "SELECT TOP 2 * FROM tesy ORDER BY aap;": expected_results,
            }
        )
        return MockMSSQLConnection(cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    retriever = Retriever(
        "localhost",
        "some-user",
        "some-pass",
        "some-database",
        "tesy",
        top=2,
        sort_order=["aap"],
    )
    results = retriever.retrieve()

    assert results.error is None
    assert results.results == expected_results
