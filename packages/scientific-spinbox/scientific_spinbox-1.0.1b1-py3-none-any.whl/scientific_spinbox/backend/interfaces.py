from abc import ABC, abstractmethod
from typing import Union, List
from decimal import Decimal, Context, setcontext

import pint

from pint import facets as pint_facets

from ..errors.backend import (
    IncompatibleConversionUnitError,
    EmptyArrayError,
    InvalidUnitError
)

from ..defaults import multiplier_symbols

class BackendInterface(ABC):
    """
    Abstract interface between the unit-handling backend and the ScientificSpinbox

    Requires the implementation of methods for handling quantities, units and their
    representations in numeric and text forms.
    """
    @abstractmethod
    def __init__(self, unit_system: str, precision: int):
        """
        Args:
            unit_system (str): unit system to be used (SI, kgs, ...).
            precision (int): precision to be used in the numeric representation.
        """
        pass
    
    @property
    @abstractmethod
    def unitSystem(self) -> str:
        """str: Unit System to be used."""
        pass

    @property
    @abstractmethod
    def unitRegistry(self) -> object:
        """object: Unit Registry object."""
        pass
    
    @property
    @abstractmethod
    def precision(self) -> int:
        """int: precision of the numeric representation."""
        pass

    @abstractmethod
    def quantityFromText(self, text: str, unit: str) -> object:
        """
        Creates a new quantity object based on the text representation.

        Args:
            text (str): text representation of the new quantity.
            unit (str): unit representation in text.

        Returns:
            object: quantity object created from text.
        """
        pass

    @abstractmethod
    def isUnitRegistered(self, unit) -> bool:
        """Verifies if a unit is registered in the Unit Registry.
        
        Args:
            unit (str): unit representation in text.

        Returns:
            bool: True if it is registered, False otherwise.
        """
        pass
    
    @abstractmethod
    def unitFromText(self, text: str) -> object:
        """
        Creates a new Unit object based on its text representation.
        
        Args:
            text (str): text representation of the new unit.
        
        Returns:
            object: unit object created from text.
        """
        pass
    
    @abstractmethod
    def unitToText(self, unit) -> str:
        """
        Returns the text representation of a unit object.
        
        Args:
            unit (object): unit object.
        
        Returns:
            str: text representation of the unit.
        """
        pass
    
    @abstractmethod
    def getQuantityValueNumeric(self, quantity) -> Decimal:
        """Returns the numeric part of a quantity object.
        
        Args:
            quantity (object): quantity object.
        
        Returns:
            object: numeric representation of the quantity.
        """
        pass

    @abstractmethod
    def getQuantityValueStr(self, quantity) -> str:
        """Returns the numeric part of a quantity object converted to string.
        
        Args:
            quantity (object): quantity object.
        
        Returns:
            str: numeric part of the quantity converted to string.
        """
        pass
    
    @abstractmethod
    def getQuantityUnitStr(self, quantity) -> str:
        """
        Returns the text representation of the unit part of a
        quantity object.
        
        Args:
            quantity (object): quantity object.
        
        Returns:
            str: text representation of unit part.
        """
        pass
    
    @abstractmethod
    def getQuantityUnit(self, quantity) -> object:
        """
        Returns the unit object of a quantity.
        
        Args:
            quantity (object): quantity object.
        
        Returns:
            object: unit object of the quantity.
        """
        pass
    
    @abstractmethod
    def quantityTextRepr(self, quantity, unit_separator: str, normalize: bool, formatter) -> str:
        """
        Returns the text representation of a quantity object.
        
        Args:
            quantity (object): quantity object.
            unit_separator (str): separator between numeric and unit parts.
            normalize (bool): whether to normalize the numeric part.
            formatter (function): a function to be applied on the quantity that returns the text.
        
        Returns:
            str: text representation of the quantity.
        """
        pass

    @abstractmethod
    def isQuantityCompatibleWithUnit(self, quantity, unit) -> bool:
        """Verifies if a quantity is compatible with an unit.
        
        Args:
            quantity (object): quantity object.
            unit (Union[object, str]): unit object or its text representation.

        Returns:
            bool: True if it is compatible, False otherwise.
        """
        pass
    
    @abstractmethod
    def isUnitsCompatible(self, unit1, unit2) -> bool:
        """Verifies if two units are compatible.

        Args:
            unit1 (Union[object, str]): unit object 1 or its text representation.
            unit2 (Union[object, str]): unit object 2 or its text representation.

        Returns:
            bool: True if they are compatible, False otherwise.
        """
        pass

    @abstractmethod
    def isQuantitiesCompatible(self, q1, q2) -> bool:
        """
        Verifies if two quantities are compatible.

        Args:
            q1 (object): quantity object 1.
            q2 (object): quantity object 2.

        Returns:
            bool: True if the quantities are compatible, False otherwise.
        """
        pass
    
    @abstractmethod
    def isArrayOfSameDimension(self, array) -> bool:
        """
        Verifies if an array of units are all of the same dimension.

        Args:
            array (List[str]): array of unit strings

        Returns:
            bool: True if the array is of the same dimension, False otherwise.
        """
        pass
    
    @abstractmethod
    def isQuantitiesUnitsEqual(self, q1, q2) -> bool:
        """
        Verifies if the units of two quantities have the same text representations.

        Args:
            q1 (object): quantity object 1.
            q2 (object): quantity object 2.

        Returns:
            bool: True if the units have the same text representation, False otherwise.
        """
        pass
    
    @abstractmethod
    def isUnitsEqual(self, u1, u2) -> bool:
        """
        Verifies if two units have equal text representations.

        Args:
            u1 (Union[object, str]): unit object 1 or its text representation.
            u2 (Union[object, str]): unit object 2 or its text representation.

        Returns:
            bool: True if their text representations are equal, False otherwise.
        """
        pass

    @abstractmethod
    def changeQuantityUnit(self, quantity, new_unit, formatter) -> object:
        """Returns a new quantity object with the new unit.
        
        Takes in a quantity object with numeric and unit parts,
        and returns a new quantity object with the numeric and
        unit parts converted to the new unit.

        Args:
            quantity (object): quantity object.
            new_unit (Union[object, str]): unit object or its text representation.
            formatter (function): a function to be applied on the quantity instead of the default conversion.
        
        Returns:
            object: new quantity object with the new unit and numeric parts.
        """
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """Returns a string representation of the interface."""
        pass

