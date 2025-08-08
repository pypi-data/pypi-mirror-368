from typing import Optional, List, Union


class ParamFormatter:
    """
    A helper class to format parameters for DHIS2 API requests.

    Provides utility methods to convert lists into API-compatible
    semicolon-separated strings and to extract disaggregation elements.
    """

    @staticmethod
    def format_params(items: Union[List[Union[str, int]], None]) -> str:
        """
        Converts a list of items into a semicolon-separated string.

        Parameters
        ----------
        items : list[str | int] or None
            List of elements (e.g., dates, indicators). If None or empty, returns an empty string.

        Returns
        -------
        str
            Semicolon-separated string representation of the list items.
        """
        if not items:
            return ""
        return ";".join(str(item).strip() for item in items if item is not None)

    @staticmethod
    def format_disaggregate_elems(disaggregate: Optional[Union[List[str], str]]) -> Optional[str]:
        """
        Extracts and formats disaggregation element names from provided strings.

        This method removes any suffixes after ":" in each element, returning only the
        base element names joined by semicolons.

        Parameters
        ----------
        disaggregate : list[str] or str or None
            Disaggregation dimension(s), e.g., ["age:group", "sex:male"] or "age:group".

        Returns
        -------
        str or None
            Semicolon-separated base elements, or None if no disaggregation is provided.
        """
        if not disaggregate:
            return None

        # Ensure input is treated as a list
        elems = disaggregate if isinstance(disaggregate, list) else [disaggregate]

        # Extract only the part before ":" and format
        base_elems = [elem.split(":")[0] for elem in elems if isinstance(elem, str)]
        return ParamFormatter.format_params(base_elems)
