from genie_flow_invoker.invoker.ms_sql_server import (
    MSSQLServerRetrieveInvoker,
    MSSQLServerStoreInvoker,
    MSSQLServerQueryInvoker,
)


def test_retrieve_invoker_env_vars(monkeypatch):
    monkeypatch.setenv("MS_SQL_SERVER", "patched-localhost")
    monkeypatch.setenv("MS_SQL_SERVER_USERNAME", "patched-username")
    monkeypatch.setenv("MS_SQL_SERVER_PASSWORD", "patched-password")
    monkeypatch.setenv("MS_SQL_SERVER_DATABASE", "patched-database")
    monkeypatch.setenv("MS_SQL_SERVER_TABLE", "patched-table")

    retriever = MSSQLServerRetrieveInvoker.from_config(dict())

    assert retriever.base_config["server"] == "patched-localhost"
    assert retriever.base_config["username"] == "patched-username"
    assert retriever.base_config["password"] == "patched-password"
    assert retriever.base_config["database"] == "patched-database"
    assert retriever.base_config["table"] == "patched-table"
    assert retriever.base_config["top"] is None
    assert retriever.base_config["sort_order"] is None


def test_retrieve_invoker_mix(monkeypatch):
    monkeypatch.setenv("MS_SQL_SERVER", "patched-localhost")
    monkeypatch.setenv("MS_SQL_SERVER_USERNAME", "patched-username")
    monkeypatch.setenv("MS_SQL_SERVER_PASSWORD", "patched-password")
    monkeypatch.setenv("MS_SQL_SERVER_DATABASE", "patched-database")

    retriever = MSSQLServerRetrieveInvoker.from_config(
        dict(table="set-table", top=25, sort_order=["-aap", "noot"])
    )

    assert retriever.base_config["server"] == "patched-localhost"
    assert retriever.base_config["username"] == "patched-username"
    assert retriever.base_config["password"] == "patched-password"
    assert retriever.base_config["database"] == "patched-database"
    assert retriever.base_config["table"] == "set-table"
    assert retriever.base_config["top"] == 25
    assert retriever.base_config["sort_order"] == ["-aap", "noot"]


class MSQSQLServerStoreInvoker:
    pass


def test_store_invoker_env_vars(monkeypatch):
    monkeypatch.setenv("MS_SQL_SERVER", "patched-localhost")
    monkeypatch.setenv("MS_SQL_SERVER_USERNAME", "patched-username")
    monkeypatch.setenv("MS_SQL_SERVER_PASSWORD", "patched-password")
    monkeypatch.setenv("MS_SQL_SERVER_DATABASE", "patched-database")
    monkeypatch.setenv("MS_SQL_SERVER_TABLE", "patched-table")

    storer = MSSQLServerStoreInvoker.from_config(dict())

    assert storer.base_config["server"] == "patched-localhost"
    assert storer.base_config["username"] == "patched-username"
    assert storer.base_config["password"] == "patched-password"
    assert storer.base_config["database"] == "patched-database"
    assert storer.base_config["table"] == "patched-table"


def test_store_invoker_mix(monkeypatch):
    monkeypatch.setenv("MS_SQL_SERVER", "patched-localhost")
    monkeypatch.setenv("MS_SQL_SERVER_USERNAME", "patched-username")
    monkeypatch.setenv("MS_SQL_SERVER_PASSWORD", "patched-password")
    monkeypatch.setenv("MS_SQL_SERVER_DATABASE", "patched-database")

    storer = MSSQLServerStoreInvoker.from_config(
        dict(
            table="set-table",
            strategy="upsert",
            primary_key=["aap", "noot"],
        )
    )

    assert storer.base_config["server"] == "patched-localhost"
    assert storer.base_config["username"] == "patched-username"
    assert storer.base_config["password"] == "patched-password"
    assert storer.base_config["database"] == "patched-database"
    assert storer.base_config["table"] == "set-table"
    assert storer.base_config["strategy"] == "upsert"
    assert storer.base_config["primary_key"] == ["aap", "noot"]


def test_query_invoker_env_vars(monkeypatch):
    monkeypatch.setenv("MS_SQL_SERVER", "patched-localhost")
    monkeypatch.setenv("MS_SQL_SERVER_USERNAME", "patched-username")
    monkeypatch.setenv("MS_SQL_SERVER_PASSWORD", "patched-password")
    monkeypatch.setenv("MS_SQL_SERVER_DATABASE", "patched-database")

    querier = MSSQLServerQueryInvoker.from_config(dict())

    assert querier.base_config["server"] == "patched-localhost"
    assert querier.base_config["username"] == "patched-username"
    assert querier.base_config["password"] == "patched-password"
    assert querier.base_config["database"] == "patched-database"
