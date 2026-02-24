from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QMessageBox,
    QInputDialog,
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from ATE_Lib_AN8103.ate_lib import COMM_Error, ATE_Instrument_Error
import datetime
import re
from .data_store import SessionData, PhaseResult
from .phase_config import PHASES, PHASE_CONFIG
from .phase_controller import make_phase_runner, make_subtest_runner


class LoginPage(QWidget):
    def __init__(self, start_callback):
        super().__init__()
        self.start_callback = start_callback

        layout = QVBoxLayout()
        layout.setSpacing(16)

        title = QLabel("SRFD II RF Amplifier 1.5T ATE")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        layout.addWidget(title)

        self.operator_edit = QLineEdit()
        self.station_edit = QLineEdit()
        self.dut_serial_edit = QLineEdit()
        self.part_number_edit = QLineEdit()
        self.date_edit = QLineEdit()

        self.station_edit.setText("01")
        self.part_number_edit.setText("2351573-02")
        self.date_edit.setText(datetime.datetime.now().strftime("%Y-%m-%d"))

        def add_row(label_text, widget):
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setFixedWidth(150)
            row.addWidget(label)
            row.addWidget(widget)
            layout.addLayout(row)

        add_row("SSO de l'opérateur:", self.operator_edit)
        add_row("ID de la station:", self.station_edit)
        add_row("Numéro de série du DUT:", self.dut_serial_edit)
        add_row("Numéro de pièce:", self.part_number_edit)
        add_row("Date:", self.date_edit)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        start_button = QPushButton("Démarrer la séquence de tests")
        start_button.setFont(QFont("Arial", 14, QFont.Bold))
        start_button.clicked.connect(self.on_start)
        layout.addWidget(start_button)

        self.setLayout(layout)

    def on_start(self):
        tech = {
            "SSO": self.operator_edit.text().strip(),
            "Station_ID": self.station_edit.text().strip(),
        }
        dut = {
            "DUT_Serial": self.dut_serial_edit.text().strip(),
            "Part_Number": self.part_number_edit.text().strip(),
            "Test_Date": self.date_edit.text().strip(),
        }
        if not tech["SSO"]:
            self.status_label.setText("Veuillez entrer le SSO de l'opérateur.")
            return
        self.start_callback(tech, dut)


