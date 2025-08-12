"""Common validation errors for the SST validation module."""


class ValidationError(Exception):
    """Base class for all validation errors in the SST validation module."""

    pass


class ValidationDataError(ValidationError):
    """Exception raised for errors in the validation data.

    This includes issues with data format, missing data, or invalid data values.
    """

    def __init__(self, message: str = "Validation data error"):
        super().__init__(message)


class ValidationThresholdError(ValidationError):
    """Exception raised for invalid validation thresholds.

    This includes issues with threshold values being out of range or invalid.
    """

    def __init__(self, message: str = "Validation threshold error"):
        super().__init__(message)


class ValidationInputError(ValidationError):
    """Exception raised for invalid input data.

    This includes issues with input file formats, missing columns, or invalid values.
    """

    def __init__(self, message: str = "Input data error"):
        super().__init__(message)


class NoDataError(ValidationDataError):
    """Exception raised when no data is available for validation.

    This includes cases where input files are empty or contain no valid data.
    """

    def __init__(self, message: str = "No data available"):
        super().__init__(f"No data available: {message}")


class InvalidDataFormatError(ValidationInputError):
    """Exception raised when input data format is invalid.

    This includes issues with data types, missing values, or incorrect formats.
    """

    def __init__(self, message: str = "Invalid data format"):
        super().__init__(f"Invalid data format: {message}")


class MissingRequiredColumnError(ValidationInputError):
    """Exception raised when required columns are missing from input data.

    This includes cases where expected columns are not present in input files.
    """

    def __init__(self, message: str = "Missing required columns"):
        super().__init__(f"Missing required columns: {message}")


class InvalidThresholdValueError(ValidationThresholdError):
    """Exception raised when threshold values are invalid.

    This includes cases where threshold values are out of range or logically invalid.
    """

    def __init__(self, message: str = "Invalid threshold value"):
        super().__init__(f"Invalid threshold value: {message}")


class ValidationConfigurationError(ValidationError):
    """Exception raised for invalid validation configuration.

    This includes issues with validation settings, parameters, or configuration files.
    """

    def __init__(self, message: str = "Configuration error"):
        super().__init__(f"Configuration error: {message}")
