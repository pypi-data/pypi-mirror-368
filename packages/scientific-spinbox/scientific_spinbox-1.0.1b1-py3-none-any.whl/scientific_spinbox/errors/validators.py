# ScientificInputValidator errors
class CaptureGroupNameNotFoundOnRegex(Exception):
    """
    Exception raised when capture group name is not found on the
    ScientificInputValidator's regex.
    """
    def __init__(self, group_name: str):
        self._message = f"The capture group `{group_name}` doesn't exist on ScientificInputValidator's regex."
        super().__init__(self._message)

class InvalidValidatorStateError(Exception):
    """
    Exception raised when an invalid validator state is provided.
    """
    def __init__(self, state):
        self._message = f"Invalid state `{state}`."
        super().__init__(self._message)