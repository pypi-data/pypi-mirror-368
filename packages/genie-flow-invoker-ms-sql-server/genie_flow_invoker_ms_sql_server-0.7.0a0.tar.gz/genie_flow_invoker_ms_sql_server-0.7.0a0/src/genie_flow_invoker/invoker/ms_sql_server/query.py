from hashlib import md5

import pymssql
from loguru import logger

from .manager import MSSQLServerOperator
from .model import RetrievedResults


class Querier(MSSQLServerOperator):

    def query(self, query: str) -> RetrievedResults:
        """
        Run the provided query against the configured database.

        :param query: the query to run
        :return: A `RetrievedResults` instance that contains the results and/or
        any errors or warnings that were raised.
        """
        logger.debug(
            "Sending query to MS SQL Server: '{}'",
            query,
        )
        logger.info(
            "Sending query to MS SQL Server: hashed '{}'",
            md5(query.encode('utf-8'), usedforsecurity=False).hexdigest(),
        )
        with self._manager_factory.create_manager() as connection:
            with connection.cursor(as_dict=True) as cursor:
                try:
                    cursor.execute(query)
                except pymssql.Error as e:
                    logger.warning("Query failed with error {}", str(e))
                    return RetrievedResults(
                        error=f"error {e.__class__.__name__}: {e.args}",
                    )
                except pymssql.Warning as e:
                    logger.warning("Query failed with warning {}", str(e))
                    return RetrievedResults(
                        results=cursor.fetchall() if cursor.rowcount > 0 else [],
                        error=f"warning {e.__class__.__name__}: {e.args}",
                    )

                logger.info("Query succeeded and returned {} rows", cursor.rowcount)
                return RetrievedResults(
                    results=cursor.fetchall(),
                )
