from fastapi import FastAPI, HTTPException, Depends, status, Query
import httpx

app = FastAPI()

print('llm')

API_URL = 'https://service-testnet.maschain.com'

@app.get("/")
def root():
    return {"data": "dllm!"};

@app.get('/get-mr')
async def create_mr():
    endpoint = '/api/audit/audit'
    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL+endpoint)
        return response.json()
    
    # if response.status_code == 200:
    #     return response.json()
    # else:
    #     return {"error": "Failed to fetch data from external API"}
