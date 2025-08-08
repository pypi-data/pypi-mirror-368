import os

import pytest
from pytest import fixture
import pymssql

from genie_flow_invoker.invoker.ms_sql_server.query import Querier
from genie_flow_invoker.invoker.ms_sql_server.retrieve import Retriever
from genie_flow_invoker.invoker.ms_sql_server.store import Storer


if os.environ.get("SKIP_SQL_SERVER_TESTS") == "true":
    # We seem to have an issue with running these tests on the Gitlab Runner
    pytest.skip("Skipping SQLServer tests", allow_module_level=True)


@fixture(scope="function")
def connection(sql_server_details):
    connection = pymssql.connect(*sql_server_details)

    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS tesy")
    connection.commit()

    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE tesy (aap int, noot varchar(64))")
    connection.commit()

    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO tesy VALUES (1, 'wim'), (2, 'zus'), (3, 'jet')")
    connection.commit()

    yield connection

    connection.close()


def test_sqlserver_retrieve(sql_server_details, connection):
    retriever = Retriever(*sql_server_details, table="tesy")
    results = retriever.retrieve()

    assert results.results == [
        dict(aap=1, noot="wim"),
        dict(aap=2, noot="zus"),
        dict(aap=3, noot="jet"),
    ]
    assert results.error is None


def test_sqlserver_retrieve_missing_table(sql_server_details, connection):
    retriever = Retriever(*sql_server_details, table="non_existent")
    results = retriever.retrieve()

    assert results.error is not None


def test_sqlserver_retrieve_ordered(sql_server_details, connection):
    retriever = Retriever(*sql_server_details, table="tesy", sort_order=["-aap"])
    results = retriever.retrieve()

    assert results.error is None
    assert results.results == [
        dict(aap=3, noot="jet"),
        dict(aap=2, noot="zus"),
        dict(aap=1, noot="wim"),
    ]


def test_sqlserver_store(sql_server_details, connection):
    storer = Storer(*sql_server_details, table="tesy")
    results = storer.store([dict(aap=10, noot="vuur")])

    with connection.cursor(as_dict=True) as cursor:
        cursor.execute("SELECT * FROM tesy WHERE aap = 10")
        vuur = cursor.fetchall()

    assert results == ["inserted"]
    assert vuur == [dict(aap=10, noot="vuur")]


def test_sqlserver_update(sql_server_details, connection):
    storer = Storer(
        *sql_server_details,
        table="tesy",
        strategy="update",
        primary_key=["aap"],
    )
    results = storer.store([dict(aap=1, noot="vuur")])

    with connection.cursor(as_dict=True) as cursor:
        cursor.execute("SELECT * FROM tesy WHERE aap = 1")
        vuur = cursor.fetchall()

    assert results == ["updated"]
    assert vuur == [dict(aap=1, noot="vuur")]


def test_sqlserver_upsert(sql_server_details, connection):
    storer = Storer(
        *sql_server_details,
        table="tesy",
        strategy="upsert",
        primary_key=["aap"],
    )
    results = storer.store([dict(aap=1, noot="vuur"), dict(aap=10, noot="vuur")])

    with connection.cursor(as_dict=True) as cursor:
        cursor.execute("SELECT * FROM tesy WHERE noot = 'vuur'")
        vuur = cursor.fetchall()

    assert results == ["updated", "inserted"]
    assert vuur == [dict(aap=1, noot="vuur"), dict(aap=10, noot="vuur")]


def test_sqlserver_query(sql_server_details, connection):
    querier = Querier(*sql_server_details)
    results = querier.query("SELECT MAX(aap) AS max_aap FROM tesy;")

    assert results.error is None
    assert results.results == [dict(max_aap=3)]
