from abc import ABC
from typing import Optional

from loguru import logger
import pymssql


class MSSQLServerManager:

    def __init__(
            self,
            server: str,
            username: str,
            password: str,
            database: str,
    ):
        """
        A connection creator that takes server, username, password and database name and serves
        as a context manager for connections to MS SQL Server.

        :param server: the host name of the server to connect to
        :param username: the username to use
        :param password: the password to use
        :param database: the database to connect to
        """
        self._server = server
        self._username = username
        self._password = password
        self._database = database
        self._connection: Optional[pymssql.Connection] = None

    def __enter__(self):
        if self._connection is not None:
            logger.critical("Entering a context manager that is already entered")
            raise RuntimeError("Entering a context manager that is already entered")

        logger.info(
            "Creating connection to server {} with username {}",
            self._server,
            self._username
        )
        try:
            self._connection = pymssql.connect(
                self._server,
                self._username,
                self._password,
                self._database,
            )
        except Exception as e:
            logger.exception(e)
            raise

        return self._connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info(
            "Closing connection to server {} with username {}",
            self._server,
            self._username,
        )
        try:
            self._connection.close()
        except Exception as e:
            logger.exception(e)
            raise


class MSSQLServerManagerFactory:
    """
    A factory for `MSSQLServerManager`s
    """

    def __init__(
            self,
            server: str,
            username: str,
            password: str,
            database: str,
    ):
        """
        Retain the base parameters required to create an MS SQL Server manager.

        :param server: the host name of the server to connect to
        :param username: the username to use
        :param password: the password to use
        :param database: the database to connect to
        """
        self._server = server
        self._username = username
        self._password = password
        self._database = database

    def create_manager(self) -> MSSQLServerManager:
        """
        Creates a new MS SQL Server manager instance with the persisted parameters from
        this factory.

        :return: a new instance of an `MSSQLServerManager`
        """
        return MSSQLServerManager(
            self._server,
            self._username,
            self._password,
            self._database,
        )


class MSSQLServerOperator(ABC):

    def __init__(
            self,
            server: str,
            username: str,
            password: str,
            database: str,
    ):
        """
        An abstract base class for MS SQL Server operators. Stores the base
        properties required to connect to the database server.

        Creates a manager factory able to create `MSSQLServerManager`s.

        :param server: the host name of the server to connect to
        :param username: the username to connect with
        :param password: the password to connect with
        :param database: the database to connect to
        """
        self._manager_factory = MSSQLServerManagerFactory(
            server,
            username,
            password,
            database,
        )
