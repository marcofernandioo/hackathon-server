from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx
import json
import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import bcrypt
import base64
import secrets

### Global Variable ---------------------------------------------------------------------
load_dotenv()
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

### FastAPI and CORS initialization -------------------------------------
app = FastAPI()

origins = [
    "http://localhost",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print('llm')                            

API_URL = 'https://service-testnet.maschain.com'

basic_headers = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

post_headers = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "content-type": 'application/json'
}

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

### Ping -------------------------------------------------------------------
@app.get("/")
def root():
    return {"data": "llm1!"}

### Create Medical Record by Create Audit Trail ---------------------------
@app.post('/mr/create')
async def create_mr(request_data: dict):
    # Generate RSA keys
    private_key_pem, public_key_pem = generate_rsa_keys()

    # Encrypt data with public key
    encrypted_data = encrypt_with_public_key(public_key_pem, json.dumps(request_data))

    # Encrypt the private key with AES
    aes_key = secrets.token_bytes(32)
    encrypted_private_key = encrypt_private_key(private_key_pem, aes_key)

    url = API_URL + '/api/audit/audit'
    async with httpx.AsyncClient() as client:
        request_data = {
            "metadata": encrypted_data,
            "contract_address": "0x922f65BB86BE4a2153e900153204fD6eBA725638",
            "wallet_address": "0x7687C7Fda5357d86DfEe7ea4bdc373D128aabFE2",
            "callback_url": "https://postman-echo.com/post?"
        }

        response = await client.post(url, headers=post_headers, json=request_data)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="External API request failed")

        if not response.content:
            return {"message": "External API returned an empty response"}

        try:
            return {
                "encrypted_data": encrypted_data,
                "encrypted_private_key": encrypted_private_key,
                "aes_key": base64.b64encode(aes_key).decode(),
                "response": response.json()
            }
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON", "content": response.text}

### Run the Server ---------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8001)