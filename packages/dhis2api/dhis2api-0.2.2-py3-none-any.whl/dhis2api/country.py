"""Country data downloader with controlled parallelism and progress bar.

This module provides a `Country` class to fetch country-level data from an HTTP
API using bounded parallel requests. Responses are parsed into DataFrames,
saved once as a single CSV, and validated against requested indicators.
"""

from __future__ import annotations

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from .generate_params import GenerateParams

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Country:
    """
    Fetch and store country-level data from an API with controlled parallelism.

    Generates API query parameters via ``GenerateParams``, performs parallel GET
    requests with a bounded number of workers, aggregates results in memory,
    writes a single CSV, and validates that all requested indicators were
    retrieved.

    Parameters
    ----------
    base_url : str
        Base API endpoint for requests.
    country : str
        Country code or identifier (also used in output filename).
    dates : list[str]
        Date string consumed by the API.
    level : str, optional
        Geographic/administrative level to request.
    folderpath : str, optional
        Directory path to save the output CSV. Defaults to current directory.
    category : str, default "core"
        Data category to request (forwarded to ``GenerateParams``).
    indicators : list[str], optional
        Indicator codes to request (forwarded to ``GenerateParams``).
    disaggregate : list[str], optional
        Disaggregation dimensions (forwarded to ``GenerateParams``).
    auth : tuple[str, str], optional
        ``(username, password)`` tuple for HTTP basic auth.
    idfilepath : str, optional
        Path to an excel file used by ``GenerateParams``.
    max_workers : int, default 5
        Maximum number of concurrent HTTP requests.

    Attributes
    ----------
    base_url : str
    country : str
    params : list[dict]
        List of parameter dictionaries used for each API request.
    disaggregate_name : str
        Concatenation of disaggregation keys used in file naming.
    folderpath : str
    max_workers : int
    filepath : str or None
        Output CSV path (set in ``request_and_save``).
    headers : list[str] or None
        Last-seen column names parsed from the API response.
    """

    def __init__(
        self,
        base_url: str,
        country: str,
        dates: str,
        level: Optional[str] = None,
        folderpath: Optional[str] = None,
        category: str = "core",
        indicators: Optional[List[str]] = None,
        disaggregate: Optional[List[str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        idfilepath: Optional[str] = None,
        max_workers: int = 5,
    ) -> None:
        self.country: str = country
        self.generate_params = GenerateParams(
            country=country,
            dates=dates,
            level=level,
            category=[category],
            indicators=indicators,
            disaggregate=disaggregate,
            idfilepath=idfilepath,
        )
        self.base_url: str = base_url
        self.auth: Optional[Tuple[str, str]] = auth
        self.params: List[Dict] = self.generate_params.get_params()
        self.disaggregate: Optional[List[str]] = disaggregate
        self.disaggregate_name: str = "".join(
            disaggregate) if disaggregate else ""
        self.folderpath: str = folderpath or "./"
        self.max_workers: int = max_workers
        self.filepath: Optional[str] = None
        self.headers: Optional[List[str]] = None

    def request_and_save(self) -> None:
        """
        Download data in parallel with a progress bar and write to CSV.

        Creates a timestamped output filename that includes the country and,
        if present, the disaggregation label. Issues multiple HTTP GET requests
        in parallel (bounded by ``max_workers``), aggregates DataFrames in
        memory, writes a single CSV file, and validates downloaded indicators.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If no parameters are available for download.
        """
        if not self.params:
            raise ValueError(
                "No parameters to request. Check GenerateParams configuration.")

        today = datetime.today().strftime("%m-%d-%Y")
        filename = f"{self.country}_{self.disaggregate_name + '_' if self.disaggregate else ''}{today}.csv"
        self.filepath = os.path.join(self.folderpath, filename)

        logger.info("Starting download for %s (%d params)",
                    self.country, len(self.params))

        dataframes: List[pd.DataFrame] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._download_param, idx, param, today): idx
                for idx, param in enumerate(self.params)
            }

            for future in tqdm(
                as_completed(futures),
                total=len(futures),
                desc=f"Downloading {self.country}",
            ):
                idx, df = future.result()
                if df is not None and not df.empty:
                    dataframes.append(df)
                else:
                    logger.debug("No data appended for param index %d", idx)

        if dataframes:
            final_df = pd.concat(dataframes, ignore_index=True)
            final_df.to_csv(self.filepath, index=False)
            logger.info("Saved %d rows to %s", len(final_df), self.filepath)
        else:
            self._save_empty_file()
            logger.warning("No data downloaded for %s", self.country)

        self._post_download_examine()

    def _download_param(self, idx: int, param: Dict, today: str) -> Tuple[int, Optional[pd.DataFrame]]:
        """
        Download a single parameter set and parse its response.

        Parameters
        ----------
        idx : int
            Zero-based parameter index (for logging).
        param : dict
            API query parameters for this request.
        today : str
            Current date string (``MM-DD-YYYY``) added to the DataFrame.

        Returns
        -------
        tuple[int, pandas.DataFrame or None]
            The index and a DataFrame if successful; otherwise ``None``.
        """
        try:
            response = requests.get(
                self.base_url, params=param, auth=self.auth, timeout=300)
            if response.status_code == 200:
                return idx, self._parse_response(response, today)
            logger.error("[%d] HTTP %d for params: %s",
                         idx, response.status_code, param)
        except requests.RequestException as exc:
            logger.error("[%d] Request failed: %s", idx, exc)
        return idx, None

    def _parse_response(self, response: requests.Response, today: str) -> Optional[pd.DataFrame]:
        """
        Convert a JSON API response to a DataFrame and add a download date.

        Parameters
        ----------
        response : requests.Response
            Completed HTTP response with JSON content.
        today : str
            Current date string (``MM-DD-YYYY``) to append as a column.

        Returns
        -------
        pandas.DataFrame or None
            A populated DataFrame if rows are present; otherwise ``None``.
        """
        content = response.json()
        cols = [hdr.get("column") for hdr in content.get("headers", [])]
        rows = content.get("rows", [])

        if not rows:
            logger.warning("Empty data returned")
            return None

        df = pd.DataFrame(rows, columns=cols)
        df["date_downloaded"] = today
        self.headers = cols
        return df

    def _save_empty_file(self) -> None:
        """
        Create an empty CSV at ``self.filepath`` when no data was fetched.

        Returns
        -------
        None
        """
        pd.DataFrame().to_csv(self.filepath, index=False)

    def _post_download_examine(self) -> None:
        """
        Validate that all requested indicators were downloaded.

        Reads the written CSV and compares unique ``dataid`` values to the
        originally requested indicators. Logs a warning with any missing
        indicators; otherwise logs success.

        Returns
        -------
        None
        """
        try:
            df = pd.read_csv(self.filepath)
            if df.empty:
                logger.warning("Empty file for %s", self.filepath)
                return

            if "dataid" not in df.columns:
                logger.warning(
                    "Column 'dataid' not found; cannot validate indicators.")
                return

            download_set = set(df["dataid"].dropna().unique())

            # `GenerateParams.indicators` may be a semicolon-joined string or a list
            indicators = self.generate_params.indicators
            if isinstance(indicators, str):
                original = [item.strip()
                            for item in indicators.split(";") if item.strip()]
            else:
                original = list(indicators or [])

            missing = set(original) - download_set
            if missing:
                logger.warning("Missing indicators: %s",
                               ", ".join(sorted(missing)))
            else:
                logger.info("All indicators downloaded successfully.")
        except Exception as exc:
            logger.error("Error checking downloaded file: %s", exc)
