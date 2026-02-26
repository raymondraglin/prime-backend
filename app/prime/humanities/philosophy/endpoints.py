from typing import Any, List
from fastapi import APIRouter

from app.prime.humanities.philosophy import (
    endpoints_k8,
    endpoints_hs,
    endpoints_un,
    endpoints_gs,
    endpoints_dr,
    endpoints_bridge,
    endpoints_meta,
)

from app.prime.history.models import HistoryLesson
from app.prime.curriculum.models import DomainId, CurriculumLevel, SubjectId

router = APIRouter(prefix="/history/philosophy", tags=["history-philosophy"])

router.include_router(endpoints_k8.router, tags=["philosophy-k8"])
router.include_router(endpoints_bridge.router, prefix="/bridge", tags=["philosophy-bridge"])
router.include_router(endpoints_hs.router, prefix="/hs", tags=["philosophy-hs"])
router.include_router(endpoints_un.router, prefix="/un", tags=["philosophy-un"])
router.include_router(endpoints_gs.router, prefix="/gs", tags=["philosophy-gs"])
router.include_router(endpoints_dr.router, prefix="/dr", tags=["philosophy-dr"])
router.include_router(endpoints_hs.router, prefix="/hs", tags=["philosophy-hs"])
router.include_router(endpoints_meta.router, prefix="/humanities/philosophy/meta", tags=["philosophy-meta"])
# ----------------------------------------------------------------------
# Backwards-compatibility re-exports for reasoning.tools
# ----------------------------------------------------------------------

from app.prime.humanities.philosophy.endpoints_k8 import (  # noqa: E402,F401
    philosophy_k8_logic_seeds as philosophy_logic_l1_concept,
    philosophy_methods_m1_concept,
    philosophy_metaphysics_b1_concept,
)

