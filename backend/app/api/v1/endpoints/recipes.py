from fastapi import APIRouter, Query

from app.services.recipe_service import search_recipes

router = APIRouter()


@router.get("/recipes/search")
async def search(query: str = Query(..., min_length=1), limit: int = 20) -> dict:
    items = await search_recipes(query=query, limit=limit)
    return {"items": [item.model_dump() for item in items]}
