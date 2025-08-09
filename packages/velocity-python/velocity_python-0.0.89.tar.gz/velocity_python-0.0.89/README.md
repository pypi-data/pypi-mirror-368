# Velocity.DB

This project's goal is to simplify database management by abstracting complex (and many times database engine specific) functions to Python methods. This project is still in its infancy and is not yet ready for production use. If you would like to contribute to this project, please feel free to fork it and submit a pull request. This documentation is severely out of date and not yet complete, but will be updated as the project progresses.

This project currently supports the following database engines:

<b>PostgreSQL</b><br/>
<b>Microsoft SQL Server</b><br/>
<b>SQLite</b><br/>
<b>MySQL</b><br/>

[The source for this project is available here][src].

<b>Prerequisites:</b><br/>
The following packages must be installed prior to using Velocity.DB:<br/>
`psycopg2` - For PostgreSQL<br/>
`pytds` - For Microsoft SQL Server<br/>
`sqlite3` - For SQLite 3<br/>
`mysqlclient` - MySQL<br/>
You will also need the MySQL Connector for your operating system before you install `mysqlclient`. You can download it <a href='https://dev.mysql.com/downloads/connector/c/'>here.</a>

<b>For Windows Users:</b><br/>
If you're using Windows, after you install the MySQL Connector you will need the Visual C++ Compiler for Python 2.7, you can download it <a href='https://www.microsoft.com/en-us/download/details.aspx?id=44266'>here.</a> After both dependencies are installed you can install `mysqlclient` without issue.

Optionally if you only want to support a single database engine or do not want to install dependencies for engines you won't be using, download the source code for velocity.db and comment out the engines you wont be using in the `python-db/velocity/db/__init_.py` file on the following lines:

<pre>
# Import for PostgreSQL Support
import servers.postgres
postgres = servers.postgres.initialize()
<br/># Import for Microsoft SQL Server Support
import servers.sqlserver
sqlserver = servers.sqlserver.initialize
<br/># Import for SQLite 3 Support
import servers.sqlite
sqlite = servers.sqlite.initialize
<br/># Import for MySQL Support
import servers.mysql
mysql = servers.mysql.initialize</pre>

If you setup your project this way, make sure to install velocity.db using: `python setup.py develop` in case you want to revert your changes.

----

# Using Velocity.DB

<b>Warning: Not all database engines are alike, and some datatypes in certain engines will be specific to the engine. This tutorial assumes you have basic knowledge of your database engine and it's specific datatypes.</b>

To setup Velocity.DB with your server, define your server variable like so:

<b>PostgreSQL:</b>
<pre>
import velocity.db
<br/>server = velocity.db.postgres({
	'database':'db-name',
	'host': 'server',
	'user':'username',
	'password':'password',
})
</pre>
<b>Microsoft SQL Server:</b>
<pre>
import velocity.db
<br/>server = velocity.db.sqlserver({
	'database': 'db-name',
	'server': 'server',
	'user':'username',
	'password':'password',
	'use_mars': True, # To enable Multiple Active Result Sets (disabled by default)
})
</pre>
<b>SQLite:</b>
<pre>
import velocity.db
<br/>server = velocity.db.sqlserver({
	'database': 'db-name' # Use ':memory:' for an in memory database
})
</pre>
<b>MySQL:</b>
<pre>
import velocity.db
<br/>server = velocity.db.mysql({
	'db':'db-name',
	'host':'server',
	'user':'username',
	'passwd':'password',
})
</pre>
<br>
<b>Basic SQL Functions:</b><br/>
Since the SQL ANSI standard holds all SQL compliant databases to the CRUD standard (Create, Read, Update, Delete) we will cover how to accomplish all of those functions using Velocity.DB.<br/>
<br/><b>The <code>@server.transaction</code> Decorator:</b><br/>
All SQL transactions have to live in their own functions so that in case some part of the function fails, the transaction will not commit. In order to signify a method as a transaction, use the <code>@server.transaction</code> decorator. Any function using this decorator will not commit any changes to the database unless the function successfully completes without error. This also passes the argument <code>tx</code> to your method which allows you to access the transaction object within your method.<br/>
<br/><b>Creating a Table:</b>
<pre>
@server.transaction
def create_new_table(self, tx):
	t = tx.table('new_table')
    t.create()
</pre>
Once the function is complete the transaction will commit and you will have a new table in your database titled 'new_table'.<br>
If you would like to create a new row and add a column, you could do so using the following syntax:
<pre>
@server.transaction
def add_column(self,tx):
	# We will be using the same table we made in the above method.
	t = tx.table('new_table')
    # Creates a new row with a primary key of 1 (sys_id by default)
    r = t.row(1)
    r['new_column'] = 'Value to be placed in the first row of the new column'
</pre>
<br/><b>Reading Data from a Table:</b>
<br/>Now let's say you already have a table with data named 'people', and you want to read the 'firstname' column of your table on the third row and return that field. You would accomplish this in Velocity.DB like so:
<pre>
@server.transaction
def read_third_firstname(self, tx):
	t = tx.table('people')
    r = t.row(3)
    return r['firstname']
</pre>
The above method will return the value of the 'firstname' column in row 3 of the table. The table object is iterable so if you would like to return the values of each field in the 'firstname' column you could do so like this:
<pre>
@server.transaction
def read_all_firstnames(self,tx):
	t = tx.table('people')
    name_list = []
    for r in t:
    	name_list.append(r['firstname'])
    return name_list
</pre>
<b>Updating a Preexisting Table:</b><br/>
If you already have a table that you would like to update the data within, you can update data fields using the same syntax that you would use to create the field. This example will be working on a table named 'people' with columns: 'firstname' and 'lastname' with information filled out for 3 rows. Let's assume that the person on row 2 just got married and their last name has changed so we need to update it within the database.
<pre>
@server.transaction
def update_lastname(self, tx):
	t = tx.table('people')
    r = t.row(2)
    r['lastname'] = 'Newname'
</pre>
Notice the syntax is the same as if we were creating a new column. This syntax will attempt to insert the data, and if the column doesn't exist then it will create it. It will also see if the data is already populated, and if so it will issue a UPDATE command to the database instead.<br/>
<br/><b>Deleting Data and Dropping Tables:</b><br/>
To delete data from an existing table you may want to only delete a specific row. We will use the same 'people' database, let's go ahead and delete the person that was occupying row 3.
<pre>
@server.transaction
def delete_person(self, tx):
	t = tx.table('people')
    r = t.row(3)
    r.delete()
</pre>
It's as simple as that! But what if instead you were wanting to drop the whole table? <b>Warning: Executing the following code will drop the table from the database, if you are testing on your own database make sure you have a backup first.</b>
<pre>
@server.transaction
def drop_table(self, tx):
	t = tx.table('people')
    t.drop()
</pre>
Keep in mind this will use the "IF EXISTS" SQL statement so if you accidentally misspell a table name, your program will not hang and no tables will be dropped.<br/>
<br/>Congratulations, you now know how to use basic CRUD functionality with Velocity.DB. Velocity.DB has many advanced features as well, so if you'd like to see how some of those methods are used check out the <code>python-db/velocity/tests/db/unit_tests.py</code> file for examples.

[src]: https://github.com/
