# Genie Flow Invoker MS SQL Server

This invoker package includes interfaces to Microsoft SQL Server.

## Install
Simply `pip install genie-flow-invoker-ms-sql-server` will install this set of invokers. In
the file `requirements.txt` of your agent, just add this package as requirement.

## Server Configuration
Configuring these invokers involves specifying the server name, username and password. Since
these invokers use `pymssql` to interface with the MS SQL Server, information about the
database connection can be [found here](https://pymssql.readthedocs.io/en/stable/pymssql_examples.html#basic-features-strict-db-api-compliance)

These can be configured in the `meta.yaml` file that is stored in the template directory, 
but these parameters also have an environment variable, as follows:

* MS_SQL_SERVER: server
* MS_SQL_SERVER_USERNAME: username
* MS_SQL_SERVER_PASSWORD: password
* MS_SQL_SERVER_DATABASE: database
* MS_SQL_SERVER_TABLE: table

To prevent these invokers from flooding the system, it is important to limit the number of
records that are returned. We need to put an absolute cap on the total number of records 
returned.

> BEWARE: retrieving all data from a very large table will break your agent - it will run
> out of memory.

## Retrieve from table - `MSSQLServerRetrieveInvoker`
This invoker retrieves records from an existing table.

By specifying the attribute `top`, only the specified number of records will be returned.
A default can be specified with the configuration of the invoker.

If no `top` has been specified, all records will be returned

An optional sort order can be given, where the fields to sort by (ascending or descending)
can be specified.

`sort_order`
: The order in which records should be returned is specified by a list of column names.
Columns should be stated in decreasing level of precedence. By default, the columns are
ordered in Ascending order. Ordering in Descending order can be achieved by prepending
the column name with a `-` sign.

### Override
The values stored in `meta.yaml` form the base configuration. Any of these configuration
values can be overriden by specifying them in the `content` of the invocation. For example,
if you want to make the `top` parameter dependent of user content, then you can provide
content as follows:

```json
{
  "top": 12
}
```
which will override any value that may be configured in the `meta.yaml` file.

### Return values
Records are returned as JSON objects with a key for every column and their accompanying value.

Return value would look like:

```json
{
  "results": [
    {
      "col1": "value",
      "col2": 1234
    },
    {
      "col1": "another value",
      "col2": 5678
    }
  ]
}
```

Here we have just one list of two records, each with the same columns but different values. 

## Store into table - `MSSQLServerStoreInvoker`
This invoker will store values into a table. The data expected is either a simple dictionary
stating all (required) columns and their value, or a list of such objects.

Configuration of this store invoker can potentially contain a list of columns that form the
primary key of the table. This means that a verification is done (by the server) to make sure
that new records will have a unique set of values for those columns.

If no primary key is defined, no special effort will be made to ensure uniqueness. Also, this
invoker can only add new records to the table as there would be no way to identify already
existing records to update.

### storage strategy
One can configure what should be done when a conflicting primary key is used. The strategies
are "insert", "update" or "upsert". The first (insert) means: a record with that primary key
should not yet exist and generate an error if it does. The second (update) means: a record 
with that key should already exist and the new values overwrite already existing values. 
This strategy would generate an error if such record does not yet exist. The final strategy
(upsert) means that, if a record with the same primary key already exists, the values are
updated. If not, a new record is created.

When an update happens (so a record already exists with the same primary key), one can suffice
with only sending the columns that need to be updated - irrespective if columns have been
defined as `NON NULL`. Only the columns stated will then be updated.

### storage feedback
Feedback on whether the data is stored or is sent back as a dictionary of the following form:

```json
{
  "results": [
    "updated",
    "missing"
  ]
}
```

Which would denote the successful updating of the first record, but an update that could not
be made because the specified primary key did not exist.

The following results can be returned for the different strategies:

| strategy | updated | missing | added | conflicting |
|----------|---------|---------|-------|-------------|
| insert   |         |         | *     | *           |
| update   | *       | *       |       |             |
| upsert   | *       |         | *     |             |

## Run SQL Query -- `MSSQLServerQueryInvoker`
For generic SQL queries, this invoker will pass what-ever query is sent to it, to the SQL
Server. Results are sent back to the client, using the same pagination logic as specified
above.

The `content` passed to this invoker is passed as SQL Query to the server. The object
returned is the same as what gets returned from the `MSSQLServerRetrieveInvoker`.