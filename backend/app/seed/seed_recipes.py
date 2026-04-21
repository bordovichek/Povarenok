from __future__ import annotations

import random
import app.models

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session

from app.models.common import Difficulty, MealType
from app.models.recipe import Ingredient, Recipe, RecipeIngredient
import app.models.cooking
import app.models.user
from app.seed.image_gen import generate_recipe_image


def _img_bytes(title: str) -> tuple[bytes, str]:
    """Generate simple warm placeholder image and return (bytes, mime)."""
    w, h = 640, 420
    img = Image.new("RGB", (w, h), (243, 217, 190))  # warm background
    draw = ImageDraw.Draw(img)

    # abstract shapes
    for _ in range(12):
        r = random.randint(30, 120)
        x = random.randint(-20, w - 1)
        y = random.randint(-20, h - 1)
        color = (
            random.randint(180, 255),
            random.randint(140, 210),
            random.randint(120, 190),
        )
        draw.ellipse((x, y, x + r, y + r), fill=color)

    # text (use default font to avoid font dependencies)
    text = title[:32]
    draw.rectangle((20, h - 90, w - 20, h - 20), fill=(255, 255, 255))
    draw.text((30, h - 80), text, fill=(55, 55, 55))

    out = __import__("io").BytesIO()
    img.save(out, format="WEBP", quality=78, method=6)
    return out.getvalue(), "image/webp"


def _get_or_create_ingredient(db: Session, name: str) -> Ingredient:
    key = name.strip().lower()
    ing = db.query(Ingredient).filter(Ingredient.name == key).first()
    if ing:
        return ing
    ing = Ingredient(name=key)
    db.add(ing)
    db.flush()  # get id
    return ing


def _add_recipe(
    db: Session,
    title: str,
    meal_type: MealType,
    time_minutes: int,
    difficulty: Difficulty,
    kcal: int,
    protein_g: float,
    fat_g: float,
    carbs_g: float,
    ingredients: list[tuple[str, float, str]],
    steps: list[str],
    popularity: int,
):
    r = Recipe(
        title=title,
        meal_type=meal_type.value,
        time_minutes=time_minutes,
        difficulty=difficulty.value,
        kcal=kcal,
        protein_g=protein_g,
        fat_g=fat_g,
        carbs_g=carbs_g,
        steps=steps,
        popularity=popularity,
    )
    db.add(r)
    db.flush()  # <-- теперь r.id уже есть

    # уникальная картинка на каждое блюдо
    r.image_bytes = generate_recipe_image(r.title, r.id)
    r.image_mime = "image/webp"

    for name, qty, unit in ingredients:
        ing = _get_or_create_ingredient(db, name)
        db.add(RecipeIngredient(recipe_id=r.id, ingredient_id=ing.id, quantity=qty, unit=unit))


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _macros_for(title: str, base_kcal: int) -> tuple[float, float, float]:
    # Simple plausible macro split
    rnd = random.random()
    protein = _clamp((base_kcal * (0.18 + 0.08 * rnd)) / 4, 8, 55)
    fat = _clamp((base_kcal * (0.25 + 0.10 * (1 - rnd))) / 9, 4, 40)
    carbs = _clamp((base_kcal - protein * 4 - fat * 9) / 4, 10, 110)
    return round(protein, 1), round(fat, 1), round(carbs, 1)


