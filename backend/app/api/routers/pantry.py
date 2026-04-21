from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.pantry import PantryItem
from app.models.user import User
from app.schemas.pantry import PantryItemIn, PantryItemOut

router = APIRouter(prefix="/pantry", tags=["pantry"])


@router.get("/", response_model=list[PantryItemOut])
def list_pantry(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(PantryItem).filter(PantryItem.user_id == user.id).order_by(PantryItem.name.asc()).all()
    return [
        PantryItemOut(
            id=i.id,
            name=i.name,
            category=i.category,
            quantity=float(i.quantity),
            unit=i.unit,
        )
        for i in items
    ]


@router.post("/", response_model=PantryItemOut, status_code=201)
def create_item(data: PantryItemIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = PantryItem(
        user_id=user.id,
        name=data.name.strip().lower(),
        category=data.category.strip(),
        quantity=data.quantity,
        unit=data.unit.strip(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return PantryItemOut(id=item.id, name=item.name, category=item.category, quantity=float(item.quantity), unit=item.unit)


@router.put("/{item_id}", response_model=PantryItemOut)
def update_item(item_id: int, data: PantryItemIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(PantryItem, item_id)
    if not item or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    item.name = data.name.strip().lower()
    item.category = data.category.strip()
    item.quantity = data.quantity
    item.unit = data.unit.strip()
    db.add(item)
    db.commit()
    db.refresh(item)
    return PantryItemOut(id=item.id, name=item.name, category=item.category, quantity=float(item.quantity), unit=item.unit)


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(PantryItem, item_id)
    if not item or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return None
