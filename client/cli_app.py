# client/cli_app.py
import argparse
import os
import requests
from utils import BASE_URL, save_token, load_token, clear_token, get_auth_headers

def login(email, password):
    res = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if res.ok:
        data = res.json()
        token = data.get("token")
        save_token(token)
        print("✅ Login successful")
    else:
        print("❌ Login failed:", res.json())

def logout():
    clear_token()
    print("✅ Logged out (token cleared)")

def upload(path):
    token = load_token()
    if not token:
        print("❌ Not logged in. Run: cli_app.py login --email ... --password ...")
        return
    if not os.path.exists(path):
        print("❌ File does not exist:", path)
        return
    with open(path, "rb") as f:
        res = requests.post(f"{BASE_URL}/files/upload", files={"file": f}, headers=get_auth_headers())
    print(res.status_code, res.json())

def list_files():
    res = requests.get(f"{BASE_URL}/files/list", headers=get_auth_headers())
    if res.ok:
        data = res.json()
        files = data.get("files", [])
        if not files:
            print("No files uploaded yet.")
            return
        print(f"{'Filename':40} {'Size (KB)':>10} {'Uploaded At'}")
        print("-" * 80)
        for f in files:
            size_kb = f.get("size", 0) / 1024
            print(f"{f.get('filename', ''):40} {size_kb:10.2f} {f.get('uploaded_at', '')}")
    else:
        print("❌", res.status_code, res.json())

def download(filename, out=None):
    if not filename:
        print("❌ Provide filename to download")
        return
    out_name = out or filename
    res = requests.get(f"{BASE_URL}/files/download/{filename}", headers=get_auth_headers(), stream=True)
    if res.ok:
        with open(out_name, "wb") as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)
        print("⬇️ Downloaded:", out_name)
    else:
        try:
            print("❌", res.status_code, res.json())
        except Exception:
            print("❌", res.status_code, res.text)

def delete(filename):
    if not filename:
        print("❌ Provide filename to delete")
        return
    res = requests.delete(f"{BASE_URL}/files/delete/{filename}", headers=get_auth_headers())
    print(res.status_code, res.json())

def main():
    parser = argparse.ArgumentParser(prog="cloudfile-cli", description="CloudFileStorage CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_login = sub.add_parser("login")
    p_login.add_argument("--email", required=True)
    p_login.add_argument("--password", required=True)

    p_logout = sub.add_parser("logout")

    p_upload = sub.add_parser("upload")
    p_upload.add_argument("--file", required=True)

    p_list = sub.add_parser("list")

    p_download = sub.add_parser("download")
    p_download.add_argument("--name", required=True)
    p_download.add_argument("--out", required=False)

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("--name", required=True)

    args = parser.parse_args()

    if args.cmd == "login":
        login(args.email, args.password)
    elif args.cmd == "logout":
        logout()
    elif args.cmd == "upload":
        upload(args.file)
    elif args.cmd == "list":
        list_files()
    elif args.cmd == "download":
        download(args.name, args.out)
    elif args.cmd == "delete":
        delete(args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
