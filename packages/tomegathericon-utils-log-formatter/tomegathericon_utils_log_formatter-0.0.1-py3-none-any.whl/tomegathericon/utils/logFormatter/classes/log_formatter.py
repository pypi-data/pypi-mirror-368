import copy
from datetime import datetime, UTC
from typing import Final, FrozenSet, Any
import logging

from tomegathericon.utils.exceptions import DefaultValueError

from .formatter_type import FormatterType, InvalidFormatterTypeProvidedError


class InvalidFormatterMappingValueProvidedError(DefaultValueError):
    """
    An exception indicating that an invalid formatter mapping value was provided.

    This exception is raised when the provided mapping value is not valid.
    It suggests the user verify their input against the allowed `LogRecord` attributes
    to correct the issue.

    :ivar invalid_value: The string value that was found to be invalid.
    :type invalid_value: str
    """

    def __init__(self, invalid_value: str) -> None:
        """Initializes the exception with a detailed error message.

        The error message informs the user which value was invalid and provides
        a list of all valid `LogRecord` attributes to choose from.

        Args:
            invalid_value: The string value that was found to be invalid.
        """
        super().__init__(
            f"Invalid value provided for mapping: {invalid_value}, "
            f"must be one of: {', '.join(LogFormatter.LOG_RECORD_BUILTIN_ATTRS)}"
        )

