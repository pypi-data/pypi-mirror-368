import re
import operator
from enum import Enum, auto
from dateutil import parser
from datetime import datetime, timedelta, time
from copy import deepcopy

"""
CSV Remapper Library.

This module provides the CSVFile class for loading, manipulating, and saving CSV files.
It supports operations such as renaming columns, removing columns, merging columns
with various types, and converting data types (numbers, percentages, dates, and times).
"""

class MergeType(Enum):
    """
    Enumeration of supported merge operation types.
    """
    NUMBER = auto()
    TEXT = auto()
    TIME = auto()
    DATE = auto()
    PERCENTAGE = auto()

class ConnectorType:
    """
    Class used to establish the merging behavior for CSV columns.

    Args:
        type (MergeType): The type of merge operation to perform.
        operator (str): The operator for NUMBER and DATE merge types (e.g., "+", "-", "*", "/").
        delimiter (str): The string used to join text when using TEXT merge type.
        time_format (str): The output format specifier for DATE merge type:
            "d" or "D" -> Number of days
            "m" or "M" -> Number of months
            "y" or "Y" -> Number of years
            "" (empty) -> ISO date (YYYY/mm/dd).
    """
    def __init__(self, type: MergeType, operator : str = "+", delimiter : str = " ", time_format : str = "") -> None:
        self.type = type
        self.operator = operator
        self.delimiter = delimiter
        self.time_format = time_format

