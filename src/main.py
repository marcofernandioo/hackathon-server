from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import json

# Generate RSA key pair (This would normally be done separately and keys stored securely)
def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Serialize keys for storage or sharing
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem

# Encrypt data using public key
def encrypt_data(public_key_pem, data):
    public_key = serialization.load_pem_public_key(
        public_key_pem,
        backend=default_backend()
    )

    encrypted = public_key.encrypt(
        data.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted

# Decrypt data using private key
def decrypt_data(private_key_pem, encrypted_data):
    private_key = serialization.load_pem_private_key(
        private_key_pem,  # Load the private key
        password=None,    # Assuming the private key is not encrypted with a password
        backend=default_backend()
    )

    decrypted = private_key.decrypt(
        encrypted_data,   # The encrypted data to be decrypted
        padding.OAEP(     # The padding scheme used during encryption
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted.decode('utf-8')  # Convert the decrypted bytes back to a string

# Example patient data to be encrypted
patient_data = {
    "name": "John Doe",
    "dob": "1990-01-01",
    "condition": "Hypertension",
    "medications": ["Lisinopril", "Amlodipine"],
    "doctor": "Dr. Smith"
}

# Step 1: Generate RSA Keys (Private and Public)
print("Generating RSA keys...")
private_key_pem, public_key_pem = generate_keys()

# Print complete keys
print("\nPrivate Key:\n", private_key_pem.decode('utf-8'))
print("\nPublic Key:\n", public_key_pem.decode('utf-8'))

# Step 2: Encrypt the patient data using the public key
print("\nEncrypting patient data...")
try:
    encrypted_data = encrypt_data(public_key_pem, json.dumps(patient_data))
    print("\nEncrypted Data (hex):", encrypted_data.hex(), "\n")  # Show the full hex data
except Exception as e:
    print("Encryption failed:", str(e))

# Step 3: Decrypt the data using the private key to retrieve the original data
print("Decrypting data...")
try:
    decrypted_data = decrypt_data(private_key_pem, encrypted_data)
    print("\nDecrypted Data (formatted):")
    decrypted_json = json.loads(decrypted_data)
    for key, value in decrypted_json.items():
        print(f'"{key}": {json.dumps(value)}')
except Exception as e:
    print("Decryption failed:", str(e))
