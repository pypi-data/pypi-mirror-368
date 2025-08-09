"""
Validators module.

Provides the text validators and text processing utilities
to be used within a ScientificSpinBox.

Since:
  2024/02/06

Authors:
  - Breno H. Pelegrin S. <breno.pelegrin@usp.br>
"""

from qtpy import QtGui, PYSIDE2
from typing import Type

from .errors.validators import (
    CaptureGroupNameNotFoundOnRegex,
    InvalidValidatorStateError
)
if PYSIDE2:
    raise NotImplementedError(
        "Compatibility layer for `pyside2` is not yet implemented. This module is only compatible with `pyqt5`, `pyqt6` and `pyside6`."
    )
else:
    from qtpy.QtGui import QRegularExpressionValidator
    from qtpy.QtCore import QRegularExpression

class ScientificInputValidator(QRegularExpressionValidator):
    """Input validator for a ScientificSpinBox.
    
    Verifies if the provided input is a valid scientific number with
    or without units based on a regular expression.

    Implements methods for manipulating captured groups to extract
    parts from the scientific input.
    """
    # Please note that QRegularExpression isn't compatible with Qt4.
    # The new QRegularExpression implements match group names that are
    # useful for this application.
    def __init__(self, parent=None):
        """
        Args:
            parent (object): parent Qt object
        """
        # Allows only patterns like "-0123456789.0123456789E+0123456789 /aBCµΩºde/FG***HI*Jkl*m*/no"

        # (?<full>(?<sci_repr>^(?<num_repr>(?<num_sgn>[+-])?(?<int_num>[0-9]+)?(?<dec_repr>(?<dec_sep>[.,])?(?<dec_num>[0-9]+))?)(?<exp_repr>[eE](?<exp_num>(?<exp_sgn>[+-])[0-9]+))?)(?<txt_repr> *(?<txt_unit>\µ?\Ω?\º?[a-zA-Z0-9?\/*\**\(*\)*]+))?)$
        self._regex = QRegularExpression(
            r"^(?<full>(?<sci_repr>^(?<num_repr>(?<num_sgn>[+-])?(?<int_num>[0-9]+)?(?<dec_repr>(?<dec_sep>[.])?(?<dec_num>[0-9]+))?)(?<exp_repr>[eE](?<exp_num>(?<exp_sgn>[+-])[0-9]+))?)(?<txt_repr> *(?<txt_unit>\µ?\Ω?\º?[a-zA-Z0-9?\/*\**\(*\)*]+))?)$"
        )
        super().__init__(self._regex, parent)

    @property
    def regExpCaptureGroups(self):
        """
        Returns the named capture groups from the regex.

        Returns:
            list: list of named capture groups.
        """
        groups = self._regex.namedCaptureGroups().copy()
        groups.pop(0)
        return groups
        
    def getCapturedGroups(self, text):
        """Returns a ScientificCapturedGroups object for the given text.
        
        Args:
            text (str): text to fill the capture groups.

        Returns:
            ScientificCapturedGroups: object with the captured groups.
        """
        return ScientificCapturedGroups(text, self)

    def stateToStr(self, state: QtGui.QValidator.State):
        """
        Transforms a QValidator state into a string.

        Args:
            state (QtGui.QValidator.State): QValidator state.
            
        Raises:
            InvalidValidatorStateError: if the provided state is not one of the
                known QValidator states (Acceptable, Invalid, Intermediate).
            
        Returns:
            str: string representation of the QValidator state.
                Can be `Acceptable`, `Invalid` or `Intermediate`.
        """
        valid_states = [
            QtGui.QValidator.State.Acceptable,
            QtGui.QValidator.State.Invalid,
            QtGui.QValidator.State.Intermediate
        ]

        if state not in valid_states:
            raise InvalidValidatorStateError(state)

        if state == QtGui.QValidator.State.Intermediate:
            return 'Intermediate'
        elif state == QtGui.QValidator.State.Invalid:
            return 'Invalid'
        elif state == QtGui.QValidator.State.Acceptable:
            return 'Acceptable'

    def getRegExpGroupIdx(self, group_name: str):
        """
        Gets the index of a named capture group based on its name.

        Args:
            group_name (str): name of the group to get index.
        
        Returns:
            int: index of the group.

        Raises:
            Exception: if the group doesn't exist on the regex.
        """
        groups = self.regExpCaptureGroups
        if group_name in groups:
            return groups.index(group_name)
        raise CaptureGroupNameNotFoundOnRegex(group_name)
    
    def interpretText(self, text):
        """
        Replaces commas with dots on the text.

        Args:
            text (str): text to replace commas.

        Returns:
            str: text with only dots.
        """
        text = str(text).replace(',', '.')
        return text
    
    def getAllCaptured(self, text):
        """
        Returns a dictionary with all the capture groups and
        the corresponding text captured by each group.

        Args:
            text (str): text to fill the capture groups.
        """
        captured_dict = {}
        captured_dict = dict.fromkeys(self.regExpCaptureGroups)

        text = self.interpretText(text)
        match = self._regex.match(text)
        for key in captured_dict:
            captured_dict[key] = match.captured(key)

        return captured_dict

    def validate(self, text, position):
        """
        Reimplements the validate method from the parent class.
        
        On the current implementation, it just returns the result from
        the parent class method.

        Args:
            text (str): text to validate.
            position (int): position of the cursor before validation.

        Returns:
            state (QtGui.QValidator.State): state of the validator.
            text (str): text after the validation.
            position (int): position of the cursor after validation.
        """
        pre_state, text, position = super().validate(text, position)

        return (pre_state, text, position)

    def fixup(self, a0):
        """
        Reimplements the fixup method from the parent class.
        
        On the current implementation, it just returns the result from
        the parent class method.

        Args:
            text (str): text to fixup.

        Returns:
            str: fixed up text.
        """
        return super().fixup(a0)
    
