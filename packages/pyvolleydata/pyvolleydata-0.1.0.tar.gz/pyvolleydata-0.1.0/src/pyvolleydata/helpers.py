import pandas as pd
from datetime import datetime


def validate_seasons(seasons, league_start_year):
    """
    Checks whether all the provided seasons are valid years and raises an error if not.

    Parameters
    ----------
    seasons: list of int
        A list of years representing seasons to validate.

    Returns
    -------
    None

    Examples
    --------
    >>> validate_seasons([2024, 2025], 2024)
    >>> validate_seasons(['2020'], 2024)  # Raises TypeError
    >>> validate_seasons([2022, 2023, 2030], 2024)  # Raises ValueError
    """
    if not isinstance(seasons, list):
        raise TypeError('Expected a list of years')
    for year in seasons:
        if not isinstance(year, int):
            raise TypeError(f'Expected an integer for year, got {type(year).__name__}')
        if year < league_start_year or year > datetime.now().year:
            raise ValueError(f'Year {year} out of valid range ({league_start_year}-{datetime.now().year})')