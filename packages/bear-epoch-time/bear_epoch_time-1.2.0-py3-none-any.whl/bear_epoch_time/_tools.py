def add_ord_suffix(number: int) -> str:
    """Add an ordinal suffix to a given number, usually used for dates or rankings.

    Parameters:
    number: int - The number to add an ordinal suffix to.

    Returns:
    str - The number with its ordinal suffix.
    """
    eleventh = 11
    thirteenth = 13
    suffix: str = ["th", "st", "nd", "rd", "th"][min(number % 10, 4)]
    if eleventh <= (number % 100) <= thirteenth:
        suffix = "th"
    return f"{number}{suffix}"


__all__ = ["add_ord_suffix"]
