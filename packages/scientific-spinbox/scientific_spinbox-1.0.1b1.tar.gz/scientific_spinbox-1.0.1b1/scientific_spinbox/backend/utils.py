from typing import List
from decimal import Decimal, ROUND_UP, setcontext
from functools import partial

from scientific_spinbox.backend.interfaces import PintInterface
from scientific_spinbox.validators import ScientificInputValidator

def quantityChangeUnitFormatter(backend: PintInterface,
                                input_validator: ScientificInputValidator,
                                default_decimals: int,
                                unit_separator: str,
                                old_quantity: PintInterface.QuantityType,
                                new_quantity: PintInterface.QuantityType) -> PintInterface.QuantityType:
    """
    Formats `new_quantity` to match the decimal precision of `old_quantity`.

    Args:
        backend (PintInterface): Interface for unit and quantity operations.
        input_validator (ScientificInputValidator): Validator for parsing numeric values.
        default_decimals (int): Default decimal places if `old_quantity` has none.
        unit_separator (str): Text separator for units.
        old_quantity (PintInterface.QuantityType): Quantity to determine initial precision.
        new_quantity (PintInterface.QuantityType): Quantity to reformat.

    Returns:
        PintInterface.QuantityType: Formatted `new_quantity` with matched decimal precision.
    """
    setcontext(backend.decimalsContext)

    # Gets decimal places of original quantity
    old_quantity_text = backend.quantityTextRepr(old_quantity, unit_separator)
    old_captured = input_validator.getCapturedGroups(old_quantity_text)
    old_real_text = f"{Decimal(old_captured.scientificRepresentation):f}"
    old_decimals = len(input_validator.getCapturedGroups(old_real_text).decimalNumbers)

    # Creates a Decimal only to work with decimal places
    old_unit = backend.getQuantityUnitStr(old_quantity)
    new_unit = backend.getQuantityUnitStr(new_quantity)
    if old_decimals is None or old_decimals == 0:
        old_decimals = default_decimals

    control_places = Decimal("0." + '0' * (old_decimals - 1) + '1')
    control_quantity = backend.quantityFromDecimal(control_places, old_unit)
    new_control_quantity = backend.changeQuantityUnit(control_quantity, new_unit)
    new_control_places = Decimal(f"{backend.getQuantityValueNumeric(new_control_quantity):f}")
    captured_control = input_validator.getCapturedGroups(f"{new_control_places:f}")
    new_decimals = len(captured_control.decimalNumbers)
    #_logger.debug(f"{captured_control=}, {new_decimals=}, {new_control_places=}")

    if new_decimals is not None and new_decimals == 0:
        new_decimals = default_decimals

    if new_decimals:
        # Formats the new_quantity
        new_quantity_text = backend.quantityTextRepr(new_quantity, unit_separator)
        new_captured = input_validator.getCapturedGroups(new_quantity_text)
        new_scientific = new_captured.scientificRepresentation
        formatted_scientific = f"{Decimal(new_scientific).quantize(new_control_places, ROUND_UP):f}"
        formatted_quantity = backend.quantityFromText(formatted_scientific, new_unit)
        #_logger.debug(f"{new_decimals=}, {old_quantity_text=}, {new_control_quantity=}, {new_control_places=}, {new_scientific=}, {formatted_quantity=}")
        return formatted_quantity
    else:
        return new_quantity

def convert_to_nearest_preferred_unit(
        quantity: PintInterface.QuantityType,
        preferred_units: List[str],
        unit_separator: str,
        default_decimals: int,
        validator: ScientificInputValidator,
        interface: PintInterface
    ) -> PintInterface.QuantityType:
    """
    Converts a PintInterface's quantity to the nearest preferred unit.

    Args:
        quantity (PintInterface.QuantityType): quantity object.
        preferred_units (list[str]): list of preferred units.
        unit_separator (str): unit separator.
        validator (ScientificInputValidator): validator object.
        interface (PintInterface): interface object.

    Returns:
        PintInterface.QuantityType: converted quantity object.
    """
    selected_quantity = quantity
    
    # Formatter setup
    mockedQuantityChangeUnitFormatter = partial(
        quantityChangeUnitFormatter,
        interface,
        validator,
        default_decimals,
        unit_separator
    )

    # Populate the data list with converted quantities and their integer/decimal sizes
    data = []
    for unit in preferred_units:
        converted_quantity = interface.changeQuantityUnit(
            quantity, unit, formatter=mockedQuantityChangeUnitFormatter
        )
        captured = validator.getCapturedGroups(
            interface.quantityTextRepr(
                converted_quantity,
                unit_separator,
                normalize=True,
                formatter=lambda x: f"{x:f}"
            )
        )
        integer_part = captured.integerNumbers
        decimal_part = captured.decimalNumbers
        data.append({
            'integer_size': len(integer_part) if integer_part and int(integer_part) != 0 else 0,
            'decimal_size': len(decimal_part) if decimal_part and int(decimal_part) != 0 else 0,
            'converted_quantity': converted_quantity
        })

    # Filter for entries with non-zero integer size and sort by integer size
    nonzero_sorted_int = sorted(
        (item for item in data if item['integer_size'] > 0),
        key=lambda x: x['integer_size']
    )

    if nonzero_sorted_int:
        # Use the smallest integer size if available
        selected_quantity = nonzero_sorted_int[0]['converted_quantity']
    else:
        # If all integer sizes are zero, sort by decimal size
        nonzero_sorted_decimal = sorted(
            (item for item in data if item['decimal_size'] > 0),
            key=lambda x: x['decimal_size']
        )
        selected_quantity = (
            nonzero_sorted_decimal[0]['converted_quantity']
            if nonzero_sorted_decimal else quantity
        )

    # Return the quantity in the selected unit
    return interface.changeQuantityUnit(quantity, interface.getQuantityUnitStr(selected_quantity))
