import httpx
import asyncio
from fastapi import APIRouter

IMAGINARY_API_X = "https://jsonplaceholder.typicode.com/posts/1"
IMAGINARY_API_Y = "https://jsonplaceholder.typicode.com/comments/1"

router = APIRouter()


async def retrieve_data(client: httpx.AsyncClient, url: str):
    res = await client.get(url)
    res.raise_for_status()
    return res.json()


@router.get("/combine-data", tags=["Part 6"])
async def combine_data():
    async with httpx.AsyncClient() as client:
        res_x, res_y = await asyncio.gather(
            retrieve_data(client, IMAGINARY_API_X),
            retrieve_data(client, IMAGINARY_API_Y)
        )
    return {"X_RESULTS": res_x, "Y_RESULTS": res_y}
