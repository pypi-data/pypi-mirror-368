import pymssql

from conftest import MockMSSQLCursor, MockMSSQLConnection
from genie_flow_invoker.invoker.ms_sql_server.query import Querier


def test_syntax_error(monkeypatch):

    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(
            exception=pymssql.OperationalError("Syntax Error"),
        )
        return MockMSSQLConnection(cursor=cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    querier = Querier(
        "localhost",
        "some-user",
        "some-password",
        "some-database",
    )
    results = querier.query("SELECT AND INSERT SOME STUFF")

    assert results.results == []
    assert results.error == "error OperationalError: ('Syntax Error',)"


def test_no_results(monkeypatch):

    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(results={"SELECT * FROM tesy;": []})
        return MockMSSQLConnection(cursor=cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    querier = Querier(
        "localhost",
        "some-user",
        "some-password",
        "some-database",
    )
    results = querier.query("SELECT * FROM tesy;")

    assert results.results == []
    assert results.error is None


def test_query(monkeypatch):

    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(
            results={"SELECT * FROM tesy;": [dict(aap=10, noot=20)]}
        )
        return MockMSSQLConnection(cursor=cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    querier = Querier(
        "localhost",
        "some-user",
        "some-password",
        "some-database",
    )
    results = querier.query("SELECT * FROM tesy;")

    assert results.results == [dict(aap=10, noot=20)]
    assert results.error is None


def test_insert(monkeypatch):
    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(
            results={"INSERT INTO tesy (aap, noot) VALUES (10, 20);": []}
        )
        return MockMSSQLConnection(cursor=cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    querier = Querier(
        "localhost",
        "some-user",
        "some-password",
        "some-database",
    )
    results = querier.query("INSERT INTO tesy (aap, noot) VALUES (10, 20);")
    assert results.results == []
