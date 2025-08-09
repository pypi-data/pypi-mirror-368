import sys
from decimal import Decimal

import pytest
from qtpy import QtCore, QtWidgets

from scientific_spinbox.widget import ScientificSpinBox
from scientific_spinbox.validators import ScientificInputValidator
from scientific_spinbox.defaults import set_default_interface
from scientific_spinbox.backend.interfaces import PintInterface

@pytest.fixture(scope='function', autouse=False)
def validator(qtbot):
    dummy_widget = QtWidgets.QLineEdit()
    qtbot.addWidget(dummy_widget)
    validator = ScientificInputValidator(parent=dummy_widget)
    dummy_widget.setValidator(validator)

    yield dummy_widget.validator()
    validator.deleteLater()

@pytest.fixture(scope='package', autouse=False)
def backend():
    interface = PintInterface('SI')
    set_default_interface(interface)
    return interface

@pytest.fixture(scope='function', autouse=False)
def gui_utils(qtbot):
    class GUIUtils:
        def __init__(self):
            pass

        def eraseAndEnterText(self, spinbox, text):
            linedit = spinbox.lineEdit()
            linedit.clear()
            qtbot.keyClicks(linedit, text)
            qtbot.keyClick(linedit, QtCore.Qt.Key_Enter)
    
    obj = GUIUtils()
    yield obj

@pytest.fixture(scope='function', autouse=False)
def widget_default(qtbot, backend):
    spinbox = ScientificSpinBox(
        backend_interface = backend,
    )
    qtbot.addWidget(spinbox)
    yield spinbox
    spinbox.deleteLater()
    
@pytest.fixture(scope='function', autouse=False)
def widget_dimensionless_wo_thousand_sep(qtbot, backend):
    spinbox = ScientificSpinBox(
        backend_interface = backend,
        thousand_separators=False,
    )
    qtbot.addWidget(spinbox)
    yield spinbox
    spinbox.deleteLater()

@pytest.fixture(scope='function', autouse=False)
def widget_dimensionless_with_thousand_sep(qtbot, backend):
    spinbox = ScientificSpinBox(
        backend_interface = backend,
        thousand_separators=True,
    )
    qtbot.addWidget(spinbox)
    yield spinbox
    spinbox.deleteLater()

@pytest.fixture(scope='function', autouse=False)
def widget_with_baseunit_wo_thousand_sep(qtbot, backend):
    spinbox = ScientificSpinBox(
        backend_interface = backend,
        base_unit='m',
        thousand_separators=False,
    )
    qtbot.addWidget(spinbox)
    yield spinbox
    spinbox.deleteLater()

@pytest.fixture(scope='function', autouse=False)
def widget_with_baseunit_with_thousand_sep(qtbot, backend):
    spinbox = ScientificSpinBox(
        backend_interface = backend,
        base_unit='m',
        thousand_separators=True,
    )
    qtbot.addWidget(spinbox)
    yield spinbox
    spinbox.deleteLater()

@pytest.fixture(scope='function', autouse=False)
def widget_with_displayunit_with_thousand_sep(qtbot, backend):
    spinbox = ScientificSpinBox(
        backend_interface = backend,
        base_unit="m",
        display_unit='m',
        thousand_separators=True,
    )
    qtbot.addWidget(spinbox)
    yield spinbox
    spinbox.deleteLater()

@pytest.fixture(scope='function', autouse=False)
def widget_with_displayunit_wo_thousand_sep(qtbot, backend):
    spinbox = ScientificSpinBox(
        backend_interface = backend,
        base_unit="m",
        display_unit='m',
        thousand_separators=False,
    )
    qtbot.addWidget(spinbox)
    yield spinbox
    spinbox.deleteLater()

@pytest.fixture(scope='function', autouse=False)
def all_widgets(qtbot,
                widget_dimensionless_wo_thousand_sep,
                widget_dimensionless_with_thousand_sep,
                widget_with_baseunit_wo_thousand_sep,
                widget_with_baseunit_with_thousand_sep,
                widget_with_displayunit_with_thousand_sep,
                widget_with_displayunit_wo_thousand_sep
    ):
    
    obj = {
        'dimensionless_wo_thousand_sep': widget_dimensionless_wo_thousand_sep,
        'dimensionless_with_thousand_sep': widget_dimensionless_with_thousand_sep,
        'with_baseunit_wo_thousand_sep': widget_with_baseunit_wo_thousand_sep,
        'with_baseunit_with_thousand_sep': widget_with_baseunit_with_thousand_sep,
        'with_displayunit_with_thousand_sep': widget_with_displayunit_with_thousand_sep,
        'with_displayunit_wo_thousand_sep': widget_with_displayunit_wo_thousand_sep
    }

    for key in obj.keys():
        qtbot.addWidget(obj[key])
    
    yield obj

    for key in obj.keys():
        obj[key].deleteLater()