# ScientificSpinBox errors
class InvalidBackendError(Exception):
    """Exception raised when backend interface is invalid."""
    def __init__(self):
        self._message = "ScientificSpinBox requires a valid backend interface object. Please pass it as a paremeter or set a valid default interface."
        super().__init__(self._message)

class NullBaseUnitError(Exception):
    """Exception raised when base unit is null."""
    def __init__(self):
        self._message = "`base_unit` must be provided."
        super().__init__(self._message)

class IncompatibleDisplayAndBaseUnitsError(Exception):
    """Exception raised when display and base units are incompatible."""
    def __init__(self):
        self._message = "`display_unit` and `base_unit` must have the same dimension."
        super().__init__(self._message)

class ArrayWithIncompatibleUnitsError(Exception):
    """Exception raised when an array with incompatible units is provided."""
    def __init__(self):
        self._message = "all units in the array must have the same dimension."
        super().__init__(self._message)

class ArrayIncompatibleWithBaseUnitError(Exception):
    """Exception raised when an array with units incompatible with base is provided."""
    def __init__(self):
        self._message = "`allowed_units` and `base_unit` must have the same dimension."
        super().__init__(self._message)

class DisplayUnitNotInAllowedUnitsError(Exception):
    """Exception raised when display unit is not in allowed units."""
    def __init__(self):
        self._message = "`display_unit` must be in `allowed_units`."
        super().__init__(self._message)

class BaseUnitNotInAllowedUnitsError(Exception):
    """Exception raised when base unit is not in allowed units."""

    def __init__(self):
        self._message = "`base_unit` must be in `allowed_units`."
        super().__init__(self._message)

class UnallowedFeatureError(Exception):
    """Exception raised when an unallowed feature is used."""
    def __init__(self, message: str):
        self._message = message
        super().__init__(self._message)