class CSVFile:
    """
    This class is used for making transformations to CSV files,
    like renaming, removing, merging, and type conversions.
    """
    def __init__(self, path: str = ""):
        """
        Initialize CSVFile with a file path and load its content.

        Args:
            path (str): Path to the CSV file to process.

        Raises:
            ValueError: If no path is provided.
        """
        self.path : str = path
        self.file = None
        self.content : list[list] = [] # Holds CSV data as list of rows
        self.content_keys : list = []
        self.delimiter : str = "," # Default delimiter before detection
        self.open_file() # Load file contents into memory
        
    def open_file(self):
        """
        Open and read the CSV file, detect its delimiter,
        replace Spanish-style floats, and load content into rows.

        Returns:
            file object: The opened file handle.

        Raises:
            ValueError: If the path is not provided.
        """
        if not self.path:
            raise ValueError("Path to the CSV file is not provided.")
        # Read entire file into string for preprocessing
        with open(self.path, 'r', encoding='utf-8') as file:
            self.file = file
            str_content = file.read()

            # Convert quoted Spanish floats (e.g., "123,45") to standard format 123.45
            spanish_float_numbers : list[str] = re.findall('"[0-9]+,[0-9]+"', str_content)
            for spanish_number in spanish_float_numbers:
                # Delete " simbol, then divide the numbers by comma. Replace the original number by new one using dot instead comma
                new_number_divided = spanish_number.replace('"', "").split(",")
                new_number = '%s.%s' % (new_number_divided[0], new_number_divided[1])
                str_content = str_content.replace(spanish_number, new_number)

            # Split text into lines and detect delimiter from header row
            counter = 0
            for line in str_content.split("\n"):
                # Skip empty lines
                if len(line) == 0:
                    continue
                # To look for the delimiter of the csv file we are comparing the number of times
                # that one of each posibilities apears at keys row. It has to be 1 time less than the number of keys.
                if counter == 0:
                    # Evaluate common delimiters and pick the one matching header columns
                    posible_delimiters = {
                        ",": line.count(","),
                        ";": line.count(";"),
                        "\t": line.count("\t"),
                        "|": line.count("|"),
                        ":": line.count(":")
                    }
                    for delimiter_key in posible_delimiters.keys():
                        splitted_keys = line.split(delimiter_key)
                        delimiter_counts = posible_delimiters.get(delimiter_key)
                        if delimiter_counts != 0 and delimiter_counts == len(splitted_keys) - 1:
                            self.delimiter = delimiter_key
                            break
                # Adding lists of items to content splitted by calculated delimiter 
                raw_cells = line.split(self.delimiter)
                types_cells = [self.__infer_type(c) for c in raw_cells]
                self.content.append(types_cells)
                counter += 1
            self.content_keys = self.content[0]
        return self.file
    
    def close_file(self):
        """
        Close the file handle if it is currently open.
        """
        if self.file:
            self.file.close()
            self.file = None
            self.content = []
    
    def merge_keys(self, ordered_key_list: list[str], connector: ConnectorType, new_key_name: str, delete_old_keys: bool = True) -> None:
        """
        Merge multiple columns into a single new column based on connector settings.

        Args:
            ordered_key_list (list[str]): Column names to merge, in sequence.
            connector (ConnectorType): Defines how values combine:

                For MergeType.TEXT, concatenates strings using connector.delimiter (default is " ").
                For MergeType.NUMBER, applies connector.operator (e.g., "+" by default) between numeric values.
                For MergeType.PERCENTAGE, needs exactly two values per row or a numeric base and one column name:
                  first element can be a number (constant base) or a column name (base per row);
                  calculates second value as percentage of base and appends "%".
                For MergeType.DATE, requires at least two dates per row;
                  parses to timestamps, applies connector.operator, then formats according to connector.time_format:
                    "d"/"D" for days, "m"/"M" for months, "y"/"Y" for years,
                    or ISO date (YYYY-MM-DD) if empty.
                For MergeType.TIME, requires at least two ISO-format time strings per row;
                  converts to timedeltas and applies connector.operator, returning an ISO 8601 duration.

            new_key_name (str): Column header for merged data.
            delete_old_keys (bool): Remove original columns after merging if True.

        Raises:
            ValueError: On empty key list, missing keys, invalid connector settings, or merge errors.
        """
        # Create a working copy to avoid mutating original content
        tmp_content = deepcopy(self.content)
        key_indexes = [] # Store column indices for merging
        keys_not_found = [] # Track keys not found in header
        # Map string operators to actual functions
        ops = {
                "+": operator.add,
                "-": operator.sub,
                "x": operator.mul,
                "*": operator.mul,
                "/": operator.truediv,
                "//": operator.floordiv,
                }

        # Append header for new merged column
        tmp_content[0].append(new_key_name)

        
        if not isinstance(ordered_key_list, list) or len(ordered_key_list) == 0:
            raise ValueError("Ordered key list is empty")
        
        # Optional base value for percentage merges
        base_percentage_value = None
        if isinstance(ordered_key_list[0], (int, float)):
            base_percentage_value = ordered_key_list[0]
            ordered_key_list.pop(0)

        # Resolve header names to column indexes
        for key in ordered_key_list:
            key_index = self.__found_key(key)
            if key_index != None:
                key_indexes.append(key_index)
            else:
                keys_not_found.append(key)
        
        # Raise error if there is any key at list that was not found
        if len(keys_not_found) > 0:
            raise ValueError("Keys: %s, were not found" % (str(keys_not_found)))

        # Iterate over each data row to compute merged value
        for idx, row in enumerate(tmp_content):
            if idx == 0:
                continue # Skip header row
            new_value = ""
            for index in key_indexes:
                if connector.type == MergeType.TEXT:
                    # Perform text concatenation
                    if connector.delimiter == None:
                        raise ValueError("Connector delimiter cannot be None for TEXT type")
                    if new_value == "":
                        new_value = row[index]
                    else:
                        new_value += connector.delimiter + row[index]
                elif connector.type == MergeType.NUMBER:
                    # Numeric operations (add/subtract/etc.)
                    if not isinstance(new_value, (int, float)):
                        try:
                            new_value = float(row[index])
                        except ValueError:
                            raise ValueError("One value are not numbers")  
                    else:
                        fn = ops.get(connector.operator)
                        if fn is None:
                            raise ValueError(f"Unknown operator: {connector.operator!r}")
                        try:
                            new_value = fn(new_value, float(row[index]))
                        except ValueError:
                            raise ValueError("One value are not numbers")
                elif connector.type == MergeType.PERCENTAGE:
                    # Percentage: calculate value relative to base_pct or first column
                    if base_percentage_value and len(ordered_key_list) != 1 or not base_percentage_value and len(ordered_key_list) != 2:
                        raise ValueError("There are necesary only 2 keys to calculate the percentage")
                    new_value = base_percentage_value if base_percentage_value else ""
                    try:
                        if not isinstance(new_value, (int, float)):
                            new_value = float(row[index])
                        else:
                            new_value = round(float(row[index])*100/new_value, 2)
                            new_value = str(new_value) + "%"
                    except ValueError as e:
                        raise ValueError("Value: %s could not be converted to number" % (row[index]))
                elif connector.type == MergeType.DATE:
                    # Date arithmetic using timestamps
                    try:
                        if isinstance(row[index], datetime):
                            value_timestamp = row[index].timestamp()
                        else:
                            value_timestamp = parser.parse(row[index]).timestamp()

                        if not isinstance(new_value, (int, float)):
                            new_value = value_timestamp
                        else:
                            fn = ops.get(connector.operator)
                            if fn is None:
                                raise ValueError(f"Unknown operator: %s" % (connector.operator))
                            # Timestamp calculated date
                            new_value = fn(new_value, value_timestamp)
                    except parser.ParserError: 
                        raise ValueError("One or more values are not a date")
                elif connector.type == MergeType.TIME:
                    # Time arithmetic using timedeltas
                    if not isinstance(new_value, (timedelta)):
                        # Time sould have ISO format %T:%M:%s
                        try:
                            time_from_str = time.fromisoformat(row[index])
                        except ValueError: 
                            raise ValueError("Invalid time isoformat string: %s" % (row[index]))
                        
                        new_value = timedelta(
                            hours=time_from_str.hour,
                            minutes=time_from_str.minute,
                            seconds=time_from_str.second
                        )
                    else:
                        fn = ops.get(connector.operator)
                        if fn is None:
                            raise ValueError(f"Unknown operator: %s" % (connector.operator))
                        try:
                            time_from_str = time.fromisoformat(row[index])
                        except ValueError: 
                            raise ValueError("Invalid time isoformat string: %s" % (row[index]))
                        new_value = fn(
                            new_value, 
                            timedelta(
                                hours=time_from_str.hour,
                                minutes=time_from_str.minute,
                                seconds=time_from_str.second
                            )
                        )
                    
                else:
                    raise ValueError("Connector type is not valid")
            
            # Format date result according to time_format specifier
            if connector.type == MergeType.DATE and isinstance(new_value, (int, float)):
                if connector.time_format == "d" or connector.time_format == "D":
                    new_value = round(new_value/60/60/24, 2)
                elif connector.time_format == "m" or connector.time_format == "M":
                    new_value = round(new_value/60/60/24/30, 2)
                elif connector.time_format == "y" or connector.time_format == "Y":
                    new_value = round(new_value/60/60/24/30/12, 2)
                else:
                    new_value = datetime.fromtimestamp(new_value).date()

            new_value = str(new_value)

            # Quote merged value if it contains delimiter or newline
            if isinstance(new_value, str) and (self.delimiter in new_value or "\n" in new_value):
                new_value = '"'+ new_value +'"'
            row.append(new_value)

        # Commit merged content and optionally drop original columns
        self.content = tmp_content
        if delete_old_keys:
            self.remove_keys(ordered_key_list)

    
    def rename_key(self, old_key: str, new_key: str):
        """
        Rename a single column in the CSV header.

        Args:
            old_key (str): Existing column name to replace.
            new_key (str): New column name.

        Raises:
            KeyError: If old_key is not found.
        """
        key_index = None

        # Found Index for matching key
        key_index = self.__found_key(old_key)

        if key_index != None:
            self.content[0][key_index] = new_key
        else:
            raise Exception("Old key not found")
    
    def rename_keys(self, key_dict: dict[str, str]):
        """
        Rename multiple columns based on a mapping dictionary.

        Args:
            key_map (dict): Mapping of old_key to new_key.

        Raises:
            KeyError: If any old_key in mapping is not found.
        """
        tmp_content = deepcopy(self.content)
        for old_key in key_dict.keys():
            # Found Index for matching key
            key_index = self.__found_key(old_key)
            if key_index == None:
                raise Exception("One or more key in dict not found")
                
            tmp_content[0][key_index] = key_dict.get(old_key)
        
        self.content = tmp_content

    def remove_key(self, key: str):
        """
        Remove a single column from the CSV content.

        Args:
            key (str): Column name to remove.

        Raises:
            KeyError: If key is not found.
        """
        key_index = None

        # Found Index for matching key
        key_index = self.__found_key(key)

        if key_index != None:
            for row in self.content:
                row.pop(key_index)
        else:
            raise Exception("Key not found")
    
    def remove_keys(self, keys: list[str]):
        """
        Remove multiple columns from the CSV content.

        Args:
            keys (list): List of column names to remove.

        Raises:
            KeyError: If any key is not found.
        """
        key_indexes = []
        for key in keys:
            key_indexes.append(self.__found_key(key))
        
        if None not in key_indexes:
            # IMPORTANT: Order indexes desc to delete last items first
            key_indexes.sort(reverse=True)

            for idx, row in enumerate(self.content):
                for key in key_indexes:
                    try:
                        row.pop(key)
                    except IndexError as e:
                        raise ValueError("The %s row: %s have not enought elemnts: Index out of range" % (str(idx), str(row)))
        else:
            raise Exception("One or more keys not found")
        
    def to_positive_number(self, key: str) -> int | list[int]:
        """
        Convert all values in the specified column to their absolute (positive) values.

        Args:
            key (str): Column name to convert.

        Returns:
            int: 0 if all conversions succeeded, -1 if none succeeded.
            list[int]: List of row indices where conversion failed (header row is 0).

        Raises:
            KeyError: If key is not found.
        """
        key_index = self.__found_key(key)
        if key_index is None:
            raise Exception("Key not found")
        error_row_indexes = []
        
        for idx, row in enumerate(self.content):
            if idx > 0:
                try:
                    value = float(row[key_index])
                    if value < 0:
                        value = value * -1
                    row[key_index] = str(value)

                except Exception as e:
                    error_row_indexes.append(idx)
        # Case no errors
        if len(error_row_indexes) == 0:
            return 0
        # Case all values error
        elif len(error_row_indexes) == len(self.content) - 1:
            return -1
        # Case some errores
        else:
            return error_row_indexes
    
    def to_negative_number(self, key: str) -> int | list[int]:
        """
        Convert all values in the specified column to negative values.

        Args:
            key (str): Column name to convert.

        Returns:
            int: 0 if all conversions succeeded, -1 if none succeeded.
            list[int]: List of row indices where conversion failed (header row is 0).

        Raises:
            KeyError: If key is not found.
        """
        key_index = self.__found_key(key)
        if key_index is None:
            raise Exception("Key not found")
        error_row_indexes = []
        
        for idx, row in enumerate(self.content):
            if idx > 0:
                try:
                    value = float(row[key_index])
                    if value > 0:
                        value = value * -1
                    row[key_index] = str(value)

                except Exception as e:
                    error_row_indexes.append(idx)
        # Case no errors
        if len(error_row_indexes) == 0:
            return 0
        # Case all values error
        elif len(error_row_indexes) == len(self.content) - 1:
            return -1
        # Case some errores
        else:
            return error_row_indexes

    def to_date(self, key: str) -> int | list[int]:
        """
        Parse all values in the specified column into ISO date strings (YYYY-MM-DD).

        Args:
            key (str): Column name to convert.

        Returns:
            int: 0 if all conversions succeeded, -1 if none succeeded.
            list[int]: List of row indices where conversion failed (header row is 0).

        Raises:
            KeyError: If key is not found.
        """
        key_index = self.__found_key(key)
        if key_index is None:
            raise Exception("Key not found")
        error_row_indexes = []
        
        for idx, row in enumerate(self.content):
            if idx > 0:
                try:
                    value_to_change = row[key_index]
                    if isinstance(value_to_change, datetime):
                        new_value = str(value_to_change.date())
                    else:
                        new_value = str(parser.parse(value_to_change).date())
                    row[key_index] = new_value
                except parser.ParserError as e:
                    error_row_indexes.append(idx)
        # Case no errors
        if len(error_row_indexes) == 0:
            return 0
        # Case all values error
        elif len(error_row_indexes) == len(self.content) - 1:
            return -1
        # Case some errores
        else:
            return error_row_indexes

    def save(self, new_path: str = ""):
        """
        Write current CSV content back to file, overwriting or to a new path.

        Args:
            new_path (str): Optional new file path. If empty, overwrite original file.

        Raises:
            ValueError: If there is no content to save.
        """
        save_path = new_path or self.path
        if not self.content:
            raise ValueError("There is no csv data")
        # In this context, save does not perform any action as changes are saved immediately
        # after writing to the file in replace_key method.
        with open(save_path, 'w', encoding='utf-8') as file:
            # Compression algorithim
            str_content = ""
            for row_idx, row in enumerate(self.content):
                for item_idx, item in enumerate(row):
                    item = str(item)
                    if item_idx == 0:
                        str_content += item
                    else:
                        str_content += self.delimiter + item
                # Prevent to add new line character to end of file
                if row_idx + 1 != len(self.content):
                    str_content += "\n"

            file.write(str_content)

    def to_json(self) -> list[dict]:
        """
        Convert the CSV content to a list of dictionaries (JSON-like structure).

        Returns:
            list[dict]: List of dictionaries, each representing a row with column names as keys.

        Raises:
            ValueError: If there is no CSV data loaded.
        """
        if not self.content:
            raise ValueError("There is no CSV data")
        json_content = []
        for row_idx, row in enumerate(self.content):
            if row_idx > 0:
                json_row = {}
                for item_idx, item in enumerate(row):
                    json_row[self.content_keys[item_idx]] = item
                json_content.append(json_row)
        return json_content

    def type_of(self, key_name: str):
        """
        Get the data type of all values in the specified column.

        Args:
            key_name (str): The column name to check.

        Returns:
            type: The type if all values in the column are of the same type, otherwise None.

        Raises:
            ValueError: If there is no CSV content or key_name is invalid.
        """
        if not self.content:
            raise ValueError("There is no CSV content")
        if not key_name or not isinstance(key_name, str):
            raise ValueError("The key_name is missing or not a string")
        key_idx = self.__found_key(key_name)
        # Get a set of all types present in the column values (excluding header)
        key_type_values = {type(value[key_idx]) for value in self.content[1:]}
        # If only one type exists, return it; otherwise, return None
        return key_type_values.pop() if key_type_values and len(key_type_values) == 1 else None

    def all_key_types(self):
        """
        Get the data type for each column in the CSV.

        Returns:
            dict: Dictionary mapping column names to their data type (or None if mixed types).

        Raises:
            ValueError: If there is no CSV content or header is invalid.
        """
        if not self.content:
            raise ValueError("There is no CSV content")
        if not self.content_keys or not isinstance(self.content_keys, list):
            raise ValueError("The header row is missing or invalid")
        key_type_dict = {}
        for key in self.content_keys:
            key_idx = self.__found_key(key)
            # Get a set of all types present in the column values (excluding header)
            key_type_values = {type(value[key_idx]) for value in self.content[1:]}
            # If only one type exists, use it; otherwise, set as None
            key_type = key_type_values.pop() if key_type_values and len(key_type_values) == 1 else None
            key_type_dict[key] = key_type

        return key_type_dict

    def __found_key(self, key: str = ""):
        """
        Find the index of a column name in the header row.

        Args:
            key (str): Column name to search for.

        Returns:
            int: Index of the column, or None if not found.
        """
        for idx, csv_key in enumerate(self.content[0]):
            if key == csv_key:
                return idx
        return None
    
    def __infer_type(self, s: str):
        """
        Attempt to infer the type of the input string.

        Tries to convert the input string to:
            1. int (if it matches an integer pattern)
            2. float (if it matches a decimal number pattern)
            3. datetime (if it matches known date formats: YYYY-MM-DD or DD/MM/YYYY)
            4. str (if none of the above patterns match)

        Args:
            s (str): The input string to infer type for.

        Returns:
            int | float | datetime | str: The value converted to the inferred type, or the original string if no match.
        """
        valid_datetime_formats = (
            "%Y-%m-%d",            # 2025-08-07
            "%d/%m/%Y",            # 07/08/2025
            "%d-%m-%Y",            # 07-08-2025
            "%Y-%m-%dT%H:%M:%S",   # 2025-08-07T14:30:00
            "%Y-%m-%dT%H:%M:%S%z", # 2025-08-07T14:30:00+0200
            "%Y-%m-%d %H:%M:%S",   # 2025-08-07 14:30:00
            "%d %B %Y",            # 7 August 2025
            "%d %b %Y",            # 7 Aug 2025
            "%B %d, %Y",           # August 7, 2025
            "%b %d, %Y",           # Aug 7, 2025
            "%d.%m.%Y",            # 07.08.2025
            "%A, %d %B %Y",        # Thursday, 07 August 2025
        )

        # 1) Try integer (e.g., "123" or "-123")
        if re.fullmatch(r"-?\d+", s):
            return int(s)
        # 2) Try float (e.g., "123.45" or "-123.45")
        if re.fullmatch(r"-?\d+\.\d+", s):
            return float(s)
        # 3) Try date (formats: "2025-08-07" or "07/08/2025")
        for fmt in valid_datetime_formats:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                pass
        # 4) If no match, return as string
        return s