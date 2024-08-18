from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import bcrypt
import base64
import secrets

### RSA Key Generation ---------------------------------------------------
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    # Private key in PEM format
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Public key in PEM format
    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return pem_private_key, pem_public_key

### Encrypt data with RSA public key -------------------------------------
def encrypt_with_public_key(public_key_pem, data):
    public_key = serialization.load_pem_public_key(public_key_pem)
    encrypted_data = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted_data).decode()

### Decrypt data with RSA private key -------------------------------------
def decrypt_with_private_key(private_key_pem, encrypted_data):
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    decrypted_data = private_key.decrypt(
        base64.b64decode(encrypted_data.encode()),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data.decode()

### Password Hashing with bcrypt ------------------------------------------
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()

### Encrypt private key with AES ------------------------------------------
def encrypt_private_key(private_key_pem, aes_key):
    iv = secrets.token_bytes(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    encrypted_key = encryptor.update(private_key_pem) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_key).decode()

### Decrypt private key with AES ------------------------------------------
def decrypt_private_key(encrypted_private_key, aes_key):
    encrypted_data = base64.b64decode(encrypted_private_key)
    iv = encrypted_data[:16]
    encrypted_key = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    decryptor = cipher.decryptor()
    decrypted_key = decryptor.update(encrypted_key) + decryptor.finalize()
    return decrypted_key
