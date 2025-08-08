import json

import pymssql

from conftest import MockMSSQLCursor, MockMSSQLConnection
from genie_flow_invoker.invoker.ms_sql_server.store import Storer


def test_store_table_not_found(monkeypatch):

    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(
            exception=pymssql.OperationalError("Table not found"),
        )
        return MockMSSQLConnection(cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    storer = Storer(
        "localhost",
        "some-user",
        "some-pass",
        "some-database",
        "tesy",
        "insert",
    )
    result = storer.store([dict(aap=1)])

    assert result == ["error OperationalError: ('Table not found',)"]


def test_store_insert(monkeypatch):

    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(
            results={
                (
                    "INSERT INTO tesy (aap, noot) VALUES (%s, %s);",
                    json.dumps([(i, 10 * i)]),
                ): "inserted"
                for i in range(1, 3)
            }
        )
        return MockMSSQLConnection(cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    storer = Storer(
        "localhost",
        "some-user",
        "some-pass",
        "some-database",
        "tesy",
        "insert",
    )
    result = storer.store([dict(aap=1, noot=10), dict(aap=2, noot=20)])

    assert result == ["inserted", "inserted"]


def test_store_update(monkeypatch):

    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(
            results={
                "UPDATE tesy SET mies = 10 WHERE aap = 'noot';": ["updated"],
            },
            missing={
                "UPDATE tesy SET mies = 20 WHERE aap = 'wim';": ["missing"],
            },
        )
        return MockMSSQLConnection(cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    storer = Storer(
        "localhost",
        "some-user",
        "some-pass",
        "some-database",
        "tesy",
        "update",
        ["aap"],
    )
    result = storer.store([dict(aap="noot", mies=10), dict(aap="wim", mies=20)])

    assert result == ["updated", "missing"]


def test_store_update_missing_keys(monkeypatch):

    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(results={})
        return MockMSSQLConnection(cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    storer = Storer(
        "localhost",
        "some-user",
        "some-pass",
        "some-database",
        "tesy",
        "update",
        primary_key=["aap", "noot"],
    )
    result = storer.store([dict(wim=10)])

    assert result == ["warning: missing primary key columns: aap, noot"]


def test_store_update_multi(monkeypatch):

    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(
            results={
                "UPDATE tesy SET mies = 10 WHERE aap = 'noot';": ["updated", "updated"],
            }
        )
        return MockMSSQLConnection(cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    storer = Storer(
        "localhost",
        "some-user",
        "some-pass",
        "some-database",
        "tesy",
        "update",
        primary_key=["aap"],
    )
    result = storer.store([dict(aap="noot", mies=10)])

    assert result == ["warning: updated 2 records"]


def test_store_upsert(monkeypatch):

    def connect(*args, **kwargs):
        cursor = MockMSSQLCursor(
            results={
                "UPDATE tesy SET mies = 10 WHERE aap = 'noot';": ["updated"],
                (
                    "INSERT INTO tesy (aap, mies) VALUES (%s, %s);",
                    json.dumps([("wim", 20)]),
                ): ["inserted"],
            }
        )
        return MockMSSQLConnection(cursor)

    monkeypatch.setattr(pymssql, "connect", connect)

    storer = Storer(
        "localhost",
        "some-user",
        "some-pass",
        "some-database",
        "tesy",
        "upsert",
        primary_key=["aap"],
    )
    result = storer.store([dict(aap="noot", mies=10), dict(aap="wim", mies=20)])

    assert result == ["updated", "inserted"]
