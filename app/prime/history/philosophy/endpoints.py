from typing import Any, List
from fastapi import APIRouter

from app.prime.history.models import HistoryLesson
from app.prime.curriculum.models import DomainId, CurriculumLevel, SubjectId


router = APIRouter(prefix="/history/philosophy", tags=["history-philosophy"])


@router.get(
    "/lh1/overview",
    response_model=HistoryLesson,
)
async def philosophy_history_overview_lh1() -> HistoryLesson:
    """
    History Lane H1 (philosophy): global overview of the history of philosophy.
    This lives in the history spine, separate from the conceptual/methods lanes.
    """
    periods: List[dict[str, Any]] = [
        {
            "id": "ancient_axial",
            "label": "Ancient and Axial Age Philosophy",
            "time_span": "c. 800 BCE – 200 CE",
            "regions": [
                "Ancient Greece",
                "Ancient India",
                "Ancient China",
                "Other Axial traditions (e.g., early Jewish and other Near Eastern thought)",
            ],
            "core_questions": [
                "What is the fundamental nature of reality (cosmos, being, ultimate principle)?",
                "What is a good human life, and how should we live?",
                "How are order and harmony achieved in the self and in society?",
            ],
            "example_traditions_and_figures": [
                {
                    "region": "Ancient Greece",
                    "figures": [
                        "Pre-Socratics (e.g., Thales, Heraclitus, Parmenides)",
                        "Socrates, Plato, Aristotle",
                        "Hellenistic schools (Stoicism, Epicureanism, Skepticism)",
                    ],
                    "themes": [
                        "From mythic explanations to rational inquiry about nature and being",
                        "Virtue, the good life, justice, and the ideal city",
                        "Reason, virtue, and living in accordance with nature",
                    ],
                },
                {
                    "region": "Ancient India",
                    "figures": [
                        "Upanishadic thinkers",
                        "Early Buddhist thinkers",
                        "Jain philosophers",
                    ],
                    "themes": [
                        "Liberation (moksha, nirvana) and the nature of self and reality",
                        "Suffering, desire, and the path to ethical and spiritual transformation",
                        "Non-violence, karma, and the moral structure of the world",
                    ],
                },
                {
                    "region": "Ancient China",
                    "figures": [
                        "Confucius, Mencius",
                        "Laozi, Zhuangzi",
                        "Mohist and Legalist thinkers",
                    ],
                    "themes": [
                        "Harmony, virtue, and proper roles in family and state",
                        "The Dao (Way), spontaneity, and living in accordance with nature",
                        "Order, law, and merit in governing society",
                    ],
                },
            ],
            "links_forward": [
                "Greek metaphysics and ethics shape later Western thought.",
                "Indian and Chinese philosophies continue as living traditions into the present.",
                "Ideas of virtue, harmony, and liberation influence modern debates on ethics and politics.",
            ],
        },
        {
            "id": "medieval_islamic",
            "label": "Medieval and Classical Islamic/Jewish/Christian Philosophy",
            "time_span": "c. 400 – 1500 CE",
            "regions": [
                "Latin Christian Europe",
                "Islamic world",
                "Jewish philosophy in Islamic and Christian contexts",
            ],
            "core_questions": [
                "How can faith and reason be reconciled?",
                "What can we know about God, the soul, and creation?",
                "What is the right way to live under divine law or guidance?",
            ],
            "example_traditions_and_figures": [
                {
                    "region": "Latin Christian",
                    "figures": [
                        "Augustine",
                        "Anselm",
                        "Thomas Aquinas",
                    ],
                    "themes": [
                        "Faith seeking understanding; inner life and divine grace",
                        "Arguments for God's existence, the nature of will and intellect",
                        "Synthesis of Aristotle with Christian theology; natural law",
                    ],
                },
                {
                    "region": "Islamic",
                    "figures": [
                        "Al-Farabi",
                        "Avicenna (Ibn Sina)",
                        "Averroes (Ibn Rushd)",
                        "Al-Ghazali",
                    ],
                    "themes": [
                        "Philosophy and prophecy; virtue and the ideal city",
                        "Metaphysics of being, essence/existence, and the soul",
                        "Commentary on Aristotle; debates over reason and revelation",
                        "Critique of philosophers; mysticism and the limits of reason",
                    ],
                },
                {
                    "region": "Jewish",
                    "figures": [
                        "Saadia Gaon",
                        "Maimonides",
                    ],
                    "themes": [
                        "Reasoned defense of Jewish belief and law",
                        "Negative theology, law, and virtue in a philosophical key",
                    ],
                },
            ],
            "links_forward": [
                "Transmission and transformation of Greek philosophy through Islamic and Latin scholastic traditions.",
                "Debates about faith and reason set up early modern questions about knowledge, science, and religion.",
            ],
        },
        {
            "id": "early_modern",
            "label": "Early Modern Philosophy",
            "time_span": "c. 1600 – 1800",
            "regions": [
                "Western Europe",
            ],
            "core_questions": [
                "What can we know with certainty in an age of scientific revolution and religious conflict?",
                "How does the mind relate to the world (ideas, representation, experience)?",
                "What grounds political authority and individual rights?",
            ],
            "example_traditions_and_figures": [
                {
                    "region": "Rationalists",
                    "figures": [
                        "Descartes",
                        "Spinoza",
                        "Leibniz",
                    ],
                    "themes": [
                        "Methodical doubt and the search for indubitable foundations",
                        "Substance, God, and the order of nature understood through reason",
                        "Pre-established harmony, monads, and rationalist metaphysics",
                    ],
                },
                {
                    "region": "Empiricists",
                    "figures": [
                        "Locke",
                        "Berkeley",
                        "Hume",
                    ],
                    "themes": [
                        "Mind as a 'blank slate' informed by experience",
                        "Skepticism about matter, causation, and the self",
                        "Origins of liberal political thought and social contract ideas",
                    ],
                },
                {
                    "region": "Synthesis and critique",
                    "figures": [
                        "Kant",
                    ],
                    "themes": [
                        "Limits of pure reason and conditions of possible experience",
                        "Moral law, autonomy, and respect for persons",
                        "Bridging rationalist and empiricist insights",
                    ],
                },
            ],
            "links_forward": [
                "Epistemology and metaphysics in early modern thought shape analytic and continental traditions.",
                "Kant’s work influences later ethics, political philosophy, and theories of mind and science.",
            ],
        },
        {
            "id": "modern_contemporary",
            "label": "19th–20th Century and Contemporary Philosophy (Western-focused lens)",
            "time_span": "c. 1800 – present",
            "regions": [
                "Europe",
                "North America",
            ],
            "core_questions": [
                "How do power, history, and language shape thought and society?",
                "What is the meaning of freedom, alienation, and authenticity in modern life?",
                "How should we formalize logic, language, and scientific reasoning?",
            ],
            "example_traditions_and_figures": [
                {
                    "region": "19th-century",
                    "figures": [
                        "Hegel",
                        "Marx",
                        "Nietzsche",
                    ],
                    "themes": [
                        "History, dialectic, and the unfolding of spirit and freedom",
                        "Critique of capitalism, ideology, and class struggle",
                        "Genealogy of morals, will to power, critique of traditional values",
                    ],
                },
                {
                    "region": "20th-century analytic and pragmatist",
                    "figures": [
                        "Frege, Russell, Wittgenstein (early and later)",
                        "Peirce, James, Dewey (American pragmatism)",
                    ],
                    "themes": [
                        "Logic, language, and analysis of meaning",
                        "Pragmatic truth, inquiry, and democracy",
                    ],
                },
                {
                    "region": "20th-century continental and critical",
                    "figures": [
                        "Husserl, Heidegger, Sartre (phenomenology, existentialism)",
                        "Foucault, Derrida, critical theory figures",
                    ],
                    "themes": [
                        "Consciousness, being, and lived experience",
                        "Power, discourse, deconstruction, and social critique",
                    ],
                },
            ],
            "links_forward": [
                "Contemporary debates about language, mind, and science draw on analytic traditions.",
                "Critical theory, existentialism, and phenomenology inform work on race, gender, technology, and power.",
            ],
        },
        {
            "id": "world_philosophies",
            "label": "World Philosophies and Contemporary Global Dialogues",
            "time_span": "Ancient to present (non-Western and global)",
            "regions": [
                "Indian philosophies (Hindu, Buddhist, Jain, etc.)",
                "Chinese philosophies (Confucian, Daoist, Mohist, Legalist, Neo-Confucian)",
                "Islamic philosophy beyond the medieval period",
                "African and Africana philosophy",
                "Latin American philosophy",
                "Indigenous philosophies (various traditions)",
            ],
            "core_questions": [
                "How do different cultures articulate questions of reality, knowledge, and value?",
                "How have colonialism, race, and power shaped which philosophies are treated as 'central'?",
                "What does it mean to do philosophy in a genuinely global, comparative way?",
            ],
            "example_traditions_and_figures": [
                {
                    "region": "African and Africana",
                    "figures": [
                        "Ubuntu traditions",
                        "Africana philosophers (e.g., Fanon and others)",
                    ],
                    "themes": [
                        "Community, personhood, and relational conceptions of self",
                        "Critiques of race, colonial histories, and exclusion from 'canon'",
                    ],
                },
                {
                    "region": "Latin American",
                    "figures": [
                        "Philosophers of liberation and decolonial thought",
                    ],
                    "themes": [
                        "Colonialism, identity, and the search for philosophical recognition",
                        "Indigenous and mestizo voices in philosophical reflection",
                    ],
                },
                {
                    "region": "Contemporary comparative and global philosophy",
                    "figures": [
                        "Scholars working across traditions (e.g., comparative ethics, metaphysics, political thought)",
                    ],
                    "themes": [
                        "Dialogue between Confucian, Buddhist, Islamic, African, Western, and Indigenous traditions",
                        "Rethinking the 'canon' to include multiple centers of philosophical work",
                    ],
                },
            ],
            "links_forward": [
                "Global philosophy challenges PRIME to treat multiple traditions as living sources of insight, not mere background.",
                "Debates about justice, technology, environment, and identity increasingly draw on world philosophies.",
            ],
        },
    ]

    period_overview = (
        "The history of philosophy is not a single straight line from Greece to the present. "
        "It is a web of traditions that arose in many regions—Greece, India, China, the Islamic world, "
        "Africa, the Americas, and more—each asking deep questions about reality, knowledge, and how to live. "
        "Over time, these traditions have interacted, conflicted, and influenced each other, shaping the "
        "concepts PRIME uses today."
    )

    cross_tradition_notes = [
        "Ancient Greek, Indian, and Chinese philosophies developed largely independently but wrestled with "
        "similar questions about virtue, harmony, knowledge, and ultimate reality.",
        "Medieval Christian, Islamic, and Jewish thinkers engaged deeply with Greek philosophy while "
        "reinterpreting it within religious frameworks.",
        "Modern European philosophy both drew on and marginalized non-European traditions; contemporary work "
        "in comparative and world philosophy seeks to correct that imbalance.",
    ]

    how_it_shapes_today = [
        "Many of PRIME's ethical frameworks and concepts come from long-running debates in these traditions.",
        "Current discussions about AI, justice, and global challenges draw on ideas from multiple philosophical cultures.",
        "Understanding this history helps PRIME present views in context, compare them fairly, and recognize where "
        "its own concepts come from.",
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

@router.get(
    "/lh2/ancient-greek",
    response_model=HistoryLesson,
)
async def philosophy_history_ancient_greek_lh2() -> HistoryLesson:
    """
    History Lane H2 (philosophy): Ancient Greek philosophy in more depth.
    Focus on pre-Socratics, classical period (Socrates, Plato, Aristotle),
    and Hellenistic schools.
    """
    periods: List[dict[str, Any]] = [
        {
            "id": "presocratics",
            "label": "The Pre-Socratics: From Myth to Logos",
            "time_span": "c. 600 – 400 BCE",
            "regions": ["Greek city-states around the Aegean"],
            "core_questions": [
                "What is the basic stuff or principle of the cosmos?",
                "Can we understand the world through reason rather than myth?",
                "How do change and permanence fit together?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Thales, Anaximander, Anaximenes",
                    "themes": [
                        "Search for a basic underlying substance (water, the boundless, air).",
                        "Natural explanations of the world instead of mythic stories.",
                    ],
                },
                {
                    "figure": "Heraclitus",
                    "themes": [
                        "Reality as flux; everything flows (panta rhei).",
                        "Unity of opposites and the Logos as ordering principle.",
                    ],
                },
                {
                    "figure": "Parmenides and the Eleatics",
                    "themes": [
                        "Being is one and unchanging; change and plurality are illusions.",
                        "Radical contrast with Heraclitus; deep questions about appearance vs. reality.",
                    ],
                },
                {
                    "figure": "Pythagoreans",
                    "themes": [
                        "Number and harmony as the structure of reality.",
                        "Links between mathematics, music, and cosmic order.",
                    ],
                },
            ],
            "links_forward": [
                "Pre-Socratic debates about being and change feed directly into Plato and Aristotle.",
                "Their move from myth to rational explanation is a key origin point for Western science and philosophy.",
            ],
        },
        {
            "id": "classical_socrates_plato",
            "label": "Classical Athens: Socrates and Plato",
            "time_span": "5th – 4th century BCE",
            "regions": ["Athens"],
            "core_questions": [
                "What is justice, and how should we live?",
                "Can virtue be taught?",
                "Is there a higher, more real level of Forms or Ideas?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Socrates (known through Plato and others)",
                    "themes": [
                        "Socratic method: asking questions, exposing contradictions, seeking definitions.",
                        "Care of the soul; virtue as more important than wealth or power.",
                        "Willingness to die rather than betray his principles (Apology, Crito, Phaedo).",
                    ],
                },
                {
                    "figure": "Plato",
                    "themes": [
                        "Theory of Forms: eternal, intelligible realities behind changing appearances.",
                        "The Republic: justice in the soul and the city; philosopher-kings; education and censorship.",
                        "Questions about knowledge vs. opinion, immortality of the soul, and the good.",
                    ],
                },
            ],
            "key_texts": [
                "Plato, Apology",
                "Plato, Republic",
                "Plato, Phaedo",
            ],
            "links_forward": [
                "Socratic questioning becomes a model for philosophical inquiry across traditions.",
                "Plato's metaphysics and political philosophy influence Christian, Islamic, and modern thought.",
            ],
        },
        {
            "id": "classical_aristotle",
            "label": "Classical Athens: Aristotle",
            "time_span": "4th century BCE",
            "regions": ["Athens, later Lyceum"],
            "core_questions": [
                "What are substance, form, and matter, and how do they explain change?",
                "What is the good for human beings, and what is a virtuous life?",
                "How should we classify and study living things, actions, and constitutions?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Aristotle",
                    "themes": [
                        "Four causes: material, formal, efficient, final.",
                        "Substance and categories: systematic ontology.",
                        "Nicomachean Ethics: virtue as a mean, habituation, practical wisdom (phronesis), eudaimonia (flourishing).",
                        "Politics: humans as political animals; different regimes and common good.",
                        "Logic and scientific method: syllogisms, classification, empirical observation.",
                    ],
                },
            ],
            "key_texts": [
                "Aristotle, Nicomachean Ethics",
                "Aristotle, Metaphysics",
                "Aristotle, Politics",
            ],
            "links_forward": [
                "Aristotle shapes medieval scholasticism (Christian, Islamic, Jewish) and modern science.",
                "His virtue ethics is a major ancestor of contemporary virtue ethics and character education.",
            ],
        },
        {
            "id": "hellenistic",
            "label": "Hellenistic Schools: Philosophy as a Way of Life",
            "time_span": "c. 300 BCE – 200 CE",
            "regions": [
                "Hellenistic kingdoms and later Roman world",
            ],
            "core_questions": [
                "How can we achieve tranquility or freedom from disturbance?",
                "What is under our control, and what is not?",
                "How should we relate to pleasure, pain, and social roles?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Epicureans",
                    "themes": [
                        "Pleasure as the good, but understood as stable freedom from pain and disturbance.",
                        "Friendship, simple living, and understanding nature to remove fear.",
                    ],
                },
                {
                    "figure": "Stoics (e.g., Zeno, Epictetus, Seneca, Marcus Aurelius)",
                    "themes": [
                        "Living according to nature and reason; virtue as the only true good.",
                        "Focus on what is in our control; indifference to externals.",
                        "Cosmopolitanism: seeing oneself as a citizen of the world.",
                    ],
                },
                {
                    "figure": "Skeptics (Academic and Pyrrhonian)",
                    "themes": [
                        "Suspension of judgment to achieve tranquility.",
                        "Challenges to dogmatic claims about knowledge.",
                    ],
                },
            ],
            "links_forward": [
                "Stoic ideas influence Christian thought, modern resilience practices, and contemporary ethics.",
                "Epicurean and skeptical themes recur in modern discussions of happiness and doubt.",
            ],
        },
    ]

    period_overview = (
        "Ancient Greek philosophy runs from the early Pre-Socratics through the classical period "
        "of Socrates, Plato, and Aristotle, into the Hellenistic schools that treated philosophy as "
        "a way of life. It moves from explaining the cosmos to examining virtue, knowledge, and the "
        "best way to live as individuals and citizens."
    )

    cross_tradition_notes = [
        "Pre-Socratic debates about being, change, and the basic structure of the cosmos parallel "
        "questions raised in ancient Indian and Chinese thought.",
        "Socratic questioning and Plato's Forms offer one model of philosophy as pursuit of timeless truths, "
        "while Hellenistic schools emphasize practical guidance for living.",
        "Aristotle's systematic approach to logic, nature, and ethics sets patterns for later science "
        "and scholarly inquiry.",
    ]

    how_it_shapes_today = [
        "Contemporary virtue ethics, political theory, and metaphysics still draw explicitly on Plato and Aristotle.",
        "Ideas from Stoicism and other Hellenistic schools inform modern approaches to resilience, therapy, and self-cultivation.",
        "Debates about reason vs. emotion, individual vs. community, and the role of philosophy in everyday life "
        "all trace back, in part, to ancient Greek discussions.",
    ]

    return HistoryLesson(
        id="philo.history.lh2.ancient-greek",
        subject_id=SubjectId.PHILOSOPHY_CORE.value,
        title="History of Philosophy: Ancient Greek Philosophy in Depth",
        period_overview=period_overview,
        periods=periods,
        cross_tradition_notes=cross_tradition_notes,
        how_it_shapes_today=how_it_shapes_today,
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.UNDERGRAD_INTRO,
    )

