class UniqInspector:

    def __init__(self, column_name, table_name):
        self.column_name = column_name
        self.table_name = table_name

    def column_values_are_unique(self):
        return (
            f"SELECT\n"
            f"    COUNT(*) AS total_rows,\n"
            f"    SUM(CASE WHEN dup_count > 1 THEN 1 ELSE 0 END) AS duplicate_values,\n"
            f"    CASE WHEN SUM(CASE WHEN dup_count > 1 THEN 1 ELSE 0 END) = 0 THEN 1 ELSE 0 END AS passed\n"
            f"FROM (\n"
            f"    SELECT {self.column_name}, COUNT(*) AS dup_count\n"
            f"    FROM {self.table_name}\n"
            f"    GROUP BY {self.column_name}\n"
            f") t;"
        )

    def column_unique_value_count_is_between(self, lower_bound, upper_bound):
        return (
            f"SELECT\n"
            f"    COUNT(DISTINCT {self.column_name}) AS observed_value,\n"
            f"    {lower_bound} AS expected_lower_bound,\n"
            f"    {upper_bound} AS expected_upper_bound,\n"
            f"    CASE WHEN COUNT(DISTINCT {self.column_name}) >= {lower_bound} "
            f"              AND COUNT(DISTINCT {self.column_name}) <= {upper_bound} "
            f"         THEN 1 ELSE 0 END AS passed\n"
            f"FROM {self.table_name};"
        )

    def column_value_frequency_is_between(self, min_count, max_count):
        return (
            f"SELECT\n"
            f"    MIN(cnt) AS min_frequency,\n"
            f"    MAX(cnt) AS max_frequency,\n"
            f"    {min_count} AS expected_min_frequency,\n"
            f"    {max_count} AS expected_max_frequency,\n"
            f"    CASE WHEN MIN(cnt) >= {min_count} AND MAX(cnt) <= {max_count} "
            f"         THEN 1 ELSE 0 END AS passed\n"
            f"FROM (\n"
            f"    SELECT {self.column_name}, COUNT(*) AS cnt\n"
            f"    FROM {self.table_name}\n"
            f"    GROUP BY {self.column_name}\n"
            f") t;"
        )

    def no_empty_strings(self):
        return (
            f"SELECT\n"
            f"    COUNT(*) AS total_rows,\n"
            f"    SUM(CASE WHEN TRIM({self.column_name}) = '' THEN 1 ELSE 0 END) AS empty_string_count,\n"
            f"    CASE WHEN SUM(CASE WHEN TRIM({self.column_name}) = '' THEN 1 ELSE 0 END) = 0 "
            f"         THEN 1 ELSE 0 END AS passed\n"
            f"FROM {self.table_name};"
        )

    def primary_key_check(self):
        return (
            f"SELECT\n"
            f"    COUNT(*) AS total_rows,\n"
            f"    COUNT(DISTINCT {self.column_name}) AS distinct_count,\n"
            f"    SUM(CASE WHEN {self.column_name} IS NULL THEN 1 ELSE 0 END) AS null_count,\n"
            f"    CASE WHEN COUNT(DISTINCT {self.column_name}) = COUNT(*) "
            f"              AND SUM(CASE WHEN {self.column_name} IS NULL THEN 1 ELSE 0 END) = 0 "
            f"         THEN 1 ELSE 0 END AS passed\n"
            f"FROM {self.table_name};"
        )

    def distinct_ratio_is_above(self, ratio_threshold):
        return (
            f"SELECT\n"
            f"    CAST(COUNT(DISTINCT {self.column_name}) AS FLOAT) / COUNT(*) AS distinct_ratio,\n"
            f"    {ratio_threshold} AS expected_min_ratio,\n"
            f"    CASE WHEN CAST(COUNT(DISTINCT {self.column_name}) AS FLOAT) / COUNT(*) >= {ratio_threshold} "
            f"         THEN 1 ELSE 0 END AS passed\n"
            f"FROM {self.table_name};"
        )