class PintInterface(BackendInterface):
    """
    Interface between pint and ScientificSpinbox

    Implements required methods for creating quantities,
    verifying units and converting units.
    """

    def __init__(self, unit_system: str = 'SI', precision=30):
        """
        Args:
            unit_system (str): unit system to use on the pint.UnitRegistry.
                Defaults to 'SI'.
            precision (int): precision to use for Decimal. Defaults to 30.
        """
        self._unitSystem = unit_system
        self._unitRegistry = pint.UnitRegistry(
            system=self._unitSystem,
            case_sensitive=True,
            autoconvert_offset_to_baseunit=False,
        )
        self._unitRegistry.formatter.default_format = '~'
        self._precision = precision

        # Sets Decimal context
        self._decimalsContext = Context(
            prec=self._precision,       # maximum precision
            capitals=1,                 # prints exponential in uppercase
        )
        setcontext(self._decimalsContext)

    QuantityType = pint_facets.plain.PlainQuantity
    ValueType = Decimal

    @property
    def decimalsContext(self):
        """
        Context to be used in Decimal library.
        """
        return self._decimalsContext

    @property
    def precision(self):
        """
        int: precision of the numeric representation.
        """
        return self._precision

    @property
    def unitSystem(self):
        """
        str: the unit system being used with pint.
        """
        return self._unitSystem

    @property
    def unitRegistry(self) -> pint.UnitRegistry:
        """
        pint.UnitRegistry: the unit registry being used.
        """
        return self._unitRegistry

    def quantityFromText(self, text: str, unit: str) -> pint_facets.plain.PlainQuantity:
        """
        Creates a new quantity object based on the text representation.

        Args:
            text (str): text representation of the new quantity.
            unit (str): unit representation in text.

        Returns:
            pint.Quantity: quantity object created from text.
        """
        return self.unitRegistry.Quantity(Decimal(text), unit)
    
    def quantityFromDecimal(self, value: Decimal, unit: str):
        """
        Creates a new quantity object based on the numeric representation.

        Args:
            value (Decimal): numeric representation of the new quantity.

        Returns:
            pint.Quantity: quantity object created from numeric representation.
        """
        return self.unitRegistry.Quantity(value, unit)

    def isUnitRegistered(self, unit: str) -> bool:
        """Verifies if a unit is registered in the Unit Registry.
        
        Args:
            unit (str): unit representation in text.

        Returns:
            bool: True if it is registered, False otherwise.
        """
        try:
            _ = self.unitRegistry.Unit(unit)
            return True
        except Exception:
            return False

    def unitFromText(self, text: str) -> object:
        """
        Creates a new Unit object based on its text representation.
        
        Args:
            text (str): text representation of the new unit.
            
        Raises:
            InvalidUnitError: if the unit is not registered in the interface's UnitRegistry.
        
        Returns:
            pint.Unit: unit object created from text.
        """
        if not self.isUnitRegistered(text):
            raise InvalidUnitError(text)
        return self.unitRegistry.Unit(text)
        
    def unitToText(self, unit: pint.Unit) -> str:
        """
        Returns the text representation of a unit object.
        
        Args:
            unit (pint.Unit): unit object.
        
        Returns:
            str: text representation of the unit.
        """
        return f"{unit:~}"
        
    def getQuantityValueNumeric(self, quantity: QuantityType) -> Decimal:
        """Returns the numeric part of a quantity object as Decimal.
        
        Args:
            quantity (pint.Quantity): quantity object.
        
        Returns:
            Decimal: numeric representation of the quantity.
        """
        return quantity.m

    def getQuantityValueStr(self, quantity: QuantityType) -> str:
        """Returns the numeric part of a quantity object converted to string.
        
        Args:
            quantity (pint.Quantity): quantity object.
        
        Returns:
            str: numeric part of the quantity converted to string.
        """
        return f'{quantity.m}'
    
    def getQuantityUnitStr(self, quantity: QuantityType) -> str:
        """
        Returns the text representation of the unit part of a
        quantity object.
        
        Args:
            quantity (pint.Quantity): quantity object.
        
        Returns:
            str: text representation of unit part.
        """
        unit = f'{quantity.u:~}'
        unit_splitted = list(unit)

        # Algorithm to replace possible multiplier symbols e.g. greek characters
        # with preferred characters.
        for symbol in multiplier_symbols.keys():
            item = multiplier_symbols[symbol]
            preferred = item["preferred"]
            for possible in item["possibles"]:
                if possible in unit_splitted:
                    unit = unit.replace(possible, preferred)
        return unit
    
    def getQuantityUnit(self, quantity: QuantityType) -> pint.Unit | pint_facets.plain.PlainUnit:
        """
        Returns the unit object of a quantity.
        
        Args:
            quantity (pint.Quantity): quantity object.
        
        Returns:
            pint.Unit: unit object of the quantity.
        """
        return quantity.u
    
    def quantityTextRepr(self,
                         quantity: QuantityType, 
                         unit_separator: str, 
                         normalize: bool = False, 
                         formatter = lambda x: f"{x:f}") -> str:
        """
        Returns the text representation of a quantity object.
        
        Args:
            quantity (pint.Quantity): quantity object.
            unit_separator (str): separator between numeric and unit parts.
            normalize (bool): whether to normalize the numeric part.
                Defaults to False.
            formatter (function): a function to be applied on the quantity that returns the text.
                Defaults to ``lambda x: f"{x:f}"``.
        
        Returns:
            str: text representation of the quantity.
        """
        if normalize:
            if formatter:
                return f'{formatter(quantity.m.normalize())}{unit_separator}{self.getQuantityUnitStr(quantity)}'
            else:
                return f'{quantity.m.normalize()}{unit_separator}{self.getQuantityUnitStr(quantity)}'
        else:
            if formatter:
                return f'{formatter(quantity.m)}{unit_separator}{self.getQuantityUnitStr(quantity)}'
            else:
                return f'{quantity.m}{unit_separator}{self.getQuantityUnitStr(quantity)}'

    def isQuantityCompatibleWithUnit(self, quantity: QuantityType, unit: Union[pint.Unit, str]) -> bool:
        """Verifies if a quantity is compatible with an unit.
        
        Args:
            quantity (pint.Quantity): quantity object.
            unit (Union[pint.Unit, str]): unit object or its text representation.

        Returns:
            bool: True if it is compatible, False otherwise.
        """
        if isinstance(unit, str) and not self.isUnitRegistered(unit):
            return False
        try:
            is_compatible = quantity.is_compatible_with(unit)
            return is_compatible
        except Exception:
            return False
            
    def isUnitsCompatible(self, unit1: str, unit2: str) -> bool:
        """Verifies if two units are compatible.

        Args:
            unit1 (Union[pint.Unit, str]): unit object 1 or its text representation.
            unit2 (Union[pint.Unit, str]): unit object 2 or its text representation.

        Returns:
            bool: True if they are compatible, False otherwise.
        """
        try:
            u1 = self.unitRegistry.Unit(unit1)
            u2 = self.unitRegistry.Unit(unit2)
            return u1.is_compatible_with(u2)
        except Exception:
            return False

    def isQuantitiesCompatible(self, q1: QuantityType, q2: QuantityType) -> bool:
        """
        Verifies if two quantities are compatible.

        Args:
            q1 (pint.Quantity): quantity object 1.
            q2 (pint.Quantity): quantity object 2.

        Returns:
            bool: True if the quantities are compatible, False otherwise.
        """
        try:
            is_compatible = q1.is_compatible_with(q2)
            return is_compatible
        except Exception:
            return False
        
    def isArrayOfSameDimension(self, array: List[str]) -> bool:
        """
        Verifies if an array of units are all of the same dimension.

        Args:
            array (List[str]): array of unit strings

        Returns:
            bool: True if the array is of the same dimension, False otherwise.
        """
        if len(array) < 1:
            raise EmptyArrayError()
        
        for item in array:
            if not self.isUnitRegistered(item):
                return False
            if not self.isUnitsCompatible(array[0], item):
                return False
        return True
    
    def isQuantitiesUnitsEqual(self, q1, q2) -> bool:
        """
        Verifies if the units of two quantities have the same text representations.

        Args:
            q1 (pint.Quantity): quantity object 1.
            q2 (pint.Quantity): quantity object 2.

        Returns:
            bool: True if the units have the same text representation, False otherwise.
        """
        if f"{self.getQuantityUnitStr(q1)}" == f"{self.getQuantityUnitStr(q2)}":
            return True
        else:
            return False
        
    def isUnitsEqual(self, u1, u2) -> bool:
        """
        Verifies if two units have equal text representations.

        Args:
            u1 (pint.Unit): unit object 1.
            u2 (pint.Unit): unit object 2.

        Returns:
            bool: True if their text representations are equal, False otherwise.
        """
        if f"{u1:~}" == f"{u2:~}":
            return True
        else:
            return False

    def changeQuantityUnit(self, quantity: QuantityType, new_unit: Union[str, pint.Unit], formatter=None) -> QuantityType:
        """Returns a new quantity object with the new unit.
        
        Takes in a quantity object with numeric and unit parts,
        and returns a new quantity object with the numeric and
        unit parts converted to the new unit.

        Args:
            quantity (pint.Quantity): quantity object.
            new_unit (Union[pint.Unit, str]): unit object or its text representation.
            formatter (function): a function to be applied on the quantity instead of the default conversion.
                If it is None, doesn't apply. Defaults to None.
        
        Returns:
            pint.Quantity: new quantity object with the new unit and numeric parts.
        """
        try:
            new_quantity = quantity.to(new_unit)
            if formatter:
                return formatter(quantity, new_quantity)
            else:
                return new_quantity
        except pint.DimensionalityError:
            raise IncompatibleConversionUnitError()

    def __repr__(self):
        """Returns a string representation of the PintInterface."""
        return f"PintInterface(unit_system=`{self.unitSystem}`, precision={self.precision})"