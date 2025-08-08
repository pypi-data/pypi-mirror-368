import json
from abc import ABC
from typing import Optional

from genie_flow_invoker.genie import GenieInvoker
from genie_flow_invoker.invoker.ms_sql_server.query import Querier
from genie_flow_invoker.invoker.ms_sql_server.retrieve import Retriever
from genie_flow_invoker.invoker.ms_sql_server.store import StoreStrategyType, Storer
from genie_flow_invoker.utils import get_config_value


class AbstractMSSQLServerInvoker(GenieInvoker, ABC):

    def __init__(
            self,
            server: str,
            username: str,
            password: str,
            database: str,
    ):
        """
        An abstract base class to store basic properties used in all subsequent MS SQL invokers.

        :param server: the host name of the server
        :param username: the username to use for login
        :param password: the password to use for login
        :param database: the database to use
        """

        self.base_config = dict(
            server=server,
            username=username,
            password=password,
            database=database,
        )

    @classmethod
    def _get_operator_config(cls, config: dict) -> dict:
        """
        Creates a new instance with the relevant parameters. All parameters are read from
        the configuration. The following parameters are also read from environment variables,
        where the environment variable takes precedence.

        - server MS_SQL_SERVER
        - username MS_SQL_SERVER_USERNAME
        - password MS_SQL_SERVER_PASSWORD
        - database MS_SQL_SERVER_DATABASE

        :param config: the configuration dictionary
        :return: a new instance with the relevant parameters
        """
        return dict(
            server=get_config_value(
                config,
                "MS_SQL_SERVER",
                "server",
                "SQL Server hostname",
            ),
            username=get_config_value(
                config,
                "MS_SQL_SERVER_USERNAME",
                "username",
                "SQL Server username",
            ),
            password=get_config_value(
                config,
                "MS_SQL_SERVER_PASSWORD",
                "password",
                "SQL Server password",
            ),
            database = get_config_value(
                config,
                "MS_SQL_SERVER_DATABASE",
                "database",
                "SQL Server database name",
            ),
        )

    def compile_config(self, content: str) -> dict:
        """
        Compiles the ultimate configuration into a dictionary. Precedence of configuration
        parameters is as follows:
        1. any parameter specified in the content passed to the invoker
        2. any parameter that is specified through an environment variable
        3. any parameter that is specified in the `meta.yaml` file

        :param content: the content that is passed to the invoker
        :return: a dictionary with the ultimate valued for the relevant parameters
        """
        try:
            override_config = json.loads(content)
        except json.decoder.JSONDecodeError:
            override_config = {}

        config = self.base_config.copy()
        config.update(override_config)
        return config


class AbstractMSSQLServerWithTableInvoker(AbstractMSSQLServerInvoker, ABC):

    def __init__(
            self,
            server: str,
            username: str,
            password: str,
            database: str,
            table: str,
    ):
        """
        An abstract base class to store basic properties used in all subsequent MS SQL invokers
        that refer to a table.

        :param server: the host name of the server
        :param username: the username to use for login
        :param password: the password to use for login
        :param database: the database to use
        :param table: the name of the table to retrieve data from
        """
        super().__init__(server, username, password, database)
        self.base_config["table"] = table

    @classmethod
    def _get_operator_config(cls, config: dict) -> dict:
        result = super()._get_operator_config(config)
        result["table"] = get_config_value(
            config,
            "MS_SQL_SERVER_TABLE",
            "table",
            "SQL Server table name",
        )
        return result


class MSSQLServerRetrieveInvoker(AbstractMSSQLServerWithTableInvoker):

    def __init__(
            self,
            server: str,
            username: str,
            password: str,
            database: str,
            table: str,
            top: Optional[int] = None,
            sort_order: Optional[list[str]] = None,
    ):
        """
        Invoker for retrieving data from an MSSQL server table.

        If `top` is specified, a maximum of `top` records will be returned.

        If `sort_order` is specified, the retrieved records will be sorted. That parameter
        should be a list of column names, in descending order of precedence. Putting a minus
        sign in front of the column name will do a descending order for that column.

        :param server: the host name of the server
        :param username: the username to use for login
        :param password: the password to use for login
        :param database: the database to use
        :param table: the name of the table to retrieve data from
        :param top: the maximum number of records to return
        :param sort_order: the column names to sort by
        """
        super().__init__(server, username, password, database, table)
        self.base_config["top"] = top
        self.base_config["sort_order"] = sort_order


    @classmethod
    def from_config(cls, config: dict):
        """
        Creates a new instance with the relevant parameters. All parameters are read from the
        configuration. The following parameters are also used from environment variables:
        - server MS_SQL_SERVER
        - username MS_SQL_SERVER_USERNAME
        - password MS_SQL_SERVER_PASSWORD
        - database MS_SQL_SERVER_DATABASE
        - table MS_SQL_SERVER_TABLE

        :param config: a dictionary with configuration parameters
        :return: a new instance with the relevant parameters
        """
        operator_config = cls._get_operator_config(config)
        operator_config["top"]=config.get("top", None)
        operator_config["sort_order"]=config.get("sort_order", None)
        return cls(**operator_config)

    def invoke(self, content: str) -> str:
        """
        Invoke the retrieval. All parameters can be overriden in the content by specifying
        a JSON string that gives a new value to a configuration parameter.

        :param content: potentially a JSON string with overriding values
        :return: a JSON version of the retrieved records
        """
        config = self.compile_config(content)
        retriever = Retriever(**config)
        result = retriever.retrieve()

        return result.model_dump_json()


