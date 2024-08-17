from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # to handle Cross-Origin Resource Sharing (CORS)
import uvicorn                                      # ASGI server to run FastAPI application
import httpx
import json
import os
from dotenv import load_dotenv

### Global Variable ---------------------------------------------------------------------
load_dotenv()                                   # load environment variables from: .env
CLIENT_ID = os.environ.get("CLIENT_ID")         # Retrieve dri env
CLIENT_SECRET = os.environ.get("CLIENT_SECRET") # Retrieve dri env


### 2 FastAPI and CORS initialization -------------------------------------
app = FastAPI()                                     # initializes the FastAPI application

origins = [                                         # list allowed origins to make requests to API
    "http://localhost",                        
    "http://127.0.0.1:5173",                        # INI NANTI GANTI SESUAI PORT JS MASING MASING
]

app.add_middleware(                                 # CORS Middleware: handle requestt from specified origins
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print('llm')                                    # to Ping

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

### ping -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"data": "llm1!"}

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

### marco: Create Medical Record by Create Audit Trail 
@app.post('/mr/create')
async def create_mr(request_data: dict):
    url = API_URL + '/api/audit/audit'
    async with httpx.AsyncClient() as client:
        request_data = {
            "metadata": json.dumps(request_data),
            "contract_address": "0x922f65BB86BE4a2153e900153204fD6eBA725638",
            "wallet_address": "0x7687C7Fda5357d86DfEe7ea4bdc373D128aabFE2",
            "callback_url": "https://postman-echo.com/post?"
        }
       
        response = await client.post(url, headers=post_headers, json=request_data)
        
        if response.status_code != 200:                 # Check status code
            raise HTTPException(status_code=response.status_code, detail="External API request failed")
       
        if not response.content:                        # Check if content is empty
            return {"message": "External API returned an empty response"}
       
        
        try:                                            # Try to parse JSON
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

### 5 Run the Server ------------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8001)
