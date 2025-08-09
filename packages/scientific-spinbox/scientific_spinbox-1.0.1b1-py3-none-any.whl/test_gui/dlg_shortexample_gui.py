from qtpy import QtWidgets, QtCore

from scientific_spinbox.widget import ScientificSpinBox
from test_gui.ui.dlg_testspinbox_shortexample_gui import Ui_Dialog as Ui_ShortExampleGUI

class ShortExampleGUIDialog(QtWidgets.QDialog):
    """
    Dialog that shows ScientificSpinBox and some test controls.

    Used to test the behaviour of the ScientificSpinBox GUI.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_ShortExampleGUI()

        # Configures Ui
        self.ui.setupUi(self)

        self.scientificSpinBox = ScientificSpinBox(
            base_unit='ms',
            allowed_units=['ms', 's', 'us'],
            parent=self.ui.testSpinBox1.parentWidget()
        )

        # Replaces necessary widgets
        self.ui.testSpinBox1.parentWidget().layout().replaceWidget(
            self.ui.testSpinBox1,
            self.scientificSpinBox
        )
        self.ui.testSpinBox1 = self.scientificSpinBox
        self.scientificSpinBox.valueChanged.connect(self.onValueChangeSlot)
        self.scientificSpinBox.baseValueChanged.connect(self.onBaseValueChangeSlot)

    def onValueChangeSlot(self):
        self.ui.valueLabel.setText(f"value: {str(self.scientificSpinBox.value)}")
        self.ui.unitLabel.setText(f"unit: {str(self.scientificSpinBox.unit)}")
        self.ui.baseUnitLabel.setText(f"baseUnit: {str(self.scientificSpinBox.baseUnit)}")

    def onBaseValueChangeSlot(self):
        self.ui.baseValueLabel.setText(f"baseValue: {str(self.scientificSpinBox.baseValue)}")

    