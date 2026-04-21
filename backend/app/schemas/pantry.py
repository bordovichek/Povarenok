from pydantic import BaseModel, Field


class PantryItemIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(default="", max_length=80)
    quantity: float = Field(default=0, ge=0)
    unit: str = Field(default="", max_length=30)


class PantryItemOut(BaseModel):
    id: int
    name: str
    category: str
    quantity: float
    unit: str
