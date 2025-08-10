from .inspectors.uniq import UniqInspector
from .inspectors.numeric import NumericInspector


VALIDATIONS = {
    # ===== Generic / Null Checks =====
    "is_not_null": {
        "inspector": None,
        "params": [("column", "Please enter the column name to check for NOT NULL")],
        "builder": lambda table, column: (
            f"SELECT COUNT(*) AS null_count\n"
            f"FROM {table}\n"
            f"WHERE {column} IS NULL;"
        ),
        "description": lambda column: f'✔ Will check that column "{column}" is not null.'
    },

    "has_no_duplicates": {
        "inspector": None,
        "params": [("column", "Please enter the column name to check for duplicates")],
        "builder": lambda table, column: (
            f"SELECT {column}, COUNT(*) AS cnt\n"
            f"FROM {table}\n"
            f"GROUP BY {column}\n"
            f"HAVING COUNT(*) > 1;"
        ),
        "description": lambda column: f'✔ Will check that column "{column}" has no duplicates.'
    },

    # ===== Uniqueness =====
    "column_values_are_unique": {
        "inspector": UniqInspector,
        "params": [("column", "Please enter the column name to check for uniqueness")],
        "method": "column_values_are_unique",
        "description": lambda column: f'✔ Will check that "{column}" column values are unique.'
    },

    "column_unique_value_count_is_between": {
        "inspector": UniqInspector,
        "params": [
            ("column", "Please enter the column name"),
            ("lower_bound", "Please enter the lower bound"),
            ("upper_bound", "Please enter the upper bound")
        ],
        "method": "column_unique_value_count_is_between",
        "description": lambda col, lb, ub: f'✔ Will check that "{col}" has a unique value count between {lb} and {ub}.'
    },

    "column_value_frequency_is_between": {
        "inspector": UniqInspector,
        "params": [
            ("column", "Please enter the column name"),
            ("min_count", "Please enter the minimum allowed frequency"),
            ("max_count", "Please enter the maximum allowed frequency")
        ],
        "method": "column_value_frequency_is_between",
        "description": lambda col, min_c, max_c: (
            f'✔ Will check that the frequency of each distinct value in "{col}" '
            f'is between {min_c} and {max_c}.'
        )
    },

    "no_empty_strings": {
        "inspector": UniqInspector,
        "params": [
            ("column", "Please enter the column name to check for empty strings")
        ],
        "method": "no_empty_strings",
        "description": lambda col: (
            f'✔ Will check that column "{col}" contains no empty string values.'
        )
    },

    "primary_key_check": {
        "inspector": UniqInspector,
        "params": [
            ("column", "Please enter the column name to check as primary key")
        ],
        "method": "primary_key_check",
        "description": lambda col: (
            f'✔ Will check that column "{col}" can serve as a primary key '
            f'(unique and not null).'
        )
    },

    "distinct_ratio_is_above": {
        "inspector": UniqInspector,
        "params": [
            ("column", "Please enter the column name"),
            ("ratio_threshold", "Please enter the minimum distinct ratio threshold")
        ],
        "method": "distinct_ratio_is_above",
        "description": lambda col, ratio: (
            f'✔ Will check that the ratio of distinct values in "{col}" '
            f'is at least {ratio}.'
        )
    },


    # ===== Numeric Checks =====
    "column_max_is_between": {
        "inspector": NumericInspector,
        "params": [
            ("column", "Please enter the column name"),
            ("lower_bound", "Please enter the lower bound"),
            ("upper_bound", "Please enter the upper bound")
        ],
        "method": "column_max_is_between",
        "description": lambda col, lb, ub: f'✔ Will check that "{col}" column MAX values are between {lb} and {ub}'
    },

    "column_min_is_between": {
        "inspector": NumericInspector,
        "params": [
            ("column", "Please enter the column name"),
            ("lower_bound", "Please enter the lower bound"),
            ("upper_bound", "Please enter the upper bound")
        ],
        "method": "column_min_is_between",
        "description": lambda col, lb, ub: f'✔ Will check that "{col}" column MIN values are between {lb} and {ub}'
    },

    "column_sum_is_between": {
        "inspector": NumericInspector,
        "params": [
            ("column", "Please enter the column name"),
            ("lower_bound", "Please enter the lower bound"),
            ("upper_bound", "Please enter the upper bound")
        ],
        "method": "column_sum_is_between",
        "description": lambda col, lb, ub: f'✔ Will check that "{col}" column SUM values are between {lb} and {ub}'
    },

    "column_mean_is_between": {
        "inspector": NumericInspector,
        "params": [
            ("column", "Please enter the column name"),
            ("lower_bound", "Please enter the lower bound"),
            ("upper_bound", "Please enter the upper bound")
        ],
        "method": "column_mean_is_between",
        "description": lambda col, lb, ub: f'✔ Will check that "{col}" column MEAN values are between {lb} and {ub}'
    },

    "column_standard_deviation_is_between": {
        "inspector": NumericInspector,
        "params": [
            ("column", "Please enter the column name"),
            ("lower_bound", "Please enter the lower bound"),
            ("upper_bound", "Please enter the upper bound")
        ],
        "method": "column_standard_deviation_is_between",
        "description": lambda col, lb, ub: f'✔ Will check that "{col}" column standard deviation values are between {lb} and {ub}'
    },

    "column_values_are_between": {
        "inspector": NumericInspector,
        "params": [
            ("column", "Please enter the column name"),
            ("lower_bound", "Please enter the lower bound"),
            ("upper_bound", "Please enter the upper bound")
        ],
        "method": "column_values_are_between",
        "description": lambda col, lb, ub: f'✔ Will check that "{col}" column values are between {lb} and {ub}'
    },

    "column_has_no_nulls": {
        "inspector": NumericInspector,
        "params": [
            ("column", "Please enter the column name to check for NULL values")
        ],
        "method": "column_has_no_nulls",
        "description": lambda col: (
            f'✔ Will check that column "{col}" contains no NULL values.'
        )
    },

    "column_has_values_greater_than": {
        "inspector": NumericInspector,
        "params": [
            ("column", "Please enter the column name"),
            ("threshold", "Please enter the minimum allowed value")
        ],
        "method": "column_has_values_greater_than",
        "description": lambda col, th: (
            f'✔ Will check that all values in column "{col}" are greater than {th}.'
        )
    },

    "column_median_is_between": {
        "inspector": NumericInspector,
        "params": [
            ("column", "Please enter the column name"),
            ("lower_bound", "Please enter the lower bound"),
            ("upper_bound", "Please enter the upper bound")
        ],
        "method": "column_median_is_between",
        "description": lambda col, lb, ub: (
            f'✔ Will check that the median of column "{col}" is between {lb} and {ub}.'
        )
    },

    "column_non_negative": {
        "inspector": NumericInspector,
        "params": [
            ("column", "Please enter the column name")
        ],
        "method": "column_non_negative",
        "description": lambda col: (
            f'✔ Will check that all values in column "{col}" are non-negative.'
        )
    },


    # ===== Row Count Checks =====
    "table_row_count_is_between": {
        "inspector": None,
        "params": [
            ("lower_bound", "Please enter the lower bound for row count"),
            ("upper_bound", "Please enter the upper bound for row count")
        ],
        "builder": lambda table, lb, ub: (
            f"SELECT COUNT(*) AS row_count\n"
            f"FROM {table}\n"
            f"HAVING row_count BETWEEN {lb} AND {ub};"
        ),
        "description": lambda lb, ub: f'✔ Will check that table row count is between {lb} and {ub}'
    },

    "table_row_count_equals": {
        "inspector": None,
        "params": [("expected_count", "Please enter the expected row count")],
        "builder": lambda table, cnt: (
            f"SELECT COUNT(*) AS row_count\n"
            f"FROM {table}\n"
            f"HAVING row_count = {cnt};"
        ),
        "description": lambda cnt: f'✔ Will check that table row count equals {cnt}'
    }
}