class LogFormatter(logging.Formatter):
    """
    Represents a customizable log formatter for transforming logging records into
    various string formats. The `LogFormatter` allows flexibility in log field
    mapping, formatter types (e.g., JSON, key-value), and the inclusion of
    additional static fields.

    This class provides mechanisms to define mappings between log record attributes
    and desired output fields, supports multiple formatter types, and ensures
    defensive programming practices by encapsulating its internal state.

    :ivar LOG_RECORD_BUILTIN_ATTRS: A set of built-in attributes available in
        `logging.LogRecord`. These values are used to validate the provided field
        mappings.
    :type LOG_RECORD_BUILTIN_ATTRS: FrozenSet[str]
    :ivar DEFAULT_MAPPING: The default mapping between logging output fields and
        `LogRecord` attributes.
    :type DEFAULT_MAPPING: dict[str, str]
    :ivar DEFAULT_EXTRA_FIELDS: A default dictionary for static key-value pairs to
        be included in log outputs for all records.
    :type DEFAULT_EXTRA_FIELDS: dict[str, Any]
    :ivar SPECIAL_FIELD_MESSAGE: Reserved key for the "message" field in mappings.
    :type SPECIAL_FIELD_MESSAGE: str
    :ivar SPECIAL_FIELD_TIMESTAMP: Reserved key for the "timestamp" field in
        mappings.
    :type SPECIAL_FIELD_TIMESTAMP: str
    :ivar DEFAULT_FORMATTER_TYPE: The default formatter type used for generating
        log strings.
    :type DEFAULT_FORMATTER_TYPE: FormatterType
    """

    LOG_RECORD_BUILTIN_ATTRS: Final[FrozenSet[str]] = frozenset({
        "args", "asctime", "created", "exc_info", "exc_text",
        "filename", "funcName", "levelname", "levelno", "lineno",
        "module", "msecs", "message", "msg", "name", "pathname",
        "process", "processName", "relativeCreated", "stack_info",
        "thread", "threadName", "taskName", "timestamp"
    })

    DEFAULT_MAPPING: Final[dict[str, str]] = {
        "name": "name",
        "timestamp": "timestamp",
        "level": "levelname",
        "message": "message",
    }

    DEFAULT_EXTRA_FIELDS: Final[dict[str, Any]] = {}

    SPECIAL_FIELD_MESSAGE: Final[str] = "message"

    SPECIAL_FIELD_TIMESTAMP: Final[str] = "timestamp"

    DEFAULT_FORMATTER_TYPE: Final[FormatterType] = FormatterType.JSON

    def __init__(self) -> None:
        """Initializes the LogFormatter instance.

        Creates shallow copies of the `DEFAULT_MAPPING`, `DEFAULT_EXTRA_FIELDS`,
        and `DEFAULT_FORMATTER_TYPE` to ensure each instance has its own
        mutable, independent state. This prevents one instance's modifications
        from affecting others.
        """
        super().__init__()
        self._mapping: dict[str, str] = self.DEFAULT_MAPPING.copy()
        self._extra_fields: dict[str, Any] = self.DEFAULT_EXTRA_FIELDS.copy()
        self._formatter_type: FormatterType = self.DEFAULT_FORMATTER_TYPE

    @property
    def mapping(self) -> dict[str, str]:
        """dict[str, str]: The mapping of output field names to LogRecord attributes.

        This getter returns a shallow copy of the internal mapping dictionary.
        This defensive practice prevents callers from modifying the internal
        state directly and ensures the integrity of the object's configuration.
        """
        return self._mapping.copy()

    @mapping.setter
    def mapping(self, new_mapping: dict[str, str]) -> None:
        """Sets the mapping for the formatter.

        This setter validates the values in the new mapping to ensure they
        correspond to a known `LogRecord` attribute. Upon successful validation,
        it creates a shallow copy of the new mapping to assign to the instance's
        internal state.

        Args:
            new_mapping: A dictionary where keys are the desired output field
                names and values are the corresponding LogRecord attribute names.

        Raises:
            InvalidFormatterMappingValueProvidedError: If any value in the
                `new_mapping` is not a valid `LogRecord` attribute.
        """
        for log_attr in new_mapping.values():
            if log_attr not in self.LOG_RECORD_BUILTIN_ATTRS:
                raise InvalidFormatterMappingValueProvidedError(log_attr)
        self._mapping = new_mapping.copy()

    @property
    def extra_fields(self) -> dict[str, Any]:
        """dict[str, Any]: Additional key-value pairs to include in the log output.

        This getter returns a shallow copy of the internal dictionary of extra
        fields. This prevents external code from mutating the object's internal
        state, which is a key tenet of defensive programming.
        """
        return self._extra_fields.copy()

    @extra_fields.setter
    def extra_fields(self, new_extra_fields: dict[str, Any]) -> None:
        """Sets the extra fields for the formatter.

        Creates a shallow copy of the provided dictionary to ensure that the
        instance's internal state is independent of any external changes to the
        original dictionary.

        Args:
            new_extra_fields: A dictionary of additional key-value pairs to be
                included in the log output.
        """
        self._extra_fields = new_extra_fields.copy()

    @property
    def formatter_type(self) -> FormatterType:
        """FormatterType: The type of formatter to use.

        This property returns the `FormatterType` enum member representing
        the current formatting style (e.g., JSON, KEY_VALUE, etc.).
        """
        return self._formatter_type

    @formatter_type.setter
    def formatter_type(self, formatter_type: str) -> None:
        """Sets the formatter type based on a string name.

        This setter accepts a string and attempts to match it to a
        member of the `FormatterType` enum. The input string is converted
        to uppercase to allow for case-insensitive matching.

        Args:
            formatter_type: A string name corresponding to a `FormatterType`
                member (e.g., "json", "KEY_VALUE").

        Raises:
            InvalidFormatterTypeProvidedError: If the provided string does not
                match any member of the `FormatterType` enum.
        """
        if formatter_type.upper() in FormatterType.__members__.keys():
            self._formatter_type = FormatterType[formatter_type.upper()]
        else:
            raise InvalidFormatterTypeProvidedError(formatter_type)

    @classmethod
    def create_default(cls) -> 'LogFormatter':
        """Creates a new formatter instance with default settings.

        This is a convenience factory method that returns a new instance of the
        `LogFormatter` class, initialized with the class's default mapping and
        extra fields.

        Returns:
            A new instance of the `LogFormatter` class.
        """
        return cls()

    def format(self, record: logging.LogRecord) -> str:
        """Formats the specified log record.

        This method overrides the base `logging.Formatter.format` method to
        generate a string representation of the log record based on the
        current formatter's configuration. The process involves:
        1. Transforming the `LogRecord` attributes into a dictionary.
        2. Adding any configured extra fields to that dictionary.
        3. Converting the resulting dictionary into a string using the
           specified `formatter_type`'s rules.

        Args:
            record: The `LogRecord` instance to be formatted.

        Returns:
            A string representation of the log data.
        """
        transformed_data = self._transform_record(record)
        self._add_extra_fields(transformed_data)
        return self._transform_formatted_log_to_str(transformed_data)

    def _add_extra_fields(self, transformed_data: dict[str, Any]) -> None:
        """Adds extra fields to the transformed data if they exist.

        This is a helper method that updates the `transformed_data` dictionary
        with the contents of `self.extra_fields`. This allows for the inclusion
        of static, user-defined fields in every log message.

        Args:
            transformed_data: The dictionary to be updated with extra fields.
        """
        if self.extra_fields:
            transformed_data.update(self.extra_fields)

    def _transform_record(self, record: logging.LogRecord) -> dict[str, Any]:
        """Transforms a LogRecord object into a dictionary based on the mapping.

        This method iterates through the formatter's `mapping` and populates
        a new dictionary with key-value pairs, where the key is the desired
        output field name and the value is retrieved from the `LogRecord`
        instance. It handles special fields like "message" and "timestamp"
        differently to ensure the correct data is captured.

        Args:
            record: The `LogRecord` instance to be transformed.

        Returns:
            A dictionary containing the transformed log record data.
        """
        transformed_data: dict[str, Any] = {}

        for key, value in self.mapping.items():
            if value == self.SPECIAL_FIELD_MESSAGE:
                transformed_data[key] = record.getMessage()
            elif value == self.SPECIAL_FIELD_TIMESTAMP:
                transformed_data[key] = datetime.now(UTC).isoformat()
            else:
                transformed_data[key] = getattr(record, value)

        return transformed_data

    def _transform_formatted_log_to_str(self, formatted_log: dict[str, Any]) -> str:
        """Converts a formatted log dictionary to a string based on formatter type.

        This method handles the final conversion of the log data from a
        dictionary to a string. If the formatter type is "json", it simply
        returns the string representation of the dictionary. Otherwise, it
        iterates through the dictionary to construct a string using the
        `delimiter` and `seperator` defined in the `FormatterConfig` for
        the chosen `FormatterType`.

        Args:
            formatted_log: The dictionary containing the formatted log data.

        Returns:
            A string representing the log data in the specified format.
        """
        if self.formatter_type.name.lower() == "json":
            return str(formatted_log)
        formatted_log_str: str = ""
        for k, v in formatted_log.items():
            if v == list(formatted_log.values())[-1]:
                formatted_log_str += f"{k}{self.formatter_type.value.delimiter}{v}"
                break
            formatted_log_str += f"{k}{self.formatter_type.value.delimiter}{v}{self.formatter_type.value.seperator}"
        return formatted_log_str

    def __copy__(self) -> 'LogFormatter':
        """
        Creates and returns a copy of the current `LogFormatter` instance. The new
        copy will contain the same mappings, extra fields, and formatter type as
        the original instance.

        :return: A new `LogFormatter` instance that is a copy of the original.
        :rtype: LogFormatter
        """
        new_formatter = LogFormatter()
        new_formatter._mapping = self._mapping.copy()
        new_formatter._extra_fields = self._extra_fields.copy()
        new_formatter._formatter_type = self._formatter_type
        return new_formatter

    def __deepcopy__(self, memo=None) -> 'LogFormatter':
        """
        Creates a deep copy of the LogFormatter instance.

        In this method, the function ensures that a new instance of the
        LogFormatter class is created, with all attributes deeply copied,
        preventing shared references between the original and the new object.

        :param memo: Dictionary to track objects during the deepcopy process to
            support cyclic references. Defaults to None if not provided.
        :type memo: dict, optional
        :return: A new deeply copied instance of LogFormatter.
        :rtype: LogFormatter
        """
        if memo is None:
            memo = {}
        new_formatter = LogFormatter()
        memo[id(self)] = new_formatter
        new_formatter._mapping = copy.deepcopy(self._mapping, memo)
        new_formatter._extra_fields = copy.deepcopy(self._extra_fields, memo)
        new_formatter._formatter_type = self._formatter_type
        return new_formatter

