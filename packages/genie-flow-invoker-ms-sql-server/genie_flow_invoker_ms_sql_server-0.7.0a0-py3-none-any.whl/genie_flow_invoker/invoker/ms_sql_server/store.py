import collections
from collections import namedtuple
from typing import Literal, Any

from loguru import logger
import pymssql

from .manager import MSSQLServerOperator

StoreStrategyType = Literal["insert", "update", "upsert"]
IndexedRecord = namedtuple("IndexedRecord", ["index", "record"])


def quote_if_string(value: Any) -> Any:
    """
    Strings in SQL command needs to be quoted. This function will quote the passed value
    if it is a string.

    :param value: the value to (potentially) quote
    :return: the value as it can be used in a SQL command
    """
    if isinstance(value, str):
        return f"'{value}'"
    return value


class Storer(MSSQLServerOperator):

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
        A Storer is an MS SQL Server operator that stores records in a table. Depending on the
        strategy chose, it "insert"s, "update"s or "upsert"s new records. The output is a
        list of results. These can be "inserted", "updated" or a warning or error, followed by
        the message sent from the server.

        :param server: the hostname of the server
        :param username: the username to login to the server
        :param password: the password to login to the server
        :param database: the database to use when logged in
        :param table: the table to store into
        :param strategy: the strategy to use ("insert", "update", "upsert")
        :param primary_key: the primary key columns that define a unique record
        """
        if strategy != "insert" and (primary_key is None or len(primary_key) == 0):
            logger.error(
                "Cannot store using strategy {} when no primary_key is provided",
                strategy,
            )
            raise ValueError("Primary key must be provided when strategy is update or upsert")

        super().__init__(server, username, password, database)
        self._table = table
        self._strategy = strategy
        self._primary_key = primary_key

    def _insert(self, connection: pymssql.Connection, records: list[dict]) -> list[str]:
        """
        Insert records into the specified table.

        :param connection: the database connection to use
        :param records: the records to insert
        :return: a list of results, specifying `inserted` or an error or warning
        """
        logger.debug(
            "Inserting records into table {}: {}",
            self._table,
            records,
        )
        logger.info(
            "Inserting {} records into table {}",
            len(records),
            records,
        )

        results = []
        with connection.cursor() as cursor:
            for record in records:
                columns = record.keys()
                column_names = ", ".join(columns)

                value_placeholders = ", ".join(["%s"] * len(columns))

                q = f"INSERT INTO {self._table} ({column_names}) VALUES ({value_placeholders});"
                try:
                    logger.debug("Inserting record using query {}", q)
                    cursor.execute(q, [record[column] for column in columns])
                except pymssql.Error as e:
                    logger.warning("Failed to insert record, '{}'", str(e))
                    results.append(f"error {e.__class__.__name__}: {e.args}")
                except pymssql.Warning as e:
                    logger.warning("Warning with inserting record, '{}'", str(e))
                    results.append(f"warning {e.__class__.__name__}: {e.args}")
                else:
                    logger.debug("Inserted record")
                    results.append("inserted")

        return results

    def _check_missing_primary_key_columns(self, record: dict) -> list[str]:
        """
        Check what columns in the primary key are not included on the record.
        :param record: the record to check
        :return: a list of primary key columns that should be included in the record
        """
        return [
            col_name
            for col_name in self._primary_key
            if col_name not in record.keys()
        ]

    def _compile_assignments(self, record: dict[str, Any]) -> str:
        """
        Compile the assignments that should go on the SET part of the query

        :param record: the record to compile from
        :return: the string of assignments
        """
        assignments = [
            f"{col_name} = {quote_if_string(value)}"
            for col_name, value in record.items()
            if col_name not in self._primary_key
        ]
        return ", ".join(assignments)

    def _compile_where(self, record: dict[str, Any]) -> str:
        """
        Compile the WHERE clause to select the record to update.
        :param record: the record to compile from
        :return: the string of WHERE filter
        """
        where = [
            f"{col_name} = {quote_if_string(record[col_name])}"
            for col_name in self._primary_key
        ]
        return " AND ".join(where)

    def _update(self, connection: pymssql.Connection, records: list[dict]) -> list[str]:
        """
        Updating records in the configured table. Records should contain the values for
        the primary key columns. Values outside of these primary key columns are set to
        the values provided in the record.

        :param connection: the connection to the database
        :param records: the records to update
        :return: a list of results, specifying `updated` or an error or warning
        """
        logger.debug("Updating records in table {}: {}", self._table, records)
        logger.info("Updating {} records in table {}", len(records), self._table)

        result = []
        with connection.cursor() as cursor:
            for record in records:
                assignments = self._compile_assignments(record)
                if assignments == "":
                    logger.warning("No fields to update")
                    result.append("warning: no fields to update")
                    continue

                try:
                    where = self._compile_where(record)
                except KeyError:
                    missing_key_columns = ", ".join(
                        [
                            col_name
                            for col_name in self._primary_key
                            if col_name not in record.keys()
                        ]
                    )
                    logger.warning("Missing primary key columns '{}'", missing_key_columns)
                    result.append(f"warning: missing primary key columns: {missing_key_columns}")
                    continue

                q = f"UPDATE {self._table} SET {assignments} WHERE {where};"

                try:
                    logger.debug("Updating record using query {}", q)
                    cursor.execute(q)
                except pymssql.Error as e:
                    logger.warning("Failed to update record, '{}'", str(e))
                    result.append(f"error {e.__class__.__name__}: {e.args}")
                    continue
                except pymssql.Warning as e:
                    logger.warning("Warning with update record, '{}'", str(e))
                    result.append(f"warning {e.__class__.__name__}: {e.args}")

                if cursor.rowcount > 1:
                    logger.warning(
                        "Updated more than one records ({}) using primary key {}",
                        cursor.rowcount,
                        where,
                    )
                    result.append(f"warning: updated {cursor.rowcount} records")
                elif cursor.rowcount == 1:
                    logger.debug("Updated single record using primary key {}", where)
                    result.append("updated")
                else:
                    logger.warning("Updated no records using primary key {}", where)
                    result.append("missing")

        return result

    def _upsert(self, connection: pymssql.Connection, records: list[dict]) -> list[str]:
        """
        Upsert (Update or Insert) records into the configured table. Records should contain
        values for the primary key columns. Values outside of these primary key columns are
        set to the values provided in the record.

        :param connection: the connection to the database
        :param records: the records to upsert
        :return: a list of results, specifying `updated`, `inserted` or an error or warning
        """
        logger.debug("Upserting records in table {}: {}", self._table, records)
        logger.info("Upserting {} records in table {}", len(records), self._table)

        update_results = self._update(connection, records)
        records_to_insert = [
            IndexedRecord(index=index, record=record)
            for index, record in enumerate(records)
            if update_results[index] == "missing"
        ]
        if not records_to_insert:
            logger.debug("Upserted (only updates) records with results: {}", update_results)
            logger.info("No records to insert, only updated {} records", len(update_results))
            return update_results

        logger.info(
            "Upserting (inserts) {} records into table {}",
            len(records_to_insert),
            self._table,
        )
        insert_results = self._insert(
            connection,
            [indexed_record.record for indexed_record in records_to_insert]
        )
        logger.debug("Upsert inserting results: {}", insert_results)
        for insert_index, insert_result in enumerate(insert_results):
            original_index = records_to_insert[insert_index].index
            update_results[original_index] = insert_result

        return update_results

    def store(self, records: list[dict]) -> list[str]:
        """
        Store records into the configured table, using the configured strategy. Returns a
        list of results per record.

        :param records: the records to store
        :return: a list of results in the same order as the provided records.
        """
        if len(records) == 0:
            logger.warning("No records to store")
            return []

        with self._manager_factory.create_manager() as connection:
            match self._strategy:
                case "insert":
                    results = self._insert(connection, records)
                case "update":
                    results = self._update(connection, records)
                case "upsert":
                    results = self._upsert(connection, records)
                case _:
                    raise ValueError("Strategy must be insert, update or upsert")

            connection.commit()
            logger.debug(
                "Stored {} records into table {}, using strategy {}, with results: {}",
                len(records),
                self._table,
                self._strategy,
                results,
            )
            counter = collections.Counter(results)
            logger.info(
                "Stored {} records into table {}, using strategy {}, with result counts: {}",
                len(records),
                self._table,
                self._strategy,
                dict(counter),
            )
            return results