class ScientificCapturedGroups:
    """Class that represents captured groups for a given text.
    
    Implements methods to access each group with ease.
    """
    def __init__(self, text: str, validator: ScientificInputValidator):
        """
        Args:
            text (str): text to fill the capture groups.
            validator (ScientificInputValidator): validator object reference.
        """
        self._inputText = text
        self._captured = validator.getAllCaptured(text)

    @property
    def fullText(self) -> str | None:
        """Full captured text."""
        return self._captured['full']

    @property
    def scientificRepresentation(self) -> str | None:
        """Scientific representation, without unit text.
        
        Can contain:
            - numeric signal
            - integer numbers
            - decimal separator
            - decimal numbers
            - exponential symbol
            - exponential signal
            - exponential numbers.

        Doesn't contain:
            - unit text
        """
        return self._captured['sci_repr']
    
    # <num_repr>
    @property
    def numericRepresentation(self) -> str | None:
        """Numeric representation, without exponential.
        
        Can contain:
            - numeric signal
            - integer numbers
            - decimal separator
            - decimal numbers

        Doesn't contain:
            - exponential symbol
            - exponential signal
            - exponential numbers
            - unit text
        """
        return self._captured['num_repr']

    @property
    def numericSignal(self) -> str | None:
        """Signal of the numeric part."""
        return self._captured['num_sgn']

    @property
    def integerNumbers(self) -> str | None:
        """Integer part, not including signal."""
        return self._captured['int_num']
    
    # <dec_repr>
    @property
    def decimalRepresentation(self) -> str | None:
        """Decimal part, including separator and numbers."""
        return self._captured['dec_repr']
    
    @property
    def decimalSeparator(self) -> str | None:
        """Decimal separator."""
        return self._captured['dec_sep']
    
    @property
    def decimalNumbers(self) -> str | None:
        """Numbers of the decimal part."""
        return self._captured['dec_num']
    
    @property
    def exponentialRepresentation(self) -> str | None:
        """Exponential part, including exponential sign, number and signal."""
        return self._captured['exp_repr']
    
    @property
    def exponentialNumber(self) -> str | None:
        """Number after the exponential sign, including signal."""
        return self._captured['exp_num']
    
    @property
    def exponentialSignal(self) -> str | None:
        """Signal of the exponential."""
        return self._captured['exp_sgn']
    
    @property
    def unitRepresentation(self) -> str | None:
        """Unit part, with the preceding spaces."""
        return self._captured['txt_repr']

    @property
    def unitText(self) -> str | None:
        """Text of the unit part, without the preceding spaces."""
        return self._captured['txt_unit']