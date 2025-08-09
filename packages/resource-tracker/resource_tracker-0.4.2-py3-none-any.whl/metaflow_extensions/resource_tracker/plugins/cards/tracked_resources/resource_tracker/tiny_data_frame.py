"""
A very inefficient data-frame implementation for manipulating resource usage data.

If you don't like this helper class, grab the `_data` instance attribute that is
a list of lists (column vectors) and do whatever you want with it.
"""

from collections import defaultdict
from csv import QUOTE_MINIMAL, QUOTE_NONNUMERIC, DictReader
from csv import writer as csv_writer
from io import StringIO
from logging import getLogger
from time import sleep
from typing import Callable, Dict, Iterator, List, NamedTuple, Optional, Union
from urllib.parse import urlparse
from urllib.request import urlopen

logger = getLogger(__name__)


class StatSpec(NamedTuple):
    """Specification of a statistic to collect on a column.

    Args:
        column: The name of the column to apply the agg function to.
        agg: The aggregation function to apply to the column.
        agg_name: The name of the field to store the statistic in. Defaults to None, which means using the name of the agg function.
        round: The number of decimal places to round the statistic to. Defaults to None, which means no rounding.
    """

    column: str
    agg: Callable
    agg_name: Optional[str] = None
    round: Optional[int] = None


