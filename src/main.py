from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware  # to handle Cross-Origin Resource Sharing (CORS)
import uvicorn                                      # ASGI server to run FastAPI application
import httpx
import json
import os
from dotenv import load_dotenv
from src.util import generate_rsa_keys, encrypt_with_public_key, decrypt_with_private_key, hash_password, encrypt_private_key, decrypt_private_key
from src.stat_data import stat

### Global Variable ---------------------------------------------------------------------
load_dotenv()                                   # load environment variables from: .env
CLIENT_ID = os.environ.get("CLIENT_ID")         # Retrieve dri env
CLIENT_SECRET = os.environ.get("CLIENT_SECRET") # Retrieve dri env


### 2 FastAPI and CORS initialization -------------------------------------
app = FastAPI()                                     # initializes the FastAPI application

origins = [                                         # list allowed origins to make requests to API
    "http://localhost:5175",                        
    "http://127.0.0.1:5175",                        # INI NANTI GANTI SESUAI PORT JS MASING MASING
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    # allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
print('llm')                                    # to Ping

API_URL = 'https://service-testnet.maschain.com'

wallet_db = [
    {"wallet_address": "0x71c9751A2b199864bd486b72a342373Df1eFb5C9", "password": "owen123"}, ## owen
    {"wallet_address": "0x9975Cb544e12440e45F1ebbe8809221E486a0937", "password": "divaldo123"}, ## divaldo
    {"wallet_address": "0x3f4615Fdf53Bc923d84Fe098D7Aa7735f45aAa63", "password": "marco123"}, ## marco
    {"wallet_address": "0xC95bd91f1744704306c2eeB60d62fE9105d31fAc", "password": "stanley123"}, ## stanley
]
basic_headers = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
}

post_headers = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "content-type": 'application/json'
}

temp_mr = {}
temp_mr_view = {}

### ping -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"data": "llm1!!!!"}

### AUDIT TRAIL ----------------------------------------------------------------------


### Create new Account by Create Audit Trail 
@app.post('/reg')
async def create_acc(
    password_data: dict
):
    url = API_URL + '/api/audit/audit'                         # Create Audit Trail
    
    async with httpx.AsyncClient() as client:
        password_data = {
            "wallet_address": password_data["wallet_address"],      # Req
            "contract_address": password_data["contract_address"],  # Req
            "metadata": {                                           # Req
                "password": password_data["password"],                         #
                "privatekey": "",                                   # Tar di ubah marco
            },
            "callback_url": password_data["callback_url"],          # Req
            "category_id": [9]                                  # Not Req, 8=mr 9= acc, dtype: array
        }
        response = await client.post(url, headers=basic_headers, json=password_data)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to log password update")
        
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response", "content": response.text}

# Called by the MS to create the MR.
@app.post("/mr/store")
async def store_endpoint(request: dict):
    global temp_mr
    temp_mr = json.dumps(request);
    return {"message": "Request body stored successfully"}

# Get one MR, for Patient to access.
@app.get('/mr/one')
async def mr_global():
    global temp_mr
    return temp_mr

### marco: Create Medical Record by Create Audit Trail 
@app.post('/mr/create')
async def create_mr(request_data: dict):
    # Generate RSA keys
    # private_key_pem, public_key_pem = generate_rsa_keys()

    # # Encrypt data with public key
    # encrypted_data = encrypt_with_public_key(public_key_pem, json.dumps(request_data))

    url = API_URL + '/api/audit/audit'
    global temp_mr
    
    
    async with httpx.AsyncClient() as client:
        request_data = {
            "metadata": temp_mr,
            "contract_address": "0x922f65BB86BE4a2153e900153204fD6eBA725638",
            "wallet_address": "0x7687C7Fda5357d86DfEe7ea4bdc373D128aabFE2",
            "callback_url": "https://postman-echo.com/post?"
        }
        
        # return request_data
               
        response = await client.post(url, headers=post_headers, json=request_data)
        
        if response.status_code != 200:                 # Check status code
            raise HTTPException(status_code=response.status_code, detail="External API request failed")
       
        if not response.content:                        # Check if content is empty
            return {"message": "External API returned an empty response"}
       
        
        try:                                            # Try to parse JSON
            temp_mr = {}
            return response.json()
        except json.JSONDecodeError:                    # If JSON parsing fails, return the raw text content
            return {"error": "Failed to parse JSON", "content": response.text}


### Wallet Management ----------------------------------------------------------------------

### Create new User Wallet by Create User Wallet 
@app.post('/wallet/create')
async def create_wallet_user(
    wallet_data: dict
):
    url = API_URL + '/api/wallet/create-user'  # Endpoint to create a wallet user
    
    async with httpx.AsyncClient() as client:
        payload = {
            "name": wallet_data["name"],  # Required: User's name
            "email": wallet_data["email"],  # Required: User's email
            "ic": wallet_data["ic"]  # Required: User's identification code
        }
        response = await client.post(url, headers=basic_headers, data=payload)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to create wallet user")
        
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response", "content": response.text}


### Create new organization wallet by Create Organisation Wallet 
@app.post('/wallet/wallet')
async def create_wallet_org(
    wallet_data: dict
):
    url = API_URL + '/api/wallet/wallet'  # Endpoint to create a wallet user
    
    async with httpx.AsyncClient() as client:
        payload = {
            "name": wallet_data["name"]  # Required: User's name
        }
        response = await client.post(url, headers=basic_headers, data=payload)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to create wallet user")
        
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response", "content": response.text}

### Check wallet to login by Get Wallet by address      ### Maybe not used
@app.get('/wallet/get/{address}')                       #### this to login only by wallet address
async def get_wallet_by_address(address: str):
    url = f"{API_URL}/api/wallet/wallet/{address}"
   
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=basic_headers)
       
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to retrieve wallet")
       
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response", "content": response.text}
 

### 19 ---------------------------------
### Login by Get Wallet by address & Database

 
@app.post('/wallet/login')
async def login(wallet_data: dict):
    wallet_address = wallet_data.get("wallet_address")
    input_password = wallet_data.get("password")
 
    # Step 1: Check if the wallet address is registered on the blockchain
    url = f"{API_URL}/api/wallet/wallet/{wallet_address}" # call: Get Wallet by address (endpoint)
   
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=basic_headers)
       
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to retrieve wallet from blockchain")
        
        wallet_info = response.json()
   
    # if wallet address is found
    # Step 2: Check if the wallet address and password match any of the wallet database
    for data in wallet_db:
        if data["wallet_address"] == wallet_address and data["password"] == input_password:
            return {"message": wallet_info}
 
    return {"message": "Invalid wallet address or password"}
 
 
@app.get('/statistics')
def get_stat():
    return stat

def store_request_body(body: dict, file_path: str = "request_body.txt"):
    with open(file_path, "w") as file:
        json.dump(body, file)

def clear_request_body(file_path: str = "request_body.txt"):
    with open(file_path, "w") as file:
        file.write("")

# This is the actual create MR stored onchain.
@app.delete("/delete")
async def delete_endpoint():
    global temp_mr
    temp_mr = {}
    return {"message": "Request body cleared successfully"}


### 5 Run the Server ------------------------------------------------------------------------------
if __name__ == "__main__":
    # uvicorn.run(app, host='localhost', port=8001)
    print("running")
