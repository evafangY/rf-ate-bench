import datetime
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QMessageBox,
    QInputDialog,
)
from ATE_Lib_AN8103.ate_lib import COMM_Error, ATE_Instrument_Error
from .data_store import SessionData, PhaseResult
from .phase_config import PHASES, PHASE_CONFIG, ATE_CONFIGURATIONS
from .phase_controller import make_phase_runner, make_subtest_runner
from .phase_services import TestResult
from .phase_views import render_diagnostic_report, render_performance_report
from .login_page import LoginPage
from .setup_page import SetupPage
from .phase_menu_page import PhaseMenuPage
from .phase_page import PhasePage


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
            # Ensure the button is enabled so the user can re-run the test if needed
            self.menu_page.set_phase_enabled(index, True)

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
        page = self.phase_pages[index]
        page.reset_operator_flow()
        # Index 0 is Login, 1 is Menu, 2 is Phase 1...
        self.stack.setCurrentIndex(2 + index)

    def interaction_callback(self, msg):
        if isinstance(msg, dict) and msg.get("type") == "manual_input":
            title = msg.get("title", "Saisie Manuelle")
            instruction = msg.get("instruction", "Veuillez saisir une valeur:")
            default_value = msg.get("default_value", 0.0)
            min_val = msg.get("min_value", -1000.0)
            max_val = msg.get("max_value", 1000.0)
            decimals = msg.get("decimals", 2)
            
            val, ok = QInputDialog.getDouble(
                self,
                title,
                instruction,
                default_value,
                min_val,
                max_val,
                decimals,
            )
            return {
                "ok": ok,
                "value": val
            }

        if isinstance(msg, dict) and msg.get("type") == "step6_gain_adjust":
            title = msg.get("title", "Réglage Manuel")
            instruction = msg.get("instruction", "")
            target = msg.get("target_dbm")
            tol = msg.get("tolerance_db")
            measured = msg.get("measured_dbm")
            status = msg.get("status", "")
            stable_count = int(msg.get("stable_count", 0) or 0)
            required_count = int(msg.get("required_count", 3) or 3)
            allow_auto_measure = bool(msg.get("allow_auto_measure", False))
            allow_manual_measure = bool(msg.get("allow_manual_measure", True))

            measured_text = "N/A" if measured is None else f"{float(measured):.2f} dBm"
            target_text = "N/A" if target is None else f"{float(target):.2f} dBm"
            tol_text = "N/A" if tol is None else f"±{float(tol):.2f} dB"

            text = (
                f"{instruction}\n\n"
                f"Cible: {target_text} ({tol_text})\n"
                f"Mesure actuelle: {measured_text}\n"
                f"Statut: {status}\n"
                f"Mesures consécutives valides: {stable_count}/{required_count}\n\n"
                "Mesurer: saisir une nouvelle lecture du wattmètre.\n"
                "Continuer: valider cette étape.\n"
                "Annuler: arrêter l'étape."
            )

            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(title)
            msg_box.setText(text)
            measure_btn = msg_box.addButton("Mesurer", QMessageBox.YesRole) if allow_manual_measure else None
            continue_btn = msg_box.addButton("Continuer", QMessageBox.NoRole)
            auto_btn = msg_box.addButton("Mesure ATE", QMessageBox.ActionRole) if allow_auto_measure else None
            abort_btn = msg_box.addButton("Annuler", QMessageBox.RejectRole)
            msg_box.exec_()

            clicked = msg_box.clickedButton()
            if auto_btn is not None and clicked == auto_btn:
                return {
                    "action": "auto_measure",
                    "measured_dbm": measured,
                }
            if measure_btn is not None and clicked == measure_btn:
                default_value = float(measured) if measured is not None else (float(target) if target is not None else 72.0)
                val, ok = QInputDialog.getDouble(
                    self,
                    "Mesure wattmètre",
                    "Puissance mesurée (dBm):",
                    default_value,
                    -100.0,
                    100.0,
                    2,
                )
                return {
                    "action": "measure",
                    "measured_dbm": float(val) if ok else measured,
                }
            if clicked == abort_btn:
                return {
                    "action": "abort",
                    "measured_dbm": measured,
                }
            return {
                "action": "continue",
                "measured_dbm": measured,
            }

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Réglage Manuel")
        msg_box.setText(msg)
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
        
        # Robustness: Ensure all completed phases have their menu buttons enabled
        for i, page in enumerate(self.phase_pages):
            status_text = page.status_label.text()
            if "Réussi" in status_text or "Échec" in status_text:
                self.menu_page.set_phase_enabled(i, True)
                
        self.stack.setCurrentIndex(1)
