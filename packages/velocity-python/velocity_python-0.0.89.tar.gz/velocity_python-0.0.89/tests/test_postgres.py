import unittest
import decimal
from velocity.db.servers.postgres import (
    make_where,
    quote,
    SQL,
)  # Replace 'your_module' with the actual module name


class TestSQLModule(unittest.TestCase):
    def test_quote_simple_identifier(self):
        self.assertEqual(quote("test"), "test")

    def test_quote_reserved_word(self):
        self.assertEqual(quote("SELECT"), '"SELECT"')

    def test_quote_with_special_characters(self):
        self.assertEqual(quote("my/schema"), '"my/schema"')

    def test_quote_dot_notation(self):
        self.assertEqual(quote("my_table.my_column"), "my_table.my_column")

    def test_quote_list_identifiers(self):
        self.assertEqual(
            quote(["test", "SELECT", "my_table"]), ["test", '"SELECT"', "my_table"]
        )

    def test_make_where_simple_equality(self):
        sql = []
        vals = []
        make_where({"column1": "value1"}, sql, vals)
        self.assertEqual(" ".join(sql), "WHERE column1 = %s")
        self.assertEqual(vals, ["value1"])

    def test_make_where_with_null(self):
        sql = []
        vals = []
        make_where({"column1": None}, sql, vals)
        self.assertEqual(" ".join(sql), "WHERE column1 is NULL")
        self.assertEqual(vals, [])

    def test_make_where_with_not_null(self):
        sql = []
        vals = []
        make_where({"column1!": None}, sql, vals)
        self.assertEqual(" ".join(sql), "WHERE column1 is not NULL")
        self.assertEqual(vals, [])

    def test_make_where_with_operators(self):
        sql = []
        vals = []
        make_where({"column1>": 10, "column2!": "value2"}, sql, vals)
        self.assertEqual(" ".join(sql), "WHERE column1 > %s AND column2 <> %s")
        self.assertEqual(vals, [10, "value2"])

    def test_make_where_with_list(self):
        sql = []
        vals = []
        make_where({"column1": [1, 2, 3]}, sql, vals)
        self.assertEqual(" ".join(sql), "WHERE column1 in %s")
        self.assertEqual(vals, [(1, 2, 3)])

    def test_make_where_with_between(self):
        sql = []
        vals = []
        make_where({"column1><": [1, 10]}, sql, vals)
        self.assertEqual(" ".join(sql), "WHERE column1 between %s and %s")
        self.assertEqual(vals, [1, 10])

    def test_sql_select_simple(self):
        sql_query, params = SQL.select(columns="*", table="my_table")
        self.assertEqual(sql_query, "SELECT * FROM my_table")
        self.assertEqual(params, ())

    def test_sql_select_with_where(self):
        sql_query, params = SQL.select(columns="*", table="my_table", where={"id": 1})
        self.assertEqual(sql_query, "SELECT * FROM my_table WHERE id = %s")
        self.assertEqual(params, (1,))

    def test_sql_select_with_order_by(self):
        sql_query, params = SQL.select(columns="*", table="my_table", orderby="id DESC")
        self.assertEqual(sql_query, "SELECT * FROM my_table ORDER BY id DESC")
        self.assertEqual(params, ())

    def test_sql_insert(self):
        sql_query, params = SQL.insert(
            table="my_table", data={"column1": "value1", "column2": 2}
        )
        self.assertEqual(
            sql_query, "INSERT INTO my_table (column1,column2) VALUES (%s,%s)"
        )
        self.assertEqual(params, ("value1", 2))

    def test_sql_update(self):
        sql_query, params = SQL.update(
            table="my_table", data={"column1": "new_value"}, pk={"id": 1}
        )
        self.assertEqual(sql_query, "UPDATE my_table SET column1 = %s WHERE id = %s")
        self.assertEqual(params, ("new_value", 1))

    def test_sql_delete(self):
        sql_query, params = SQL.delete(table="my_table", where={"id": 1})
        self.assertEqual(sql_query, "DELETE FROM my_table WHERE id = %s")
        self.assertEqual(params, (1,))

    def test_sql_create_table(self):
        sql_query, params = SQL.create_table(
            name="public.test_table", columns={"name": str, "age": int}, drop=True
        )
        self.assertIn("CREATE TABLE public.test_table", sql_query)
        self.assertIn("DROP TABLE IF EXISTS public.test_table CASCADE;", sql_query)
        self.assertEqual(params, ())

    def test_sql_drop_table(self):
        sql_query, params = SQL.drop_table("public.test_table")
        self.assertEqual(sql_query, "drop table if exists public.test_table cascade;")
        self.assertEqual(params, ())

    def test_sql_create_index(self):
        sql_query, params = SQL.create_index(
            table="my_table", columns="column1", unique=True
        )
        self.assertIn("CREATE UNIQUE INDEX", sql_query)
        self.assertIn("ON my_table (column1)", sql_query)
        self.assertEqual(params, ())

    def test_sql_drop_index(self):
        sql_query, params = SQL.drop_index(table="my_table", columns="column1")
        self.assertIn("DROP INDEX IF EXISTS", sql_query)
        self.assertEqual(params, ())

    def test_sql_foreign_key_creation(self):
        sql_query, params = SQL.create_foreign_key(
            table="child_table",
            columns="parent_id",
            key_to_table="parent_table",
            key_to_columns="id",
        )
        self.assertIn("ALTER TABLE child_table ADD CONSTRAINT", sql_query)
        self.assertIn(
            "FOREIGN KEY (parent_id) REFERENCES parent_table (id);", sql_query
        )
        self.assertEqual(params, ())

    def test_sql_merge_insert(self):
        sql_query, params = SQL.merge(
            table="my_table",
            data={"column1": "value1"},
            pk={"id": 1},
            on_conflict_do_nothing=True,
            on_conflict_update=False,
        )
        self.assertIn("INSERT INTO my_table", sql_query)
        self.assertIn("ON CONFLICT (id) DO NOTHING", sql_query)
        self.assertEqual(params, ("value1", 1))

    def test_sql_merge_update(self):
        sql_query, params = SQL.merge(
            table="my_table",
            data={"column1": "value1"},
            pk={"id": 1},
            on_conflict_do_nothing=False,
            on_conflict_update=True,
        )
        self.assertIn("INSERT INTO my_table", sql_query)
        self.assertIn("ON CONFLICT (id) DO UPDATE SET", sql_query)
        self.assertEqual(params, ("value1", 1))

    def test_get_type_mapping(self):
        self.assertEqual(SQL.get_type("string"), "TEXT")
        self.assertEqual(SQL.get_type(123), "BIGINT")
        self.assertEqual(SQL.get_type(123.456), "NUMERIC(19, 6)")
        self.assertEqual(SQL.get_type(True), "BOOLEAN")
        self.assertEqual(SQL.get_type(None), "TEXT")

    def test_py_type_mapping(self):
        self.assertEqual(SQL.py_type("INTEGER"), int)
        self.assertEqual(SQL.py_type("NUMERIC"), decimal.Decimal)
        self.assertEqual(SQL.py_type("TEXT"), str)
        self.assertEqual(SQL.py_type("BOOLEAN"), bool)

    def test_sql_truncate(self):
        sql_query, params = SQL.truncate("my_table")
        self.assertEqual(sql_query, "truncate table my_table")
        self.assertEqual(params, ())

    def test_sql_create_view(self):
        sql_query, params = SQL.create_view(
            name="my_view", query="SELECT * FROM my_table", temp=True, silent=True
        )
        self.assertIn(
            "CREATE OR REPLACE TEMPORARY VIEW my_view AS SELECT * FROM my_table",
            sql_query,
        )
        self.assertEqual(params, ())

    def test_sql_drop_view(self):
        sql_query, params = SQL.drop_view(name="my_view", silent=True)
        self.assertEqual(sql_query, "DROP VIEW IF EXISTS my_view")
        self.assertEqual(params, ())

    # Additional tests can be added here to cover more methods and edge cases


if __name__ == "__main__":
    unittest.main()
