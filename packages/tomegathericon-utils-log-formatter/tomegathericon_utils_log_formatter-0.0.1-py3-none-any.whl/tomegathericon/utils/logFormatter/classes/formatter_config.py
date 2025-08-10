from dataclasses import dataclass


@dataclass
class FormatterConfig:
    """
    Represents the configuration for a text formatter.

    This class is used to define the configuration parameters such as the delimiter
    and separator that a formatter will utilize for organizing and processing textual
    data. It ensures that the formatting rules can be customized and reused as needed.

    :ivar delimiter: The delimiter used to separate values in the formatting process.
    :type delimiter: str
    :ivar seperator: The separator used to split segments in the formatting process.
    :type seperator: str
    """
    delimiter: str
    seperator: str