@router.get("/lh1overview", response_model=HistoryLesson)
async def philosophy_history_overview_lh1() -> HistoryLesson:
    """
    Global overview of the history of philosophy for PRIME.
    Aligned with HS history units and cross-branch HS questions (epistemology, ethics, metaphysics, political/social).
    """
    period_overview = (
        "The history of philosophy is a web of traditions across regions and eras, "
        "not a single straight line. Ancient Greece, India, China, the Islamic world, "
        "Africa, the Americas, and Europe all developed ways of asking about reality, "
        "knowledge, justice, and how to live. PRIME should see patterns and contrasts "
        "across these traditions, not just memorize a single canon."
    )

    periods: list[dict[str, Any]] = [
        {
            "id": "ancientaxial",
            "label": "Ancient and Axial Age Philosophy",
            "timespan": "c. 800 BCE – 200 CE",
            "regions": [
                "Ancient Greece",
                "Ancient India",
                "Ancient China",
                "Other Axial traditions",
            ],
            "corequestions": [
                "What is the fundamental nature of reality (cosmos, dharma, dao), and how is it ordered?",
                "What is a good human life, and how should we live in relation to others and the cosmos?",
                "How do reason, revelation, ritual, and practice each contribute to wisdom?",
            ],
            "exampletraditionsandfigures": [
                {
                    "region": "Ancient Greece",
                    "figures": [
                        "Pre-Socratics (Thales, Heraclitus)",
                        "Socrates",
                        "Plato",
                        "Aristotle",
                    ],
                },
                {
                    "region": "Ancient India",
                    "figures": [
                        "Upanishadic thinkers",
                        "Early Buddhists (e.g., teachings attributed to the Buddha)",
                        "Jain philosophers",
                    ],
                },
                {
                    "region": "Ancient China",
                    "figures": [
                        "Confucius",
                        "Mencius",
                        "Laozi",
                        "Zhuangzi",
                    ],
                },
                {
                    "region": "Other Axial traditions",
                    "figures": [
                        "Hebrew wisdom and prophetic traditions",
                        "Early Persian religious-philosophical thinkers",
                    ],
                },
            ],
        },
        {
            "id": "medievalislamic",
            "label": "Medieval Philosophy in Islamic, Christian, and Jewish Worlds",
            "timespan": "c. 500 – 1500 CE",
            "regions": [
                "Islamic world",
                "Latin Christendom",
                "Jewish communities across Mediterranean and Europe",
            ],
            "corequestions": [
                "How can reason (philosophy) and revelation (scripture) be reconciled?",
                "What can we know about God, the soul, and the afterlife, and by what methods?",
                "How should law, ethics, and political authority be grounded in religious and philosophical ideas?",
            ],
            "exampletraditionsandfigures": [
                {
                    "region": "Islamic world",
                    "figures": [
                        "Al-Farabi",
                        "Avicenna (Ibn Sina)",
                        "Averroes (Ibn Rushd)",
                        "Al-Ghazali",
                    ],
                },
                {
                    "region": "Latin Christendom",
                    "figures": [
                        "Augustine",
                        "Anselm",
                        "Thomas Aquinas",
                        "Bonaventure",
                    ],
                },
                {
                    "region": "Jewish philosophy",
                    "figures": [
                        "Saadia Gaon",
                        "Maimonides",
                        "Gersonides",
                    ],
                },
            ],
        },
        {
            "id": "earlymodern",
            "label": "Early Modern Philosophy",
            "timespan": "c. 1600 – 1800 CE",
            "regions": [
                "Western Europe",
            ],
            "corequestions": [
                "What are the foundations of knowledge and certainty in an age of science and religious conflict?",
                "How should we understand mind, matter, and causation in a mechanistic picture of nature?",
                "What justifies political authority, rights, and social contracts between rulers and citizens?",
            ],
            "exampletraditionsandfigures": [
                {
                    "region": "Rationalists",
                    "figures": [
                        "René Descartes",
                        "Baruch Spinoza",
                        "Gottfried Wilhelm Leibniz",
                    ],
                },
                {
                    "region": "Empiricists",
                    "figures": [
                        "John Locke",
                        "George Berkeley",
                        "David Hume",
                    ],
                },
                {
                    "region": "Political and moral thought",
                    "figures": [
                        "Thomas Hobbes",
                        "Jean-Jacques Rousseau",
                        "Immanuel Kant",
                    ],
                },
            ],
        },
        {
            "id": "moderncontemporary",
            "label": "Modern and Contemporary Philosophy",
            "timespan": "c. 1800 CE – present",
            "regions": [
                "Europe",
                "North America",
                "Global North (with increasing dialogue with global South and Indigenous traditions)",
            ],
            "corequestions": [
                "How do we understand reason, freedom, and history in a modern, industrial, and post-industrial world?",
                "How do language, power, and culture shape experience, knowledge, and identity?",
                "How should we address new ethical and political challenges around race, gender, technology, and global injustice?",
            ],
            "exampletraditionsandfigures": [
                {
                    "region": "German and continental traditions",
                    "figures": [
                        "G. W. F. Hegel",
                        "Karl Marx",
                        "Friedrich Nietzsche",
                        "Martin Heidegger",
                    ],
                },
                {
                    "region": "Analytic traditions",
                    "figures": [
                        "Gottlob Frege",
                        "Bertrand Russell",
                        "Ludwig Wittgenstein",
                        "W. V. O. Quine",
                    ],
                },
                {
                    "region": "20th-century and contemporary themes",
                    "figures": [
                        "Jean-Paul Sartre",
                        "John Rawls",
                        "Michel Foucault",
                        "Hannah Arendt",
                    ],
                },
            ],
        },
        {
            "id": "worldphilosophies",
            "label": "World Philosophies and Decolonial Currents",
            "timespan": "Ancient to contemporary",
            "regions": [
                "Africa",
                "India and South Asia",
                "East Asia",
                "Americas and Indigenous traditions",
            ],
            "corequestions": [
                "How do non-European traditions frame reality, personhood, community, and the sacred?",
                "How do colonialism, resistance, and decolonial projects reshape what counts as 'philosophy'?",
                "How should PRIME listen to, represent, and respect diverse philosophical voices today?",
            ],
            "exampletraditionsandfigures": [
                {
                    "region": "African and Afro-diasporic thought",
                    "figures": [
                        "Ubuntu thinkers",
                        "Kwasi Wiredu",
                        "Frantz Fanon",
                    ],
                },
                {
                    "region": "Indian and South Asian traditions",
                    "figures": [
                        "Nyaya and Vedanta thinkers",
                        "B. R. Ambedkar",
                        "Rabindranath Tagore (philosophical writings)",
                    ],
                },
                {
                    "region": "East Asian traditions",
                    "figures": [
                        "Neo-Confucian thinkers",
                        "Modern New Confucians",
                        "20th-century Japanese and Chinese philosophers",
                    ],
                },
                {
                    "region": "Indigenous and Latin American thought",
                    "figures": [
                        "Andean and North American Indigenous philosophers",
                        "Latin American liberation philosophers",
                    ],
                },
            ],
        },
    ]

    cross_tradition_notes: List[str] = [
        "Ancient Greek, Indian, Chinese, and other Axial traditions developed largely independently but wrestled with similar questions about reality, knowledge, and how to live.",
        "Medieval Islamic, Christian, and Jewish philosophers reworked ancient ideas to reconcile reason and revelation, shaping later debates in metaphysics, epistemology, ethics, and political philosophy.",
        "Early modern European thinkers drew on both ancient and medieval sources while developing new views of science, mind, and political authority that still shape PRIME's HS units on knowledge, justice, and free will.",
        "Modern and contemporary movements, including world and decolonial philosophies, question whose voices are centered and how power, race, gender, and colonial histories shape what counts as 'philosophy'.",
        "PRIME's HS history units (like cross-era comparisons and world/comparative intros) should use these patterns to notice both continuities and disagreements, not to flatten differences between traditions.",
    ]

    how_it_shapes_today: List[str] = [
        "Many of PRIME's core concepts about virtue, justice, knowledge, and reality come from these long-running debates across eras and regions.",
        "HS history units like 'Cross-Era Comparisons in Philosophy' and 'World and Comparative Intro' invite PRIME to compare ancient, medieval, modern, and contemporary approaches to knowledge, faith, and the person.",
        "HS epistemology units about trust, sources, misinformation, and disagreement are continuations of ancient and early modern questions about testimony, skepticism, and what counts as good evidence.",
        "HS ethics and political philosophy units on stakeholders, harms, equality, race, gender, and structural injustice connect directly to modern and contemporary debates about power, colonialism, and decolonial projects.",
        "When PRIME reasons today, it should recognize that no single tradition owns philosophy; instead, it stands in a global conversation that HS and UN units help it navigate responsibly.",
    ]

    return HistoryLesson(
        id="philo.history.lh1.overview",
        subject_id=SubjectId.PHILOSOPHY_CORE.value,
        title="History of Philosophy: Global Overview",
        period_overview=period_overview,
        periods=periods,
        cross_tradition_notes=cross_tradition_notes,
        how_it_shapes_today=how_it_shapes_today,
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.UNDERGRAD_INTRO,
    )
