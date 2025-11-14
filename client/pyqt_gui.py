#!/usr/bin/env python3
"""
client/pyqt_gui.py
PyQt5 GUI for CloudFileStorage (login + dashboard).
Self-contained token helpers included.
"""

import sys
import os
import json
import requests
from PyQt5 import QtWidgets, QtCore

BASE_URL = "http://127.0.0.1:5000"
TOKEN_PATH = os.path.join(os.path.dirname(__file__), ".token")


# ---------------- Token helpers ----------------
def save_token(token: str):
    with open(TOKEN_PATH, "w") as f:
        json.dump({"token": token}, f)


def load_token() -> str | None:
    if not os.path.exists(TOKEN_PATH):
        return None
    try:
        with open(TOKEN_PATH, "r") as f:
            return json.load(f).get("token")
    except Exception:
        return None


def clear_token():
    if os.path.exists(TOKEN_PATH):
        os.remove(TOKEN_PATH)


def auth_headers():
    token = load_token()
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


# ---------------- GUI Windows ----------------
class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CloudFileStorage - Login")
        self.setFixedSize(380, 220)
        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("<h2>CloudFileStorage</h2>", alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        form = QtWidgets.QFormLayout()
        self.email_input = QtWidgets.QLineEdit()
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Email:", self.email_input)
        form.addRow("Password:", self.password_input)
        layout.addLayout(form)

        self.msg = QtWidgets.QLabel("")
        layout.addWidget(self.msg)

        btn_layout = QtWidgets.QHBoxLayout()
        login_btn = QtWidgets.QPushButton("Login")
        login_btn.clicked.connect(self.do_login)
        btn_layout.addStretch()
        btn_layout.addWidget(login_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def do_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if not email or not password:
            self.msg.setText("<font color='red'>Email and password required</font>")
            return
        try:
            res = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        except Exception as e:
            self.msg.setText("<font color='red'>Network error</font>")
            return
        if res.ok:
            data = res.json()
            token = data.get("token")
            if token:
                save_token(token)
                self.msg.setText("<font color='green'>Login successful</font>")
                QtCore.QTimer.singleShot(400, self.open_dashboard)
                return
            else:
                self.msg.setText("<font color='red'>No token returned</font>")
                return
        else:
            try:
                err = res.json().get("error", "Login failed")
            except Exception:
                err = "Login failed"
            self.msg.setText(f"<font color='red'>{err}</font>")

    def open_dashboard(self):
        self.hide()
        self.dashboard = DashboardWindow()
        self.dashboard.show()


class DashboardWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CloudFileStorage - Dashboard")
        self.resize(900, 600)

        v = QtWidgets.QVBoxLayout(self)
        toolbar = QtWidgets.QHBoxLayout()

        self.upload_btn = QtWidgets.QPushButton("Upload File")
        self.upload_btn.clicked.connect(self.upload_file)
        self.refresh_btn = QtWidgets.QPushButton("Refresh List")
        self.refresh_btn.clicked.connect(self.load_files)
        self.logout_btn = QtWidgets.QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)

        toolbar.addWidget(self.upload_btn)
        toolbar.addWidget(self.refresh_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.logout_btn)
        v.addLayout(toolbar)

        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Filename", "Size (KB)", "Uploaded At", "S3 Key"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        v.addWidget(self.table)

        action_layout = QtWidgets.QHBoxLayout()
        self.download_btn = QtWidgets.QPushButton("Download Selected")
        self.download_btn.clicked.connect(self.download_selected)
        self.delete_btn = QtWidgets.QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected)
        action_layout.addWidget(self.download_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addStretch()
        v.addLayout(action_layout)

        QtCore.QTimer.singleShot(100, self.load_files)

    def ensure_logged(self):
        if not load_token():
            QtWidgets.QMessageBox.warning(self, "Authentication", "Please login first.")
            return False
        return True

    def upload_file(self):
        if not self.ensure_logged():
            return
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose file to upload")
        if not path:
            return
        try:
            with open(path, "rb") as f:
                r = requests.post(f"{BASE_URL}/files/upload", headers=auth_headers(), files={"file": f})
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Network error: {e}")
            return
        if r.ok:
            QtWidgets.QMessageBox.information(self, "Upload", r.json().get("message", "Uploaded"))
            self.load_files()
        else:
            try:
                err = r.json().get("error", "Upload failed")
            except Exception:
                err = "Upload failed"
            QtWidgets.QMessageBox.critical(self, "Upload failed", err)

    def load_files(self):
        if not self.ensure_logged():
            return
        try:
            r = requests.get(f"{BASE_URL}/files/list", headers=auth_headers())
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Network error: {e}")
            return
        if not r.ok:
            try:
                err = r.json().get("error", "Failed to fetch")
            except Exception:
                err = "Failed"
            QtWidgets.QMessageBox.critical(self, "Error", err)
            return
        files = r.json().get("files", [])
        self.table.setRowCount(0)
        for f in files:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(f.get("filename", "")))
            size_kb = round((f.get("size") or 0) / 1024, 2)
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(size_kb)))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(f.get("uploaded_at", "")))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(f.get("s3_key", "")))

    def get_selected_row(self):
        r = self.table.currentRow()
        if r < 0:
            QtWidgets.QMessageBox.warning(self, "No selection", "Please select a file first.")
            return None
        return r

    def download_selected(self):
        if not self.ensure_logged():
            return
        r = self.get_selected_row()
        if r is None:
            return
        s3_key = self.table.item(r, 3).text()
        if not s3_key:
            QtWidgets.QMessageBox.warning(self, "Error", "S3 key missing for this file.")
            return
        out_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save As", os.path.basename(s3_key))
        if not out_path:
            return
        try:
            r = requests.get(f"{BASE_URL}/files/download", headers=auth_headers(), params={"s3_key": s3_key})
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Network error: {e}")
            return
        if not r.ok:
            try:
                err = r.json().get("error", "Failed to get presigned url")
            except Exception:
                err = "Failed"
            QtWidgets.QMessageBox.critical(self, "Error", err)
            return
        presigned = r.json().get("presigned_url")
        if not presigned:
            QtWidgets.QMessageBox.critical(self, "Error", "No presigned URL returned.")
            return
        try:
            r2 = requests.get(presigned, stream=True)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Network error: {e}")
            return
        if r2.ok:
            try:
                with open(out_path, "wb") as fd:
                    for chunk in r2.iter_content(8192):
                        if chunk:
                            fd.write(chunk)
                QtWidgets.QMessageBox.information(self, "Download", "File saved successfully.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Could not save file: {e}")
        else:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to download from S3: {r2.status_code}")

    def delete_selected(self):
        if not self.ensure_logged():
            return
        r = self.get_selected_row()
        if r is None:
            return
        s3_key = self.table.item(r, 3).text()
        if not s3_key:
            QtWidgets.QMessageBox.warning(self, "Error", "S3 key missing for this file.")
            return
        confirm = QtWidgets.QMessageBox.question(self, "Confirm", f"Delete {s3_key}?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirm != QtWidgets.QMessageBox.Yes:
            return
        try:
            res = requests.delete(f"{BASE_URL}/files/delete", headers=auth_headers(), params={"s3_key": s3_key})
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Network error: {e}")
            return
        if res.ok:
            QtWidgets.QMessageBox.information(self, "Delete", res.json().get("message", "Deleted"))
            self.load_files()
        else:
            try:
                err = res.json().get("error", "Failed to delete")
            except Exception:
                err = "Failed to delete"
            QtWidgets.QMessageBox.critical(self, "Error", err)

    def logout(self):
        clear_token()
        QtWidgets.QMessageBox.information(self, "Logout", "You have been logged out.")
        self.close()
        self.login = LoginWindow()
        self.login.show()


def main():
    app = QtWidgets.QApplication(sys.argv)
    if load_token():
        w = DashboardWindow()
        w.show()
    else:
        w = LoginWindow()
        w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
