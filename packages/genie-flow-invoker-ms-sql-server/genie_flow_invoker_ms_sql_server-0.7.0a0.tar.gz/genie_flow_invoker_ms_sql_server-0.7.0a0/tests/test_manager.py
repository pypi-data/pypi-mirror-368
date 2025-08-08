import pymssql.exceptions
import pytest

from genie_flow_invoker.invoker.ms_sql_server.manager import MSSQLServerManagerFactory
from conftest import MockMSSQLConnection


def test_connection_fails(monkeypatch):

    def connect(*args, **kwargs):
        raise pymssql.exceptions.DatabaseError("Failed to connect")

    monkeypatch.setattr(pymssql, "connect", connect)

    factory = MSSQLServerManagerFactory(
        "localhost",
        "sa",
        "FakePassword",
        "some_database",
    )
    with pytest.raises(pymssql.exceptions.DatabaseError) as excinfo:
        with factory.create_manager():
            ...

    assert "Failed to connect" in str(excinfo.value)


def test_connection_closes(monkeypatch):

    def connect(*args, **kwargs):
        return MockMSSQLConnection()

    monkeypatch.setattr(pymssql, "connect", connect)

    factory = MSSQLServerManagerFactory(
        "localhost",
        "sa",
        "FakePassword",
        "some_database",
    )
    with factory.create_manager() as connection:
        assert connection.open

    assert not connection.open
