import pprint
import re
from collections.abc import Mapping
from ..core.table import Query


class TableHelper:
    """
    A helper class used to build SQL queries with joined/aliased tables,
    including foreign key expansions, pointer syntax, etc.
    """

    reserved = []
    operators = {}

    def __init__(self, tx, table):
        self.tx = tx
        self.letter = 65
        self.table_aliases = {}
        self.foreign_keys = {}
        self.current_table = table
        self.table_aliases["current_table"] = chr(self.letter)
        self.letter += 1

    def __str__(self):
        return "\n".join(
            f"{key}: {pprint.pformat(value)}" for key, value in vars(self).items()
        )

    def split_columns(self, query):
        """
        Splits a string of comma-separated column expressions into a list, keeping parentheses balanced.
        """
        columns = []
        balance = 0
        current = []
        for char in query:
            if char == "," and balance == 0:
                columns.append("".join(current).strip())
                current = []
            else:
                if char == "(":
                    balance += 1
                elif char == ")":
                    balance -= 1
                current.append(char)
        if current:
            columns.append("".join(current).strip())
        return columns

    def requires_joins(self):
        return len(self.table_aliases) > 1

    def has_pointer(self, column):
        """
        Checks if there's an '>' in the column that indicates a pointer reference, e.g. 'local_column>foreign_column'.
        """
        if not isinstance(column, str) or not re.search(r"^[a-zA-Z0-9_>*]", column):
            raise Exception(f"Invalid column specified: {column}")
        return bool(re.search(r"[a-zA-Z0-9_]+>[a-zA-Z0-9_]+", column))

    def __fetch_foreign_data(self, key):
        if key in self.foreign_keys:
            return self.foreign_keys[key]
        local_column, foreign_column = key.split(">")
        foreign = self.tx.table(self.current_table).foreign_key_info(local_column)
        if not foreign:
            raise Exception(
                f"Foreign key `{self.current_table}.{local_column}>{foreign_column}` not defined."
            )
        ref_table = foreign["referenced_table_name"]
        ref_schema = foreign["referenced_table_schema"]
        ref_column = foreign["referenced_column_name"]
        if ref_table not in self.table_aliases:
            self.table_aliases[ref_table] = chr(self.letter)
            self.letter += 1
        alias = self.table_aliases[ref_table]
        data = {
            "alias": alias,
            "ref_table": ref_table,
            "ref_schema": ref_schema,
            "local_column": local_column,
            "ref_column": ref_column,
        }
        self.foreign_keys[key] = data
        return data

    def resolve_references(self, key, options=None):
        """
        Resolves pointer syntax or table alias references.
        `options` can control whether to alias columns and/or tables.
        """
        if not key:
            raise Exception(f"Invalid key={key}")
        if options is None:
            options = {"alias_column": True, "alias_table": False, "alias_only": False}
        column = self.extract_column_name(key)

        if not column:
            if options.get("bypass_on_error"):
                return key
            raise Exception(f"Invalid column={column}")

        alias = self.get_table_alias("current_table")
        if not self.has_pointer(column):
            # Standard column
            if options.get("alias_table") and alias != "A":
                name = alias + "." + self.quote(column)
            else:
                name = self.quote(column)
            return self.remove_operator(key).replace(column, name)

        local_column, foreign_column = column.split(">")
        if options.get("alias_only"):
            return f"{local_column}_{foreign_column}"
        data = self.__fetch_foreign_data(column)
        if options.get("alias_table"):
            name = f"{self.get_table_alias(data['ref_table'])}.{self.quote(foreign_column)}"
        else:
            name = f"{data['ref_table']}.{self.quote(foreign_column)}"

        result = self.remove_operator(key).replace(column, name)
        if options.get("alias_column"):
            result += f" as {local_column}_{foreign_column}"
        return result

    def get_operator(self, key, val):
        """
        Determines the SQL operator from the start of `key` or defaults to '='.
        """
        key = " ".join(key.replace('"', "").split())
        for symbol, operator in self.operators.items():
            if key.startswith(symbol):
                return operator
        return "="

    def remove_operator(self, key):
        """
        Strips recognized operator symbols from the start of `key`.
        """
        for symbol in self.operators.keys():
            if key.startswith(symbol):
                return key.replace(symbol, "", 1)
        return key

    def extract_column_name(self, sql_expression):
        """
        Extracts the 'bare' column name from a SQL expression.

        Supports:
        - Aliases (AS ...)
        - Window functions (OVER(... ORDER BY ...))
        - CAST(... AS ...)
        - CASE WHEN ... THEN ... ELSE ... END
        - Nested function calls
        - Grabs column from inside expressions (e.g. PLAID_ERROR from SUM(CASE...))

        Args:
            sql_expression (str): SQL expression (SELECT column) string.

        Returns:
            str or None: Extracted column name or None if undetectable.
        """
        expr = sql_expression.replace('"', "").strip()

        # Remove trailing alias
        expr = re.sub(r"(?i)\s+as\s+\w+$", "", expr).strip()

        # If OVER clause: extract column inside ORDER BY
        over_match = re.search(r"(?i)OVER\s*\(\s*ORDER\s+BY\s+([^\s,)]+)", expr)
        if over_match:
            return over_match.group(1)

        # Remove CAST(... AS ...)
        while re.search(r"(?i)CAST\s*\(([^()]+?)\s+AS\s+[^\)]+\)", expr):
            expr = re.sub(r"(?i)CAST\s*\(([^()]+?)\s+AS\s+[^\)]+\)", r"\1", expr)

        # Remove CASE WHEN ... THEN ... ELSE ... END, keep just the WHEN part
        while re.search(
            r"(?i)CASE\s+WHEN\s+(.+?)\s+THEN\s+.+?(?:\s+ELSE\s+.+?)?\s+END", expr
        ):
            expr = re.sub(
                r"(?i)CASE\s+WHEN\s+(.+?)\s+THEN\s+.+?(?:\s+ELSE\s+.+?)?\s+END",
                r"\1",
                expr,
            )

        # Unwrap function calls (SUM(...), MAX(...), etc.)
        while re.search(r"\b\w+\s*\(([^()]+)\)", expr):
            expr = re.sub(r"\b\w+\s*\(([^()]+)\)", r"\1", expr)

        # If multiple columns, take the first
        if "," in expr:
            expr = expr.split(",")[0].strip()

        # Extract column name (basic or dotted like table.col or *)
        match = re.search(
            r"\b([a-zA-Z_][\w]*\.\*|\*|[a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)?)\b", expr
        )
        return match.group(1) if match else None

    def are_parentheses_balanced(self, expression):
        """
        Checks if parentheses in `expression` are balanced.
        """
        stack = []
        opening = "({["
        closing = ")}]"
        matching = {")": "(", "}": "{", "]": "["}
        for char in expression:
            if char in opening:
                stack.append(char)
            elif char in closing:
                if not stack or stack.pop() != matching[char]:
                    return False
        return not stack

    def get_table_alias(self, table):
        return self.table_aliases.get(table)

    def make_predicate(self, key, val, options=None):
        """
        Builds a piece of SQL and corresponding parameters for a WHERE/HAVING predicate based on `key`, `val`.
        """
        if options is None:
            options = {"alias_table": True, "alias_column": False}
        case = None
        column = self.resolve_references(key, options=options)
        op = self.get_operator(key, val)

        # Subquery?
        if isinstance(val, Query):
            if op in ("<>"):
                return f"{column} NOT IN ({val})", val.params or None
            return f"{column} IN ({val})", val.params or None

        # Null / special markers
        if val is None or isinstance(val, bool) or val in ("@@INFINITY", "@@UNKNOWN"):
            if isinstance(val, str) and val.startswith("@@"):
                val = val[2:]
            if val is None:
                val = "NULL"
            if op == "<>":
                return f"{column} IS NOT {str(val).upper()}", None
            return f"{column} IS {str(val).upper()}", None

        # Lists / tuples => IN / NOT IN
        if isinstance(val, (list, tuple)) and "><" not in key:
            # Convert to tuple for better PostgreSQL parameter handling
            val_tuple = tuple(val)
            # Use IN/NOT IN instead of ANY for better type compatibility
            if "!" in key:
                placeholders = ",".join(["%s"] * len(val_tuple))
                return f"{column} NOT IN ({placeholders})", val_tuple
            else:
                placeholders = ",".join(["%s"] * len(val_tuple))
                return f"{column} IN ({placeholders})", val_tuple

        # "@@" => pass as literal
        if isinstance(val, str) and val.startswith("@@") and val[2:]:
            return f"{column} {op} {val[2:]}", None

        # Between operators
        if op in ["BETWEEN", "NOT BETWEEN"]:
            return f"{column} {op} %s and %s", tuple(val)

        if case:
            return f"{case}({column}) {op} {case}(%s)", val

        # Default single-parameter predicate
        return f"{column} {op} %s", val

    def make_where(self, where):
        """
        Converts a dict-based WHERE into a list of predicate strings + param values.
        """
        if isinstance(where, Mapping):
            new_where = []
            for key, val in where.items():
                new_where.append(self.make_predicate(key, val))
            where = new_where

        sql = []
        vals = []
        if where:
            sql.append("WHERE")
            join = ""
            for pred, val in where:
                if join:
                    sql.append(join)
                sql.append(pred)
                join = "AND"
                if val is not None:
                    if isinstance(val, tuple):
                        vals.extend(val)
                    else:
                        vals.append(val)
        return " ".join(sql), tuple(vals)

    @classmethod
    def quote(cls, data):
        """
        Quotes identifiers (columns/tables) if needed, especially if they match reserved words or contain special chars.
        """
        if isinstance(data, list):
            new_list = []
            for item in data:
                if item.startswith("@@"):
                    new_list.append(item[2:])
                else:
                    new_list.append(cls.quote(item))
            return new_list

        parts = data.split(".")
        quoted_parts = []
        for part in parts:
            if '"' in part:
                quoted_parts.append(part)
            elif part.upper() in cls.reserved or re.findall(r"[/]", part):
                quoted_parts.append(f'"{part}"')
            else:
                quoted_parts.append(part)
        return ".".join(quoted_parts)
