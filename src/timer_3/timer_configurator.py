from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QRegularExpression, Qt
from PyQt6.QtGui import QRegularExpressionValidator

from . import functions as f
from .const import Const as C
from .focus_transition import FocusTransition
from .param_keys import ParamKeys
from .timer_controller import Timer3Controller

if TYPE_CHECKING:
    from .main import Timer_3


class Timer3UiConfigurator:
    def __init__(self, window: Timer_3, controller: Timer3Controller) -> None:
        self.window = window
        self.controller = controller
        self.context = controller.context

        self.focus_transition = FocusTransition(self.window)
        self.validator_hour = QRegularExpressionValidator(
            QRegularExpression(C.RE_PATTERN_0_24)
        )
        self.validator_min_sec = QRegularExpressionValidator(
            QRegularExpression(C.RE_PATTERN_0_60)
        )
        self.set_validators()
        self.connect_signals()
        self.init_active_button_style()
        self.init_vars_and_focus()

    def set_validators(self) -> None:
        self.window.lineEdit_HM_H.setValidator(self.validator_hour)
        self.window.lineEdit_HM_M.setValidator(self.validator_min_sec)
        self.window.lineEdit_MS_M.setValidator(self.validator_min_sec)
        self.window.lineEdit_MS_S.setValidator(self.validator_min_sec)

    def connect_signals(self) -> None:
        self.window.btnQuit.clicked.connect(f.go_quit)
        self.window.btnStart.clicked.connect(self.controller.on_btn_start_click)
        self.window.btnTunes.clicked.connect(self.controller.on_btn_tunes_click)

        self.window.lineEdit_HM_H.textEdited.connect(
            lambda: self.controller.on_line_edit_edited(self.window.lineEdit_HM_H)
        )
        self.window.lineEdit_HM_M.textEdited.connect(
            lambda: self.controller.on_line_edit_edited(self.window.lineEdit_HM_M)
        )
        self.window.lineEdit_MS_M.textEdited.connect(
            lambda: self.controller.on_line_edit_edited(self.window.lineEdit_MS_M)
        )
        self.window.lineEdit_MS_S.textEdited.connect(
            lambda: self.controller.on_line_edit_edited(self.window.lineEdit_MS_S)
        )
        self.window.lineEditCycleIntervals.textEdited.connect(
            self.controller.on_lineEditCycleIntervals_edited
        )
        self.window.checkboxEndlessly.stateChanged.connect(
            self.controller.on_endlessly_changed
        )

        self.window.spinBoxCycleRepetitions.valueChanged.connect(
            self.controller.on_cycle_Repetitions_changed
        )

        self.window.tabWidgetSetTime.currentChanged.connect(
            self.controller.on_QTabWidget_changed
        )

    def init_vars_and_focus(self) -> None:
        self.window.lblSec.setText("")

        if self.context.model.restore_time:
            self.init_ordinary_fields()
            self.init_cycle_fields()
        else:
            self.reser_ordinary_fields()
            self.reset_cycle_fields()

        self.focus_transition.set_mouse_only_focus()
        self.init_current_tab_and_focus()

    def init_ordinary_fields(self) -> None:
        model = self.context.model

        if model.hm_h != 0 or model.hm_m != 0:
            self.window.lineEdit_HM_H.setText(str(model.hm_h))
            self.window.lineEdit_HM_M.setText(str(model.hm_m))

        if model.ms_m != 0 or model.ms_s != 0:
            self.window.lineEdit_MS_M.setText(str(model.ms_m))
            self.window.lineEdit_MS_S.setText(str(model.ms_s))

    def init_cycle_fields(self) -> None:
        model = self.context.model
        self.window.lineEditCycleIntervals.setText(
            f.to_cycle_interval(model.cycle_intervals)
        )
        self.window.checkboxEndlessly.setCheckState(
            Qt.CheckState.Checked if model.endlessly else Qt.CheckState.Unchecked
        )
        self.window.spinBoxCycleRepetitions.setValue(model.cycle_Repetitions)

    def reser_ordinary_fields(self) -> None:
        self.context.set_value(ParamKeys.HM_M, 0)
        self.context.set_value(ParamKeys.HM_M, 0)
        self.context.set_value(ParamKeys.MS_M, 0)
        self.context.set_value(ParamKeys.MS_S, 0)

    def reset_cycle_fields(self) -> None:
        self.context.set_value(ParamKeys.CYCLE_INTERVALS, "")
        self.context.set_value(ParamKeys.CYCLE_ENDLESSLY, False)
        self.context.set_value(ParamKeys.CYCLE_Repetitions, 1)

    def init_current_tab_and_focus(self) -> None:
        tab_index = self.context.model.active_tab_in_QTabWidget
        self.window.tabWidgetSetTime.setCurrentIndex(tab_index)
        self.controller.init_focus_for_tab(tab_index)

    def init_tabCycle(self) -> None:
        model = self.context.model

        self.window.lineEditCycleIntervals.setText(
            f.cycle_intervals_to_display(model.cycle_intervals)
        )

        self.window.checkboxEndlessly.setCheckState(
            Qt.CheckState.Checked if model.endlessly else Qt.CheckState.Unchecked
        )
        self.window.spinBoxCycleRepetitions.setValue(model.cycle_Repetitions)

    def init_active_button_style(self) -> None:
        self.window.setStyleSheet(
            self.window.styleSheet()
            + """
            QPushButton:focus {
                border: 2px solid #00a6b2;
                border-radius: 6px;
                background-color: #e8f8fa;
                font-weight: bold;
            }
            """
        )
