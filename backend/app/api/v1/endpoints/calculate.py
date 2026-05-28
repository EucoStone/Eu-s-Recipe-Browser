from fastapi import APIRouter, HTTPException

from app.schemas.calculator import CalculateRequest, CalculateResponse
from app.services.calculator import calculate_item

router = APIRouter()


@router.post("/calculate", response_model=CalculateResponse)
async def calculate(payload: CalculateRequest) -> CalculateResponse:
    if not payload.target_item.strip():
        raise HTTPException(status_code=400, detail="target_item is required.")

    inventory = {entry.item_id: float(entry.amount) for entry in payload.inventory}
    result = await calculate_item(
        item_id=payload.target_item.strip(),
        amount=float(payload.amount),
        inventory=inventory,
        recipe_id=payload.recipe_id,
    )
    return CalculateResponse(
        target_item=payload.target_item,
        target_label=result["target_label"],
        amount=payload.amount,
        tree=result["tree"],
        materials=result["materials"],
        unresolved_cycles=result["unresolved_cycles"],
    )
