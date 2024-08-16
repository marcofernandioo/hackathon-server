from fastapi import FastAPI, HTTPException
import httpx
import json

app = FastAPI()

print('llm')

API_URL = 'https://service-testnet.maschain.com'
basic_headers = {
        "client_id": '13aab0e5a2d89c1e68d8e9f581f54bd255e0eea3e7e027c43b5b3faf34e40b82',
        "client_secret": 'sk_4c7fe1e868e87458867f2edcd3461266392ff960c3d9dde5639a563edb2f0c84'
}

post_headers = {
    "client_id": '13aab0e5a2d89c1e68d8e9f581f54bd255e0eea3e7e027c43b5b3faf34e40b82',
    "client_secret": 'sk_4c7fe1e868e87458867f2edcd3461266392ff960c3d9dde5639a563edb2f0c84',
    "content-type": 'application/json'
}

@app.get("/")
def root():
    return {"data": "llm123!!!"}

@app.get('/mr/all')
async def get_mr():
    url = API_URL+'/api/audit/audit'
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=basic_headers)
        
        # Check status code
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="External API request failed")
        
        # Check if content is empty
        if not response.content:
            return {"message": "External API returned an empty response"}
        
        # Try to parse JSON
        try:
            return response.json()
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw text content
            return {"error": "Failed to parse JSON", "content": response.text}

@app.post('/mr/create')
async def create_mr(request_data: dict):
    url = API_URL + '/api/audit/audit'
    async with httpx.AsyncClient() as client:
        # request_data = {
        #     "metadata": "encrypted-metadata",
        #     "contract_address": "0x922f65BB86BE4a2153e900153204fD6eBA725638",
        #     "wallet_address": "0xF0cBfd7D27902f15A16c8ad2ad1cfe8B155120D7",
        #     "callback_url": "https://postman-echo.com/post?"
        # }
        response = await client.post(url, headers=post_headers, json=request_data)
        
        # Check status code
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="External API request failed")
        
        # Check if content is empty
        if not response.content:
            return {"message": "External API returned an empty response"}
        
        # Try to parse JSON
        try:
            return response.json()
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw text content
            return {"error": "Failed to parse JSON", "content": response.text}