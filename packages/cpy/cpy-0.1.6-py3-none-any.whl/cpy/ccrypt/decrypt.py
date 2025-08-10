from getpass import getpass
import os
import json
from base64 import b64decode
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class DecryptionError(Exception):
    pass


def decrypt_data(payload: dict, password: str) -> bytes:
    salt = b64decode(payload['salt'])
    iv = b64decode(payload['iv'])
    ciphertext = b64decode(payload['ciphertext'])

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    key = kdf.derive(password.encode())
    aesgcm = AESGCM(key)

    return aesgcm.decrypt(iv, ciphertext, None)


def decrypt_file(enc_path, password, out_dir):
    with open(enc_path, 'r') as f:
        payload = json.load(f)

    salt = b64decode(payload['salt'])
    iv_data = b64decode(payload['iv_data'])
    iv_name = b64decode(payload['iv_name'])
    ciphertext = b64decode(payload['ciphertext'])
    filename_enc = b64decode(payload['filename_enc'])

    # Derive the same key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    key = kdf.derive(password.encode())
    aesgcm = AESGCM(key)

    # Decrypt filename and file data
    try:
        filename = aesgcm.decrypt(iv_name, filename_enc, None).decode()
        file_data = aesgcm.decrypt(iv_data, ciphertext, None)
    except:
        raise DecryptionError(
            "Failed to decrypt the file. Check your password and the file format.")

    output_path = out_dir
    if os.path.isdir(out_dir):
        output_path = os.path.join(out_dir, filename)

    with open(output_path, 'wb') as f:
        f.write(file_data)

    print(f"Decrypted to {output_path}")


def decrypt_fs(enc_path, password, out_dir):
    if not os.path.isdir(enc_path):
        decrypt_file(enc_path, password, out_dir)
        return

    for root, _, files in os.walk(enc_path):
        for file in files:
            full_path = os.path.join(root, file)
            out_file_path = os.path.join(
                out_dir, os.path.relpath(full_path, enc_path)
            )
            out_file_path = os.path.dirname(out_file_path)

            os.makedirs(out_file_path, exist_ok=True)
            decrypt_file(full_path, password, out_file_path)


def add_arguments(parser):
    parser.add_argument('input', help='Input file/directory path')
    parser.add_argument('output', help='Output file/directory path')


def main(args):
    file_path = os.path.abspath(args.input)
    out_path = os.path.abspath(args.output)
    password = getpass("Enter the password: ")

    try:
        decrypt_fs(file_path, password, out_path)
    except DecryptionError as e:
        print(e)
        exit(1)


def _direct():
    file_path = os.path.abspath(input("Enter the ecrypted file path: "))
    password = getpass("Enter the password: ")
    out_path = os.path.abspath(input("Enter the output file/folder path: "))

    try:
        decrypt_fs(file_path, password, out_path)
    except DecryptionError as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    _direct()