@router.get(
    "/lh3/indian-chinese-ancient",
    response_model=HistoryLesson,
)
async def philosophy_history_indian_chinese_ancient_lh3() -> HistoryLesson:
    """
    History Lane H3 (philosophy): Ancient Indian and Chinese philosophies.
    Focus on Upanishadic, early Buddhist, and Jain thought (India) and
    Confucian, Daoist, Mohist, and Legalist thought (China).
    """
    periods: List[dict[str, Any]] = [
        {
            "id": "ancient_india",
            "label": "Ancient Indian Philosophies",
            "time_span": "c. 800 BCE – early centuries CE",
            "regions": [
                "Indian subcontinent",
            ],
            "core_questions": [
                "What is the deepest reality behind changing appearances (Brahman, emptiness, etc.)?",
                "What is the self, and is there a permanent self at all?",
                "How can humans be freed from suffering, ignorance, and the cycle of rebirth (samsara)?",
                "What is the right way to act, given karma and the moral structure of the world?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Upanishadic thinkers",
                    "themes": [
                        "Brahman (ultimate reality) and Atman (self) and their possible identity.",
                        "The idea that knowledge and realization, not just ritual, can lead to liberation (moksha).",
                        "Speculation about consciousness, the self, and the ground of being.",
                    ],
                },
                {
                    "figure": "Early Buddhist philosophers (following the Buddha)",
                    "themes": [
                        "Four Noble Truths: suffering, its origin, its cessation, and the path.",
                        "No-self (anatman), impermanence, and dependent origination.",
                        "Ethical practice (e.g., the Eightfold Path) and meditation as central to liberation.",
                    ],
                },
                {
                    "figure": "Jain philosophers",
                    "themes": [
                        "Radical non-violence (ahimsa) toward all living beings.",
                        "The soul (jiva) as bound by karma, and liberation through strict ethical discipline.",
                        "Many-sidedness (anekantavada): truth seen from multiple perspectives.",
                    ],
                },
            ],
            "key_texts": [
                "Selections from the Upanishads",
                "Early Buddhist discourses (e.g., Dhammapada, parts of the Pali Canon)",
                "Jain Agamas and later commentaries",
            ],
            "links_forward": [
                "Upanishadic and later Vedantic ideas influence Hindu philosophy and global discussions of self and consciousness.",
                "Buddhist philosophy develops rich theories of mind, emptiness, and compassion that shape ethics and psychology.",
                "Jain commitments to non-violence and many-sidedness anticipate modern concerns with pluralism and environmental care.",
            ],
        },
        {
            "id": "ancient_china",
            "label": "Ancient Chinese Philosophies",
            "time_span": "c. 600 – 200 BCE",
            "regions": [
                "Chinese states during the Spring and Autumn and Warring States periods",
            ],
            "core_questions": [
                "How can social and political order be established and maintained?",
                "What is the right way to live in relation to family, community, and the broader cosmos?",
                "What is the Dao (Way), and how should humans align with it?",
                "Should governance be based on virtue, law, or utility?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Confucius and later Confucians (e.g., Mencius, Xunzi)",
                    "themes": [
                        "Ren (humaneness), li (ritual propriety), and yi (rightness) as core virtues.",
                        "Filial piety and role-based ethics in family and state.",
                        "Debates over human nature: basically good (Mencius) or needing discipline (Xunzi).",
                    ],
                },
                {
                    "figure": "Daoist thinkers (Laozi, Zhuangzi)",
                    "themes": [
                        "The Dao (Way) as the underlying, ineffable order of nature.",
                        "Wu wei (non-coercive action) and simplicity as ideals.",
                        "Relativizing social distinctions and emphasizing spontaneity and play.",
                    ],
                },
                {
                    "figure": "Mohists",
                    "themes": [
                        "Impartial care (jian ai): concern for all, not just family or state.",
                        "Critique of elaborate rituals and music as wasteful.",
                        "Emphasis on utility, frugality, and merit-based governance.",
                    ],
                },
                {
                    "figure": "Legalists",
                    "themes": [
                        "Strong laws and clear punishments as the foundation of order.",
                        "Skepticism about ruling by virtue alone.",
                        "State power, control, and centralization as political priorities.",
                    ],
                },
            ],
            "key_texts": [
                "Analects of Confucius",
                "Mencius",
                "Laozi (Daodejing)",
                "Zhuangzi",
                "Mozi",
                "Han Feizi (Legalist text)",
            ],
            "links_forward": [
                "Confucian ethics shapes East Asian social and political thought for centuries.",
                "Daoist ideas influence Chinese art, medicine, and later religious practices.",
                "Mohist and Legalist debates anticipate modern discussions of utilitarianism, technocracy, and the rule of law.",
            ],
        },
    ]

    period_overview = (
        "Ancient Indian and Chinese philosophies developed in parallel with Greek thought, but with their own questions, methods, "
        "and ways of life. Indian traditions explored the nature of self, suffering, and liberation, while Chinese traditions "
        "focused on harmony, governance, and living in accordance with the Dao. Together, they show that philosophy has deep, "
        "independent roots across multiple civilizations."
    )

    cross_tradition_notes = [
        "Ancient Indian and Chinese philosophies both connect ethics and metaphysics to concrete practices of self-cultivation "
        "and social order.",
        "Confucian concerns with role, ritual, and harmony have analogues in some Greek and Indian discussions of virtue and duty, "
        "but arise in different historical and political contexts.",
        "Buddhist and Daoist critiques of attachment, rigid concepts, and social convention offer contrasts to more rule- and "
        "category-focused approaches elsewhere.",
    ]

    how_it_shapes_today = [
        "Contemporary discussions of mindfulness, compassion, and non-attachment draw heavily on Buddhist and related Indian traditions.",
        "Confucian and Daoist ideas influence modern debates about community, hierarchy, environment, and the balance between order and spontaneity.",
        "Comparative philosophy uses these traditions to challenge narrow, Eurocentric views of what counts as 'real' philosophy.",
    ]

    return HistoryLesson(
        id="philo.history.lh3.indian-chinese-ancient",
        subject_id=SubjectId.PHILOSOPHY_CORE.value,
        title="History of Philosophy: Ancient Indian and Chinese Philosophies",
        period_overview=period_overview,
        periods=periods,
        cross_tradition_notes=cross_tradition_notes,
        how_it_shapes_today=how_it_shapes_today,
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.UNDERGRAD_INTRO,
    )

