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
    QComboBox,
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from ATE_Lib_AN8103.ate_lib import COMM_Error, ATE_Instrument_Error
import datetime
import re
from .data_store import SessionData, PhaseResult
from .phase_config import PHASES, PHASE_CONFIG, ATE_CONFIGURATIONS
from .phase_controller import make_phase_runner, make_subtest_runner
from .phase_services import TestResult
from .phase_views import render_diagnostic_report, render_performance_report, render_results_table

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
        self.ate_combo = QComboBox()
        self.ate_combo.addItems(["ATE01", "ATE02"])
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
        add_row("Sélection ATE:", self.ate_combo)
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
            "ATE_ID": self.ate_combo.currentText(),
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


class SetupPage(QWidget):
    def __init__(self, proceed_callback):
        super().__init__()
        self.proceed_callback = proceed_callback
        self.target_index = -1
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        self.title_label = QLabel("Configuration Setup")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 22, QFont.Bold))
        layout.addWidget(self.title_label)
        
        self.instruction_label = QLabel("")
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.instruction_label)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        
        confirm_btn = QPushButton("Configuration Prête / Continue")
        confirm_btn.setFont(QFont("Arial", 16, QFont.Bold))
        confirm_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        confirm_btn.clicked.connect(self.on_proceed)
        layout.addWidget(confirm_btn)
        
        self.setLayout(layout)

    def set_config(self, config_data, target_index):
        self.target_index = target_index
        title = config_data.get("title", "Setup Configuration")
        instruction = config_data.get("instruction", "")
        image_path = config_data.get("image", "")
        
        self.title_label.setText(title)
        self.instruction_label.setText(instruction)
        
        if image_path:
            pix = QPixmap(image_path)
            if not pix.isNull():
                self.image_label.setPixmap(pix.scaledToHeight(400, Qt.SmoothTransformation))
            else:
                self.image_label.clear()
        else:
            self.image_label.clear()

    def on_proceed(self):
        if self.target_index != -1:
            self.proceed_callback(self.target_index)


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

            cfg = PHASE_CONFIG.get(phase, {})
            display_name = cfg.get("display_name", phase)

            btn = QPushButton(f"{index + 1}. {display_name}")
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
            if ok is None:
                label.setText("Non testé")
                label.setStyleSheet("color: black;")
                label.setFont(QFont("Arial", 11))
            elif ok:
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
        enable_subtests_on_run=False,
        locked_subtests=None,
        unlock_when_subtests_done=None,
        status_callback=None,
    ):
        super().__init__()
        self.phase_name = phase_name
        self.run_callback = run_callback
        self.back_callback = back_callback
        self.status_callback = status_callback
        self.require_check = require_check
        self.checked = not require_check
        self.subtests = subtests or []
        self.enable_subtests_on_run = enable_subtests_on_run
        self.locked_subtests = set(locked_subtests or [])
        self.unlock_when_subtests_done = set(unlock_when_subtests_done or [])
        self.subtest_buttons = []
        self.subtest_buttons_by_label = {}
        self.subtest_results = {}
        self.eng_mode = False

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
                btn.clicked.connect(self.make_subtest_handler(cb, label))
                btn.setEnabled(False)
                self.subtest_buttons.append(btn)
                self.subtest_buttons_by_label[label] = btn
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

        self.next_button = QPushButton("Étape suivante")
        self.next_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.next_button.setEnabled(False)
        button_row.addWidget(self.next_button)

        layout.addLayout(button_row)
        self.setLayout(layout)

    def set_eng_mode(self, enabled: bool):
        self.eng_mode = enabled
        if enabled:
            self.run_button.setEnabled(True)
            self.enable_subtests(True)
        else:
            self.run_button.setEnabled(self.checked)
            self.enable_subtests(False)

    def enable_subtests(self, enabled: bool):
        if self.eng_mode:
            for btn in self.subtest_buttons:
                btn.setEnabled(True)
            return

        for label, btn in self.subtest_buttons_by_label.items():
            if not enabled:
                btn.setEnabled(False)
                continue
            if label in self.locked_subtests:
                btn.setEnabled(False)
            else:
                btn.setEnabled(True)
        if enabled:
            self.update_locked_subtests()

    def update_locked_subtests(self):
        if self.eng_mode:
            return

        if not self.locked_subtests:
            return

        # Check dependencies: must be present AND passed
        deps_met = True
        if self.unlock_when_subtests_done:
            for dep in self.unlock_when_subtests_done:
                if dep not in self.subtest_results:
                    deps_met = False
                    break
                
                # Check result status
                res_list = self.subtest_results[dep]
                if not isinstance(res_list, list):
                    res_list = [res_list]
                
                step_passed = True
                for r in res_list:
                    if isinstance(r, TestResult):
                        if r.status not in ("PASS", "OK"):
                            step_passed = False
                            break
                if not step_passed:
                    deps_met = False
                    break
        
        if deps_met:
            for label in self.locked_subtests:
                btn = self.subtest_buttons_by_label.get(label)
                if btn:
                    btn.setEnabled(True)

    def set_status(self, ok: bool, enable_next: bool = True):
        if self.status_callback:
            self.status_callback(ok)
        if ok:
            if enable_next:
                self.next_button.setEnabled(True)
            self.status_label.setText("Statut du test : Réussi")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Statut du test : Échec")
            self.status_label.setStyleSheet("color: red;")

    def collect_subtest_results(self):
        combined = []
        for lbl, _ in self.subtests:
            if lbl in self.subtest_results:
                res = self.subtest_results[lbl]
                if isinstance(res, list):
                    combined.extend(res)
                else:
                    combined.append(res)
        return combined

    def all_subtests_ran(self):
        for lbl, _ in self.subtests:
            if lbl not in self.subtest_results:
                return False
        return True

    def all_subtests_passed(self):
        for lbl, _ in self.subtests:
            res_list = self.subtest_results[lbl]
            if isinstance(res_list, list) and len(res_list) > 0 and isinstance(res_list[0], TestResult):
                for r in res_list:
                    if r.status not in ("PASS", "OK"):
                        return False
        return True

    def on_checked(self):
        self.checked = True
        self.run_button.setEnabled(True)
        self.enable_subtests(False)
        self.check_button.setStyleSheet("background-color: green; color: white;")

    def on_run(self):
        if self.enable_subtests_on_run and self.subtests:
            self.result_display.clear()
            self.subtest_results = {}
            self.status_label.setText("Statut du test : Non testé")
            self.status_label.setStyleSheet("")
            self.enable_subtests(True)
            if "Non testé" in self.status_label.text():
                self.status_label.setText("Veuillez exécuter les sous-tests")
        else:
            self.handle_run(self.run_callback, True)

    def make_subtest_handler(self, cb, label):
        def handler():
            self.handle_run(cb, False, subtest_label=label)

        return handler

    def handle_run(self, callback, update_status, subtest_label=None):
        if not subtest_label:
            self.result_display.clear()
            self.subtest_results = {}

        try:
            results, ok = callback()

            if subtest_label:
                self.subtest_results[subtest_label] = results
                self.update_locked_subtests()
                combined = self.collect_subtest_results()
                if self.all_subtests_ran():
                    if self.all_subtests_passed():
                        self.set_status(True)
                        combined.append(
                            TestResult(
                                test_id="FINAL",
                                label="Résultat final",
                                value="PASS",
                                unit="",
                                min_spec=None,
                                max_spec=None,
                                status="PASS",
                            )
                        )
                    else:
                        self.set_status(False)
                        combined.append(
                            TestResult(
                                test_id="FINAL",
                                label="Résultat final",
                                value="FAIL",
                                unit="",
                                min_spec=None,
                                max_spec=None,
                                status="FAIL",
                            )
                        )
                results = combined
            if results:
                if isinstance(results[0], TestResult):
                    self.result_display.setHtml(render_results_table(results))
                else:
                    text_lines = results
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
                self.set_status(ok)
                self.enable_subtests(True)
        except COMM_Error as e:
            QMessageBox.warning(self, "Amplificateur error", f"Error {hex(e.code)}")
            if update_status:
                self.set_status(False, enable_next=False)
        except ATE_Instrument_Error as e:
            QMessageBox.warning(self, "Instrument error", str(e.instrument))
            if update_status:
                self.set_status(False, enable_next=False)
        except Exception as e:
            QMessageBox.warning(self, "Unexpected error", str(e))
            if update_status:
                self.set_status(False, enable_next=False)


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
        self.current_config_id = None  # Track current configuration

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

        # Create pages for phases (indices 2 to 2+len(PHASES)-1)
        for index, phase in enumerate(PHASES):
            cfg = PHASE_CONFIG.get(phase, {})
            display_name = cfg.get("display_name", phase)
            instruction_text = cfg.get("instruction", "")
            image_path = cfg.get("image", None)
            require_check = bool(cfg.get("require_check", False))
            check_text = cfg.get("check_text", None) or None
            caption_text = cfg.get("caption", None) or None
            enable_subtests_on_run = bool(cfg.get("enable_subtests_on_run", False))
            locked_subtests = set(cfg.get("locked_subtests", []) or [])
            unlock_when_subtests_done = set(cfg.get("unlock_when_subtests_done", []) or [])
            subtest_defs = cfg.get("subtests", [])
            subtests = []
            for st in subtest_defs:
                method_name = st.get("method")
                label = st.get("label") or method_name
                if not method_name:
                    continue
                runner = make_subtest_runner(method_name, self.ate, self.interaction_callback)
                subtests.append((label, runner))
            
            def make_status_callback(idx):
                def callback(ok):
                    self.update_phase_status(idx, ok)
                return callback

            page = PhasePage(
                display_name,
                self.make_phase_runner(phase),
                self.back_to_menu,
                instruction_text,
                image_path,
                require_check=require_check,
                check_text=check_text,
                caption_text=caption_text,
                subtests=subtests,
                enable_subtests_on_run=enable_subtests_on_run,
                locked_subtests=locked_subtests,
                unlock_when_subtests_done=unlock_when_subtests_done,
                status_callback=make_status_callback(index),
            )
            page.next_button.clicked.connect(self.next_phase)
            self.phase_pages.append(page)
            self.stack.addWidget(page)

        # Setup Page (index = 2 + len(PHASES))
        self.setup_page = SetupPage(self.resume_phase_after_setup)
        self.stack.addWidget(self.setup_page)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.current_phase_index = -1

    def update_phase_status(self, index, ok):
        if 0 <= index < len(PHASES):
            phase_name = PHASES[index]
            self.phase_ok[phase_name] = ok
            self.menu_page.set_phase_status(index, ok)

    def start_sequence(self, technician_info, dut_info):
        self.eng_mode = False
        for page in self.phase_pages:
            page.set_eng_mode(False)
        self.session.technician_info = technician_info
        self.session.dut_info = dut_info
        self.stack.setCurrentIndex(1)
        self.current_phase_index = -1
        self.current_config_id = None # Reset config on new sequence
        
        # Apply ATE restrictions based on selection
        ate_id = technician_info.get("ATE_ID", "ATE01")
        
        # Reset all buttons first
        for btn in self.menu_page.phase_buttons:
            btn.setVisible(True)
            
        try:
            special_phase_index = PHASES.index("Output conditional tuning")
        except ValueError:
            special_phase_index = -1
            
        if ate_id == "ATE01":
            # ATE01: All tests EXCEPT "Output conditional tuning"
            for i, btn in enumerate(self.menu_page.phase_buttons):
                if i == special_phase_index:
                    btn.setEnabled(False)
                    btn.setToolTip("Only available on ATE02")
                else:
                    btn.setEnabled(False)
                    btn.setToolTip("Use 'Start Sequence' button")
                
        elif ate_id == "ATE02":
            # ATE02: ONLY "Output conditional tuning"
            for i, btn in enumerate(self.menu_page.phase_buttons):
                if i == special_phase_index:
                    btn.setEnabled(False)
                    btn.setToolTip("Use 'Start Sequence' button")
                else:
                    btn.setEnabled(False)
                    btn.setToolTip("Only available on ATE01")

    def start_from_beginning(self):
        if self.eng_mode:
            # In engineering mode, always start from beginning
            self.go_to_phase_safely(0)
            return

        ate_id = self.session.technician_info.get("ATE_ID", "ATE01")
        target_index = 0
        
        try:
            special_phase_index = PHASES.index("Output conditional tuning")
        except ValueError:
            special_phase_index = -1
            
        if ate_id == "ATE01":
            target_index = 0
        elif ate_id == "ATE02":
            target_index = special_phase_index if special_phase_index != -1 else 0
        
        self.go_to_phase_safely(target_index)

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
                p.set_eng_mode(True)
            QMessageBox.information(self, "Engineering mode", "Engineering mode enabled.")
        else:
            QMessageBox.warning(self, "Engineering mode", "Incorrect password.")

    def select_phase(self, index: int):
        if 0 <= index < len(PHASES):
            self.go_to_phase_safely(index)

    def go_to_phase_safely(self, index):
        """
        Handles transition to a phase, checking for configuration changes first.
        """
        if index < 0 or index >= len(PHASES):
            return

        phase_name = PHASES[index]
        config_id = PHASE_CONFIG.get(phase_name, {}).get("ate_config")
        
        # Always show setup page if config_id is defined, regardless of current config
        if config_id:
            config_data = ATE_CONFIGURATIONS.get(config_id, {})
            self.setup_page.set_config(config_data, index)
            self.stack.setCurrentWidget(self.setup_page)
            self.current_config_id = config_id
        else:
            # Go directly to phase
            self.resume_phase_after_setup(index)

    def resume_phase_after_setup(self, index):
        self.current_phase_index = index
        # Index 0 is Login, 1 is Menu, 2 is Phase 1...
        self.stack.setCurrentIndex(2 + index)

    def interaction_callback(self, msg):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Réglage Manuel")
        msg_box.setText(msg)
        
        # Custom buttons
        retry_btn = msg_box.addButton("Mesurer", QMessageBox.YesRole)
        continue_btn = msg_box.addButton("Continuer", QMessageBox.NoRole)
        
        msg_box.exec_()
        
        return msg_box.clickedButton() == retry_btn

    def make_phase_runner(self, phase_name):
        base_runner = make_phase_runner(phase_name, self.ate, self.interaction_callback)

        def runner():
            # Dynamically handle different return signatures from base_runner
            ret = base_runner()
            lines = []
            ok = False
            values = {}
            test_results = []
            
            if len(ret) == 3:
                lines, ok, values = ret
                if phase_name == "Diagnostic":
                    lines = [render_diagnostic_report(values)]
            elif len(ret) == 2:
                # Could be (lines, ok) or (results, ok)
                first, second = ret
                ok = second
                if isinstance(first, list) and len(first) > 0 and isinstance(first[0], TestResult):
                    test_results = first
                    # Generate simple lines for display if needed
                    if phase_name == "Performance test / burn":
                        lines = [render_performance_report(test_results)]
                    else:
                        lines = [f"{tr.label}: {tr.value} {tr.unit} [{tr.status}]" for tr in test_results]
                    # Populate values map for legacy lookups
                    for tr in test_results:
                        if tr.test_id and tr.test_id not in ("INFO", "ERROR"):
                            values[tr.test_id] = tr.value
                else:
                    lines = first
            else:
                lines = []
                ok = False
            
            # Store result
            self.session.add_phase_result(PhaseResult(phase_name, lines, ok, values, test_results=test_results))
            
            # Update UI state
            self.phase_ok[phase_name] = True
            if phase_name in PHASES:
                try:
                    idx = PHASES.index(phase_name)
                    self.menu_page.set_phase_enabled(idx, True)
                    self.menu_page.set_phase_status(idx, ok)
                except ValueError:
                    pass # Phase might not be in main list (e.g. subtest?)
            
            # Return what the caller expects. 
            # PhasePage.handle_run expects (results, ok).
            # If we have test_results AND we haven't already rendered a custom report in lines, return test_results.
            # If we rendered a custom report (like for Performance), we want to return 'lines' so PhasePage displays that HTML.
            
            # For Performance test, we want to use the rendered lines.
            if phase_name == "Performance test / burn" and lines:
                return lines, ok

            if test_results:
                return test_results, ok
            return lines, ok

        return runner

    def next_phase(self):
        ate_id = self.session.technician_info.get("ATE_ID", "ATE01")
        
        try:
            special_phase_index = PHASES.index("Output conditional tuning")
        except ValueError:
            special_phase_index = -1
            
        next_index = self.current_phase_index + 1
        
        # In engineering mode, skip ATE logic and just go to next
        if not self.eng_mode:
            if ate_id == "ATE01":
                # If next is the special one, skip it
                if next_index == special_phase_index:
                    next_index += 1
                    
            elif ate_id == "ATE02":
                # If we just finished the special one (or anything else), we stop
                if next_index > special_phase_index:
                    next_index = len(PHASES) # Trigger finish
                elif next_index < special_phase_index:
                    # Jump to it if we somehow started before it
                    next_index = special_phase_index

        if next_index < len(PHASES):
            self.go_to_phase_safely(next_index)
        else:
            self.session.end_time = datetime.datetime.now()
            self.generate_reports()
            QMessageBox.information(self, "Sequence finished", "All phases completed.")

    def generate_reports(self):
        try:
            # Generate CSV (TestID data only)
            import csv
            import os
            import json
            
            timestamp = self.session.start_time.strftime("%Y%m%d_%H%M%S")
            dut_sn = self.session.dut_info.get("DUT_Serial", "UNKNOWN")
            base_dir = "TestResults"
            os.makedirs(base_dir, exist_ok=True)
            
            # 1. Production CSV (Only TestID data)
            csv_filename = f"{base_dir}/PROD_{dut_sn}_{timestamp}.csv"
            rows = self.session.to_csv_rows()
            if rows:
                with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                    # Determine fieldnames from first row, or standard set
                    fieldnames = ["phase", "test_key", "value", "ok", "timestamp", "label", "unit", "min_spec", "max_spec", "status"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                    writer.writeheader()
                    writer.writerows(rows)
            
            # 2. Full Diagnostic Report (JSON/HTML)
            report_data = self.session.to_full_report_data()
            json_filename = f"{base_dir}/DIAG_{dut_sn}_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=4, default=str)
                
        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Failed to generate reports: {e}")

    def back_to_menu(self):
        if 0 <= self.current_phase_index < len(PHASES):
            self.menu_page.set_phase_enabled(self.current_phase_index, True)
            
            # Update menu status based on phase result
            phase_page = self.phase_pages[self.current_phase_index]
            status_text = phase_page.status_label.text()
            
            if "Réussi" in status_text:
                self.phase_ok[PHASES[self.current_phase_index]] = True
                self.menu_page.set_phase_status(self.current_phase_index, True)
            elif "Échec" in status_text:
                self.phase_ok[PHASES[self.current_phase_index]] = False
                self.menu_page.set_phase_status(self.current_phase_index, False)
            else:
                self.phase_ok[PHASES[self.current_phase_index]] = False
                self.menu_page.set_phase_status(self.current_phase_index, None)
                
        self.stack.setCurrentIndex(1)