def seed_if_empty(db: Session) -> int:
    """Seed ~500 recipes if DB has none. Returns number created."""
    if db.query(Recipe).count() > 0:
        return 0

    random.seed(42)

    # --- templates ---
    breakfasts = [
        {
            "base": "Овсянка на {milk} с {fruit}",
            "ings": [
                ("овсяные хлопья", 60, "г"),
                ("{milk}", 200, "мл"),
                ("{fruit}", 1, "шт"),
                ("мёд", 1, "ч.л."),
            ],
            "steps": [
                "Смешайте овсяные хлопья с {milk} в небольшой кастрюле.",
                "Доведите до кипения и варите 5–7 минут, помешивая.",
                "Снимите с огня, добавьте {fruit} и мёд.",
                "Дайте настояться 2 минуты и подавайте.",
            ],
            "time": 12,
            "difficulty": Difficulty.easy,
            "kcal": 420,
        },
        {
            "base": "Омлет с {veg} и сыром",
            "ings": [
                ("яйца", 3, "шт"),
                ("{veg}", 100, "г"),
                ("сыр", 30, "г"),
                ("молоко", 40, "мл"),
                ("соль", 1, "щеп."),
                ("масло", 1, "ч.л."),
            ],
            "steps": [
                "Взбейте яйца с молоком и солью.",
                "Нарежьте {veg} небольшими кусочками.",
                "Разогрейте сковороду с маслом, обжарьте {veg} 2–3 минуты.",
                "Влейте яичную смесь, готовьте под крышкой 4–6 минут.",
                "Посыпьте сыром, дождитесь расплавления и подавайте.",
            ],
            "time": 15,
            "difficulty": Difficulty.easy,
            "kcal": 360,
        },
        {
            "base": "Творожные сырники с {topping}",
            "ings": [
                ("творог", 200, "г"),
                ("яйца", 1, "шт"),
                ("мука", 3, "ст.л."),
                ("сахар", 1, "ст.л."),
                ("масло", 1, "ст.л."),
                ("{topping}", 2, "ст.л."),
            ],
            "steps": [
                "Смешайте творог, яйцо, сахар и 2 ст.л. муки до однородности.",
                "Сформируйте небольшие сырники, обваляйте в оставшейся муке.",
                "Обжарьте на сковороде с маслом по 2–3 минуты с каждой стороны.",
                "Подавайте с {topping}.",
            ],
            "time": 20,
            "difficulty": Difficulty.medium,
            "kcal": 480,
        },
    ]

    lunches = [
        {
            "base": "Паста с {sauce} и {protein}",
            "ings": [
                ("паста", 80, "г"),
                ("{sauce}", 180, "г"),
                ("{protein}", 120, "г"),
                ("чеснок", 1, "зуб"),
                ("соль", 1, "щеп."),
                ("масло", 1, "ст.л."),
            ],
            "steps": [
                "Отварите пасту до состояния al dente.",
                "На сковороде разогрейте масло, добавьте чеснок на 30 секунд.",
                "Добавьте {protein} и обжарьте 4–6 минут.",
                "Влейте {sauce}, прогрейте 3–4 минуты.",
                "Смешайте с пастой, посолите по вкусу и подавайте.",
            ],
            "time": 25,
            "difficulty": Difficulty.medium,
            "kcal": 650,
        },
        {
            "base": "Суп-пюре из {veg} с сухариками",
            "ings": [
                ("{veg}", 300, "г"),
                ("лук", 1, "шт"),
                ("морковь", 1, "шт"),
                ("бульон или вода", 700, "мл"),
                ("сливки", 80, "мл"),
                ("соль", 1, "щеп."),
            ],
            "steps": [
                "Нарежьте лук и морковь, слегка обжарьте 3–4 минуты.",
                "Добавьте {veg} и бульон, варите 15–20 минут до мягкости.",
                "Измельчите суп блендером до кремовой текстуры.",
                "Влейте сливки, посолите, прогрейте 2 минуты и подавайте с сухариками.",
            ],
            "time": 30,
            "difficulty": Difficulty.medium,
            "kcal": 430,
        },
        {
            "base": "Гречка с {mushroom} и луком",
            "ings": [
                ("гречка", 80, "г"),
                ("{mushroom}", 200, "г"),
                ("лук", 1, "шт"),
                ("масло", 1, "ст.л."),
                ("соль", 1, "щеп."),
            ],
            "steps": [
                "Промойте гречку и отварите до готовности.",
                "Нарежьте лук, обжарьте на масле 2–3 минуты.",
                "Добавьте {mushroom} и готовьте 6–8 минут.",
                "Смешайте с гречкой, посолите и подавайте.",
            ],
            "time": 25,
            "difficulty": Difficulty.easy,
            "kcal": 520,
        },
    ]

    dinners = [
        {
            "base": "{protein} с овощами на сковороде",
            "ings": [
                ("{protein}", 180, "г"),
                ("овощная смесь", 250, "г"),
                ("масло", 1, "ст.л."),
                ("соль", 1, "щеп."),
                ("перец", 1, "щеп."),
            ],
            "steps": [
                "Нарежьте {protein} кусочками.",
                "Разогрейте масло, обжарьте {protein} 6–8 минут до румяности.",
                "Добавьте овощную смесь, готовьте ещё 8–10 минут.",
                "Посолите и поперчите, подавайте горячим.",
            ],
            "time": 25,
            "difficulty": Difficulty.easy,
            "kcal": 560,
        },
        {
            "base": "Запечённая {fish} с лимоном",
            "ings": [
                ("{fish}", 200, "г"),
                ("лимон", 0.5, "шт"),
                ("соль", 1, "щеп."),
                ("масло", 1, "ст.л."),
                ("травы", 1, "ч.л."),
            ],
            "steps": [
                "Разогрейте духовку до 200°C.",
                "Посолите рыбу, сбрызните лимоном и маслом, добавьте травы.",
                "Запекайте 15–20 минут до готовности.",
                "Подавайте с ломтиками лимона и зеленью.",
            ],
            "time": 25,
            "difficulty": Difficulty.medium,
            "kcal": 500,
        },
        {
            "base": "Рагу из {veg} и фасоли",
            "ings": [
                ("{veg}", 250, "г"),
                ("фасоль консервированная", 200, "г"),
                ("томаты", 200, "г"),
                ("лук", 1, "шт"),
                ("масло", 1, "ст.л."),
                ("соль", 1, "щеп."),
            ],
            "steps": [
                "Нарежьте лук и обжарьте на масле 2–3 минуты.",
                "Добавьте {veg} и тушите 6–8 минут.",
                "Добавьте томаты и фасоль, посолите.",
                "Томите на слабом огне 10–12 минут и подавайте.",
            ],
            "time": 30,
            "difficulty": Difficulty.easy,
            "kcal": 540,
        },
    ]

    any_meals = [
        {
            "base": "Фруктовый салат с {dressing}",
            "ings": [
                ("яблоко", 1, "шт"),
                ("банан", 1, "шт"),
                ("апельсин", 1, "шт"),
                ("{dressing}", 2, "ст.л."),
            ],
            "steps": [
                "Нарежьте фрукты кубиками.",
                "Смешайте в миске и добавьте {dressing}.",
                "Аккуратно перемешайте и подавайте.",
            ],
            "time": 10,
            "difficulty": Difficulty.easy,
            "kcal": 260,
        },
        {
            "base": "Салат из огурцов и {cheese}",
            "ings": [
                ("огурцы", 2, "шт"),
                ("{cheese}", 80, "г"),
                ("зелень", 20, "г"),
                ("масло", 1, "ст.л."),
                ("соль", 1, "щеп."),
            ],
            "steps": [
                "Нарежьте огурцы и {cheese}.",
                "Смешайте с зеленью, заправьте маслом и посолите.",
                "Перемешайте и подавайте.",
            ],
            "time": 8,
            "difficulty": Difficulty.easy,
            "kcal": 320,
        },
    ]

    variations = {
        "milk": ["молоко", "вода", "растительное молоко"],
        "fruit": ["бананом", "яблоком", "ягодами", "грушей"],
        "veg": ["шпинат", "помидоры", "болгарский перец", "грибы"],
        "topping": ["сметаной", "йогуртом", "вареньем", "мёдом"],
        "sauce": ["томатный соус", "сливочный соус", "песто"],
        "protein": ["курица", "индейка", "тофу", "тунец"],
        "mushroom": ["шампиньоны", "вешенки"],
        "fish": ["лосось", "треска", "форель"],
        "dressing": ["йогуртом", "мёдом", "лимонным соком"],
        "cheese": ["фетой", "моцареллой", "брынзой"],
    }

    targets = [
        (MealType.breakfast, breakfasts, 50),
        (MealType.lunch, lunches, 100),
        (MealType.dinner, dinners, 250),
        (MealType.any, any_meals, 100),
    ]

    created = 0
    for meal_type, templates, count in targets:
        for i in range(count):
            tpl = templates[i % len(templates)]
            fmt = {k: random.choice(v) for k, v in variations.items()}
            title = tpl["base"].format(**fmt)

            ings = []
            for name, qty, unit in tpl["ings"]:
                ings.append((name.format(**fmt), qty, unit))

            steps = [s.format(**fmt) for s in tpl["steps"]]

            # small randomization in nutrition/time
            time_m = max(5, int(tpl["time"] + random.randint(-2, 6)))
            kcal = max(180, int(tpl["kcal"] + random.randint(-60, 90)))
            p, f, c = _macros_for(title, kcal)

            diff = tpl["difficulty"]
            # vary difficulty a bit
            if random.random() < 0.15:
                diff = Difficulty.medium if diff == Difficulty.easy else diff

            popularity = random.randint(0, 60)

            _add_recipe(
                db,
                title=title,
                meal_type=meal_type,
                time_minutes=time_m,
                difficulty=diff,
                kcal=kcal,
                protein_g=p,
                fat_g=f,
                carbs_g=c,
                ingredients=ings,
                steps=steps,
                popularity=popularity,
            )
            created += 1

    db.commit()
    return created