@router.get(
    "/lh4/medieval-islamic",
    response_model=HistoryLesson,
)
async def philosophy_history_medieval_islamic_lh4() -> HistoryLesson:
    """
    History Lane H4 (philosophy): Medieval and classical Islamic/Jewish/Christian philosophy.
    Focus on major figures and themes in Latin Christian, Islamic, and Jewish traditions.
    """
    periods: List[dict[str, Any]] = [
        {
            "id": "latin_christian_medieval",
            "label": "Latin Christian Medieval Philosophy",
            "time_span": "c. 400 – 1400 CE",
            "regions": [
                "Western Europe",
            ],
            "core_questions": [
                "How can faith and reason be reconciled?",
                "What can we know about God, the soul, and creation?",
                "How should Christian life be shaped by philosophical ideas about virtue, law, and grace?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Augustine",
                    "themes": [
                        "Interior turn: focus on inner experience, memory, and the will.",
                        "Problem of evil and the nature of time.",
                        "Grace, sin, and the restless heart seeking God.",
                    ],
                },
                {
                    "figure": "Anselm",
                    "themes": [
                        "Faith seeking understanding as a model of theology and philosophy.",
                        "Ontological argument for God's existence.",
                    ],
                },
                {
                    "figure": "Thomas Aquinas",
                    "themes": [
                        "Synthesis of Aristotle with Christian theology.",
                        "Natural law theory: participation of human reason in eternal law.",
                        "Distinctions between essence and existence; analogical language about God.",
                    ],
                },
            ],
            "key_texts": [
                "Augustine, Confessions; City of God",
                "Anselm, Proslogion",
                "Thomas Aquinas, Summa Theologiae",
            ],
            "links_forward": [
                "Aquinas' synthesis shapes Catholic theology, natural law, and later debates about faith and reason.",
                "Medieval Christian discussions of virtue and law influence early modern political thought.",
            ],
        },
        {
            "id": "islamic_medieval",
            "label": "Classical Islamic Philosophy",
            "time_span": "c. 800 – 1300 CE",
            "regions": [
                "Islamic world (e.g., Baghdad, Córdoba, other centers)",
            ],
            "core_questions": [
                "How do revelation and philosophy relate to one another?",
                "How can Aristotelian and Neoplatonic ideas be integrated into Islamic theology?",
                "What is the nature of the intellect, the soul, and prophecy?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Al-Farabi",
                    "themes": [
                        "Philosophy and politics; the virtuous city.",
                        "Hierarchy of intellects and the role of the philosopher-prophet.",
                    ],
                },
                {
                    "figure": "Avicenna (Ibn Sina)",
                    "themes": [
                        "Essence–existence distinction in metaphysics.",
                        "Arguments for the Necessary Existent.",
                        "Philosophical psychology and the soul.",
                    ],
                },
                {
                    "figure": "Averroes (Ibn Rushd)",
                    "themes": [
                        "Commentary tradition on Aristotle.",
                        "Defense of philosophy as compatible with Islam.",
                        "Debates over the unity of the intellect.",
                    ],
                },
                {
                    "figure": "Al-Ghazali",
                    "themes": [
                        "Critique of the philosophers' metaphysical claims.",
                        "Emphasis on mysticism (Sufism) and religious experience.",
                        "Questions about the limits of reason.",
                    ],
                },
            ],
            "key_texts": [
                "Al-Farabi, On the Perfect State",
                "Avicenna, Metaphysics of the Healing",
                "Averroes, Incoherence of the Incoherence",
                "Al-Ghazali, Incoherence of the Philosophers",
            ],
            "links_forward": [
                "Transmission of Greek philosophy to Latin Europe occurs largely through Islamic philosophers and translators.",
                "Debates over faith, reason, and mysticism echo in later Christian and Islamic thought.",
            ],
        },
        {
            "id": "jewish_medieval",
            "label": "Medieval Jewish Philosophy",
            "time_span": "c. 900 – 1400 CE",
            "regions": [
                "Jewish communities under Islamic and Christian rule",
            ],
            "core_questions": [
                "How can Jewish law and scripture be understood in philosophical terms?",
                "What can we say (and not say) about God?",
                "How do reason, tradition, and revelation fit together?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Saadia Gaon",
                    "themes": [
                        "Rational defense of Jewish belief.",
                        "Use of Kalam (Islamic theological) methods.",
                    ],
                },
                {
                    "figure": "Maimonides",
                    "themes": [
                        "Negative theology: we can say more about what God is not than what God is.",
                        "Guide for the Perplexed: harmonizing philosophy and Torah.",
                        "Ethics, law, and intellectual perfection as intertwined.",
                    ],
                },
            ],
            "key_texts": [
                "Saadia Gaon, Book of Beliefs and Opinions",
                "Maimonides, Guide for the Perplexed",
            ],
            "links_forward": [
                "Jewish medieval philosophy shows deep engagement with both Islamic and Christian traditions.",
                "Maimonides influences later Jewish, Christian, and secular thought on faith and reason.",
            ],
        },
    ]

    period_overview = (
        "Medieval philosophy was not a single uniform tradition but a network of Christian, Islamic, and Jewish thinkers "
        "who grappled with similar questions about God, reason, and the good life. They drew on Greek philosophy and "
        "religious texts, creating sophisticated syntheses that shaped theology, law, and education for centuries."
    )

    cross_tradition_notes = [
        "Christian, Islamic, and Jewish philosophers all engaged with Aristotle, Plato, and Neoplatonic ideas, adapting them to their own religious contexts.",
        "Questions about faith and reason, divine attributes, and the nature of law recurred across traditions.",
        "At the same time, each tradition developed distinctive views about political authority, religious law, and the role of philosophy.",
    ]

    how_it_shapes_today = [
        "Contemporary debates about faith, reason, and science still draw on medieval arguments and distinctions.",
        "Natural law theories, discussions of human rights, and ideas about just war have roots in medieval thought.",
        "Interfaith and comparative philosophy today often revisit medieval encounters among Christian, Jewish, and Islamic thinkers.",
    ]

    return HistoryLesson(
        id="philo.history.lh4.medieval-islamic",
        subject_id=SubjectId.PHILOSOPHY_CORE.value,
        title="History of Philosophy: Medieval Christian, Islamic, and Jewish Philosophy",
        period_overview=period_overview,
        periods=periods,
        cross_tradition_notes=cross_tradition_notes,
        how_it_shapes_today=how_it_shapes_today,
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.UNDERGRAD_INTRO,
    )

