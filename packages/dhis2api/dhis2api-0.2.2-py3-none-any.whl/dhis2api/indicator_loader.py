import pandas as pd
from .param_formatter import ParamFormatter

class IndicatorLoader:
    """
    Loads indicator IDs from an Excel configuration file based on country and category filters.

    This class extracts indicators dynamically for use in DHIS2 API requests. It applies
    filtering logic to match the provided `country` and `category`, and formats the
    resulting list of indicator IDs for further use.

    Attributes
    ----------
    country : str
        The country name (lowercased) to filter indicators.
    category_str : str
        Pipe-separated string of categories for filtering.
    idfilepath : str
        Path to the Excel file containing indicator definitions.
    column : str
        Column name used for category filtering (default: "category_old").

    Methods
    -------
    load_indicators_from_file() -> str
        Loads and filters indicators from the Excel file, returning them as a
        semicolon-separated string formatted for API usage.
    """

    def __init__(
        self,
        country: str,
        category: list,
        idfilepath: str,
        column: str = None
    ):
        """
        Initialize the IndicatorLoader.

        Parameters
        ----------
        country : str
            Country code or name to filter indicators.
        category : list
            List of categories used to filter indicators.
        idfilepath : str
            Path to the Excel configuration file with indicators.
        column : str, optional
            Column name for category filtering (defaults to "category_old").
        """
        self.country = country.lower()
        self.category_str = "|".join(category)
        self.idfilepath = idfilepath
        self.column = column or "category_old"

    def load_indicators_from_file(self) -> str:
        """
        Loads indicators from an Excel file, filtering by country and category.

        The method expects the Excel file to contain at least:
        - a 'country' column
        - an 'id' column (indicator IDs)
        - a column matching `self.column` (for category filtering)

        Filtering is performed using:
        - country match (case-insensitive)
        - category substring match (using regex with OR operator)

        Returns
        -------
        str
            Semicolon-separated list of indicator IDs, formatted for API usage.

        Raises
        ------
        FileNotFoundError
            If the specified Excel file does not exist.
        ValueError
            If required columns ('id' or the category column) are missing.
        RuntimeError
            If no indicators are found after filtering.
        """
        try:
            ind_df = pd.read_excel(self.idfilepath)
        except FileNotFoundError:
            raise FileNotFoundError(f"Indicator file not found: {self.idfilepath}")

        required_columns = {"id", self.column, "country"}
        missing = required_columns - set(ind_df.columns)
        if missing:
            raise ValueError(f"Missing required columns in indicator file: {missing}")

        # Filter indicators by country and category
        filtered = ind_df[
            (ind_df["country"].str.lower() == self.country) &
            (ind_df[self.column].str.contains(self.category_str, case=False, na=False))
        ]

        if filtered.empty:
            raise RuntimeError(
                f"No indicators found for country '{self.country}' and category '{self.category_str}'."
            )

        ind_list = filtered["id"].dropna().astype(str).tolist()
        return ParamFormatter.format_params(ind_list)
