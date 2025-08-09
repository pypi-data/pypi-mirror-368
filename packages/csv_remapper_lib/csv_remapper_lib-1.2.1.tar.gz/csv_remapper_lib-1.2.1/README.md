# CSV Remapper

**CSV Remapper** is a powerful Python library designed to easily transform and manipulate CSV files using customizable mapping files. Streamline your data workflows and automate common CSV cleaning and transformation tasks.

## Key Features

- **Rename columns:** Effortlessly rename columns based on your mapping rules.
- **Remove columns:** Effortlessly rename columns based on your mapping rules.
- **Merge columns:** Combine values from multiple columns, choosing the order and separator.
- **Convert values to positive:** Transform numeric values to their absolute value by key.
- **Convert values to negative:** Transform numeric values to negative by key.
- **Normalize dates:** Standardize date formats in selected columns.
- **Convert to JSON:** Convert CSV format to JSON.

## Why use CSV Remapper?

- **Easy to use:** Intuitive API and clear documentation.
- **Flexible:** Adapt CSV transformations to any workflow.
- **Automatable:** Perfect for data pipelines and batch processing.
- **Open Source:** Community-maintained and open source.

## Installation

```bash
pip install csv-remapper-lib
```

## Usage Example

```python
from csv_remapper_lib import CsvRemapper

csv = CsvRemapper("data.csv")
csv.rename_key("example_key", "new_key")
csv.save("data.csv")
```

## Contributing

Contributions are welcome! See the [CONTRIBUTING.md](CONTRIBUTING.md) file for more information.

---
## License

This project is licensed under the GNU Affero General Public License v3.0. See the [LICENSE](LICENSE) file for details.

**Keywords:** csv, python, data transformation, data cleaning, csv processing, automation, data engineering