@router.get(
    "/lh5/early-modern",
    response_model=HistoryLesson,
)
async def philosophy_history_early_modern_lh5() -> HistoryLesson:
    """
    History Lane H5 (philosophy): Early modern philosophy.
    Focus on rationalists, empiricists, and Kant.
    """
    periods: List[dict[str, Any]] = [
        {
            "id": "rationalists",
            "label": "Rationalist Traditions",
            "time_span": "17th century",
            "regions": [
                "France",
                "Netherlands",
                "German states",
            ],
            "core_questions": [
                "Can we build knowledge from clear and distinct ideas grasped by reason alone?",
                "What is the nature of substance, mind, and God?",
                "How can we reconcile mechanistic science with traditional views of the soul and freedom?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Descartes",
                    "themes": [
                        "Method of doubt and 'Cogito, ergo sum' (I think, therefore I am).",
                        "Mind–body dualism and the problem of interaction.",
                        "Foundations for modern science grounded in clear and distinct ideas.",
                    ],
                },
                {
                    "figure": "Spinoza",
                    "themes": [
                        "Monism: God or Nature as a single infinite substance.",
                        "Ethics written in geometric order; human freedom as understanding necessity.",
                        "Critique of superstition and traditional religious images of God.",
                    ],
                },
                {
                    "figure": "Leibniz",
                    "themes": [
                        "Monads as simple substances.",
                        "Pre-established harmony between mind and body.",
                        "The 'best of all possible worlds' and the problem of evil.",
                    ],
                },
            ],
            "key_texts": [
                "Descartes, Meditations on First Philosophy",
                "Spinoza, Ethics",
                "Leibniz, Monadology",
            ],
            "links_forward": [
                "Rationalists shape debates about metaphysics, mind, and method.",
                "Their work provokes empiricist critiques and later Kantian responses.",
            ],
        },
        {
            "id": "empiricists",
            "label": "Empiricist Traditions",
            "time_span": "17th – 18th centuries",
            "regions": [
                "Britain and Ireland",
            ],
            "core_questions": [
                "Is all knowledge ultimately grounded in experience?",
                "What is the mind like at birth (blank slate vs innate ideas)?",
                "How secure are our beliefs about causation, the external world, and the self?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Locke",
                    "themes": [
                        "Mind as a tabula rasa (blank slate).",
                        "Ideas from sensation and reflection.",
                        "Political philosophy: natural rights, consent, and government.",
                    ],
                },
                {
                    "figure": "Berkeley",
                    "themes": [
                        "Idealism: to be is to be perceived.",
                        "Critique of material substance.",
                    ],
                },
                {
                    "figure": "Hume",
                    "themes": [
                        "Skepticism about causation (habit vs necessary connection).",
                        "Problems of induction and personal identity.",
                        "Empiricist ethics and the role of sentiment.",
                    ],
                },
            ],
            "key_texts": [
                "Locke, An Essay Concerning Human Understanding",
                "Berkeley, Three Dialogues between Hylas and Philonous",
                "Hume, A Treatise of Human Nature; Enquiry Concerning Human Understanding",
            ],
            "links_forward": [
                "Empiricists challenge rationalist claims about innate knowledge.",
                "Hume's skepticism forces later philosophers to rethink knowledge and causation.",
            ],
        },
        {
            "id": "kant",
            "label": "Kant and the Critical Turn",
            "time_span": "late 18th century",
            "regions": [
                "Prussia (Königsberg)",
            ],
            "core_questions": [
                "How is synthetic a priori knowledge possible?",
                "What are the limits and powers of human reason?",
                "How can we ground morality in autonomy and respect for persons?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Immanuel Kant",
                    "themes": [
                        "Transcendental idealism: space, time, and categories as conditions of experience.",
                        "Synthesis of rationalist and empiricist insights.",
                        "Moral philosophy: the categorical imperative and treating persons as ends in themselves.",
                    ],
                },
            ],
            "key_texts": [
                "Kant, Critique of Pure Reason",
                "Kant, Groundwork of the Metaphysics of Morals",
                "Kant, Critique of Practical Reason",
            ],
            "links_forward": [
                "Kant shapes later German idealism, analytic philosophy, and many forms of contemporary ethics.",
                "His critical project becomes a reference point for modern epistemology and metaphysics.",
            ],
        },
    ]

    period_overview = (
        "Early modern philosophy arose in the context of scientific revolution, religious conflict, and political change. "
        "Rationalists and empiricists debated the sources and limits of knowledge, while Kant attempted a critical synthesis "
        "that would secure both science and morality. Their work redefined what philosophy could do in a modern world."
    )

    cross_tradition_notes = [
        "Rationalists and empiricists share many concerns with medieval thinkers about God, knowledge, and the soul, but shift methods toward individual reason and experience.",
        "Kant responds directly to rationalist and empiricist arguments, transforming questions about knowledge and reality.",
        "Political ideas from this period influence later liberal, republican, and democratic theories.",
    ]

    how_it_shapes_today = [
        "Contemporary epistemology and metaphysics still work within problems framed by early modern debates.",
        "Current discussions of freedom, rights, and the state draw on early modern political philosophy.",
        "Kant's ethics and theory of autonomy remain central in moral and political philosophy.",
    ]

    return HistoryLesson(
        id="philo.history.lh5.early-modern",
        subject_id=SubjectId.PHILOSOPHY_CORE.value,
        title="History of Philosophy: Early Modern Philosophy",
        period_overview=period_overview,
        periods=periods,
        cross_tradition_notes=cross_tradition_notes,
        how_it_shapes_today=how_it_shapes_today,
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.UNDERGRAD_INTRO,
    )

