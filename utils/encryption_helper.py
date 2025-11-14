from Crypto.Cipher import AES
import io
import os

# 32-byte AES key (use .env in production)
SECRET_KEY = os.getenv("ENCRYPTION_KEY", "my_super_secret_key_32b").encode()
if len(SECRET_KEY) not in [16, 24, 32]:
    SECRET_KEY = SECRET_KEY.ljust(32, b'0')[:32]

def encrypt_file(file_obj):
    """
    Encrypt file and return a BytesIO stream.
    Reads all bytes safely without closing original file.
    """
    # Make a copy of the file bytes
    file_bytes = file_obj.read()
    
    cipher = AES.new(SECRET_KEY, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(file_bytes)
    encrypted_data = cipher.nonce + tag + ciphertext
    
    # Return a new BytesIO stream
    return io.BytesIO(encrypted_data)

def decrypt_file(encrypted_bytes):
    """
    Decrypt bytes and return plaintext.
    """
    nonce = encrypted_bytes[:16]
    tag = encrypted_bytes[16:32]
    ciphertext = encrypted_bytes[32:]
    
    cipher = AES.new(SECRET_KEY, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
