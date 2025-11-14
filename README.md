CloudFileStorage

Secure Cloud-Based File Storage System with Flask API, CLI, and GUI (PyQt5)
Store, manage, and access your files in the cloud using AWS S3, a REST API, an interactive CLI, and a full GUI desktop app.

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

Running the Project :
1.Install dependencies:
  pip install -r requirements.txt
2.Start the Flask Backend :
  python app.py

Using the CLI App :
python cloudfile_cli.py

GUI Application (PyQt5) :
python pyqt_gui.py
