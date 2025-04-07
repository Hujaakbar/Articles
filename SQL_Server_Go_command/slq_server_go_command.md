# SQL Server Go command and Column Nullability considerations

## `GO` command

You can write sql statements/commands using tools such as SQL Server Management Studio **Code Editor** and `sqlcmd`. Then the sql code is executed by SQL Server. Above tools merely send your sql code to the SQL server to be executed.

SQL Server does NOT use `GO` command. It is never sent to the server. Rather, `GO` command is used by SQL Server Management Studio Code Editor, `sqlcmd` and `osql` utilities.

> GO signals the end of a batch of Transact-SQL statements to the SQL Server utilities. *[source](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/sql-server-utilities-statements-go?view=sql-server-ver16)*

What `GO` command do is to instruct the `sqlcmd`, `osql`, SQL Server Management Studio Code Editor etc. to send the code up until the `GO` command as one batch. Basically it is a code (batch) separator. The SQL Server utilities never send a GO command to the server.

### Why and When GO command is needed

Before executing the sql code, SQL server validates it. If, for example, (single batch of) sql code includes both `CREATE` and `ALTER` statements, when validating `ALTER` statement, sql server raises error. This is because when `ALTER` statements is being validated, the table does not exist yet. SQL server *thinks* `ALTER` statement is referencing undefined table and raises error.

Below code threw error when ran with `sqlcmd`:

```sql
CREATE TABLE my_table (
ID int IDENTITY(1,1) NOT NULL,
column1 VARCHAR(10) NOT NULL,
column2 DECIMAL(3,0) NOT NULL,
);

ALTER TABLE my_table
ADD column3 DATETIME NULL;
```

To avoid error, we should execute `CREATE` and `ALTER` statements separately.

```sql
CREATE TABLE my_table (
ID int IDENTITY(1,1) NOT NULL,
column1 VARCHAR(10) NOT NULL,
column2 DECIMAL(3,0) NOT NULL,
);
-- ↑↑↑ Batch 1
GO
--  ↓↓↓↓ Batch 2
ALTER TABLE my_table
ADD column3 DATETIME NULL;
```

--------------

## Nullability

While creating or altering the table, if you leave column nullability constraint unspecified ( whether the column can allow a null value or not), that column might end up with `NOT NULL` or `NULL` (nullable) data type depending on the database and session settings.

> When you use CREATE TABLE or ALTER TABLE to create or alter a table, database and session settings influence and may override the nullability of the data type that is used in a column definition. Sometimes column left blank might be `NOT NULL` or `NULL` (nullable). *[source](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver16#nullability-rules-within-a-table-definition)*

Not defining column nullability explicitly leads to unexpected behaviors. For example, all columns defined within a [PRIMARY KEY constraints](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver16#primary-key-constraints) must be defined as NOT NULL. If columns whose data types are nullable due to not being explicitly defined are used within PRIMARY KEY constraints, SQL Server raises error.

Below columns might end up either with `NOT NULL` or `NULL` (nullable) data type.

```sql
CREATE TABLE my_table (
column1 VARCHAR(10),
column2 DECIMAL(3,0),
);
```

To avoid unexpected behavior, it is recommended to explicitly define a column as NULL or NOT NULL.

```sql
CREATE TABLE my_table (
column1 VARCHAR(10) NOT NULL,
column2 DECIMAL(3,0) NULL,
);
```
