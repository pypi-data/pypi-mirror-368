import argparse

from cpy.ccrypt import encrypt, decrypt

def main():
    parser = argparse.ArgumentParser(prog='ccrypt', description='CCrypt')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Subcommand 'encrypt'
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt file/directory')
    encrypt.add_arguments(encrypt_parser)
    encrypt_parser.set_defaults(func=encrypt.main)

    # Subcommand 'decrypt'
    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt file/directory')
    decrypt.add_arguments(decrypt_parser)
    decrypt_parser.set_defaults(func=decrypt.main)

    args = parser.parse_args()
    args.func(args)
