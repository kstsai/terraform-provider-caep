# !/usr/bin/env python
# -*-coding: utf-8 -*-

import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def ssh_key_generate(dst_path, file_name):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    public_key = private_key.public_key()
    private_key_file = os.path.join(dst_path, file_name)
    with open(private_key_file, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    public_key_file = os.path.join(dst_path, file_name + '.pub')
    with open(public_key_file, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        ))