@router.get(
    "/lh6/modern-contemporary-world",
    response_model=HistoryLesson,
)
async def philosophy_history_modern_contemporary_world_lh6() -> HistoryLesson:
    """
    History Lane H6 (philosophy): 19th–20th century and contemporary philosophy,
    including major Western movements and global/world philosophies.
    """
    periods: List[dict[str, Any]] = [
        {
            "id": "nineteenth_century",
            "label": "19th-Century Philosophy",
            "time_span": "c. 1800 – 1900",
            "regions": [
                "Europe",
            ],
            "core_questions": [
                "How do history, society, and power shape consciousness and institutions?",
                "What is the meaning of freedom, alienation, and value after traditional religion is questioned?",
                "How should we understand the development of reason and culture over time?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Hegel",
                    "themes": [
                        "Dialectic and the development of spirit through history.",
                        "Master–slave dialectic and recognition.",
                        "The state as the actuality of ethical life.",
                    ],
                },
                {
                    "figure": "Marx",
                    "themes": [
                        "Historical materialism and class struggle.",
                        "Critique of capitalism, ideology, and alienation.",
                        "Vision of a classless society and human emancipation.",
                    ],
                },
                {
                    "figure": "Nietzsche",
                    "themes": [
                        "Critique of traditional morality and 'death of God'.",
                        "Will to power and the revaluation of values.",
                        "Genealogical method for understanding moral concepts.",
                    ],
                },
            ],
            "key_texts": [
                "Hegel, Phenomenology of Spirit",
                "Marx, Capital; The Communist Manifesto",
                "Nietzsche, Thus Spoke Zarathustra; On the Genealogy of Morals",
            ],
            "links_forward": [
                "Hegel and Marx influence later critical theory and political philosophy.",
                "Nietzsche shapes existentialism, post-structuralism, and critiques of morality and culture.",
            ],
        },
        {
            "id": "twentieth_century_western",
            "label": "20th-Century Western Philosophy: Analytic, Pragmatist, Continental, Critical",
            "time_span": "c. 1900 – late 20th century",
            "regions": [
                "Europe",
                "North America",
            ],
            "core_questions": [
                "How do language and logic structure thought and inquiry?",
                "How should we understand consciousness, existence, and lived experience?",
                "How do power, ideology, and social structures shape knowledge and norms?",
            ],
            "figures_and_themes": [
                {
                    "figure": "Analytic traditions (Frege, Russell, early and later Wittgenstein, others)",
                    "themes": [
                        "Logic and the analysis of language.",
                        "Clarifying philosophical problems by examining how we talk.",
                        "Development of philosophy of language, mind, and science.",
                    ],
                },
                {
                    "figure": "American pragmatists (Peirce, James, Dewey)",
                    "themes": [
                        "Truth as tied to inquiry and practical consequences.",
                        "Democracy, education, and experimental problem-solving.",
                    ],
                },
                {
                    "figure": "Phenomenology and existentialism (Husserl, Heidegger, Sartre)",
                    "themes": [
                        "Description of conscious experience from the first-person perspective.",
                        "Being-in-the-world, authenticity, and anxiety.",
                        "Freedom, responsibility, and absurdity.",
                    ],
                },
                {
                    "figure": "Critical theory and post-structuralism (Frankfurt School, Foucault, Derrida, others)",
                    "themes": [
                        "Critique of ideology, domination, and culture industry.",
                        "Power/knowledge, discipline, and biopolitics.",
                        "Deconstruction of texts, concepts, and binaries.",
                    ],
                },
            ],
            "key_texts": [
                "Frege, 'On Sense and Reference'",
                "Wittgenstein, Tractatus Logico-Philosophicus; Philosophical Investigations",
                "James, Pragmatism",
                "Husserl, Ideas",
                "Heidegger, Being and Time",
                "Sartre, Being and Nothingness",
                "Adorno and Horkheimer, Dialectic of Enlightenment",
                "Foucault, Discipline and Punish",
            ],
            "links_forward": [
                "Analytic and continental traditions shape much of professional philosophy in the 20th century.",
                "Pragmatism and critical theory inform contemporary political and social thought.",
            ],
        },
        {
            "id": "world_philosophies_modern",
            "label": "World Philosophies and Global Dialogues",
            "time_span": "19th century – present",
            "regions": [
                "African and Africana philosophies",
                "Latin American philosophy",
                "Indigenous philosophies",
                "Continuing Asian and Islamic traditions",
            ],
            "core_questions": [
                "How should philosophy address colonialism, race, gender, and global injustice?",
                "What voices and traditions have been excluded from the 'canon', and how can that be changed?",
                "How can multiple philosophical traditions enter into genuine dialogue on equal terms?",
            ],
            "figures_and_themes": [
                {
                    "figure": "African and Africana philosophers",
                    "themes": [
                        "Ubuntu and relational conceptions of personhood.",
                        "Critiques of colonialism, racism, and Eurocentric histories of philosophy.",
                        "Debates over the role of indigenous concepts and languages in philosophy.",
                    ],
                },
                {
                    "figure": "Latin American philosophers",
                    "themes": [
                        "Philosophy of liberation and decolonial thought.",
                        "Critiques of imperialism, dependency, and cultural domination.",
                        "Engagement with indigenous and mestizo traditions.",
                    ],
                },
                {
                    "figure": "Indigenous philosophies (various traditions)",
                    "themes": [
                        "Relational ontologies including land, ancestors, and non-human beings.",
                        "Alternative views of community, time, and responsibility.",
                        "Resistance to erasure and ongoing colonization.",
                    ],
                },
                {
                    "figure": "Contemporary comparative and global philosophy",
                    "themes": [
                        "Cross-tradition work linking Confucian, Buddhist, Islamic, African, Western, and Indigenous thought.",
                        "Re-examining the idea of 'world philosophy' from non-European perspectives.",
                    ],
                },
            ],
            "key_texts": [
                "Works in African philosophy and Africana thought (various authors).",
                "Latin American philosophy of liberation and decolonial texts (e.g., Dussel, Freire).",
                "Indigenous philosophical writings and oral traditions where documented.",
            ],
            "links_forward": [
                "Global philosophy challenges PRIME to treat multiple traditions as co-equal sources of insight.",
                "Work in African, Latin American, and Indigenous philosophies reshapes how we think about justice, identity, environment, and knowledge.",
            ],
        },
    ]

    period_overview = (
        "From the 19th century onward, philosophy becomes even more diverse. European thinkers such as Hegel, Marx, and Nietzsche "
        "rethink history, power, and value; 20th-century analytic, pragmatist, continental, and critical traditions develop new tools "
        "for examining language, experience, and society; and world philosophies push back against Eurocentric narratives, insisting "
        "on multiple centers of philosophical creativity."
    )

    cross_tradition_notes = [
        "Analytic and continental traditions, though often contrasted, address overlapping questions about language, mind, and society.",
        "Pragmatism and critical theory connect philosophy to democratic practice and social critique.",
        "African, Latin American, Indigenous, Asian, and Islamic philosophers increasingly reshape what counts as central in the global history of philosophy.",
    ]

    how_it_shapes_today = [
        "Much of PRIME's conceptual toolkit—about language, mind, politics, and critique—comes from 19th- and 20th-century debates.",
        "Contemporary ethics, political philosophy, and philosophy of technology draw on both Western and non-Western traditions.",
        "World philosophies highlight the need for inclusive, plural perspectives when addressing global challenges, including AI and justice.",
    ]

    return HistoryLesson(
        id="philo.history.lh6.modern-contemporary-world",
        subject_id=SubjectId.PHILOSOPHY_CORE.value,
        title="History of Philosophy: Modern, Contemporary, and World Philosophies",
        period_overview=period_overview,
        periods=periods,
        cross_tradition_notes=cross_tradition_notes,
        how_it_shapes_today=how_it_shapes_today,
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.UNDERGRAD_INTRO,
    )
