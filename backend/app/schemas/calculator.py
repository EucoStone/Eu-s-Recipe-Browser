from pydantic import BaseModel, Field


class InventoryItem(BaseModel):
    item_id: str
    amount: float = 0


class CalculateRequest(BaseModel):
    target_item: str = Field(min_length=1)
    amount: float = Field(default=1, gt=0)
    recipe_id: str | None = None
    inventory: list[InventoryItem] = Field(default_factory=list)


class TreeNode(BaseModel):
    item_id: str
    item_label: str | None = None
    amount: float
    recipe_id: str | None = None
    craft_count: float = 0
    children: list["TreeNode"] = Field(default_factory=list)
    is_base: bool = False


class MaterialItem(BaseModel):
    item_id: str
    item_label: str | None = None
    amount_needed: float
    amount_available: float = 0
    amount_shortage: float = 0


class CalculateResponse(BaseModel):
    target_item: str
    target_label: str | None = None
    amount: float
    tree: TreeNode
    materials: list[MaterialItem]
    unresolved_cycles: list[str] = Field(default_factory=list)


TreeNode.model_rebuild()