class PhaseMenuPage(QWidget):
    def __init__(self, phases, start_callback, eng_mode_callback, select_phase_callback):
        super().__init__()
        self.select_phase_callback = select_phase_callback
        self.phase_buttons = []
        self.status_labels = []

        layout = QVBoxLayout()
        layout.setSpacing(16)

        title = QLabel("Sélectionner le test")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 22, QFont.Bold))
        layout.addWidget(title)

        subtitle = QLabel("Mode opérateur: les tests sont exécutés dans l'ordre.\nMode ingénieur: sélectionnez n'importe quel test.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 11))
        layout.addWidget(subtitle)

        for index, phase in enumerate(phases):
            row = QHBoxLayout()
            status = QLabel("Non testé")
            status.setFixedWidth(90)
            status.setAlignment(Qt.AlignCenter)
            status.setFont(QFont("Arial", 11))
            row.addWidget(status)

            btn = QPushButton(f"{index + 1}. {phase}")
            btn.setFont(QFont("Arial", 13))
            btn.setEnabled(False)

            def make_handler(i):
                def handler():
                    self.select_phase_callback(i)

                return handler

            btn.clicked.connect(make_handler(index))
            self.phase_buttons.append(btn)
            self.status_labels.append(status)
            row.addWidget(btn)
            layout.addLayout(row)

        button_row = QHBoxLayout()

        start_button = QPushButton("Démarrer la séquence (mode opérateur)")
        start_button.setFont(QFont("Arial", 14, QFont.Bold))
        start_button.clicked.connect(start_callback)
        button_row.addWidget(start_button)

        eng_button = QPushButton("Mode ingénieur")
        eng_button.setFont(QFont("Arial", 14, QFont.Bold))
        eng_button.clicked.connect(eng_mode_callback)
        button_row.addWidget(eng_button)

        layout.addLayout(button_row)
        self.setLayout(layout)

    def enable_engineering(self, enabled: bool):
        for btn in self.phase_buttons:
            btn.setEnabled(enabled)

    def set_phase_enabled(self, index: int, enabled: bool):
        if 0 <= index < len(self.phase_buttons):
            self.phase_buttons[index].setEnabled(enabled)

    def set_phase_status(self, index: int, ok: bool):
        if 0 <= index < len(self.status_labels):
            label = self.status_labels[index]
            if ok:
                label.setText("Réussi")
                label.setStyleSheet("color: green;")
            else:
                label.setText("Échec")
                label.setStyleSheet("color: red;")


class PhasePage(QWidget):
    def __init__(
        self,
        phase_name,
        run_callback,
        back_callback,
        instruction_text="",
        image_path=None,
        require_check=False,
        check_text=None,
        caption_text=None,
        subtests=None,
    ):
        super().__init__()
        self.phase_name = phase_name
        self.run_callback = run_callback
        self.back_callback = back_callback
        self.require_check = require_check
        self.checked = not require_check
        self.subtests = subtests or []
        self.subtest_buttons = []

        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel(phase_name)
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 22, QFont.Bold))
        layout.addWidget(title)

        self.status_label = QLabel("Statut du test : Non testé")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 11))
        layout.addWidget(self.status_label)

        if instruction_text:
            instruction_label = QLabel(instruction_text)
            instruction_label.setWordWrap(True)
            instruction_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            instruction_label.setFont(QFont("Arial", 12))
            layout.addWidget(instruction_label)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        if image_path:
            pix = QPixmap(image_path)
            if not pix.isNull():
                self.image_label.setPixmap(pix.scaledToHeight(250, Qt.SmoothTransformation))
        layout.addWidget(self.image_label)
        if caption_text:
            caption = QLabel(caption_text)
            caption.setAlignment(Qt.AlignCenter)
            caption.setFont(QFont("Arial", 11))
            layout.addWidget(caption)

        if self.require_check:
            check_row = QHBoxLayout()
            text = check_text if check_text is not None else ""
            check_label = QLabel(text)
            check_label.setWordWrap(True)
            check_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            check_label.setFont(QFont("Arial", 12))
            check_row.addWidget(check_label)
            self.check_button = QPushButton("Vérifié")
            self.check_button.setFont(QFont("Arial", 12, QFont.Bold))
            self.check_button.clicked.connect(self.on_checked)
            check_row.addWidget(self.check_button)
            layout.addLayout(check_row)

        if self.subtests:
            sub_row = QHBoxLayout()
            for label, cb in self.subtests:
                btn = QPushButton(label)
                btn.setFont(QFont("Arial", 12))
                btn.clicked.connect(self.make_subtest_handler(cb))
                btn.setEnabled(False)
                self.subtest_buttons.append(btn)
                sub_row.addWidget(btn)
            layout.addLayout(sub_row)

        self.result_display = QTextEdit()
        self.result_display.setFont(QFont("Arial", 12))
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        button_row = QHBoxLayout()
        self.run_button = QPushButton("Exécuter le test")
        self.run_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.run_button.setEnabled(self.checked)
        self.run_button.clicked.connect(self.on_run)
        button_row.addWidget(self.run_button)

        self.back_button = QPushButton("Retour au menu")
        self.back_button.setFont(QFont("Arial", 12))
        self.back_button.clicked.connect(self.back_callback)
        button_row.addWidget(self.back_button)

        self.next_button = QPushButton("Suivant")
        self.next_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.next_button.setEnabled(False)
        button_row.addWidget(self.next_button)

        layout.addLayout(button_row)
        self.setLayout(layout)

    def enable_subtests(self, enabled: bool):
        for btn in self.subtest_buttons:
            btn.setEnabled(enabled)

    def on_checked(self):
        self.checked = True
        self.run_button.setEnabled(True)
        self.check_button.setStyleSheet("background-color: green; color: white;")

    def on_run(self):
        self.handle_run(self.run_callback, True)

    def make_subtest_handler(self, cb):
        def handler():
            self.handle_run(cb, False)

        return handler

    def handle_run(self, callback, update_status):
        self.result_display.clear()
        try:
            text_lines, ok = callback()
            if text_lines:
                joined = "\n".join(text_lines)
                if "<" in joined and ">" in joined:
                    self.result_display.setHtml(joined)
                else:
                    rows = []
                    for line in text_lines:
                        if " – " in line and "[" in line and "]" in line and ": " in line:
                            try:
                                id_part, rest = line.split(" – ", 1)
                                label_part, tail = rest.split(": ", 1)
                                before_bracket, after_bracket = tail.split("[", 1)
                                bracket_content, status_part = after_bracket.split("]", 1)
                                status = status_part.strip()
                                tokens = before_bracket.strip().split()
                                value = tokens[0]
                                unit = " ".join(tokens[1:]) if len(tokens) > 1 else ""
                                spec_min, spec_max = "", ""
                                if ".." in bracket_content:
                                    spec_min, spec_max = [t.strip() for t in bracket_content.split("..", 1)]
                                rows.append((id_part.strip(), label_part.strip(), value, unit, spec_min, spec_max, status))
                            except Exception:
                                pass
                    if rows:
                        html = []
                        html.append("<table border='1' cellspacing='0' cellpadding='3'>")
                        html.append("<tr><th>ID</th><th>Mesure</th><th>Valeur</th><th>Unité</th><th>Spec min</th><th>Spec max</th><th>Statut</th></tr>")
                        for r in rows:
                            idp, labelp, valp, unitp, smin, smax, stat = r
                            row_style = ""
                            if stat.upper() == "FAIL":
                                row_style = " style='color:red;font-weight:bold'"
                            elif stat.upper() == "OK":
                                row_style = " style='color:green'"
                            html.append(
                                f"<tr{row_style}><td>{idp}</td><td>{labelp}</td><td>{valp}</td>"
                                f"<td>{unitp}</td><td>{smin}</td><td>{smax}</td><td>{stat}</td></tr>"
                            )
                        html.append("</table>")
                        self.result_display.setHtml("".join(html))
                    else:
                        self.result_display.setText(joined)
            if update_status:
                if ok:
                    self.next_button.setEnabled(True)
                    self.status_label.setText("Statut du test : Réussi")
                    self.status_label.setStyleSheet("color: green;")
                else:
                    self.status_label.setText("Statut du test : Échec")
                    self.status_label.setStyleSheet("color: red;")
        except COMM_Error as e:
            QMessageBox.warning(self, "Amplificateur error", f"Error {hex(e.code)}")
            if update_status:
                self.status_label.setText("Statut du test : Échec")
                self.status_label.setStyleSheet("color: red;")
        except ATE_Instrument_Error as e:
            QMessageBox.warning(self, "Instrument error", str(e.instrument))
            if update_status:
                self.status_label.setText("Statut du test : Échec")
                self.status_label.setStyleSheet("color: red;")
        except Exception as e:
            QMessageBox.warning(self, "Unexpected error", str(e))
            if update_status:
                self.status_label.setText("Statut du test : Échec")
                self.status_label.setStyleSheet("color: red;")