class MSSQLServerStoreInvoker(AbstractMSSQLServerWithTableInvoker):

    def __init__(
            self,
            server: str,
            username: str,
            password: str,
            database: str,
            table: str,
            strategy: StoreStrategyType = "insert",
            primary_key: list[str] = None,
    ):
        """
        An Invoker that can store data into a table, using different strategies.

        Specifying the storage strategy as "insert" (the default), "update" or "upsert". The
        first just adds the records, the second one updates existing records, the third one
        updates existing records but adds records when they do not yet exist.

        For the "update" and "upsert" strategies to work, a primary key must be provided.

        The primary key is specified as a list of column names.

        :param server: the host name of the server
        :param username: the username to use for login
        :param password: the password to use for login
        :param database: the database to use
        :param table: the name of the table to store data into
        :param strategy: the strategy to use ("insert", "update", "upsert")
        :param primary_key: the list of columns that make up the primary key
        """
        super().__init__(server, username, password, database, table)
        self.base_config["strategy"] = strategy
        self.base_config["primary_key"] = primary_key

    @classmethod
    def from_config(cls, config: dict):
        """
        Creates a new instance with the relevant parameters. All parameters are read from the
        configuration. The following parameters will also be read from environment variables,
        where the value specified in the environment variable takes precedence.

        - server MS_SQL_SERVER
        - username MS_SQL_SERVER_USERNAME
        - password MS_SQL_SERVER_PASSWORD
        - database MS_SQL_SERVER_DATABASE
        - table MS_SQL_SERVER_TABLE

        :param config: a dictionary with configuration parameters
        :return: a new instance with the relevant parameters
        """
        operator_config = super()._get_operator_config(config)
        operator_config["strategy"] = config.get("strategy", None)
        operator_config["primary_key"] = config.get("primary_key", None)
        return cls(**operator_config)

    def invoke(self, content: str) -> str:
        """
        Invoke the storing of a new record or set of records.

        Input expected is a JSON that contains an object with keys that are the column names
        and values for these columns to store. Optionally, this can be a list of such objects.

        Output is a JSON version of a list of statuses, one per record and in the same order.
        Status can be "inserted" or "updated", a warning or error message.

        :param content: the JSON encoded record or set of records
        :return: a JSON encoded list of statuses, one per record and in the same order
        """
        try:
            records = json.loads(content)
        except json.decoder.JSONDecodeError:
            records = []

        if not isinstance(records, list):
            records = [records]
        storer = Storer(**self.base_config)
        result = storer.store(records)

        return json.dumps(result)


class MSSQLServerQueryInvoker(AbstractMSSQLServerInvoker):

    @classmethod
    def from_config(cls, config: dict):
        """
        Creates a new instance with the relevant parameters. All parameters are read from
        the configuration. The following parameters are also read from environment variables,
        where the environment variable takes precedence.

        - server MS_SQL_SERVER
        - username MS_SQL_SERVER_USERNAME
        - password MS_SQL_SERVER_PASSWORD
        - database MS_SQL_SERVER_DATABASE

        :param config: the configuration dictionary
        :return: a new instance with the relevant parameters
        """
        config = cls._get_operator_config(config)
        return cls(**config)

    def invoke(self, content: str) -> str:
        """
        Send the content as a query to the configured MS SQL server. Returns a JSON encoding
        of a retrieved records object.

        :param content: the query to run
        :return: a JSON encoded retrieved records object
        """
        querier = Querier(**self.base_config)
        result = querier.query(content)
        return result.model_dump_json()
