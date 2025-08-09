"""ScientificSpinBox package.

A Qt5 Widget based on QDoubleSpinBox that enables users to
insert and manipulate physical quantities naturally.

This init file sets up the application.
"""

import os
import logging

# Sets the default interface
from .backend.interfaces import PintInterface
from .defaults import set_default_interface
set_default_interface(PintInterface(unit_system='SI', precision=30))

__version__ = "1.0.1b1"

use_own_logger = os.getenv('SCIENTIFIC_SPINBOX_USE_OWN_LOGGER', 0)

if bool(use_own_logger):
    logging_level = os.getenv('SCIENTIFIC_SPINBOX_LOGGING_LEVEL', 'ERROR')
    if logging_level not in [
        'DEBUG',
        'INFO',
        'ERROR',
        'WARNING',
        'CRITICAL',
    ]:
        raise Exception(f"Invalid logging level `{logging_level}`")

    level_dict = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'CRITICAL': logging.CRITICAL
    }

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level_dict[logging_level])

    logging.basicConfig(
        level=level_dict[logging_level],
        format='%(asctime)s|%(levelname)s|%(module)s|%(funcName)s|: %(message)s',
        handlers=[logging.FileHandler("test_gui.log", mode='w'), stream_handler]
    )
