# generate_params.py
import itertools
from typing import List, Optional, Union
from .param_formatter import ParamFormatter
from .indicator_loader import IndicatorLoader


class GenerateParams:
    """
    A utility class to generate API request parameters for DHIS2 data extraction.
    """

    def __init__(
        self,
        country: str,
        dates: List[str],
        level: str,
        category: List[str] = ["core"],
        indicators: Optional[Union[List[str], None]] = None,
        disaggregate: Optional[str] = None,
        idfilepath: Optional[str] = None,
    ):
        """
        Initializes the parameter generator.

        Parameters
        ----------
        country : str
            Country code or name.
        dates : List[str]
            A list of periods (e.g., YYYYMM or YYYYQ).
        level : str
            Organizational unit level to query.
        category : List[str], default=["core"]
            Data categories to query.
        indicators : Optional[List[str]]
            List of indicators to fetch; if None, loaded from file.
        disaggregate : Optional[str]
            Disaggregation dimension to include.
        idfilepath : Optional[str]
            Path to an excel file with indicator definitions.
        """
        self.country = country.lower()
        self.category = category
        self.level = level

        self.dates = ParamFormatter.format_params(dates)
        self.disaggregate = disaggregate
        self.disaggregate_elems = ParamFormatter.format_disaggregate_elems(disaggregate)

        # Format indicators or load from file
        self.indicators = (
            ParamFormatter.format_params(indicators)
            if indicators
            else IndicatorLoader(self.country, category, idfilepath).load_indicators_from_file()
        )

        self.combinations = len(dates) * len(self.indicators.split(";"))
        self.dimensions = [self.level, self.dates, self.indicators]
        self.rows_elements = ["ou", "pe", "dx"]

    def split_params(
        self,
        situation: Optional[str] = None,
        chunk_size: int = 12
    ) -> itertools.product:
        """
        Generates parameter combinations based on a given strategy.

        Parameters
        ----------
        situation : Optional[str], default=None
            Strategy for splitting combinations:
            - "standard": One request with all periods.
            - "one_by_one": Individual combinations per period.
            - "chunked": Group periods into chunks of `chunk_size`.
        chunk_size : int, default=12
            Number of periods per chunk when using "chunked" strategy.

        Returns
        -------
        itertools.product
            Cartesian product of parameter combinations.
        """
        ou_items = [self.level]
        pe_items = self.dates.split(";")
        dx_items = self.indicators.split(";")

        strategies = {
            "standard": lambda: itertools.product(
                ou_items, [";".join(pe_items)], dx_items
            ),
            "one_by_one": lambda: itertools.product(
                ou_items, pe_items, dx_items
            ),
            "chunked": lambda: itertools.product(
                ou_items,
                [";".join(pe_items[i:i + chunk_size]) for i in range(0, len(pe_items), chunk_size)],
                dx_items
            )
        }

        strategy = strategies.get(situation, strategies["standard"])
        return strategy()

    def get_params(self) -> List[dict]:
        """
        Generates a list of parameter dictionaries for API requests.

        Automatically selects a splitting strategy based on data volume.

        Returns
        -------
        List[dict]
            List of parameter dictionaries for use in requests.
        """
        # Determine strategy dynamically if not set explicitly
        if self.country in ["nigeria", "ghana"]:
            strategy = "one_by_one"
        elif self.combinations >= 120:
            strategy = "chunked"
        else:
            strategy = "standard"

        combinations = self.split_params(situation=strategy)

        params = []
        for ou, pe, dx in combinations:
            dimensions = [f"ou:{ou}", f"pe:{pe}", f"dx:{dx}"]
            rows = self.rows_elements.copy()

            if self.disaggregate:
                dimensions.append(self.disaggregate)
                rows.insert(3, self.disaggregate_elems)

            param = {
                "dimension": dimensions,
                "displayProperty": "NAME",
                "ignoreLimit": "TRUE",
                "hierarchyMeta": "TRUE",
                "hideEmptyRows": "TRUE",
                "showHierarchy": "TRUE",
                "rows": ";".join(rows),
            }
            params.append(param)

        return params
