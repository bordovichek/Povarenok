from __future__ import annotations

import re


def _has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def personalize_steps(base_steps: list[str], user_constraints: str) -> tuple[list[str], list[str]]:
    """Simple heuristic personalization.

    Returns (steps, notes).
    """
    c = user_constraints or ""
    notes: list[str] = []
    steps = list(base_steps)

    if _has(r"кастрюл", c) and _has(r"(\b3\s*л|3\s*лит)", c):
        notes.append("Учтено ограничение по объёму кастрюли (до 3 л). При необходимости готовьте в 2 подхода.")
        steps = [
            s.replace("кастрюле", "небольшой кастрюле")
            .replace("в кастрюлю", "в небольшую кастрюлю")
            for s in steps
        ]

    if _has(r"нет\s+духов", c):
        notes.append("Нет духовки: шаги с запеканием адаптированы под сковороду/мультиварку (если возможно).")
        steps = [re.sub(r"запек\w+", "обжарьте/потушите", s, flags=re.IGNORECASE) for s in steps]

    if _has(r"нет\s+блендер", c):
        notes.append("Нет блендера: измельчайте ножом или используйте тёрку.")
        steps = [s.replace("взбейте блендером", "измельчите ножом/тёркой") for s in steps]

    return steps, notes
