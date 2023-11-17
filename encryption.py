import gzip
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from argparse import ArgumentParser
from enum import Enum
import binascii


class Keys(Enum):
    Datatable = ""  # Add datatable key here
    Fumen = ""  # Add Fumen key here


def read_iv_from_file(file_path):
    with open(file_path, "rb") as f:
        iv = f.read(16)
        if len(iv) != 16:
            raise Exception("Invalid file")
    return iv


def pad_data(data):
    padder = padding.PKCS7(128).padder()
    return padder.update(data) + padder.finalize()


def remove_pkcs7_padding(data):
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(data) + unpadder.finalize()


def decrypt_file(input_file, key_type: Keys = Keys(Keys.Datatable)):
    # Convert the key from hex to bytes
    key = binascii.unhexlify(Keys(key_type.value).value)

    # Read the IV from the first 16 bytes of the input file
    iv = read_iv_from_file(input_file)

    # Create an AES cipher object with CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    with open(input_file, "rb") as infile:
        # Skip the IV in the input file
        infile.seek(16)

        # Decrypt the file
        decrypted_data = b"" + decryptor.update(infile.read())

        # Remove PKCS7 padding
        unpadded_data = remove_pkcs7_padding(decrypted_data)

        # Gzip decompress the data
        decompressed_data = gzip.decompress(unpadded_data)

        # return the decompressed data
        return decompressed_data.decode()


def encrypt_file(input_file, key_type: Keys = Keys(Keys.Datatable)):
    # Convert the key from hex to bytes
    key = binascii.unhexlify(Keys(key_type.value).value)

    # Generate a random 128-bit IV
    iv = os.urandom(16)

    # Create an AES cipher object with CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(input_file, "rb") as infile:
        # Read the entire file into memory
        data = infile.read()

        # Gzip compress the data
        compressed_data = gzip.compress(data)

        # Pad the compressed data, encrypt it, and return the encrypted result
        encrypted_data = (
            encryptor.update(pad_data(compressed_data)) + encryptor.finalize()
        )

    return iv + encrypted_data


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        help="Input file",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file",
    )
    parser.add_argument(
        "-e",
        "--enc",
        action="store_true",
        default=False,
        help="Use this flag to encrypt a file",
    )
    parser.add_argument(
        "-t",
        "--type",
        default="Datatable",
        help="Datatable is default, you can also use Fumen",
    )
    args = parser.parse_args()

    if not args.input:
        print("Missing input file, pass the argument --help for help")
        exit(0)

    if not args.output:
        print("Missing output file, pass the argument --help for help")
        exit(0)

    type = Keys.Datatable if args.type == "Datatable" else Keys.Fumen

    if not args.enc:
        print("Encrypting " + args.input + " to " + args.output)
        file = decrypt_file(input_file=args.input, key_type=type)
        with open(args.output, "w") as outfile:
            outfile.write(file)
    else:
        print("Decrypting " + args.input + " to " + args.output)
        file = encrypt_file(input_file=args.input, key_type=type)
        with open(args.output, "wb") as outfile:
            outfile.write(file)