class TinyDataFrame:
    """A very inefficient data-frame implementation with a few features.

    Supported features:

    - reading CSV files from a remote URL
    - reading CSV files from a local file
    - converting a dictionary of lists/arrays to a data-frame
    - converting a list of dictionaries to a data-frame
    - slicing rows
    - slicing columns
    - slicing rows and columns
    - printing a summary of the data-frame
    - printing the data-frame as a human-readable (grid) table
    - renaming columns
    - writing to a CSV file
    - computing statistics on columns

    Args:
        data: Dictionary of lists/arrays or list of dictionaries.
        csv_file_path: Path to a properly quoted CSV file.

    Example:

        >>> df = TinyDataFrame(csv_file_path="https://raw.githubusercontent.com/plotly/datasets/refs/heads/master/mtcars.csv")
        >>> df
        TinyDataFrame with 32 rows and 12 columns. First row as a dict: {'manufacturer': 'Mazda RX4', 'mpg': 21.0, 'cyl': 6.0, 'disp': 160.0, 'hp': 110.0, 'drat': 3.9, 'wt': 2.62, 'qsec': 16.46, 'vs': 0.0, 'am': 1.0, 'gear': 4.0, 'carb': 4.0}
        >>> df[2:5][['manufacturer', 'hp']]
        TinyDataFrame with 3 rows and 2 columns. First row as a dict: {'manufacturer': 'Datsun 710', 'hp': 93.0}
        >>> print(df[2:5][['manufacturer', 'hp']])  # doctest: +NORMALIZE_WHITESPACE
        TinyDataFrame with 3 rows and 2 columns:
        manufacturer      | hp
        ------------------+------
        Datsun 710        |  93.0
        Hornet 4 Drive    | 110.0
        Hornet Sportabout | 175.0
        >>> print(df[2:5][['manufacturer', 'hp']].to_csv())  # doctest: +NORMALIZE_WHITESPACE
        "manufacturer","hp"
        "Datsun 710",93.0
        "Hornet 4 Drive",110.0
        "Hornet Sportabout",175.0
    """

    _data: List[List[float]] = []
    """Column vectors"""
    columns: List[str] = []
    """Column names"""

    def __init__(
        self,
        data: Optional[Union[Dict[str, List[float]], List[Dict[str, float]]]] = None,
        csv_file_path: Optional[str] = None,
        retries: int = 0,
        retry_delay: float = 0.1,
    ):
        """
        Initialize with either:

        - Dictionary of lists/arrays
        - List of dictionaries
        - CSV file path

        Args:
            data: Dictionary of lists/arrays or list of dictionaries.
            csv_file_path: Path to a properly quoted CSV file.
            retries: Number of retry attempts if reading CSV fails. Defaults to 0.
            retry_delay: Initial delay between retries in seconds. Doubles after each retry. Defaults to 0.1.
        """
        assert data is not None or csv_file_path is not None, (
            "either data or csv_file_path must be provided"
        )
        assert data is None or csv_file_path is None, (
            "only one of data or csv_file_path must be provided"
        )
        assert data is None or isinstance(data, dict) or isinstance(data, list), (
            "data must be a dictionary or a list"
        )
        assert csv_file_path is None or isinstance(csv_file_path, str), (
            "csv_file_path must be a string"
        )

        if csv_file_path:
            data = self._read_csv(
                csv_file_path, retries=retries, retry_delay=retry_delay
            )

        if isinstance(data, dict):
            self._data = list(data.values())
            self.columns = list(data.keys())
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            # let's preserve column order as seen in the first row(s)
            self.columns = []
            seen_columns = set()
            for row in data:
                for col in row.keys():
                    if col not in seen_columns:
                        self.columns.append(col)
                        seen_columns.add(col)
            self._data = [[row.get(col) for row in data] for col in self.columns]

    def _read_csv(
        self, csv_file_path: str, retries: int = 0, retry_delay: float = 0.1
    ) -> list[dict]:
        """Read a CSV file and return a list of dictionaries.

        This function is used to read a properly formatted CSV file (quoted
        strings, header, same columns used on all lines) and return a list of
        dictionaries. It will retry up to `retries` times if the file is not
        found or cannot be read, e.g. because the file is being locked for
        writing by another process. The retry delay will be doubled after each
        attempt.

        Args:
            csv_file_path: CSV file path or URL.
            retries: Number of retry attempts if reading fails. Defaults to 0.
            retry_delay: Initial delay between retries in seconds. Doubles after each retry. Defaults to 0.1.

        Raises:
            Exception: If reading the CSV file fails after all retry attempts.
        """
        last_error = None
        for attempt in range(retries + 1):
            csv_source = None
            try:
                parsed = urlparse(csv_file_path)
                if parsed.scheme in ("http", "https"):
                    with urlopen(csv_file_path) as response:
                        content = response.read().decode("utf-8").splitlines()
                        csv_source = content
                else:
                    csv_source = open(csv_file_path, "r", newline="")
                records = list(DictReader(csv_source, quoting=QUOTE_NONNUMERIC))
                for record in records:
                    if None in record.keys():
                        raise ValueError("Corrupt CSV file with unknown column names.")
                return records
            except Exception as e:
                last_error = e
                if attempt < retries:
                    logger.debug(
                        f"Failed to read CSV file: {csv_file_path}. "
                        f"Retry attempt {attempt + 1}/{retries}..."
                    )
                    sleep(retry_delay)
                    retry_delay *= 2
                    continue
            finally:
                if hasattr(csv_source, "close"):
                    csv_source.close()

        # all retries failed
        raise RuntimeError(
            f"Failed to read CSV file after {retries + 1} attempts: {csv_file_path}"
        ) from last_error

    def __len__(self):
        """Return the number of rows in the data-frame"""
        return len(self._data[0]) if self.columns else 0

    def __getitem__(
        self, key: Union[str, List[str], int, slice]
    ) -> Union[List[float], Dict[str, float], "TinyDataFrame"]:
        """Get a single column or multiple columns or a row or a slice of rows. Can be chained.

        Args:
            key: A single column name, a list of column names, a row index, or a slice of row indexes.

        Returns:
            A single column as a list, a list of columns as a new TinyDataFrame, a row as a dictionary, or a slice of rows as a new TinyDataFrame.
        """
        # a single column
        if isinstance(key, str):
            if key in self.columns:
                return self._data[self.columns.index(key)]
            else:
                raise KeyError(f"Column '{key}' not found")
        # multiple columns
        elif isinstance(key, List) and all(isinstance(k, str) for k in key):
            for k in key:
                if k not in self.columns:
                    raise KeyError(f"Column '{k}' not found")
            return TinyDataFrame(
                {col: self._data[self.columns.index(col)] for col in key}
            )
        # row index
        elif isinstance(key, int):
            return {col: self._data[i][key] for i, col in enumerate(self.columns)}
        # row indexes
        elif isinstance(key, slice):
            return TinyDataFrame(
                {col: self._data[i][key] for i, col in enumerate(self.columns)}
            )
        else:
            raise TypeError(f"Invalid key type: {type(key)}")

    def __iter__(self) -> Iterator[dict]:
        """Iterate through rows of the dataframe as dictionaries.

        Returns:
            Iterator of row dictionaries
        """
        for i in range(len(self)):
            yield self[i]

    def __setitem__(self, key: str, value: List[float]) -> None:
        """Set a column with the given key to the provided values.

        Args:
            key: Column name (string)
            value: List of values for the column

        Raises:
            TypeError: If key is not a string
            ValueError: If the length of values doesn't match the dataframe length
        """
        if not isinstance(key, str):
            raise TypeError(f"Column name must be a string, got {type(key)}")

        if len(self) > 0 and len(value) != len(self):
            raise ValueError(
                f"Length of values ({len(value)}) must match dataframe length ({len(self)})"
            )

        if key in self.columns:
            self._data[self.columns.index(key)] = value
        else:
            self.columns.append(key)
            self._data.append(value)

    def head(self, n: int = 5) -> "TinyDataFrame":
        """Return first n rows as a new TinyDataFrame."""
        return self[slice(0, n)]

    def tail(self, n: int = 5) -> "TinyDataFrame":
        """Return last n rows as a new TinyDataFrame."""
        return self[slice(-n, None)]

    def __repr__(self) -> str:
        """Return a string representation of the data-frame."""
        return f"TinyDataFrame with {len(self)} rows and {len(self.columns)} columns. First row as a dict: {self[0]}"

    def __str__(self) -> str:
        """Print the first 10 rows of the data-frame in a human-readable table."""
        header = (
            f"TinyDataFrame with {len(self)} rows and {len(self.columns)} columns:\n"
        )
        if len(self) == 0:
            return header + "Empty dataframe"

        max_rows = min(10, len(self))

        col_widths = {}
        for col in self.columns:
            col_widths[col] = len(str(col))
            for i in range(max_rows):
                col_widths[col] = max(col_widths[col], len(str(self[col][i])))

        rows = []
        header_row = " | ".join(str(col).ljust(col_widths[col]) for col in self.columns)
        rows.append(header_row)
        separator = "-+-".join("-" * col_widths[col] for col in self.columns)
        rows.append(separator)

        for i in range(max_rows):
            row_values = []
            for col in self.columns:
                value = str(self[col][i])
                # right-align numbers, left-align strings
                try:
                    float(value)  # check if it's a number
                    row_values.append(value.rjust(col_widths[col]))
                except ValueError:
                    row_values.append(value.ljust(col_widths[col]))
            rows.append(" | ".join(row_values))

        # add ellipsis if there are more rows
        if len(self) > max_rows:
            rows.append("..." + " " * (len(rows[0]) - 3))
        return header + "\n".join(rows)

    def rename(self, columns: dict) -> "TinyDataFrame":
        """Rename one or multiple columns.

        Args:
            columns: Dictionary mapping old column names to new column names.

        Returns:
            Self for method chaining.

        Raises:
            KeyError: If any old column name doesn't exist in the dataframe.
        """
        for old_name in columns.keys():
            if old_name not in self.columns:
                raise KeyError(f"Column '{old_name}' not found in dataframe")

        self.columns = [columns.get(col, col) for col in self.columns]
        return self

    def to_csv(
        self, csv_file_path: Optional[str] = None, quote_strings: bool = True
    ) -> str:
        """Write the data-frame to a CSV file or return as string if no path is provided.

        Args:
            csv_file_path: Path to write CSV file. If None, returns CSV as string.
            quote_strings: Whether to quote strings.
        """
        if csv_file_path:
            f = open(csv_file_path, "w", newline="")
        else:
            f = StringIO(newline="")

        try:
            writer = csv_writer(
                f, quoting=QUOTE_NONNUMERIC if quote_strings else QUOTE_MINIMAL
            )
            writer.writerow(self.columns)
            for i in range(len(self)):
                writer.writerow([self[col][i] for col in self.columns])

            if not csv_file_path:
                return f.getvalue()
        finally:
            f.close()

    def to_dict(self) -> List[dict]:
        """Convert the data-frame to a list of row dictionaries.

        Returns:
            List of dictionaries where each dictionary represents a row
        """
        return list(self)

    def stats(self, specs: List[StatSpec]) -> dict:
        """Collect statistics from the resource tracker.

        Args:
            specs: A list of [resource_tracker.StatSpec][] objects specifying the statistics to collect.

        Returns:
            A dictionary containing the collected statistics.
        """
        stats = defaultdict(dict)
        for spec in specs:
            try:
                agg_name = spec.agg_name or spec.agg.__name__
                stats[spec.column][agg_name] = spec.agg(self[spec.column])
                if spec.round is not None:
                    stats[spec.column][agg_name] = round(
                        stats[spec.column][agg_name], spec.round
                    )
            except Exception as e:
                logger.error(
                    f"Error collecting statistic on {spec.column} with {spec.agg_name}: {e}"
                )
        return stats
