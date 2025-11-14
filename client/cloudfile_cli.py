#!/usr/bin/env python3
"""
client/cloudfile_cli.py
Clean S3-backed CLI for CloudFileStorage.
Interactive menu + argparse support.
"""

import argparse
import os
import sys
import requests
import getpass
import json

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
            data = json.load(f)
            return data.get("token")
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


# ---------------- API calls ----------------
def api_login(email: str, password: str) -> bool:
    try:
        r = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    except Exception as e:
        print("Network error:", e)
        return False
    if not r.ok:
        try:
            print("Login failed:", r.json())
        except Exception:
            print("Login failed:", r.status_code, r.text)
        return False

    data = r.json()
    token = data.get("token")
    if not token:
        print("Login succeeded but no token returned.")
        return False
    save_token(token)
    print("✅ Logged in successfully.")
    return True


def api_upload(filepath: str):
    if not os.path.exists(filepath):
        print("❌ File not found:", filepath)
        return
    headers = auth_headers()
    if not headers:
        print("❌ Not logged in. Use login first.")
        return
    try:
        with open(filepath, "rb") as f:
            files = {"file": (os.path.basename(filepath), f)}
            r = requests.post(f"{BASE_URL}/files/upload", headers=headers, files=files)
    except Exception as e:
        print("Network error:", e)
        return

    if r.ok:
        data = r.json()
        print("✅ Upload successful:", data.get("message"))
        print("S3 Key:", data.get("s3_key"))
        print("Size (bytes):", data.get("file_size"))
    else:
        try:
            print("❌ Upload failed:", r.json())
        except Exception:
            print("❌ Upload failed:", r.status_code, r.text)


def api_list():
    headers = auth_headers()
    if not headers:
        print("❌ Not logged in.")
        return
    try:
        r = requests.get(f"{BASE_URL}/files/list", headers=headers)
    except Exception as e:
        print("Network error:", e)
        return
    if not r.ok:
        try:
            print("❌ List failed:", r.json())
        except Exception:
            print("❌ List failed:", r.status_code, r.text)
        return
    files = r.json().get("files", [])
    if not files:
        print("No files uploaded yet.")
        return
    print("📁 Files in your account:")
    for i, f in enumerate(files, 1):
        fname = f.get("filename")
        s3 = f.get("s3_key")
        size = f.get("size")
        uploaded = f.get("uploaded_at")
        size_text = f"{size} bytes" if size is not None else "Unknown size"
        print(f" {i}. {fname} | Size: {size_text} | Uploaded: {uploaded} | S3 Key: {s3}")


def api_get_presigned_and_download(s3_key: str, out_path: str | None = None):
    headers = auth_headers()
    if not headers:
        print("❌ Not logged in.")
        return
    try:
        r = requests.get(f"{BASE_URL}/files/download", headers=headers, params={"s3_key": s3_key})
    except Exception as e:
        print("Network error:", e)
        return
    if not r.ok:
        try:
            print("❌ Failed to get presigned URL:", r.json())
        except Exception:
            print("❌ Failed:", r.status_code, r.text)
        return
    presigned = r.json().get("presigned_url")
    if not presigned:
        print("❌ No presigned URL returned.")
        return
    # download from presigned URL
    try:
        r2 = requests.get(presigned, stream=True)
    except Exception as e:
        print("Network error while downloading:", e)
        return
    if not r2.ok:
        print("❌ Failed to download from S3:", r2.status_code)
        return
    out = out_path or os.path.basename(s3_key)
    with open(out, "wb") as fd:
        for chunk in r2.iter_content(8192):
            if chunk:
                fd.write(chunk)
    print("⬇️ Downloaded to", out)


def api_delete(s3_key: str):
    headers = auth_headers()
    if not headers:
        print("❌ Not logged in.")
        return
    try:
        r = requests.delete(f"{BASE_URL}/files/delete", headers=headers, params={"s3_key": s3_key})
    except Exception as e:
        print("Network error:", e)
        return
    if r.ok:
        print("🗑️ Deleted:", r.json().get("message"))
    else:
        try:
            print("❌ Delete failed:", r.json())
        except Exception:
            print("❌ Delete failed:", r.status_code, r.text)


# ---------------- Interactive Menu ----------------
def interactive_menu():
    print("🔐 Welcome to SecureCloud CLI")
    email = input("Enter email: ").strip()
    password = getpass.getpass("Enter password: ")
    if not api_login(email, password):
        print("Exiting.")
        return

    while True:
        print("\nChoose an action:")
        print("1. Upload a file")
        print("2. List files")
        print("3. Download a file")
        print("4. Delete a file")
        print("5. Logout & Exit")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            path = input("Enter full path of file to upload: ").strip()
            api_upload(path)
        elif choice == "2":
            api_list()
        elif choice == "3":
            s3_key = input("Enter S3 key of file to download (e.g. user_1/file.txt): ").strip()
            out = input("Save as (leave blank to use same filename): ").strip() or None
            api_get_presigned_and_download(s3_key, out)
        elif choice == "4":
            s3_key = input("Enter S3 key of file to delete: ").strip()
            confirm = input(f"Delete {s3_key}? (y/N): ").strip().lower()
            if confirm == "y":
                api_delete(s3_key)
        elif choice == "5":
            clear_token()
            print("✅ Logged out and exiting.")
            break
        else:
            print("Invalid option. Try again.")


# ---------------- CLI argument entrypoint ----------------
def main():
    parser = argparse.ArgumentParser(description="CloudFileStorage CLI (S3)")
    sub = parser.add_subparsers(dest="cmd")

    p_login = sub.add_parser("login")
    p_login.add_argument("--email", required=True)
    p_login.add_argument("--password", required=True)

    sub.add_parser("logout")

    p_upload = sub.add_parser("upload")
    p_upload.add_argument("--file", required=True)

    sub.add_parser("list")

    p_download = sub.add_parser("download")
    p_download.add_argument("--s3_key", required=True)
    p_download.add_argument("--out", required=False)

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("--s3_key", required=True)

    args = parser.parse_args()

    if args.cmd is None:
        interactive_menu()
        return

    if args.cmd == "login":
        api_login(args.email, args.password)
    elif args.cmd == "logout":
        clear_token()
        print("Logged out.")
    elif args.cmd == "upload":
        api_upload(args.file)
    elif args.cmd == "list":
        api_list()
    elif args.cmd == "download":
        api_get_presigned_and_download(args.s3_key, args.out)
    elif args.cmd == "delete":
        api_delete(args.s3_key)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
