class NumericInspector:

    def __init__(self, column_name, table_name):
        self.column_name = column_name
        self.table_name = table_name

    def _between_query(self, agg_func, lower_bound, upper_bound):
        """Helper to build a unified output query."""
        return (
            f"SELECT\n"
            f"    {agg_func}({self.column_name}) AS observed_value,\n"
            f"    {lower_bound} AS expected_lower_bound,\n"
            f"    {upper_bound} AS expected_upper_bound,\n"
            f"    CASE WHEN {agg_func}({self.column_name}) >= {lower_bound}\n"
            f"              AND {agg_func}({self.column_name}) <= {upper_bound}\n"
            f"         THEN 1 ELSE 0 END AS passed\n"
            f"FROM {self.table_name};"
        )

    def column_max_is_between(self, lower_bound, upper_bound):
        return self._between_query("MAX", lower_bound, upper_bound)

    def column_min_is_between(self, lower_bound, upper_bound):
        return self._between_query("MIN", lower_bound, upper_bound)

    def column_sum_is_between(self, lower_bound, upper_bound):
        return self._between_query("SUM", lower_bound, upper_bound)

    def column_mean_is_between(self, lower_bound, upper_bound):
        return self._between_query("AVG", lower_bound, upper_bound)
    
    def column_standard_deviation_is_between(self, lower_bound, upper_bound):
        return self._between_query("STDDEV", lower_bound, upper_bound)

    def column_values_are_between(self, lower_bound, upper_bound):
        return (
            f"SELECT\n"
            f"    COUNT(*) AS total_rows,\n"
            f"    SUM(CASE WHEN {self.column_name} < {lower_bound} "
            f"              OR {self.column_name} > {upper_bound} "
            f"             THEN 1 ELSE 0 END) AS failed_rows,\n"
            f"    {lower_bound} AS expected_lower_bound,\n"
            f"    {upper_bound} AS expected_upper_bound,\n"
            f"    CASE WHEN SUM(CASE WHEN {self.column_name} < {lower_bound} "
            f"                        OR {self.column_name} > {upper_bound} "
            f"                       THEN 1 ELSE 0 END) = 0 "
            f"         THEN 1 ELSE 0 END AS passed\n"
            f"FROM {self.table_name};"
        )

    def column_has_no_nulls(self):
        return (
            f"SELECT\n"
            f"    COUNT(*) AS total_rows,\n"
            f"    SUM(CASE WHEN {self.column_name} IS NULL THEN 1 ELSE 0 END) AS null_count,\n"
            f"    CASE WHEN SUM(CASE WHEN {self.column_name} IS NULL THEN 1 ELSE 0 END) = 0 "
            f"         THEN 1 ELSE 0 END AS passed\n"
            f"FROM {self.table_name};"
        )

    def column_has_values_greater_than(self, threshold):
        return (
            f"SELECT\n"
            f"    COUNT(*) AS total_rows,\n"
            f"    SUM(CASE WHEN {self.column_name} <= {threshold} THEN 1 ELSE 0 END) AS failed_rows,\n"
            f"    {threshold} AS min_expected_value,\n"
            f"    CASE WHEN SUM(CASE WHEN {self.column_name} <= {threshold} THEN 1 ELSE 0 END) = 0 "
            f"         THEN 1 ELSE 0 END AS passed\n"
            f"FROM {self.table_name};"
        )

    def column_median_is_between(self, lower_bound, upper_bound):
        return (
            f"SELECT\n"
            f"    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {self.column_name}) AS observed_value,\n"
            f"    {lower_bound} AS expected_lower_bound,\n"
            f"    {upper_bound} AS expected_upper_bound,\n"
            f"    CASE WHEN PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {self.column_name}) "
            f"              BETWEEN {lower_bound} AND {upper_bound} "
            f"         THEN 1 ELSE 0 END AS passed\n"
            f"FROM {self.table_name};"
        )

    def column_non_negative(self):
        return (
            f"SELECT\n"
            f"    COUNT(*) AS total_rows,\n"
            f"    SUM(CASE WHEN {self.column_name} < 0 THEN 1 ELSE 0 END) AS failed_rows,\n"
            f"    CASE WHEN SUM(CASE WHEN {self.column_name} < 0 THEN 1 ELSE 0 END) = 0 "
            f"         THEN 1 ELSE 0 END AS passed\n"
            f"FROM {self.table_name};"
        )