class MainWindow(QWidget):
    def __init__(self, ate):
        super().__init__()
        title = "RF Amplifier Test Sequence"
        if getattr(ate, "is_simulation", False):
            title += " [Simulation]"
        self.setWindowTitle(title)
        self.resize(1000, 700)

        self.ate = ate
        self.session = SessionData()
        self.eng_mode = False
        self.phase_ok = {name: False for name in PHASES}

        self.stack = QStackedWidget()
        self.phase_pages = []

        self.login_page = LoginPage(self.start_sequence)
        self.stack.addWidget(self.login_page)
    

        self.menu_page = PhaseMenuPage(
            PHASES,
            self.start_from_beginning,
            self.open_eng_mode,
            self.select_phase,
        )
        self.stack.addWidget(self.menu_page)

        for phase in PHASES:
            cfg = PHASE_CONFIG.get(phase, {})
            instruction_text = cfg.get("instruction", "")
            image_path = cfg.get("image", None)
            require_check = bool(cfg.get("require_check", False))
            check_text = cfg.get("check_text", None) or None
            caption_text = cfg.get("caption", None) or None
            subtest_defs = cfg.get("subtests", [])
            subtests = []
            for st in subtest_defs:
                method_name = st.get("method")
                label = st.get("label") or method_name
                if not method_name:
                    continue
                runner = make_subtest_runner(method_name, self.ate)
                subtests.append((label, runner))
            page = PhasePage(
                phase,
                self.make_phase_runner(phase),
                self.back_to_menu,
                instruction_text,
                image_path,
                require_check=require_check,
                check_text=check_text,
                caption_text=caption_text,
                subtests=subtests,
            )
            page.enable_subtests(self.eng_mode)
            page.next_button.clicked.connect(self.next_phase)
            self.phase_pages.append(page)
            self.stack.addWidget(page)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.current_phase_index = -1

    def start_sequence(self, technician_info, dut_info):
        self.session.technician_info = technician_info
        self.session.dut_info = dut_info
        self.stack.setCurrentIndex(1)
        self.current_phase_index = -1

    def start_from_beginning(self):
        self.current_phase_index = 0
        self.stack.setCurrentIndex(2)

    def open_eng_mode(self):
        if self.eng_mode:
            return
        password, ok = QInputDialog.getText(
            self,
            "Engineering mode",
            "Enter password:",
        )
        if not ok:
            return
        if password == "amprf":
            self.eng_mode = True
            self.menu_page.enable_engineering(True)
            for p in self.phase_pages:
                p.enable_subtests(True)
            QMessageBox.information(self, "Engineering mode", "Engineering mode enabled.")
        else:
            QMessageBox.warning(self, "Engineering mode", "Incorrect password.")

    def select_phase(self, index: int):
        if 0 <= index < len(PHASES):
            self.current_phase_index = index
            self.stack.setCurrentIndex(2 + index)

    def make_phase_runner(self, phase_name):
        base_runner = make_phase_runner(phase_name, self.ate)

        def runner():
            lines, ok, values = base_runner()
            self.session.add_phase_result(PhaseResult(phase_name, lines, ok, values))
            self.phase_ok[phase_name] = True
            if phase_name in PHASES:
                idx = PHASES.index(phase_name)
                self.menu_page.set_phase_enabled(idx, True)
                self.menu_page.set_phase_status(idx, ok)
            return lines, ok

        return runner

    def next_phase(self):
        if self.current_phase_index + 1 < len(PHASES):
            self.current_phase_index += 1
            self.stack.setCurrentIndex(2 + self.current_phase_index)
        else:
            self.session.end_time = datetime.datetime.now()
            QMessageBox.information(self, "Sequence finished", "All phases completed.")

    def back_to_menu(self):
        if 0 <= self.current_phase_index < len(PHASES):
            self.menu_page.set_phase_enabled(self.current_phase_index, True)
        self.stack.setCurrentIndex(1)
