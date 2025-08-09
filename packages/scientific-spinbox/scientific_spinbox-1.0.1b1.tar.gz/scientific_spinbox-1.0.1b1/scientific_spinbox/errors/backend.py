# PintInterface errors
class IncompatibleConversionUnitError(Exception):
    """
    Exception raised when the unit to be converted to is incompatible
    with the current unit.
    """
    def __init__(self):
        self._message = "The new unit must have the same dimensionality of the current unit."
        super().__init__(self._message)

class EmptyArrayError(Exception):
    """
    Exception raised when an empty array is passed.
    """
    def __init__(self):
        self._message = "The array must have at least one element."
        super().__init__(self._message)

class InvalidUnitError(Exception):
    """
    Exception raised when an invalid unit is passed.
    """
    def __init__(self, unit: str):
        self._message = f"The unit `{unit}` is invalid."
        super().__init__(self._message)

