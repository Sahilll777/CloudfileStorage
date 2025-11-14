CloudFileStorage
Secure Cloud-Based File Storage System with Flask API, CLI, and GUI (PyQt5)
Store, manage, and access your files in the cloud using AWS S3, a REST API, an interactive CLI, and a full GUI desktop app.

Features:
✔ User Authentication (JWT) – Secure login system
✔ File Upload to AWS S3
✔ File Download via Presigned URLs
✔ File Delete from S3
✔ Full CLI Application
✔ PyQt5 GUI File Manager
✔ MySQL Database Integration
✔ Secure environment-variable-based secret storage
✔ Fully modular project structure

Tech Stack:
| Component        | Technology                |
| ---------------- | ------------------------- |
| Backend API      | Flask, Flask-JWT-Extended |
| Cloud Storage    | AWS S3                    |
| Database         | MySQL                     |
| CLI App          | Python (Requests)         |
| GUI App          | PyQt5                     |
| Auth             | JWT                       |
| Secrets Handling | Environment Variables     |

Project Structure:
CloudFileStorage/
│── app.py                 # Flask backend API
│── config.py              # Config (uses environment variables)
│── cloudfile_cli.py       # Full CLI application
│── pyqt_gui.py            # PyQt GUI application
│── utils/
│     ├── s3_helper.py     # AWS S3 upload/download/delete helpers
│── routes/
│     ├── auth.py          # JWT login/signup routes
│     ├── files.py         # S3 upload/list/download/delete routes
│── database/
│     └── database.py      # MySQL file records manager
│── uploads/ (optional)    # Local fallback storage
│── venv/                  # Virtual environment
│── README.md              # Documentation

Running the Project :
1.Install dependencies:
  pip install -r requirements.txt
2.Start the Flask Backend :
  python app.py

Using the CLI App :
python cloudfile_cli.py

GUI Application (PyQt5) :
python pyqt_gui.py
