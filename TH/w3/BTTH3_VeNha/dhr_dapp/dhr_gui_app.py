"""GUI PySide6 — Digital Health Records DApp (BTTH3 Ve Nha).

Chay (tu thu muc dhr_dapp, Geth dang chay, da deploy):
  d:\\Study\\IS355\\.venv-ape\\Scripts\\python.exe dhr_gui_app.py
"""
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

from ape import accounts, networks, project
from eth_utils import is_address
from PySide6 import QtCore, QtWidgets

DEFAULT_RPC = "http://127.0.0.1:8545"
ADDRESS_FILE = Path(__file__).resolve().parent / "dhr_address.txt"


def fmt_time(ts: int) -> str:
    return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")


def make_table(headers):
    table = QtWidgets.QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setStretchLastSection(True)
    table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    return table


def fill_table(table, rows):
    table.setRowCount(0)
    for row in rows:
        r = table.rowCount()
        table.insertRow(r)
        for c, value in enumerate(row):
            table.setItem(r, c, QtWidgets.QTableWidgetItem(str(value)))
    table.resizeColumnsToContents()


class TxSignals(QtCore.QObject):
    done = QtCore.Signal(int, str, str, str)  # row, tx_hash, status, message


class TxWorker(QtCore.QRunnable):
    def __init__(self, row, fn, signals):
        super().__init__()
        self.row, self.fn, self.signals = row, fn, signals

    def run(self):
        try:
            receipt = self.fn()
            status = "confirmed" if receipt.status == 1 else "failed"
            self.signals.done.emit(self.row, str(receipt.txn_hash), status, f"block {receipt.block_number}")
        except Exception as err:
            self.signals.done.emit(self.row, "-", "failed", str(err).splitlines()[0][:200])


class DHRWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Health Records DApp")
        self.resize(950, 620)

        self.network_ctx = None
        self.contract = None
        self.user = None
        self.role = None
        # 1 luong: cac giao dich cua cung tai khoan phai gui tuan tu de khong trung nonce
        self.pool = QtCore.QThreadPool()
        self.pool.setMaxThreadCount(1)
        self.tx_signals = TxSignals()
        self.tx_signals.done.connect(self.on_tx_done)
        self.tx_callbacks = {}

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self.build_login_tab(), "Đăng nhập")
        self.tabs.addTab(self.build_records_tab(), "Hồ sơ sức khỏe")
        self.tabs.addTab(self.build_access_tab(), "Cấp quyền truy cập")
        self.tabs.addTab(self.build_log_tab(), "Lịch sử truy cập")
        self.tabs.addTab(self.build_tx_tab(), "Trạng thái giao dịch")
        for i in range(1, 4):
            self.tabs.setTabEnabled(i, False)
        self.setCentralWidget(self.tabs)

    # ---------- Tab: Dang nhap ----------
    def build_login_tab(self):
        w = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout()

        self.rpc_edit = QtWidgets.QLineEdit(DEFAULT_RPC)
        self.contract_edit = QtWidgets.QLineEdit(
            ADDRESS_FILE.read_text(encoding="utf-8").strip() if ADDRESS_FILE.exists() else ""
        )
        self.known_combo = QtWidgets.QComboBox()
        self.known_combo.addItem("-- chọn nhanh tài khoản Ape --", "")
        for acc in accounts:
            self.known_combo.addItem(f"{acc.alias}  {acc.address}", acc.address)
        self.known_combo.currentIndexChanged.connect(
            lambda _: self.known_combo.currentData() and self.address_edit.setText(self.known_combo.currentData())
        )
        self.address_edit = QtWidgets.QLineEdit()
        self.address_edit.setPlaceholderText("0x...")
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        login_btn = QtWidgets.QPushButton("Đăng nhập")
        login_btn.clicked.connect(self.do_login)

        form.addRow("RPC endpoint", self.rpc_edit)
        form.addRow("Địa chỉ contract DHR", self.contract_edit)
        form.addRow("Tài khoản có sẵn", self.known_combo)
        form.addRow("Địa chỉ ví", self.address_edit)
        form.addRow("Mật khẩu", self.password_edit)
        form.addRow(login_btn)

        self.role_label = QtWidgets.QLabel("Chưa đăng nhập")
        self.role_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        # Dang ky / xac thuc
        self.reg_name = QtWidgets.QLineEdit()
        self.reg_extra = QtWidgets.QLineEdit()
        self.reg_extra.setPlaceholderText("Năm sinh (bệnh nhân) hoặc chuyên khoa (bác sĩ)")
        reg_patient_btn = QtWidgets.QPushButton("Đăng ký bệnh nhân")
        reg_patient_btn.clicked.connect(self.register_patient)
        reg_doctor_btn = QtWidgets.QPushButton("Đăng ký bác sĩ")
        reg_doctor_btn.clicked.connect(self.register_doctor)
        self.verify_edit = QtWidgets.QLineEdit()
        self.verify_edit.setPlaceholderText("Địa chỉ bác sĩ cần xác thực")
        verify_btn = QtWidgets.QPushButton("Bệnh viện xác thực bác sĩ")
        verify_btn.clicked.connect(self.verify_doctor)

        reg_box = QtWidgets.QGroupBox("Đăng ký vai trò / xác thực bác sĩ")
        reg_form = QtWidgets.QFormLayout(reg_box)
        reg_form.addRow("Họ tên", self.reg_name)
        reg_form.addRow("Năm sinh / Chuyên khoa", self.reg_extra)
        btns = QtWidgets.QHBoxLayout()
        btns.addWidget(reg_patient_btn)
        btns.addWidget(reg_doctor_btn)
        reg_form.addRow(btns)
        reg_form.addRow("Bác sĩ", self.verify_edit)
        reg_form.addRow(verify_btn)

        layout = QtWidgets.QVBoxLayout(w)
        layout.addLayout(form)
        layout.addWidget(self.role_label)
        layout.addWidget(reg_box)
        layout.addStretch()
        return w

    def do_login(self):
        address = self.address_edit.text().strip()
        password = self.password_edit.text()
        try:
            if self.network_ctx is None:
                self.network_ctx = networks.parse_network_choice(f"ethereum:local:{self.rpc_edit.text().strip()}")
                self.network_ctx.__enter__()
            self.contract = project.DHR.at(self.contract_edit.text().strip())
            match = [a for a in accounts if a.address.lower() == address.lower()]
            if not match:
                raise ValueError("Không tìm thấy keystore cho địa chỉ này trong Ape")
            user = match[0]
            user.set_autosign(True, passphrase=password)
        except Exception as err:
            QtWidgets.QMessageBox.critical(self, "Đăng nhập thất bại", str(err).splitlines()[0])
            return

        self.user = user
        for table in (self.records_table, self.log_table):
            table.setRowCount(0)
        self.patient_info.setText("")
        self.access_status.setText("")
        self.rec_patient_edit.clear()
        self.log_patient_edit.clear()
        self.refresh_role()
        for i in range(1, 4):
            self.tabs.setTabEnabled(i, True)
        if self.role == "Bệnh nhân":
            self.rec_patient_edit.setText(user.address)
            self.log_patient_edit.setText(user.address)

    def refresh_role(self):
        addr = self.user.address
        if self.contract.hospital() == addr:
            self.role = "Bệnh viện"
        elif self.contract.patients(addr).exists:
            self.role = "Bệnh nhân"
        elif self.contract.doctors(addr).exists:
            verified = self.contract.doctors(addr).verified
            self.role = "Bác sĩ" + (" (đã xác thực)" if verified else " (chưa xác thực)")
        else:
            self.role = "Chưa đăng ký"
        balance = self.user.balance / 10**18
        self.role_label.setText(f"{self.user.alias} | {addr} | Vai trò: {self.role} | {balance:.4f} ETH")

    def register_patient(self):
        name, year = self.reg_name.text().strip(), self.reg_extra.text().strip() or "0"
        self.send_tx("registerPatient", lambda: self.contract.registerPatient(name, int(year), sender=self.user),
                     self.refresh_role)

    def register_doctor(self):
        name, spec = self.reg_name.text().strip(), self.reg_extra.text().strip()
        self.send_tx("registerDoctor", lambda: self.contract.registerDoctor(name, spec, sender=self.user),
                     self.refresh_role)

    def checked_address(self, edit, what):
        value = edit.text().strip()
        if not is_address(value):
            QtWidgets.QMessageBox.warning(self, "Địa chỉ không hợp lệ", f"Nhập địa chỉ ví {what} (0x... 40 ký tự hex)")
            return None
        return value

    def wait_pending(self):
        while self.tx_callbacks:
            QtWidgets.QApplication.processEvents()
            time.sleep(0.05)

    def show_read_error(self, title, err):
        traceback.print_exc()
        QtWidgets.QMessageBox.warning(self, title, str(err).splitlines()[0])

    def verify_doctor(self):
        doctor = self.checked_address(self.verify_edit, "bác sĩ")
        if not doctor:
            return
        self.send_tx("verifyDoctor", lambda: self.contract.verifyDoctor(doctor, sender=self.user))

    # ---------- Tab: Ho so ----------
    def build_records_tab(self):
        w = QtWidgets.QWidget()
        top = QtWidgets.QHBoxLayout()
        self.rec_patient_edit = QtWidgets.QLineEdit()
        self.rec_patient_edit.setPlaceholderText("Địa chỉ bệnh nhân")
        load_btn = QtWidgets.QPushButton("Xem hồ sơ")
        load_btn.clicked.connect(self.load_records)
        top.addWidget(QtWidgets.QLabel("Bệnh nhân:"))
        top.addWidget(self.rec_patient_edit)
        top.addWidget(load_btn)

        self.patient_info = QtWidgets.QLabel("")
        self.records_table = make_table(["#", "Ngày khám", "Chẩn đoán", "Đơn thuốc", "Ghi chú", "Người ghi", "Thời gian"])

        box = QtWidgets.QGroupBox("Thêm hồ sơ mới")
        form = QtWidgets.QFormLayout(box)
        self.diag_edit = QtWidgets.QLineEdit()
        self.presc_edit = QtWidgets.QLineEdit()
        self.date_edit = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.note_edit = QtWidgets.QLineEdit()
        add_btn = QtWidgets.QPushButton("Thêm hồ sơ mới")
        add_btn.clicked.connect(self.add_record)
        form.addRow("Chẩn đoán", self.diag_edit)
        form.addRow("Đơn thuốc", self.presc_edit)
        form.addRow("Ngày khám", self.date_edit)
        form.addRow("Ghi chú", self.note_edit)
        form.addRow(add_btn)

        layout = QtWidgets.QVBoxLayout(w)
        layout.addLayout(top)
        layout.addWidget(self.patient_info)
        layout.addWidget(self.records_table)
        layout.addWidget(box)
        return w

    def load_records(self):
        patient = self.checked_address(self.rec_patient_edit, "bệnh nhân")
        if not patient:
            return
        self.wait_pending()
        self.records_table.setRowCount(0)
        self.patient_info.setText("")
        try:
            info = self.contract.patients(patient)
            if not info.exists:
                raise ValueError("Địa chỉ này chưa đăng ký bệnh nhân")
            rows = []
            for i in range(self.contract.getRecordCount(patient)):
                r = self.contract.viewHealthRecord(patient, i, sender=self.user.address)
                rows.append([i, r.visitDate, r.diagnosis, r.prescription, r.note, r.doctor, fmt_time(r.timestamp)])
        except Exception as err:
            self.show_read_error("Không xem được hồ sơ", err)
            return
        self.patient_info.setText(f"Bệnh nhân: {info.name} — năm sinh {info.birthYear} — {len(rows)} hồ sơ")
        fill_table(self.records_table, rows)
        if self.user.address.lower() != patient.lower():
            self.send_tx("logView", lambda: self.contract.logView(patient, sender=self.user))

    def add_record(self):
        patient = self.checked_address(self.rec_patient_edit, "bệnh nhân")
        if not patient:
            return
        args = (patient, self.diag_edit.text(), self.presc_edit.text(),
                self.date_edit.date().toString("yyyy-MM-dd"), self.note_edit.text())
        self.send_tx("addHealthRecord", lambda: self.contract.addHealthRecord(*args, sender=self.user),
                     self.load_records)

    # ---------- Tab: Cap quyen ----------
    def build_access_tab(self):
        w = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout()
        self.access_doctor_edit = QtWidgets.QLineEdit()
        self.access_doctor_edit.setPlaceholderText("Địa chỉ ví bác sĩ")
        grant_btn = QtWidgets.QPushButton("Cấp quyền đọc/ghi")
        grant_btn.clicked.connect(self.grant_access)
        revoke_btn = QtWidgets.QPushButton("Thu hồi quyền")
        revoke_btn.clicked.connect(self.revoke_access)
        check_btn = QtWidgets.QPushButton("Kiểm tra quyền")
        check_btn.clicked.connect(self.check_access)
        self.access_status = QtWidgets.QLabel("")

        form.addRow("Bác sĩ", self.access_doctor_edit)
        btns = QtWidgets.QHBoxLayout()
        for b in (grant_btn, revoke_btn, check_btn):
            btns.addWidget(b)
        form.addRow(btns)
        form.addRow(self.access_status)

        layout = QtWidgets.QVBoxLayout(w)
        layout.addWidget(QtWidgets.QLabel("Bệnh nhân (tài khoản đang đăng nhập) cấp / thu hồi quyền cho bác sĩ."))
        layout.addLayout(form)
        layout.addStretch()
        return w

    def grant_access(self):
        doctor = self.checked_address(self.access_doctor_edit, "bác sĩ")
        if doctor:
            self.send_tx("grantAccess", lambda: self.contract.grantAccess(doctor, sender=self.user), self.check_access)

    def revoke_access(self):
        doctor = self.checked_address(self.access_doctor_edit, "bác sĩ")
        if doctor:
            self.send_tx("revokeAccess", lambda: self.contract.revokeAccess(doctor, sender=self.user), self.check_access)

    def check_access(self):
        doctor = self.checked_address(self.access_doctor_edit, "bác sĩ")
        if not doctor:
            return
        self.wait_pending()
        try:
            info = self.contract.doctors(doctor)
            has = self.contract.hasAccess(self.user.address, doctor)
        except Exception as err:
            traceback.print_exc()
            self.access_status.setText(str(err).splitlines()[0])
            return
        self.access_status.setText(
            f"Bác sĩ: {info.name or '(chưa đăng ký)'} — {info.specialty} — "
            f"{'đã xác thực' if info.verified else 'chưa xác thực'} — quyền: {'CÓ' if has else 'KHÔNG'}"
        )

    # ---------- Tab: Lich su ----------
    def build_log_tab(self):
        w = QtWidgets.QWidget()
        top = QtWidgets.QHBoxLayout()
        self.log_patient_edit = QtWidgets.QLineEdit()
        self.log_patient_edit.setPlaceholderText("Địa chỉ bệnh nhân")
        load_btn = QtWidgets.QPushButton("Tải lịch sử")
        load_btn.clicked.connect(self.load_logs)
        top.addWidget(QtWidgets.QLabel("Bệnh nhân:"))
        top.addWidget(self.log_patient_edit)
        top.addWidget(load_btn)
        self.log_table = make_table(["Thời gian", "Hành động", "Người thực hiện", "Đối tượng"])

        layout = QtWidgets.QVBoxLayout(w)
        layout.addLayout(top)
        layout.addWidget(self.log_table)
        return w

    def load_logs(self):
        patient = self.checked_address(self.log_patient_edit, "bệnh nhân")
        if not patient:
            return
        self.wait_pending()
        self.log_table.setRowCount(0)
        try:
            rows = []
            for i in range(self.contract.getLogCount(patient)):
                log = self.contract.getLog(patient, i, sender=self.user.address)
                rows.append([fmt_time(log.timestamp), log.action, log.actor, log.target])
        except Exception as err:
            self.show_read_error("Không tải được lịch sử", err)
            return
        fill_table(self.log_table, rows)

    # ---------- Tab: Trang thai giao dich ----------
    def build_tx_tab(self):
        w = QtWidgets.QWidget()
        self.tx_table = make_table(["Thời gian", "Hàm", "Transaction hash", "Trạng thái", "Chi tiết"])
        layout = QtWidgets.QVBoxLayout(w)
        layout.addWidget(self.tx_table)
        return w

    def send_tx(self, label, fn, on_success=None):
        row = self.tx_table.rowCount()
        self.tx_table.insertRow(row)
        for c, v in enumerate([datetime.now().strftime("%H:%M:%S"), label, "(đang gửi...)", "pending", ""]):
            self.tx_table.setItem(row, c, QtWidgets.QTableWidgetItem(v))
        self.statusBar().showMessage(f"{label}: pending...")
        self.tx_callbacks[row] = (label, on_success)
        self.pool.start(TxWorker(row, fn, self.tx_signals))

    @QtCore.Slot(int, str, str, str)
    def on_tx_done(self, row, tx_hash, status, message):
        label, on_success = self.tx_callbacks.pop(row)
        for c, v in ((2, tx_hash), (3, status), (4, message)):
            self.tx_table.setItem(row, c, QtWidgets.QTableWidgetItem(v))
        self.tx_table.resizeColumnsToContents()
        self.statusBar().showMessage(f"{label}: {status} {tx_hash}")
        if status == "confirmed":
            QtWidgets.QMessageBox.information(self, "Giao dịch hoàn tất", f"{label}\n{tx_hash}\n{message}")
            if on_success:
                on_success()
        else:
            QtWidgets.QMessageBox.warning(self, "Giao dịch thất bại", f"{label}\n{message}")

    def closeEvent(self, event):
        if self.network_ctx is not None:
            self.network_ctx.__exit__(None, None, None)
        super().closeEvent(event)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = DHRWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
