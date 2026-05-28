from pydantic import BaseModel, Field


class IngredientItem(BaseModel):
    item: str | None = None
    tag: str | None = None
    count: float = 1
    raw: object = Field(default_factory=dict)


class RecipeItem(BaseModel):
    recipe_id: str
    type: str = "unknown"
    outputs: list[str] = Field(default_factory=list)
    output_count: float = 1
    ingredients: list[IngredientItem] = Field(default_factory=list)
    raw: dict = Field(default_factory=dict)
    source_file: str | None = None


class RecipeSearchItem(BaseModel):
    recipe_id: str
    type: str
    outputs: list[str]
    output_labels: list[str] = Field(default_factory=list)
    output_count: float
    source_file: str | None = None
