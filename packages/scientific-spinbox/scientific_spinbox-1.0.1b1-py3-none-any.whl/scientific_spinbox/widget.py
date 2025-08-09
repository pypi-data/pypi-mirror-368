# -*- coding: utf-8 -*-
"""
Widget module.

Provides the widget and implements all logic related to
the User Interface (UI), graphical elements, and related 
resources.

Since:
  2024/02/06

Authors:
  - Breno H. Pelegrin S. <breno.pelegrin@usp.br>
"""

from decimal import Decimal, setcontext, ROUND_DOWN
from typing import List
import inspect
import logging
import os

from qtpy import QtCore, QtWidgets, QtGui

from .backend.interfaces import PintInterface
from .backend.utils import convert_to_nearest_preferred_unit, quantityChangeUnitFormatter
from .validators import ScientificInputValidator
from .errors.widget import (
    InvalidBackendError,
    NullBaseUnitError,
    IncompatibleDisplayAndBaseUnitsError,
    ArrayWithIncompatibleUnitsError,
    ArrayIncompatibleWithBaseUnitError,
    BaseUnitNotInAllowedUnitsError,
    DisplayUnitNotInAllowedUnitsError,
    UnallowedFeatureError
)

from .defaults import (
    THOUSAND_SEPARATOR,
    UNIT_SEPARATOR,
    get_default_interface
)

_logger = logging.getLogger(__name__)

IS_DEBUG_MODE = bool(os.getenv("SCIENTIFIC_SPINBOX_DEBUG_MODE", False))
DEBUG_SHOW_STACK = bool(os.getenv("SCIENTIFIC_SPINBOX_DEBUG_SHOW_STACK", False))
    
