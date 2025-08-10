# 🛡️ Qualidator  
*A modern CLI for managing SQL-based data quality checks — now with connector setup.*

![Qualidator Banner](https://img.shields.io/badge/version-0.3.0-blue?style=for-the-badge)  
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen?style=for-the-badge)  
![License](https://img.shields.io/badge/license-MIT-lightgrey?style=for-the-badge)

---

## 📌 Overview
**Qualidator** is a command-line tool that helps you **define, manage, and store SQL-based data quality validations**.  
It can set up a connector to your data source and organize validation queries in a `.qualidations` folder for easy reuse and version control.

With Qualidator, you can:
- 📂 Initialize a validations project
- 🔌 Configure a connector (Databricks, Snowflake, Postgres, or None)
- ➕ Add a variety of built-in validation checks
- 🗑 Remove one or all validations
- 📊 View project status and existing validations
- 💥 Destroy the project

---

## 🚀 Installation

```bash
pip install qualidator
```
---

## ⚡ Usage
### Run qualidator --help to see available commands:
```bash
qualidator --help
```

| Command  | Description                                                            |
|----------|------------------------------------------------------------------------|
| `init`   | Initialize `.qualidations` and optionally set up a data connector      |
| `destroy`| Delete the `.qualidations` folder (use `--force` for full removal)     |
| `add`    | Add a validation                                                       |
| `remove` | Remove a validation or all validations                                 |
| `status` | Show project status and validations                                    |
| `run`    | Execute validations and show results                                   |

---

## 🛠 Examples
### 1️⃣ Initialize and set up connector
```bash
qualidator init
```
## 📦 Creates .qualidations, then asks for a data provider:
1. Databricks
2. Snowflake
3. Postgres
4. None

### If you pick one of the first three, it prompts for credentials and saves them in:
```bash
.qualidations/config.json
```

### 2️⃣ Add validations
```bash
qualidator add --name is_not_null
```
```bash
Please enter the column name to check for NOT NULL: customer_id
✔ Will check that column "customer_id" is not null.
```

### Supported validations:
| Validation                             | Description                                                                                |
|----------------------------------------|--------------------------------------------------------------------------------------------|
| `is_not_null`                          | Checks that column values are NOT NULL                                                     |
| `has_no_duplicates`                    | Checks that the column has no duplicate values                                             |
| `column_values_are_unique`             | Checks that all values in the column are unique                                            |
| `column_unique_value_count_is_between` | Checks that the number of unique values in the column is between given bounds              |
| `column_value_frequency_is_between`    | Checks that the frequency of each distinct value in the column is within given min and max |
| `no_empty_strings`                     | Checks that the column contains no empty string values                                     |
| `primary_key_check`                    | Checks that the column can serve as a primary key (unique and not null)                    |
| `distinct_ratio_is_above`              | Checks that the ratio of distinct values in the column is at least the given threshold     |
| `column_max_is_between`                | Checks that the column's MAX value is between given bounds                                 |
| `column_min_is_between`                | Checks that the column's MIN value is between given bounds                                 |
| `column_sum_is_between`                | Checks that the column's SUM value is between given bounds                                 |
| `column_mean_is_between`               | Checks that the column's MEAN value is between given bounds                                |
| `column_standard_deviation_is_between` | Checks that the column's standard deviation is between given bounds                        |
| `column_values_are_between`            | Checks that all values in the column are between given bounds                              |
| `column_has_no_nulls`                  | Checks that the column contains no NULL values                                             |
| `column_has_values_greater_than`       | Checks that all values in the column are greater than a given threshold                    |
| `column_median_is_between`             | Checks that the median value of the column is between given bounds                         |
| `column_non_negative`                  | Checks that all values in the column are non-negative                                      |
| `table_row_count_is_between`           | Checks that the table's row count is between given bounds                                  |
| `table_row_count_equals`               | Checks that the table's row count equals a given expected count                            |



### 3️⃣ Check status
```bash
qualidator status
```

```bash
============================================================
📋 VALIDATIONS IN YOUR PROJECT
------------------------------------------------------------
1. customer_id_is_not_null
2. email_column_values_are_unique
------------------------------------------------------------
✅ Total: 2 validation(s) ready to go!
💡 You can remove with:
   qualidator remove --name your_validation_name
============================================================
```

### 4️⃣ Remove validations
#### Remove all:
```bash
qualidator remove --all
```
#### Remove one:
```bash
qualidator remove --name email_column_values_are_unique
```

### 5️⃣ Run validations
#### Run all validations:
```bash
qualidator run --all
```
#### Run a single validation:
```bash
qualidator run --name my_catalog_my_schema_my_table_customer_id_is_not_null
```

### 6️⃣ Destroy the project
```bash
qualidator destroy --force
```
#### This deletes .qualidations entirely (including config and validations).


---

## 📂 Project Structure
```css
qualidator/
│
├── connectors/
│   └── databricks.py
├── inspectors/
│   ├── uniq.py
│   ├── numeric.py
├── __init__.py
├── cli.py
├── validations_registry.py
└── README.md

```

## 🤝 Contributing
Pull requests and ideas are welcome!
Open an issue if you have suggestions for new validation types or integrations.

## 📜 License
This project is licensed under the MIT License.
