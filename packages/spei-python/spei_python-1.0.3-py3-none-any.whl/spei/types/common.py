# spei/types.py (or wherever you keep your custom types)
import re
from typing import Union

from pydantic import BeforeValidator
from typing_extensions import Annotated


def validate_date_int(value: int) -> int:  # noqa: WPS110
    """Validates and converts a date value to YYYYMMDD string format."""
    value_str = str(value)
    if not re.match(r'^\d{8}$', value_str):
        raise ValueError('must be 8 digits in YYYYMMDD format')

    # Additional date validation if needed
    year = int(value_str[:4])
    month = int(value_str[4:6])
    day = int(value_str[6:8])

    if year < 1900:  # noqa: WPS432
        raise ValueError('invalid year')

    if not (1 <= month <= 12 and 1 <= day <= 31):  # noqa: WPS432
        raise ValueError('invalid date')

    return int(value_str)


DateInt = Annotated[int, BeforeValidator(validate_date_int)]


def validate_institution_code(value: Union[str, int]) -> int:
    """Validates and converts an institution code to a 3 or 5-digit integer."""
    value_str = str(value)
    if not re.match(r'^\d{3,5}$', value_str):
        raise ValueError('must be exactly 3 or 5 digits')

    return int(value_str)


InstitutionCode = Annotated[int, BeforeValidator(validate_institution_code)]
