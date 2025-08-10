import datetime
import decimal
from velocity.misc.format import to_json


class Result:
    """
    Wraps a database cursor to provide various convenience transformations
    (dict, list, tuple, etc.) and helps iterate over query results.
    """

    def __init__(self, cursor=None, tx=None, sql=None, params=None):
        self._cursor = cursor
        self._headers = [x[0].lower() for x in getattr(cursor, "description", []) or []]
        self.__as_strings = False
        self.__enumerate = False
        self.__count = -1
        self.__columns = {}
        self.__tx = tx
        self.__sql = sql
        self.__params = params
        self.transform = lambda row: dict(zip(self.headers, row))  # Default transform

    def __str__(self):
        return repr(self.all())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.close()

    def __next__(self):
        """
        Iterator interface to retrieve the next row.
        """
        if self._cursor:
            row = self._cursor.fetchone()
            if row:
                if self.__as_strings:
                    row = ["" if x is None else str(x) for x in row]
                if self.__enumerate:
                    self.__count += 1
                    return (self.__count, self.transform(row))
                return self.transform(row)
        raise StopIteration

    def batch(self, qty=1):
        """
        Yields lists (batches) of rows with size = qty until no rows remain.
        """
        results = []
        while True:
            try:
                results.append(next(self))
            except StopIteration:
                if results:
                    yield results
                break
            if len(results) == qty:
                yield results
                results = []

    def all(self):
        """
        Retrieves all rows at once into a list.
        """
        results = []
        while True:
            try:
                results.append(next(self))
            except StopIteration:
                break
        return results

    def __iter__(self):
        return self

    @property
    def headers(self):
        """
        Retrieves column headers from the cursor if not already set.
        """
        if not self._headers and self._cursor and hasattr(self._cursor, "description"):
            self._headers = [x[0].lower() for x in self._cursor.description]
        return self._headers

    @property
    def columns(self):
        """
        Retrieves detailed column information from the cursor.
        """
        if not self.__columns and self._cursor and hasattr(self._cursor, "description"):
            for column in self._cursor.description:
                data = {
                    "type_name": self.__tx.pg_types[column.type_code],
                }
                for key in dir(column):
                    if "__" not in key:
                        data[key] = getattr(column, key)
                self.__columns[column.name] = data
        return self.__columns

    @property
    def cursor(self):
        return self._cursor

    def close(self):
        """
        Closes the underlying cursor if it exists.
        """
        if self._cursor:
            self._cursor.close()

    def as_dict(self):
        """
        Transform each row into a dictionary keyed by column names.
        """
        self.transform = lambda row: dict(zip(self.headers, row))
        return self

    def as_json(self):
        """
        Transform each row into JSON (string).
        """
        self.transform = lambda row: to_json(dict(zip(self.headers, row)))
        return self

    def as_named_tuple(self):
        """
        Transform each row into a list of (column_name, value) pairs.
        """
        self.transform = lambda row: list(zip(self.headers, row))
        return self

    def as_list(self):
        """
        Transform each row into a list of values.
        """
        self.transform = lambda row: list(row)
        return self

    def as_tuple(self):
        """
        Transform each row into a tuple of values.
        """
        self.transform = lambda row: row
        return self

    def as_simple_list(self, pos=0):
        """
        Transform each row into the single value at position `pos`.
        """
        self.transform = lambda row: row[pos]
        return self

    def strings(self, as_strings=True):
        """
        Indicate whether retrieved rows should be coerced to string form.
        """
        self.__as_strings = as_strings
        return self

    def scalar(self, default=None):
        """
        Return the first column of the first row, or `default` if no rows.
        """
        if not self._cursor:
            return None
        val = self._cursor.fetchone()
        # Drain any remaining rows.
        self._cursor.fetchall()
        return val[0] if val else default

    def one(self, default=None):
        """
        Return the first row or `default` if no rows.
        """
        try:
            row = next(self)
            # Drain remaining.
            if self._cursor:
                self._cursor.fetchall()
            return row
        except StopIteration:
            return default

    def get_table_data(self, headers=True):
        """
        Builds a two-dimensional list: first row is column headers, subsequent rows are data.
        """
        self.as_list()
        rows = []
        for row in self:
            row = ["" if x is None else str(x) for x in row]
            rows.append(row)
        if isinstance(headers, list):
            rows.insert(0, [x.replace("_", " ").title() for x in headers])
        elif headers:
            rows.insert(0, [x.replace("_", " ").title() for x in self.headers])
        return rows

    def enum(self):
        """
        Yields each row as (row_index, transformed_row).
        """
        self.__enumerate = True
        return self

    @property
    def sql(self):
        return self.__sql

    @property
    def params(self):
        return self.__params
