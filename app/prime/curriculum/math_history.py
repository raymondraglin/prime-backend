from app.prime.curriculum.models import (
    SubjectId,
    HistoryEvent,
)


def get_early_numeration_history() -> list[HistoryEvent]:
    """
    Early human numeration history: from tallies to positional systems and zero.
    """
    events: list[HistoryEvent] = []

    # 1) Tally marks and simple counts
    events.append(
        HistoryEvent(
            id="hist_num_tallies",
            title="Tally Marks and Early Counting",
            era="Prehistoric",
            approx_date="tens of thousands of years ago",
            location="Various early human societies",
            description=(
                "Early humans used tally marks on bones, wood, or stone to keep track of "
                "quantities like animals, days, or traded goods."
            ),
            significance=(
                "This is the beginning of written numbers: representing 'how many' with marks, "
                "even before formal symbols for 1, 2, 3."
            ),
            related_subjects=[SubjectId.MATH_FOUNDATIONS],
            related_lessons=[
                "math_fnd_number_foundations",
            ],
        )
    )

    # 2) Sumerian and Babylonian numeration (base 60)
    events.append(
        HistoryEvent(
            id="hist_num_sumer_babylon",
            title="Sumerian and Babylonian Base-60 Numeration",
            era="Ancient",
            approx_date="c. 3400–1800 BCE",
            location="Mesopotamia",
            description=(
                "Sumerians and Babylonians developed one of the earliest known numeration systems, "
                "using a base-60 (sexagesimal) positional system for counting and calculations."
            ),
            significance=(
                "Their base-60 system influenced how we still measure time (60 seconds, 60 minutes) "
                "and angles (360 degrees) today."
            ),
            related_subjects=[SubjectId.MATH_FOUNDATIONS],
            related_lessons=[
                "math_fnd_number_foundations",
                "math_fnd_range_0_100",
            ],
        )
    )

    # 3) Egyptian numeration (additive)
    events.append(
        HistoryEvent(
            id="hist_num_egypt",
            title="Egyptian Hieroglyphic Numerals",
            era="Ancient",
            approx_date="c. 3000–500 BCE",
            location="Egypt",
            description=(
                "Ancient Egyptians used hieroglyphic symbols to represent powers of ten, "
                "combining them additively to write numbers."
            ),
            significance=(
                "This system showed a clear idea of units, tens, hundreds, and so on, "
                "but lacked positional notation like our modern system."
            ),
            related_subjects=[SubjectId.MATH_FOUNDATIONS],
            related_lessons=[
                "math_fnd_range_0_100",
            ],
        )
    )

    # 4) Greek and Roman numerals
    events.append(
        HistoryEvent(
            id="hist_num_greek_roman",
            title="Greek and Roman Numerals",
            era="Classical",
            approx_date="c. 800 BCE–500 CE",
            location="Greece and Rome",
            description=(
                "Greek and Roman cultures used alphabetic and letter-based numerals, such as "
                "I, V, X, L, C, D, and M in the Roman system."
            ),
            significance=(
                "These systems were good for writing numbers but made long calculations harder "
                "than with positional notation."
            ),
            related_subjects=[SubjectId.MATH_FOUNDATIONS],
            related_lessons=[
                "math_fnd_range_0_100",
            ],
        )
    )

    # 5) Hindu-Arabic numerals and zero
    events.append(
        HistoryEvent(
            id="hist_num_hindu_arabic_zero",
            title="Hindu-Arabic Numerals and Zero",
            era="Classical to Medieval",
            approx_date="c. 200–1200 CE",
            location="India and the Islamic world, later Europe",
            description=(
                "Mathematicians in India developed the Hindu-Arabic numeral system with digits 0–9, "
                "place value, and a symbol for zero. Scholars in the Islamic world adopted and "
                "transmitted this system, and it eventually spread into Europe."
            ),
            significance=(
                "This positional base-10 system with zero is the foundation of modern arithmetic. "
                "It makes operations with integers, decimals, and fractions far easier than earlier systems."
            ),
            related_subjects=[SubjectId.MATH_FOUNDATIONS],
            related_lessons=[
                "math_fnd_counting_0_10",
                "math_fnd_range_0_100",
                "math_fnd_decimals_basic",
            ],
        )
    )

    # 6) Decimal fractions in everyday calculation
    events.append(
        HistoryEvent(
            id="hist_num_decimal_fractions",
            title="Decimal Fractions in Calculation",
            era="Early Modern",
            approx_date="c. 1500–1600 CE",
            location="Europe and elsewhere",
            description=(
                "Mathematicians began using decimal fractions, extending the place-value system "
                "to represent parts of a whole, such as 0.5 or 0.25."
            ),
            significance=(
                "Decimal fractions link naturally to money (like dollars and cents) and to "
                "measurement, making calculations more straightforward."
            ),
            related_subjects=[SubjectId.MATH_FOUNDATIONS],
            related_lessons=[
                "math_fnd_money_fractions",
                "math_fnd_decimals_basic",
            ],
        )
    )

    return events
