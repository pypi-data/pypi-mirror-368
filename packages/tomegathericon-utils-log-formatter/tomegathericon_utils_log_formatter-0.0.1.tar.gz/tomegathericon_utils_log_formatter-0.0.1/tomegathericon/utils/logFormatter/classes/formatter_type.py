from enum import Enum

from tomegathericon.utils.exceptions import DefaultValueError

from .formatter_config import FormatterConfig


class InvalidFormatterTypeProvidedError(DefaultValueError):
    """
    Exception raised when an invalid formatter type is provided.

    This exception is used to indicate that the provided formatter type does
    not match any of the valid options defined in the system. It extends from
    DefaultValueError and provides a detailed error message to help identify
    the invalid input.

    :ivar invalid_value: The invalid formatter type that was provided.
    :type invalid_value: str
    """

    def __init__(self, invalid_value: str) -> None:
        super().__init__(
            f"Invalid value provided for formatter type: {invalid_value} must be one of: {', '.join(list(FormatterType.__members__.keys())).lower()}")


class FormatterType(Enum):
    """
    Enumeration for different formatter types.

    This class defines distinct formatter types used for configuring
    output formatting. Each formatter type is associated with a
    specific configuration defined by the `FormatterConfig`. These
    formatter configurations include settings for delimiters and
    separators, allowing customization of the formatting behavior.

    :ivar JSON: Formatter configured with no delimiter and no separator.
    :type JSON: FormatterConfig
    :ivar KEY_VALUE: Formatter configured with ':' as a delimiter and a space as a separator.
    :type KEY_VALUE: FormatterConfig
    :ivar LOGFMT: Formatter configured with '=' as a delimiter and a space as a separator.
    :type LOGFMT: FormatterConfig
    :ivar COMMA_SEPARATED: Formatter configured with ':' as a delimiter and ',' as a separator.
    :type COMMA_SEPARATED: FormatterConfig
    """
    JSON = FormatterConfig(delimiter="", seperator="")
    KEY_VALUE = FormatterConfig(delimiter=":", seperator=" ")
    LOGFMT = FormatterConfig(delimiter="=", seperator=" ")
    COMMA_SEPARATED = FormatterConfig(delimiter=":", seperator=",")
