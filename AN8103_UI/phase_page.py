from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QMessageBox,
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from ATE_Lib_AN8103.ate_lib import COMM_Error, ATE_Instrument_Error
from .phase_views import render_results_table
from .test_steps.test_result import TestResult


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
        self.subtests_unlocked = not enable_subtests_on_run
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
            # Create two rows for subtest buttons
            sub_row1 = QHBoxLayout()
            sub_row2 = QHBoxLayout()
            
            # Determine split point (halfway)
            count = len(self.subtests)
            mid = (count + 1) // 2
            
            for i, (label, cb) in enumerate(self.subtests):
                btn = QPushButton(label)
                btn.setFont(QFont("Arial", 12))
                btn.clicked.connect(self.make_subtest_handler(cb, label))
                btn.setEnabled(False)
                self.subtest_buttons.append(btn)
                self.subtest_buttons_by_label[label] = btn
                
                # Add to first or second row based on index
                if i < mid:
                    sub_row1.addWidget(btn)
                else:
                    sub_row2.addWidget(btn)
            
            layout.addLayout(sub_row1)
            layout.addLayout(sub_row2)

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

        if not enabled:
            for btn in self.subtest_buttons:
                btn.setEnabled(False)
            return

        if self.enable_subtests_on_run and not self.subtests_unlocked:
            for btn in self.subtest_buttons:
                btn.setEnabled(False)
            return

        for label, btn in self.subtest_buttons_by_label.items():
            if label in self.locked_subtests:
                btn.setEnabled(False)
            else:
                btn.setEnabled(True)
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
        
        for label in self.locked_subtests:
            btn = self.subtest_buttons_by_label.get(label)
            if btn:
                btn.setEnabled(deps_met)

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
        if self.enable_subtests_on_run:
            self.subtests_unlocked = False
        self.enable_subtests(False)
        self.check_button.setStyleSheet("background-color: green; color: white;")

    def on_run(self):
        if self.enable_subtests_on_run and self.subtests:
            self.result_display.clear()
            self.subtest_results = {}
            self.subtests_unlocked = True
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
        if subtest_label and self.enable_subtests_on_run and not self.subtests_unlocked and not self.eng_mode:
            return

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

    def reset_operator_flow(self):
        if self.eng_mode:
            return
        if self.require_check:
            self.checked = False
            self.run_button.setEnabled(False)
            self.check_button.setStyleSheet("")
        if self.enable_subtests_on_run and self.subtests:
            self.subtests_unlocked = False
            self.subtest_results = {}
            self.enable_subtests(False)