class ScientificSpinBox(QtWidgets.QDoubleSpinBox):
    """A Qt5 Widget to manipulate physical quantities with ease.

    Note:
        - When working with units, an unit being '' means it's dimensionless.
        - The ``baseQuantityChanged`` and ``baseValueChanged`` signals can be
          used to track changes in the base unit. They are emitted after editing
          is finished.
        - The ``valueChanged`` signal is only emitted after editing is finished.
        - The ``textChanged`` signal is only emitted after editing is finished.

    Todo:
        - implement the use of self._internalDecimalSeparator = '.'
    """

    # Creates custom signals
    baseQuantityChanged = QtCore.Signal(PintInterface.QuantityType)
    """
    pint.Quantity: Signal emitted when the base quantity is changed. Returns the new base quantity.
    """
    
    baseValueChanged = QtCore.Signal(PintInterface.ValueType)
    """
    Decimal: Signal emitted when the base value is changed. Returns the new base value.
    """
    
    displayUnitChanged = QtCore.Signal(str)
    """
    str: Signal emitted when the display unit is changed. Returns the new display unit.
    """

    decimalsChanged = QtCore.Signal(int)
    """
    int: Signal emitted when the decimals is changed. Returns the decimals.
    """

    def __init__(
            self,
            *args,
            thousand_separators: bool = True,
            default_decimals: int = 2,
            default_value: PintInterface.ValueType = Decimal(0),
            allowed_units: List[str] | str | None = None,
            preferred_units: List[str] | str | None = None,
            display_unit: str = '',
            enable_tooltip: bool = True,
            base_unit: str = '',
            backend_interface : PintInterface | None= None,
            **kwargs,
        ):
        """
        Args:
            thousand_separators (bool): if True, uses thousand separators when
                showing the text. Defaults to False.
            default_decimals (int): number of decimals to show by default.
                Defaults to 2.
            default_value (Decimal): default value of the widget.
                Defaults to 0.
            allowed_units (List[str]): list of allowed units. If provided, enables
                the 'allowed units' feature. Can't be used with 'preferred units' feature.
                Defaults to None.
            preferred_units (List[str]): list of preferred units. If provided, enables
                the `preferred units` feature. Can't be used with `allowed units` feature.
                Defaults to None.
            display_unit (str): unit which will be used to display on the spinbox. If
                using the 'preferred units' or 'allowed units' features, the features
                units array must contain the display_unit.
                Defaults to ``''`` (dimensionless).
            enable_tooltip (bool): if False, disables showing tooltips when error occurs.
                Defaults to True.
            base_unit (str): base unit in which the value will be stored on baseQuantity property.
                If base_unit='', allows only dimensionless values.
                Defaults to ``''`` (dimensionless).
            backend_interface (PintInterface): the backend interface object to use. 
                Defaults to None.
        """
        
        super().__init__(*args, **kwargs)
        
        # Connect debug signals
        if IS_DEBUG_MODE:
            self.valueChanged.connect(self.debugValueChanged)
            self.lineEdit().textChanged.connect(self.debugLineEditTextChanged)
            self.textChanged.connect(self.debugScientificSpinboxTextChanged)
            self.editingFinished.connect(self.debugEditingFinished)
            self.displayUnitChanged.connect(self.debugDisplayUnitChanged)
            self.decimalsChanged.connect(self.debugDecimalsChanged)
            self.baseValueChanged.connect(self.debugBaseValueChanged)
            self.baseQuantityChanged.connect(self.debugBaseQuantityChanged)

        # Handle arguments
        self.handleArgs(
            thousand_separators,
            default_decimals,
            default_value,
            allowed_units,
            preferred_units,
            display_unit,
            enable_tooltip,
            base_unit,
            backend_interface
        )

        self.mockedQuantityChangeUnitFormatter = lambda old_quantity, new_quantity: quantityChangeUnitFormatter(
            self._backend,
            self._inputValidator,
            self._defaultDecimals,
            UNIT_SEPARATOR,
            old_quantity,
            new_quantity
        )

        # Sets up the defaults and styles
        self.setupWidget()

    def handleArgs(
            self,
            thousand_separators,
            default_decimals,
            default_value,
            allowed_units,
            preferred_units,
            display_unit,
            enable_tooltip,
            base_unit,
            backend_interface,
        ):
        """
        Processes the arguments passed to the constructor.
        
        Do the necessary sanity checks and raises exceptions if needed.
        
        Args:
            thousand_separators (bool): if True, uses thousand separators when
                showing the text.
            default_decimals (int): number of decimals to show by default.
            default_value (Decimal): default value of the widget.
            allowed_units (List[str]): list of allowed units. If provided, enables
                the 'allowed units' feature. Can't be used with 'preferred units' feature.
            preferred_units (List[str]): list of preferred units. If provided, enables
                the `preferred units` feature. Can't be used with `allowed units` feature.
            display_unit (str): unit which will be used to display on the spinbox. If
                using the 'preferred units' or 'allowed units' features, the features
                units array must contain the display_unit.
            enable_tooltip (bool): if False, disables showing tooltips when error occurs.
                Defaults to True.
            base_unit (str): base unit in which the value will be stored on baseQuantity property.
                If base_unit='', allows only dimensionless values.
            backend_interface (PintInterface): the backend interface object to use.
        """
        self._backend: PintInterface = backend_interface if backend_interface is not None else get_default_interface()
        self._precision = self._backend.precision

        if self._backend is None:
            raise InvalidBackendError()

        self._enableDimensionless = False
        self._enableDisplayUnit = False
        self._enableAllowedUnits = False
        self._enablePreferredUnits = False

        if base_unit is None:
            raise NullBaseUnitError()
        
        if base_unit == '':
            self._enableDimensionless = True

        if display_unit is not None and display_unit != '':
            self._enableDisplayUnit = True

        if self._enableDisplayUnit:
            if not self._backend.isUnitsCompatible(display_unit, base_unit):
                raise IncompatibleDisplayAndBaseUnitsError()

        if allowed_units and preferred_units:
            raise UnallowedFeatureError('`allowed_units` and `preferred_units` are mutually exclusive.')
        
        if preferred_units and self._enableDisplayUnit:
            raise UnallowedFeatureError('`preferred_units` and `display_unit` are mutually exclusive.')
            
        if allowed_units:
            if not self._backend.isArrayOfSameDimension(allowed_units):
                raise ArrayWithIncompatibleUnitsError()
            if not self._backend.isUnitsCompatible(base_unit, allowed_units[0]):
                raise ArrayIncompatibleWithBaseUnitError()
            if base_unit not in allowed_units:
                raise BaseUnitNotInAllowedUnitsError()
            if self._enableDisplayUnit and display_unit not in allowed_units:
                raise DisplayUnitNotInAllowedUnitsError()

            self._enableAllowedUnits = True
            self._allowedUnits = allowed_units
        
        self._preferredUnits = None
        if preferred_units:
            if not self._backend.isArrayOfSameDimension(preferred_units):
                raise ArrayWithIncompatibleUnitsError()
            if not self._backend.isUnitsCompatible(base_unit, preferred_units[0]):
                raise ArrayIncompatibleWithBaseUnitError()
            
            # We can't use displayUnit and preferredUnits at the same time.
            self._enableDisplayUnit = False

            self._enablePreferredUnits = True
            self._preferredUnits = preferred_units

        # Unit handling variables
        self._baseUnit = base_unit
        self._displayUnit = display_unit
        self._enableTooltip = enable_tooltip
        self._inputValidator = ScientificInputValidator(self)

        # Value handling variables
        self._enableThousandSeparators = thousand_separators
        self._defaultDecimals = default_decimals
        self._decimals = default_decimals
        self._defaultValue = default_value
        self._minRange, self._maxRange = -1e+50, +1e+50

    def setupWidget(self):
        """
        Sets up the widget defaults before running
        """
        # Internal defaults
        self._internalUnitSeparator = '#'
        self._internalThousandSeparator = '_'
        self._internalText = ''
        self._lastCursorPosition = 0
        self._internalSignalsBlocked = False

        # Sets context for Decimal
        setcontext(self._backend.decimalsContext)
        
        # Set up unit handling defaults
        if self._enableDisplayUnit:
            self._lastText = f"{self._defaultValue:.{self._defaultDecimals}f}" + self._displayUnit
            self._quantity = self._backend.quantityFromText(
                f"{Decimal(self._defaultValue):.{self._defaultDecimals}f}",
                self._displayUnit
            )
            self._baseQuantity = self._backend.changeQuantityUnit(self._quantity, self._baseUnit)
        else:
            self._lastText = f"{self._defaultValue:.{self._defaultDecimals}f}" + self._baseUnit
            self._quantity = self._backend.quantityFromText(
                f"{Decimal(self._defaultValue):.{self._defaultDecimals}f}",
                self.baseUnit
            )
            self._baseQuantity = self._quantity

        self._value = self._backend.getQuantityValueNumeric(self._quantity)
        self._lastBaseValue = self._backend.getQuantityValueNumeric(self._baseQuantity)
        self._lastDisplayUnit = self._displayUnit
        self._lastDisplayValue = self._value

        #_logger.debug(fAfter setting up internals: "{self._lastText=}, {self._value=}")

        # Set up DoubleSpinBox defaults
        self.blockSignals(True)
        self.lineEdit().blockSignals(True)
        self.lineEdit().setText(
            self.convertInternalToText(self._lastText)
        )
        self.setValue(Decimal(self._value))
        self.setRange(self._minRange, self._maxRange)
        self.lineEdit().setCursorPosition(self._lastCursorPosition)
        self.onFocus = False
        self.setKeyboardTracking(False)
        self.setLocale(QtCore.QLocale('English'))
    
        # Sets up the stylesheet to support lineEdit text color changing on input error
        self.lineEdit().setObjectName('ScientificSpinBox_LineEdit')
        default_stylesheet = \
        """
            QLineEdit#ScientificSpinBox_LineEdit[isInputError="true"] {
                color: red;
                padding-top: auto;
                padding-bottom: auto;
            }
            QLineEdit#ScientificSpinBox_LineEdit[isInputError="false"] {
                color: white;
                padding-top: auto;
                padding-bottom: auto;
            }
        """
        # Do not use the default stylesheet, instead let the developer handle it.
        #self.lineEdit().setStyleSheet(default_stylesheet)
        self.lineEdit().setProperty('isInputError', "false")
        self.clearErrorColor()
        self.blockSignals(False)
        self.lineEdit().blockSignals(False)

        # Connect signals
        self.editingFinished.connect(self.onEditingFinished)

    def debugEditingFinished(self) -> None:
        """Debug method for the editingFinished signal."""
        msg = f"Intercepted event: emmited editingFinished."
        stack_names=[]
        if DEBUG_SHOW_STACK:
            stack = inspect.stack()
            stack_names = []
            for i, frame in enumerate(stack):
                stack_names.append(frame.function)
            sig_block = self.signalsBlocked()
            msg = f"{msg} Signals blocked: {sig_block}. Stack names: {stack_names}."
        _logger.debug(msg)
        pass

    def debugValueChanged(self, value: str) -> None:
        """Debug method for the valueChanged signal."""
        msg = f"Intercepted event: emmited valueChanged, {value=}"
        stack_names=[]
        if DEBUG_SHOW_STACK:
            stack = inspect.stack()
            stack_names = []
            for i, frame in enumerate(stack):
                stack_names.append(frame.function)
            sig_block = self.signalsBlocked()
            msg += f" Signals blocked: {sig_block}. Stack names: {stack_names}."
        _logger.debug(msg)
        pass

    def debugScientificSpinboxTextChanged(self, text: str) -> None:
        """Debug method for the textChanged signal of the ScientificSpinBox."""
        msg = f"Intercepted event: emmited scientificSpinbox.textChanged, {text=}."
        stack_names=[]
        if DEBUG_SHOW_STACK:
            stack = inspect.stack()
            stack_names = []
            for i, frame in enumerate(stack):
                stack_names.append(frame.function)
            sig_block = self.signalsBlocked()
            msg += f" Signals blocked: {sig_block}. Stack names: {stack_names}."
        _logger.debug(msg)
        pass

    def debugDisplayUnitChanged(self, unit: str) -> None:
        """Debug method for the displayUnitChanged signal."""
        msg = f"Intercepted event: emmited displayUnitChanged, {unit=}."
        stack_names=[]
        if DEBUG_SHOW_STACK:
            stack = inspect.stack()
            stack_names = []
            for i, frame in enumerate(stack):
                stack_names.append(frame.function)
            sig_block = self.signalsBlocked()
            msg = f"{msg} Signals blocked: {sig_block}. Stack names: {stack_names}."
        _logger.debug(msg)
        pass

    def debugBaseValueChanged(self, value: PintInterface.ValueType) -> None:
        """Debug method for the baseValueChanged signal."""
        msg = f"Intercepted event: emmited baseValueChanged, {value=}."
        stack_names=[]
        if DEBUG_SHOW_STACK:
            stack = inspect.stack()
            stack_names = []
            for i, frame in enumerate(stack):
                stack_names.append(frame.function)
            sig_block = self.signalsBlocked()
            msg += f" Signals blocked: {sig_block}. Stack names: {stack_names}."
        _logger.debug(msg)
        pass

    def debugBaseQuantityChanged(self, quantity: PintInterface.QuantityType) -> None:
        """Debug method for the baseQuantityChanged signal."""
        msg = f"Intercepted event: emmited baseQuantityChanged, {quantity=}"
        stack_names=[]
        if DEBUG_SHOW_STACK:
            stack = inspect.stack()
            stack_names = []
            for i, frame in enumerate(stack):
                stack_names.append(frame.function)
            sig_block = self.signalsBlocked()
            msg = f"{msg} Signals blocked: {sig_block}. Stack names: {stack_names}."
        _logger.debug(msg)
        pass

    def debugLineEditTextChanged(self, text: str) -> None:
        """Debug method for the lineEdit textChanged signal."""
        msg = f"Intercepted event: emmited lineEdit.textChanged, {text=}"
        stack_names=[]
        if DEBUG_SHOW_STACK:
            stack = inspect.stack()
            stack_names = []
            for i, frame in enumerate(stack):
                stack_names.append(frame.function)
            sig_block = self.signalsBlocked()
            msg = f"{msg} Signals blocked: {sig_block}. Stack names: {stack_names}."
        _logger.debug(msg)
        pass
    
    def debugDecimalsChanged(self, decimals: int) -> None:
        """Debug method for the decimalsChanged signal."""
        msg = f"Intercepted event: emmited decimalsChanged, {decimals=}"
        stack_names=[]
        if DEBUG_SHOW_STACK:
            stack = inspect.stack()
            stack_names = []
            for i, frame in enumerate(stack):
                stack_names.append(frame.function)
            sig_block = self.signalsBlocked()
            msg = f"{msg} Signals blocked: {sig_block}. Stack names: {stack_names}."
        _logger.debug(msg)
        pass

    @property
    def quantity(self) -> PintInterface.QuantityType:
        """PintInterface.QuantityType: quantity being displayed."""
        return self._quantity
  
    @property
    def backend(self) -> PintInterface:
        """PintInterface: backend interface used by the widget."""
        return self._backend

    @property
    def value(self) -> PintInterface.ValueType:
        """PintInterface.ValueType: value of the quantity being displayed."""
        return self._value
    
    @property
    def unit(self) -> str:
        """str: unit of the quantity being displayed."""
        return self._backend.getQuantityUnitStr(self._quantity)
    
    @value.setter
    def value(self, value: PintInterface.ValueType) -> None:
        if value != self._value:
            self.setValue(value)

    @property
    def baseValue(self) -> PintInterface.ValueType:
        """PintInterface.ValueType: value of the quantity converted to the base unit."""
        self._baseQuantity = self._backend.changeQuantityUnit(self._quantity, self._baseUnit)
        return self._backend.getQuantityValueNumeric(self._baseQuantity)
    
    @property
    def baseUnit(self) -> str:
        """str: unit of the base quantity."""
        return self._baseUnit
    
    @property
    def baseQuantity(self) -> PintInterface.QuantityType:
        """PintInterface.QuantityType: base quantity with the base unit and value converted to base unit."""
        self._baseQuantity = self._backend.changeQuantityUnit(self._quantity, self._baseUnit)
        return self._baseQuantity
    
    @property
    def defaultDecimals(self) -> int:
        """int: default number of decimals"""
        return self._defaultDecimals
    
    def _blockInternalSignals(self, block: bool) -> None:
        """Blocks or unblocks the internal signals.
        
        Args:
            block (bool): True to block the signals and False to unblock.
        """
        self._internalSignalsBlocked = block
    
    @QtCore.Slot()
    def onEditingFinished(self) -> None:
        """Executes necessary actions after editing finished.
        
        Actions:
            - Corrects the cursor position.
            - Formats the text.
            - Updates the base quantity.
        """        
        self.blockSignals(True)
        self.correctDecimals()
        last_position = self._lastCursorPosition

        # Formats the text correctly
        captured = self._inputValidator.getCapturedGroups(self.removeSeparators(self._internalText))
        numeric = f"{Decimal(captured.numericRepresentation):.{self._decimals}f}"
        new_internal = self.addSeparators(numeric + captured.unitText)
        self._internalText = new_internal
        self._lastText = self.convertInternalToText(new_internal)
        self.lineEdit().setText(self._lastText)

        # Corrects the cursor position
        self.keepCursorPosition(last_position=last_position, correct=True, is_editing_finished=True)

        # Updates the base quantity
        base_quantity = self._backend.changeQuantityUnit(self._quantity, self._baseUnit)
        self._baseQuantity = base_quantity

        self.blockSignals(False)

        # Emit custom signals
        if self._lastBaseValue != self.baseValue:
            self._lastBaseValue = self.baseValue
            if not self.signalsBlocked():
                self.baseValueChanged.emit(self.baseValue)
                self.baseQuantityChanged.emit(base_quantity)

        if self._lastDisplayUnit != self.unit:
            self._lastDisplayUnit = self.unit
            if not self.signalsBlocked():
                self.displayUnitChanged.emit(self.unit)
        #_logger.debug(f"After editing finished: {self._internalText=}, {self.baseQuantity=}, {self.baseValue=}, {self.baseUnit=}")

    def setErrorColor(self) -> None:
        """Sets the lineEdit text color to red.
        
        Sets the isInputError property to true and
        updates the lineEdit style.
        """
        self.lineEdit().setProperty('isInputError', "true")
        self.lineEdit().style().unpolish(self.lineEdit())
        self.lineEdit().style().polish(self.lineEdit())
        self.lineEdit().update()
        
    def clearErrorColor(self) -> None:
        """Sets the lineEdit text color to black.
        
        Sets the isInputError property to false and
        updates the lineEdit style.
        """
        self.lineEdit().setProperty('isInputError', "false")
        self.lineEdit().style().unpolish(self.lineEdit())
        self.lineEdit().style().polish(self.lineEdit())
        self.lineEdit().update()

    def showTooltip(self, text: str) -> None:
        """Shows immediately a tooltip with given text.
        
        Args:
            text (str): text to show on the tooltip. Can be HTML.
        """
        self.setToolTipDuration(-1)
        QtWidgets.QToolTip.showText(self.mapToGlobal(self.rect().bottomLeft()), text)

    def emptyUnitEvent(self) -> None:
        """Triggers tooltip and error color when unit is empty.

        This function is called on validation.
        """
        self.setErrorColor()
        if self._enableTooltip: 
            self.showTooltip("Unit can't be empty")

    def invalidUnitEvent(self) -> None:
        """Triggers tooltip and error color when unit is invalid.

        This function is called on validation.
        """
        self.setErrorColor()
        if self._enableTooltip:
            self.showTooltip("Invalid unit")

    def incompatibleUnitEvent(self) -> None:
        """Triggers tooltip and error color when unit is incompatible.

        This function is called on validation.
        """
        self.setErrorColor()
        if self._enableTooltip:
            self.showTooltip("Unit with incompatible dimensionality")

    def unitNotEmptyEvent(self) -> None:
        """Triggers tooltip and error color when unit is not empty.

        This function is called on validation.
        """
        self.setErrorColor()
        if self._enableTooltip:
            self.showTooltip("Unit must be empty.")

    def unitNotAllowedEvent(self) -> None:
        """Triggers tooltip and error color when unit is not allowed.

        This function is called on validation.
        """
        self.setErrorColor()
        if self._enableTooltip:
            self.showTooltip("Allowed units are: " + ", ".join(self._allowedUnits) + '.')

    def clearToolTip(self) -> None:
        """Hides the tooltip."""
        QtWidgets.QToolTip.hideText()
        
    def signalsBlocked(self):
        """
        Verify if signals are blocked.
        
        Returns:
            bool: True if signals are blocked and False otherwise.
        """
        return super().signalsBlocked()
    
    def blockSignals(self, block: bool) -> None:
        """
        Blocks the signals.
        
        Args:
            block (bool): True to block the signals and False to unblock.
        """
        return super().blockSignals(block)

    def setDisplayUnit(self, new_unit: str):
        """Converts the display quantity to a new display unit and sets the value.
        
        Args:
            new_unit (str): The new display unit.
        """
        self._lastDisplayUnit = self._displayUnit
        
        if not self._enablePreferredUnits:
            if self._enableAllowedUnits and new_unit not in self._allowedUnits:
                return

            # Sets the new display unit
            self._displayUnit = new_unit
            
            # Sets the new value and corrects the decimals
            self._quantity = self._backend.changeQuantityUnit(self._quantity, new_unit)
            self._value = self._backend.getQuantityValueNumeric(self._quantity)

            # Corrects the decimals
            # (displayUnitConversor does the job of converting the baseValue decimals to displayValue decimals)
            self._internalText = self.displayUnitConversor(f"{self._value:f}", self._displayUnit)
            self._lastText = self.convertInternalToText(self._internalText)

            self.setValue(self.backend.getQuantityValueNumeric(self._quantity))
            if not self.signalsBlocked():
                if self._lastDisplayUnit != self._displayUnit:
                    self.displayUnitChanged.emit(self.unit)
            
        else:
            return

    def setBaseValue(self, value: PintInterface.ValueType | float, from_setvalue = False) -> None:
        """Sets the widget base value.

        If the value is a float, converts the passed value
        to backend's ValueType, using the current number of decimals.

        If signals are not blocked, emits baseValueChanged with the value
        converted to ValueType.

        Args:
            value (PintInterface.ValueType): the value to set.
            from_setvalue (bool): flag to know if the function was called by setValue to
                avoid infinite loops.
        """
        if isinstance(value, float):
            # Allows handling floats differently
            value = Decimal(value)
        
        old_basevalue = self.baseValue
        self._lastBaseValue = old_basevalue
        self._baseQuantity = self.backend.quantityFromDecimal(value, self.baseUnit)
        self._quantity = self.backend.changeQuantityUnit(self._baseQuantity, self.unit)
        display_value = self.backend.getQuantityValueNumeric(self._quantity)

        new_basevalue = self._backend.getQuantityValueNumeric(self._baseQuantity)
        if not self.signalsBlocked():
            if new_basevalue != old_basevalue:
                self.baseValueChanged.emit(new_basevalue)
                self.baseQuantityChanged.emit(self._baseQuantity)
                
        if not from_setvalue:
            self.setValue(Decimal(display_value))

    def setValue(self, value: PintInterface.ValueType | float) -> None:
        """Sets the widget value.

        If the value is a float, converts the passed value
        to backend's ValueType, using the current number of decimals.

        If signals are not blocked, emits valueChanged with the value
        converted to float.

        Args:
            value (PintInterface.ValueType): the value to set.
        """

        if isinstance(value, float):
            # Allows handling floats differently
            value = Decimal(f"{value:f}")

        #_logger.debug(f"quantity repr = {self.backend.quantityTextRepr(self._quantity, UNIT_SEPARATOR)}")
        self.blockSignals(True)
        # Truncates the value to the current number of decimals
        new_numeric_text = f"{value:.{self._decimals}f}"
        value = Decimal(new_numeric_text)
        old_value = self._value
        
        self._value = value
        self._quantity = self.backend.quantityFromDecimal(value, self.unit)
        self._baseQuantity = self.backend.changeQuantityUnit(self._quantity, self._baseUnit)
        
        # Sets the text
        if self.unit:
            new_numeric_text += self.unit

        self._internalText = self.addSeparators(new_numeric_text)
        self._lastText = self.convertInternalToText(self._internalText)
        self.lineEdit().blockSignals(True)
        self.lineEdit().setText(self._lastText)
        self.lineEdit().blockSignals(False)

        #_logger.debug(f"{self._internalText=}, {self._value=}")
        self.blockSignals(False)

        if not self._internalSignalsBlocked:
            # Emit custom signals
            # We only verify after changing, to allow for setDecimals to change the value
            # e.g. 1.00 == 1.000 but we still want this change to happen if someone issues setDecimals(3)
            if value != old_value:
                if not self.signalsBlocked():
                    self.valueChanged.emit(self._value)
            # Only emit other signals if signals are not blocked
            if not self.signalsBlocked():
                if self.lineEdit().text() != self._lastText:
                    self.textChanged.emit(self._lastText)
                if self._lastBaseValue != self.baseValue:
                    self._lastBaseValue = self.baseValue
                    self.baseValueChanged.emit(self.baseValue)
                    self.baseQuantityChanged.emit(self._baseQuantity)

    def text(self) -> str:
        """Returns the widget text."""
        return self.lineEdit().text()
    
    def cleanText(self) -> str:
        """Returns only the numeric part of the displayed text."""
        return self.getNumericText()
    
    def suffix(self) -> str:
        """Returns the suffix, that is, the unit text."""
        return self.unit

    def decimals(self) -> int:
        """Returns the current number of decimals.
        
        Returns:
            int: number of decimals.
        """
        return self._decimals
    
    def setDecimals(self, prec: int) -> None:
        """Sets the number of decimals.
        
        Args:
            prec (int): number of decimals.
        """
        if isinstance(prec, int):
            if prec != self._decimals:
                self._decimals = prec
                self.decimalsChanged.emit(prec)
                self.blockSignals(True)
                self.setValue(Decimal(self._value))
                self.blockSignals(False)
        else:
            raise TypeError('The `value` passed to setDecimals must be an integer.')

    def getNumericText(self) -> str:
        """Returns only the scientific representation of the widget's internal text."""
        text = self.removeSeparators(self._internalText)
        captured = self._inputValidator.getCapturedGroups(text)
        return captured.scientificRepresentation

    def correctDecimals(self, text=None):
        """
        Corrects the number of decimal places according to
        the text, adapting to the input's decimal places.

        Note:
            - If ``text`` is not provided, uses the current internal text
              of the widget.
            - If ``text`` is provided, its expected to only contain the
              scientific representation text, e.g. ``+1234.54544E-9``.

        Examples:
            1. text = 1.23E-5 => decimal_change = 5+2 = 7
            2. text = 25e+5 => decimal_change = self._decimals
            3. text = 25e-3 and default_decimals = 2 => decimal_change = self._decimals
            4. text = 3.251 and default_decimals = 2 => decimal_change = 3
            5. text = 3.1 and default_decimals = 2 => decimal_change = 2

        Args:
            text (str, optional): text to be processed. Defaults to None.
        """
        if text:
            value_str = text.lower()
        else:
            value_str = self.getNumericText().lower()

        decimal_change = self._decimals

        if 'e' in value_str:
            real, exp = value_str.split('e')
            if int(exp) < 0:
                # Counts how many zeros between decimal point and the exponent.
                decimal_change = abs(int(exp))

                if '.' in real:
                    # If it's a real number before exponent, like 1.23E-5, adds the length of the
                    # decimal part of the real number and the size of the exponent.
                    # e.g.: 1.23E-5 = 0.0000123 => decimal_change = 5 + 2 = 7
                    integer, decimal = real.split('.')
                    decimal_change += len(decimal)

        if '.' in value_str and 'e' not in value_str:
            # If it's a real number with integer and decimal part, without exponent.
            integer, decimal = value_str.split('.')
            if decimal:
                decimal_reversed = int(decimal[::-1])
                if decimal_reversed == 0 or decimal is None:
                    # If the decimal part can be represented as zero
                    # Here we choose to NOT truncate to self._defaultDecimals.
                    decimal_change = len(decimal)
                    if decimal_change < self._defaultDecimals:
                        decimal_change = self._defaultDecimals
                else:
                    # If the decimal part is non-zero
                    new_decimal = len(decimal)
                    if new_decimal > self._defaultDecimals:
                        decimal_change = new_decimal
                    else:
                        decimal_change = self._defaultDecimals
            else:
                # If number is like "0." or "12345678."
                decimal_change = self._defaultDecimals

        if '.' not in value_str and 'e' not in value_str:
            # If it's a pure integer without decimal or exponent.
            decimal_change = self._defaultDecimals

        if value_str == '0':
            # If it's purely zero
            decimal_change = self._defaultDecimals

        # Updates the decimals if there's a change
        if value_str and decimal_change:
            #_logger.debug(f"Setting decimals: {value_str=}, {decimal_change=}")
            self.setDecimals(decimal_change)

    def validate(self, text: str, position: int) -> tuple[ScientificInputValidator.State, str, int]:
        """
        Validates the text input using two layers of validation.

        First, the text is validated by ScientificInputValidator to
        verify if the text is in the expected format for physical quantities.

        If the result of the first validator is Acceptable, does a second validation
        to verify if the unit provided is valid, compatible and not empty.

        Triggers the tooltip and error color hints.

        Args:
            text (str): text to validate.
            position (int): position of the cursor before validation.

        Returns:
            state (ScientificInputValidator.State): state of the validator.
            text (str): text after the validation.
            position (int): position of the cursor after validation.
        """
        #_logger.debug(f'Incoming text: {self.removeSeparators(text)}')
        text_wo_separators = self.removeSeparators(text)
        pre_state, pre_text, position = self._inputValidator.validate(
            text_wo_separators,
            position
        )
        
        #_logger.debug(f'After 1st validation: pre_state={self._inputValidator.stateToStr(pre_state)}, pre_text={pre_text}, position={position}')

        if pre_state == self._inputValidator.State.Intermediate or pre_state == self._inputValidator.State.Invalid:
            return pre_state, text, position
        
        captured = self._inputValidator.getCapturedGroups(text_wo_separators)
        int_num = captured.integerNumbers
        decimal_num = captured.decimalNumbers
        exp_num = captured.exponentialNumber
        unit = captured.unitText
        #_logger.debug(f"{unit=}")

        if not int_num and not decimal_num and not exp_num:
            pre_state = self._inputValidator.State.Intermediate
            return pre_state, text, position

        is_unit_empty = (not unit) and (self._baseUnit is not None)
        is_unit_invalid = not self.backend.isUnitRegistered(unit)
        is_unit_incompatible_with_base = not self._backend.isUnitsCompatible(unit, self._baseUnit)
        is_unit_not_allowed = (unit not in self._allowedUnits) if self._enableAllowedUnits else False

        #_logger.debug(f'Validation flags: {is_unit_empty=}, {is_unit_invalid=}, {is_unit_incompatible_with_base=}')

        if not self._enableDimensionless:
            if is_unit_empty:
                self.emptyUnitEvent()

            if is_unit_invalid:
                self.invalidUnitEvent()

            if is_unit_incompatible_with_base:
                self.incompatibleUnitEvent()

            if not is_unit_incompatible_with_base and is_unit_not_allowed:
                self.unitNotAllowedEvent()

            is_error = (
                is_unit_invalid or                  \
                is_unit_incompatible_with_base or   \
                is_unit_empty or                    \
                is_unit_not_allowed                 \
            )

            if is_error:
                pre_state = self._inputValidator.State.Intermediate
                #_logger.debug(f'Error on validation: unit invalid, empty or incompatible, {unit=}')
            else:
                self.clearToolTip()
                self.clearErrorColor()
        else:
            if not is_unit_empty:
                # Dimensionless is enabled, so it's expected that unit is empty or editing is not finished.
                pre_state = self._inputValidator.State.Intermediate
                self.unitNotEmptyEvent()
                #_logger.debug(f"Expected dimensionless, but unit's not empty: {unit=}, {is_unit_empty=}, state={self._inputValidator.stateToStr(pre_state)}, {pre_text=}")
            else:
                self.clearToolTip()
                self.clearErrorColor()

        #_logger.debug(f"After validation: (state, text, position) = ({self._inputValidator.stateToStr(pre_state)}, {text}, {position})")

        return pre_state, text, position
    
    def correctCursorPosition(self, pre_position, is_step_by: bool = False, is_editing_finished: bool = False):
        """Corrects the cursor position considering special cases.

        If the is_step_by flag is True, does the following:
            1. if it was at the right-side of an unit, decimal or thousand
                separator, moves the cursor to the left-side of separator.
            2. if the cursor was after the numeric part, moves it to the
                right-side of the last character of the numeric part.
            3. if the cursor is at the left-side of the numeric part, on
                the signal place, moves it to the right-side of the first
                character of the numeric part.

        If the is_step_by flag is False, does the following:
            1. if the cursor was at the right-side of the unit separator,
                moves it to the left-side of unit separator.
            2. if the cursor was at the right-side of the last character of
                the text, moves it to the right-side of the last character
                of the numeric part.
        
        Args:
            pre_position (int): position of the cursor before correction.
            is_step_by (bool, optional): if True, considers it was called from
                a stepBy and handles differently. Defaults to False.
            is_editing_finished (bool, optional): flag to know if the function was
                called inside onEditingFinished and handle it differently. 
                Defaults to False.

        Returns:
            int: new cursor position.
        """
        text_wo_thousand_sep = self.convertInternalToText(
            self.removeThousandSeparators(self._internalText)
        )

        if self._enableThousandSeparators:
            quant_thousand_sep = self._internalText.count(self._internalThousandSeparator)
        else:
            quant_thousand_sep = 0

        captured = self._inputValidator.getCapturedGroups(text_wo_thousand_sep)
        numerical_len_raw = len(captured.scientificRepresentation)
        integer_len_raw = len(captured.integerNumbers)
        signal = captured.numericSignal

        if not is_step_by:
            #_logger.debug(f"Before 'not step by' logic: {pre_position=}, last_index_of(internalText)={len(self._internalText)-1}")
            if pre_position > 0:
                if pre_position - 1 <= len(self._internalText)-1 and self._internalText[pre_position - 1] == self._internalUnitSeparator:
                    # Moves the cursor 1 unit to the left if the cursor was 1 unit after a unit separator
                    new_position = pre_position - 1
                    return new_position
                if pre_position > len(self._internalText) - 1:
                    # Moves cursor to the end of the numeric part if the cursor was after the text
                    new_position = quant_thousand_sep + numerical_len_raw
                    return new_position

            if pre_position == 0 and is_editing_finished:
                # Moves cursor to the end of the numeric part if the cursor was before the text
                new_position = quant_thousand_sep + numerical_len_raw
                return new_position
            
            return pre_position
        
        # All conditions below must only be applied if is_step_by = true.
        new_position = pre_position
        
        if pre_position == 0 and signal != '-':
            new_position = pre_position + 1
            return new_position
        
        if pre_position <= 2 and signal == '-':
            new_position += (2 - pre_position)
            return new_position

        if pre_position > numerical_len_raw + quant_thousand_sep:
            # Moves cursor to the end of the numeric part if the cursor was after the numeric part
            # Only runs if its called by a stepby.
            new_position = quant_thousand_sep + numerical_len_raw
            return new_position

        if pre_position > 0 and self._internalText[pre_position - 1] == self._internalThousandSeparator:
            # Moves the cursor 1 unit to the left if the cursor was 1 unit after a thousand separator
            # Only runs if its called by a stepby
            new_position = pre_position - 1
            return new_position
        
        if pre_position > 0 and self._internalText[pre_position - 1] == '.':
            new_position = pre_position - 1
            return new_position

        #_logger.debug(f"After all logic: {is_step_by=}, {pre_position=}, {new_position=}")
        return new_position
    
    def getNumberToChange(self, cursor_pos: int, text: str, step: float):
        """
        Gets the number to be added/subtracted to the value based on
        cursor position.

        Attention:
            - Only tested to work with abs(step) = 1 currently.
            - Can't handle exponentials.

        Args:
            cursor_pos (int): current cursor position.
            text (str): current text.
            step (float): step to take.
        """
        # Correct cursor position accounting for thousand separators
        thousand_sep_before_cursor = 0
        text_before_cursor = text[:cursor_pos]
        thousand_sep_before_cursor = text_before_cursor.count(self._internalThousandSeparator)
    
        cursor_pos_wo_sep = cursor_pos - thousand_sep_before_cursor
        text_wo_sep = self.removeSeparators(text)
        
        text_wo_units = self._inputValidator.getCapturedGroups(text_wo_sep).scientificRepresentation

        point_pos = text_wo_sep.find('.')
        if point_pos != -1:
            if cursor_pos_wo_sep <= point_pos:
                return Decimal('1' + '0'*(len(text_wo_sep[:point_pos]) - cursor_pos_wo_sep - 1)) * step

            if cursor_pos_wo_sep > point_pos:
                return Decimal('0.' + '0'*(cursor_pos_wo_sep - len(text_wo_sep[:point_pos]) - 1) + '1') * step
        else:
            # In case there's no decimal point
            return Decimal('1' + '0'*(len(text_wo_units) - cursor_pos_wo_sep - 1)) * step

        return Decimal('0.0')

    def numericSignalChange(self, text_before: str, text_after: str):
        """
        Detects if the number changed signal.

        Args:
            text_before (str): text before the change.
            text_after (str): text after the change.

        Returns:
            float: None if can't determine the signal, 1 if changed from
                   negative to positive, -1 if changed from positive to negative.
        """
        text_before = self.removeSeparators(text_before)
        text_after = self.removeSeparators(text_after)

        if len(text_before) < 1 or len(text_after) < 1:
            return None
        
        if text_before[0] == '-' and text_after[0] != '-':
            return 1
        
        if text_before[0] != '-' and text_after[0] == '-':
            return -1
        
        return None

    def stepBy(self, step: float):
        """Handles the step by functionality.
        
        Changes cursor position using correctCursorPosition to avoid separators
        and add/subtract the number using getNumberToChange.

        Also corrects the cursor position if the number signal is changed.

        Side effects:
            - sets the text and value, propagating the step.

        Args:
            step (float): step to take.
        """
        curr_pos = self.lineEdit().cursorPosition()
        last_internal_text = self._internalText

        # Corrects cursor position before calculating step
        new_position = self.correctCursorPosition(curr_pos, is_step_by=True)
        self.lineEdit().setCursorPosition(new_position)

        number_to_change = self.getNumberToChange(new_position - 1 if new_position > 0 else 0, last_internal_text, step)
        new_value = self.value + number_to_change

        #_logger.debug(f'{last_internal_text=}, {number_to_change=}, {new_value=}, {curr_pos=}, {new_position=}, {self._decimals=}')

        # Handles the stepby manually (alter text and value) instead of calling super().stepBy(step)
        new_numeric_text = f"{new_value:.{self._decimals}f}"

        # Block internal signal. The value will only be set after editing finished.
        self.blockSignals(True)
        self.setValue(Decimal(new_numeric_text))
        self.blockSignals(False)

        self._internalText = self.addSeparators(new_numeric_text)
        if self.unit:
            self._internalText += self._internalUnitSeparator + self.unit
        self._lastText = self.convertInternalToText(self._internalText)
        self.lineEdit().setText(self._lastText)
        new_internal_text = self._internalText

        # Handles cursor position when numeric signal changes
        signal_change = self.numericSignalChange(last_internal_text, new_internal_text)
        if signal_change:
            if signal_change < 0:
                # Changed from + to -
                new_position += 1

            if signal_change > 0:
                # Changed from - to +
                new_position -= 1

        # Maintains cursor position after step 
        if new_position == 0:
            new_position += 1

        # Move the cursor if the size of the text changes
        size_change = len(new_internal_text) - len(last_internal_text)
        if size_change and signal_change is None:
            new_position += size_change
        
        self.lineEdit().setCursorPosition(new_position)

    def addSeparators(self, text):
        """Formats text as internal text with internal separators.

        Uses ScientificInputValidator to get named captured groups from
        the provided text.

        Args:
            text (str): current text.

        Returns:
            str: text with internal separators.
        """        
        captured = self._inputValidator.getCapturedGroups(
            self.removeSeparators(text)
        )

        signal = captured.numericSignal
        integers = captured.integerNumbers
        decimals = captured.decimalNumbers
        exponential = captured.exponentialRepresentation
        unit = captured.unitText

        # Uses Python's native thousand separator formatting
        if self._enableThousandSeparators:
            integers = f"{int(integers):_}"
        else:
            integers = f"{int(integers)}"
        self._quant_thousand_sep = integers.count('_')
        integers = integers.replace('_', self._internalThousandSeparator)
        unit_text = self._internalUnitSeparator + unit if unit else ''
        decimals_text = '.' + decimals if decimals else ''

        if self._enableDimensionless:
            unit_text = ''
        
        new_text = f"{signal}{integers}{decimals_text}{exponential}{unit_text}"
        return new_text
    
    def removeSeparators(self, text):
        """
        Removes all internal and representation separators from text.

        Args:
            text (str): text to remove separators.
        
        Returns:
            str: text without separators.
        """
        text = text                                         \
            .replace(self._internalUnitSeparator, '')       \
            .replace(self._internalThousandSeparator, '')   \
            .replace(THOUSAND_SEPARATOR, '')                \
            .replace(UNIT_SEPARATOR, '')
        return text
    
    def removeThousandSeparators(self, text: str):
        """Remove thousand separators from text.
        
        Args:
            text (str): text to remove thousand separators.
        
        Returns:
            str: text without thousand separators
        """
        if self._enableThousandSeparators:
            return text.replace(self._internalThousandSeparator, '')
        return text
    
    def convertInternalToText(self, text: str) -> str:
        """
        Converts the internal representation to the user's representation.

        Args:
            text (str): text formatted in internal representation.

        Returns:
            str: text formatted in user representation.
        """
        text = text.replace(self._internalThousandSeparator, THOUSAND_SEPARATOR)
        text = text.replace(self._internalUnitSeparator, UNIT_SEPARATOR)
        return text
    
    def valueFromText(self, text: str) -> float:
        """
        Retrieves the value from text and sets the current value.

        This method uses the ScientificInputValidator's regex parser
        to get the named capture groups of the current text and parse
        them into a value.

        Side effects:
            - sets the representation quantity.

        Args:
            text (str): the current widget's text.
        
        Returns:
            float: the value retrieved from the text.
        """
        self._lastText = text
        captured = self._inputValidator.getCapturedGroups(
            self.removeSeparators(self.lineEdit().text())
        )

        numeric = captured.scientificRepresentation
        unit = captured.unitText

        if self._enableDimensionless:
            unit = ''

        self.correctDecimals(text=numeric)

        new_quantity = self._backend.quantityFromText(numeric, unit)
        self._quantity = new_quantity

        #_logger.debug(f"After processing: {numeric=}, {unit=}, {self._decimals=}")

        self.blockSignals(True)
        self._blockInternalSignals(True)
        self.setValue(Decimal(numeric))
        self._blockInternalSignals(False)
        self.blockSignals(False)
        
        return self._value
    
    def scientificToDecimal(self, scientific_text):
        """
        Converts text with scientific notation to a Decimal number and
        returns its text representation.

        Args:
            scientific_text (str): the input text.

        Returns:
            str: the text representation of the Decimal number.
        """
        captured = self._inputValidator.getCapturedGroups(
            self.removeSeparators(scientific_text)
        )
        numeric_repr = captured.numericRepresentation
        exp_num = captured.exponentialNumber
        if not exp_num:
            return f"{Decimal(scientific_text):f}"
        
        exp_num = int(exp_num)
        if exp_num == 0:
            return f"{Decimal(scientific_text):f}"
        
        return f"{Decimal(numeric_repr) * (Decimal(10))**exp_num:f}"
    
    def keyPressEvent(self, event: QtGui.QKeyEvent | None) -> None:
        """
        Intercepts the key press event.

        If self._lastCursorPosition is exactly at the end of
        the text, resets self._lastCursorPosition to 0 avoiding
        corrections of cursor position when editing the text.

        Args:
            event (QKeyEvent): the key press event.
        """
        self._lastCursorPosition = self.lineEdit().cursorPosition()
        if self._lastCursorPosition > len(self.lineEdit().text()) - 1:
            # In case we're typing a new number, we shouldn't maintain cursor position.
            self._lastCursorPosition = 0

        return super().keyPressEvent(event)
    
    def keepCursorPosition(self,
                           last_position = None, 
                           correct = False,
                           is_step_by = False,
                           is_editing_finished = False):
        """
        Sets the cursor position to the last position.

        Note:
            - If last_position is not provided, uses the internal last cursor position.
            - If correct is True, corrects the cursor position using correctCursorPosition.
            - The is_step_by and is_editing_finished args are passed to correctCursorPosition.

        Args:
            last_position (int, optional): the last cursor position.
                Defaults to self._lastCursorPosition.
            correct (bool, optional): whether to correct the cursor position.
                Defaults to False.
            is_step_by (bool, optional): whether the cursor position is being
                changed by a step. Passed to correctCursorPosition. Defaults to False.
            is_editing_finished (bool, optional): whether the editing is finished.
                Passed to correctCursorPosition. Defaults to False.
        """
        self.blockSignals(True)
        if last_position is None:
            last_position = self._lastCursorPosition

        if correct:
            self.lineEdit().setCursorPosition(
                self.correctCursorPosition(
                    pre_position = last_position,
                    is_step_by = is_step_by,
                    is_editing_finished = is_editing_finished
                )
            )
        else:
            self.lineEdit().setCursorPosition(last_position)
        self.blockSignals(False)
    
    def textFromValue(self, value: Decimal) -> str:
        """
        Retrieves the text from current value and sets the internal text.

        Side effects:
            - sets the number of decimals
            - corrects the cursor position

        Args:
            value (Decimal): the current numeric value of the widget.
        
        Returns:
            str: the text representation of the value.
        """
        captured = self._inputValidator.getCapturedGroups(
            self.removeSeparators(self._lastText)
        )

        numeric = str(self._value)
        unit = captured.unitText

        if self._enableDimensionless:
            unit = ''

        self.correctDecimals(text=numeric)
        result = ''

        if not self._enableDisplayUnit:
            if not self._enablePreferredUnits:
                result = self.defaultConversor(numeric, unit)
            else:
                result = self.nearestPreferredUnitConversor(numeric, unit)
        else:
            result = self.displayUnitConversor(numeric, unit)

        return self.convertInternalToText(result)
    
    def defaultConversor(self, numeric: str, unit: str) -> str:
        """
        Converts a quantity to its internal text representation.
        
        Args:
            numeric (str): text representation of the numeric part.
            unit (str): text representation of the unit part.
            
        Returns:
            str: the internal text representation.
        """
        # Doesn't do any conversions
        result = f"{Decimal(numeric):.{self._decimals}f}"
        #_logger.debug(f"Converted using defaultConversor. Params: {numeric=}, {unit=}; vars: {self._decimals=}, {result=}")

        if unit:
            result += UNIT_SEPARATOR + unit

        # Sets text, value and corrects cursor position 
        result = self.addSeparators(result)
        self._internalText = result
        self._lastText = self.convertInternalToText(self._internalText)
        self.blockSignals(True)
        self.setValue(Decimal(numeric))
        self.blockSignals(False)
        self.keepCursorPosition(correct=True)
        return self._internalText
    
    def nearestPreferredUnitConversor(self, numeric: str, unit: str) -> str:
        """
        Converts a quantity to its internal text representation with
        the nearest preferred unit.
        
        Args:
            numeric (str): text representation of the numeric part.
            unit (str): text representation of the unit part.
            
        Returns:
            str: the internal text representation in the nearest preferred unit.
        """
        # Converts to nearest preferred unit
        numeric = f"{Decimal(numeric):f}"
        old_quantity = self._backend.quantityFromText(numeric, unit)
        new_quantity = convert_to_nearest_preferred_unit(
            old_quantity,
            self._preferredUnits,
            UNIT_SEPARATOR,
            self._defaultDecimals,
            self._inputValidator,
            self._backend
        )
        new_unit = self._backend.getQuantityUnitStr(new_quantity)
        new_quantity = self._backend.changeQuantityUnit(old_quantity, new_unit, formatter=self.mockedQuantityChangeUnitFormatter)

        #_logger.debug(f"Converted using nearest_preferred: {old_quantity=} -> {new_quantity=}")

        self._quantity = new_quantity
        new_text_repr = self._backend.quantityTextRepr(new_quantity, self._internalUnitSeparator)
        captured = self._inputValidator.getCapturedGroups(
            self.removeSeparators(new_text_repr)
        )

        # Corrects decimals
        numeric = f"{Decimal(captured.scientificRepresentation):f}"
        self.correctDecimals(text=numeric)

        # Sets text, value and corrects cursor position 
        self._internalText = self.addSeparators(new_text_repr)
        self._lastText = self.convertInternalToText(self._internalText)
        self.blockSignals(True)
        self.setValue(Decimal(numeric))
        self.blockSignals(False)
        self.keepCursorPosition(correct=True)
        return self._internalText

    def displayUnitConversor(self, numeric: str, unit: str) -> str:
        """
        Converts a quantity to its internal text representation in the
        display unit.
        
        Args:
            numeric (str): text representation of the numeric part.
            unit (str): text representation of the unit part.
            
        Returns:
            str: the internal text representation in the display unit.
        """
        # Converts quantity to display unit
        new_quantity = self._backend.quantityFromText(numeric, unit)
        new_quantity = self._backend.changeQuantityUnit(new_quantity, self._displayUnit, formatter=self.mockedQuantityChangeUnitFormatter)
        self._quantity = new_quantity
        new_text_repr = self._backend.quantityTextRepr(new_quantity, self._internalUnitSeparator)
    
        # Corrects decimals
        captured = self._inputValidator.getCapturedGroups(
            self.removeSeparators(new_text_repr)
        )
        numeric = f"{Decimal(captured.scientificRepresentation):f}"
        self.correctDecimals(text=numeric)

        # Sets text, value and corrects cursor position
        self._internalText = self.addSeparators(numeric + self._displayUnit)
        self._lastText = self.convertInternalToText(self._internalText)
        self.blockSignals(True)
        self.setValue(Decimal(numeric))
        self.blockSignals(False)
        self.keepCursorPosition(correct=True)
        return self._internalText