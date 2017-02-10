import os
import sys

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import QtCore

from MLC.GUI.Autogenerated.autogenerated import Ui_BoardConfigurationWindow
from MLC.GUI.Experiment.ArduinoConfigManager.ArduinoBoardDialog import ArduinoBoardDialog
from MLC.GUI.Experiment.ArduinoConfigManager.ArduinoConnectionDialog import ArduinoConnectionDialog
from PyQt5.QtCore import pyqtSignal

from MLC.GUI.Experiment.ArduinoConfigManager.Common import create_local_full_path


class BoardConfigurationWindow(QMainWindow):
    # * The setup (all the things configured)
    # * The serial connection setup
    on_close_signal = pyqtSignal([list, list])

    def __init__(self, controller, boards, setup, parent=None):
        super(BoardConfigurationWindow, self).__init__(parent)
        self.ui = Ui_BoardConfigurationWindow()
        self.ui.setupUi(self)
        self.ui.arduinoBoard.clear()
        self.__controller = controller
        self.__boards = boards
        self.__setup = setup
        self.__board_idx = 0

        for i in boards:
            self.setup_board(
                self.__board_idx, i["NAME"], i["SHORT_NAME"] + ".png")
            self.__board_idx += 1

        self.__board_idx = 0
        self.ui.arduinoBoard.setCurrentIndex(self.__board_idx)

        self.update()
        self.ui.arduinoBoard.currentIndexChanged.connect(self.index_change)

    def closeEvent(self, event):
        board_setup = [self.__controller.get_protocol_config()]
        connection_cfg = [self.__controller.get_connection_config()]
        self.on_close_signal.emit(board_setup, connection_cfg)
        event.accept()
        #super(BoardConfigurationWindow, self).closeEvent(event)

    def update(self):
        aux_idx = 0
        self.ui.digitalPins.clear()
        digital_pin_count = len(self.__boards[self.ui.arduinoBoard.currentIndex()]["DIGITAL_PINS"])

        # Adds the not configured digital pins
        for i in self.__boards[self.ui.arduinoBoard.currentIndex()]["DIGITAL_PINS"]:
            if i not in self.__setup.digital_input_pins and i not in self.__setup.digital_output_pins and i not in self.__setup.pwm_pins:
                self.setup_pin(self.ui.digitalPins, 0, "Pin " + str(i), i)
            aux_idx += 1

        aux_idx = 0
        self.ui.analogPins.clear()
        # Adds the not configured digital pins
        for i in self.__boards[self.ui.arduinoBoard.currentIndex()]["ANALOG_PINS"]:
            if i not in self.__setup.analog_input_pins and i not in self.__setup.analog_output_pins:
                self.setup_pin(self.ui.analogPins, 0, "Pin A" + str(i - digital_pin_count), i)
            aux_idx += 1
        
        # Clear the list (QTableWidget.clearContent doesn't remove the rows!)
        for i in xrange(self.ui.digitalPinsList.rowCount(), -1, -1):
            self.ui.digitalPinsList.removeRow(i)

        for i in xrange(self.ui.analogPinList.rowCount(), -1, -1):
            self.ui.analogPinList.removeRow(i)

        for pin in self.__setup.digital_input_pins:
            self.insertPin(pin, "Pin " + str(pin),  self.ui.analogPinType.itemText(0), self.ui.digitalPinsList)

        for pin in self.__setup.digital_output_pins:
            self.insertPin(pin, "Pin " + str(pin), self.ui.analogPinType.itemText(1), self.ui.digitalPinsList)

        for pin in self.__setup.analog_input_pins:
            self.insertPin(pin, "Pin A" + str(pin - digital_pin_count),  self.ui.analogPinType.itemText(0), self.ui.analogPinList)

        for pin in self.__setup.analog_output_pins:
            self.insertPin(pin, "Pin A" + str(pin - digital_pin_count), self.ui.analogPinType.itemText(1), self.ui.analogPinList)

        for pin in self.__setup.pwm_pins:
            self.insertPin(pin, "Pin " + str(pin),  self.ui.digitalPinType.itemText(2), self.ui.digitalPinsList)

    def setup_board(self, index, board_name, image_name):
        _translate = QtCore.QCoreApplication.translate
        image_path = create_local_full_path("images", image_name)
        variant = QtCore.QVariant(image_path)
        item_name = _translate("BoardConfigurationWindow", board_name)
        self.ui.arduinoBoard.insertItem(index, item_name, variant)

    def setup_pin(self, combo, index, pin_name, pin_value):
        _translate = QtCore.QCoreApplication.translate
        variant = QtCore.QVariant(pin_value)
        item_name = _translate("BoardConfigurationWindow", pin_name)
        combo.insertItem(index, item_name, variant)

    def on_pinout_show(self):
        index = self.ui.arduinoBoard.currentIndex()
        path = self.ui.arduinoBoard.itemData(index)
        dialog = ArduinoBoardDialog(path)
        dialog.exec_()

    def checkout_connection_config(self):
        # TODO Renombrar para checkout de parametros de conexion serie
        serial_config = {
            "baudrate": int(self.ui.baud_rate_selector.currentText()),
                        "parity": self.ui.parity_bits_selector.currentIndex(),
                        "stopbits": self.ui.stop_bits_selector.currentIndex(),
                        "bytesize": self.ui.byte_size_selector.currentIndex(),
                        "port": self.ui.serial_interface_input.displayText()}
        return serial_config

    def checkout_board_setup(self):
        board_setup = {"report_mode": self.ui.report_mode_combo.currentIndex(), 
                       "read_delay": self.ui.read_delay_spin.value(), 
                       "read_count": self.ui.read_count_spin.value()}
        return board_setup

    def on_check_connection(self):
        self.__controller.check_connection()

    def create_connection_dialog(self):
        dialog = ArduinoConnectionDialog()
        return dialog

    def get_current_board(self):
        return self.__boards[self.ui.arduinoBoard.currentIndex()]

    def on_digital_pin_insert(self):
        idx = self.ui.digitalPins.currentIndex()
        self.__controller.insert_digital_pin(
            idx, self.ui.digitalPins.itemData(idx), self.ui.digitalPinType.currentIndex())
        # self.insertPin(self.ui.digitalPins, self.ui.digitalPinType,
        # self.ui.digitalPinsList)

    def on_analog_pin_insert(self):
        idx = self.ui.analogPins.currentIndex()
        self.__controller.insert_analog_pin(
            idx, self.ui.analogPins.itemData(idx), self.ui.analogPinType.currentIndex())
        # self.insertPin(self.ui.analogPins, self.ui.analogPinType,
        # self.ui.analogPinList)

    def addDigitalPin(self, pin_idx, pinType):
        self.insertPin(pin_idx, self.ui.digitalPins.itemText(pin_idx),
                       self.ui.digitalPinType.itemText(pinType), self.ui.digitalPinsList)
        self.ui.digitalPins.removeItem(pin_idx)

    def addAnalogPin(self, pin_idx, pinType):
        self.insertPin(pin_idx, self.ui.analogPins.itemText(pin_idx),
                       self.ui.analogPinType.itemText(pinType), self.ui.analogPinList)
        self.ui.analogPins.removeItem(pin_idx)

    def on_digital_pin_remove(self):
        # FIXME: The view pin removal should be made by the controller
        row = self.ui.digitalPinsList.currentRow()
        if row >= 0:
            pin = int(self.ui.digitalPinsList.item(row, 0).text()[4:])
            self.__controller.remove_digital_pin(int(pin))
            self.ui.digitalPinsList.removeRow(row)
            self.setup_pin(self.ui.digitalPins, 0, "Pin " + str(pin), pin)

    def on_analog_pin_remove(self):
        # FIXME: The view pin removal should be made by the controller
        row = self.ui.analogPinList.currentRow()
        if row >= 0:
            digital_pin_count = len(self.__boards[self.ui.arduinoBoard.currentIndex()]["DIGITAL_PINS"])
            pin = int(self.ui.analogPinList.item(row, 0).text()[5:]) + digital_pin_count
            self.__controller.remove_analog_pin(int(pin))
            self.ui.analogPinList.removeRow(row)
            self.setup_pin(self.ui.analogPins, 0, "Pin A" + str(pin - digital_pin_count), int(pin))

        return

    def insertPin(self, pin, pinText, pinType, pinsList):
        row = pinsList.rowCount()
        if pin < 0:
            return
        pinsList.insertRow(row)
        widget = QTableWidgetItem(pinText)
        widget.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        pinsList.setItem(row, 0, widget)
        widget = QTableWidgetItem(pinType)
        widget.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        pinsList.setItem(row, 1, widget)
        pinsList.verticalHeader().setVisible(False)

    def index_change(self, new_idx):
        self.__controller.board_changed(new_idx, self.__board_idx)

    def set_board(self, idx):
        self.ui.arduinoBoard.blockSignals(True)
        self.ui.arduinoBoard.setCurrentIndex(idx)
        self.ui.arduinoBoard.blockSignals(False)

    def on_bench_test_click(self):
        self.__controller.start_bench()

    def on_connection_type_toggle(self):
        print "Type toggled!"
