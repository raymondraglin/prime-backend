from enum import Enum
from typing import List

from pydantic import BaseModel


# =========================
# Angle classification
# =========================

class AngleType(str, Enum):
    ACUTE = "acute"
    RIGHT = "right"
    OBTUSE = "obtuse"


class AngleClassificationItem(BaseModel):
    id: str
    degrees: int
    correct_type: AngleType
    explanation: str


class AngleClassificationSet(BaseModel):
    description: str
    items: List[AngleClassificationItem]


def _classify_angle(degrees: int) -> AngleType:
    """
    Classify an angle in degrees as acute, right, or obtuse.
    - Acute: less than 90 degrees
    - Right: exactly 90 degrees
    - Obtuse: between 90 and 180 degrees
    """
    if degrees < 90:
        return AngleType.ACUTE
    if degrees == 90:
        return AngleType.RIGHT
    # For this early set, we assume 0 < degrees < 180
    return AngleType.OBTUSE


def generate_angle_classification_practice(count: int = 10) -> AngleClassificationSet:
    """
    Generate a small set of angles in degrees and their correct types
    for classification practice.
    """
    # Clamp count
    if count < 1:
        count = 1
    if count > 20:
        count = 20

    # Predefined angle values suitable for early practice
    base_angles = [30, 45, 60, 75, 89, 90, 91, 120, 135, 150, 179]

    items: list[AngleClassificationItem] = []
    idx = 1

    for deg in base_angles:
        if len(items) >= count:
            break
        angle_type = _classify_angle(deg)

        if angle_type == AngleType.ACUTE:
            explanation = (
                f"{deg}° is an acute angle because it is less than 90 degrees. "
                "Acute angles are 'narrower' than a right angle."
            )
        elif angle_type == AngleType.RIGHT:
            explanation = (
                f"{deg}° is a right angle because it is exactly 90 degrees. "
                "Right angles make a perfect 'L' shape."
            )
        else:
            explanation = (
                f"{deg}° is an obtuse angle because it is greater than 90 degrees "
                "but less than 180 degrees. Obtuse angles are 'wider' than a right angle."
            )

        items.append(
            AngleClassificationItem(
                id=f"angle_{idx}",
                degrees=deg,
                correct_type=angle_type,
                explanation=explanation,
            )
        )
        idx += 1

    return AngleClassificationSet(
        description=(
            "Angle classification practice: decide whether each angle is acute, "
            "right, or obtuse based on its measure in degrees."
        ),
        items=items,
    )


# =========================
# Perimeter and area
# =========================

class PerimeterAreaProblemKind(str, Enum):
    SQUARE_PERIMETER = "square_perimeter"
    RECTANGLE_PERIMETER = "rectangle_perimeter"
    RECTANGLE_AREA = "rectangle_area"


class PerimeterAreaItem(BaseModel):
    id: str
    kind: PerimeterAreaProblemKind
    length: int
    width: int | None
    question_text: str
    correct_value: int
    explanation: str


class PerimeterAreaSet(BaseModel):
    description: str
    items: List[PerimeterAreaItem]


def generate_perimeter_area_practice(count: int = 10) -> PerimeterAreaSet:
    """
    Generate simple perimeter and area problems for squares and rectangles.
    """
    if count < 1:
        count = 1
    if count > 30:
        count = 30

    items: list[PerimeterAreaItem] = []
    idx = 1

    # We'll cycle through a few fixed dimensions
    dimensions = [
        (2, 2),
        (3, 3),
        (4, 4),
        (3, 5),
        (2, 6),
        (4, 7),
    ]

    kinds_cycle = [
        PerimeterAreaProblemKind.SQUARE_PERIMETER,
        PerimeterAreaProblemKind.RECTANGLE_PERIMETER,
        PerimeterAreaProblemKind.RECTANGLE_AREA,
    ]

    while len(items) < count:
        for (length, width) in dimensions:
            if len(items) >= count:
                break

            for kind in kinds_cycle:
                if len(items) >= count:
                    break

                if kind == PerimeterAreaProblemKind.SQUARE_PERIMETER:
                    # use length as the side of a square
                    side = length
                    perim = 4 * side
                    question_text = (
                        f"A square has side length {side} units. "
                        f"What is its perimeter?"
                    )
                    explanation = (
                        f"The perimeter of a square is 4 × side. "
                        f"Here, 4 × {side} = {perim} units."
                    )
                    items.append(
                        PerimeterAreaItem(
                            id=f"geo_sq_perim_{idx}",
                            kind=kind,
                            length=side,
                            width=None,
                            question_text=question_text,
                            correct_value=perim,
                            explanation=explanation,
                        )
                    )
                    idx += 1

                elif kind == PerimeterAreaProblemKind.RECTANGLE_PERIMETER:
                    perim = 2 * (length + width)
                    question_text = (
                        f"A rectangle is {length} units long and {width} units wide. "
                        f"What is its perimeter?"
                    )
                    explanation = (
                        f"The perimeter of a rectangle is 2 × (length + width). "
                        f"Here, 2 × ({length} + {width}) = 2 × {length + width} = {perim} units."
                    )
                    items.append(
                        PerimeterAreaItem(
                            id=f"geo_rect_perim_{idx}",
                            kind=kind,
                            length=length,
                            width=width,
                            question_text=question_text,
                            correct_value=perim,
                            explanation=explanation,
                        )
                    )
                    idx += 1

                elif kind == PerimeterAreaProblemKind.RECTANGLE_AREA:
                    area = length * width
                    question_text = (
                        f"A rectangle is {length} units long and {width} units wide. "
                        f"What is its area?"
                    )
                    explanation = (
                        f"The area of a rectangle is length × width. "
                        f"Here, {length} × {width} = {area} square units."
                    )
                    items.append(
                        PerimeterAreaItem(
                            id=f"geo_rect_area_{idx}",
                            kind=kind,
                            length=length,
                            width=width,
                            question_text=question_text,
                            correct_value=area,
                            explanation=explanation,
                        )
                    )
                    idx += 1

                if len(items) >= count:
                    break
            if len(items) >= count:
                break

    return PerimeterAreaSet(
        description=(
            "Perimeter and area practice for simple squares and rectangles, "
            "using integer side lengths."
        ),
        items=items,
    )
