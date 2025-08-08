from typing import Optional

from loguru import logger
import pymssql

from .manager import MSSQLServerOperator
from .model import RetrievedResults


class Retriever(MSSQLServerOperator):

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
        super().__init__(server, username, password, database)
        self._table = table
        self._top = top
        self._sort_order = sort_order

    def _compile_query(self) -> str:
        top = f" TOP {self._top}" if self._top is not None else ""
        logger.debug(
            "Compiling query for top set at {}, with top statement '{}'",
            self._top,
            top,
        )

        sort_order = ""
        if self._sort_order is not None and len(self._sort_order) > 0:
            order = [
                f"{sort_col[1:]} DESC" if sort_col.startswith("-") else sort_col
                for sort_col in self._sort_order
            ]
            sort_order = " ORDER BY " + ", ".join(order)
            logger.debug(
                "Compiling query for sort order {} with order by statement '{}'",
                self._sort_order,
                sort_order,
            )

        return f"SELECT{top} * FROM {self._table}{sort_order};"

    def retrieve(self) -> RetrievedResults:
        """
        Retrieve the records as configured.

        :return: the retrieved records object that contains the records and / or error
        messages
        """
        logger.info(
            "Retrieving from table {} the top {} rows, ordered by {}",
            self._table,
            self._top,
            self._sort_order,
        )
        with self._manager_factory.create_manager() as connection:
            q = self._compile_query()
            logger.debug("Retrieval query: {}", q)
            with connection.cursor(as_dict=True) as cursor:
                try:
                    cursor.execute(q)
                except pymssql.Error as e:
                    logger.warning("Retrieve query failed, {}", str(e))
                    return RetrievedResults(
                        error=f"error {e.__class__.__name__}: {e.args}",
                    )
                except pymssql.Warning as e:
                    logger.warning(
                        "Retrieve query warning {} with {} results",
                        str(e),
                        cursor.rowcount,
                    )
                    return RetrievedResults(
                        results=cursor.fetchall() if cursor.rowcount > 0 else [],
                        error=f"warning {e.__class__.__name__}: {e.args}",
                    )
                else:
                    return RetrievedResults(
                        results=cursor.fetchall(),
                    )
