from typing import Any, Dict, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.prime.curriculum.models import (
    PhilosophyLesson,
    SubjectId,
    LessonKind,
    DifficultyLevel,
    DomainId,
    CurriculumLevel,
    PhilosophyPracticeRequest,
    PhilosophyPracticeResponse,
    PhilosophyQuestionKind,
    PhilosophyArgumentPracticeRequest,
    PhilosophyArgumentPracticeResponse,
    PhilosophyLane1Mode,
    PhilosophyLane1PlannerRequest,
    PhilosophyLane1PlannerResponse,
    PhilosophyBranch,
    PhilosophyBranchPracticeRequest,
    PhilosophyBranchPracticeResponse,
    PhilosophyLane2Mode,
    PhilosophyLane2PlannerRequest,
    PhilosophyLane2PlannerResponse,
    EthicsFramework,
    EthicsIntroTeachSummary,
    EthicsIntroPracticeRequest,
    EthicsFrameworkEvaluation,
    EthicsIntroPracticeResponse,
    PhilosophyLane3Mode,
    PhilosophyLane3PlannerRequest,
    PhilosophyLane3PlannerResponse,
    EthicsDigitalContextTag,
    EthicsDigitalPracticeRequest,
    EthicsDigitalFrameworkEvaluation,
    EthicsDigitalPracticeResponse,
    PhilosophyLane4Mode,
    PhilosophyLane4PlannerRequest,
    PhilosophyLane4PlannerResponse,
    ConsequentialismVariant,
    EthicsConsequentialismTeachEntry,
    EthicsConsequentialismTeachLesson,
    EthicsConsequentialismPracticeRequest,
    EthicsConsequentialismPracticeAnalysis,
    EthicsConsequentialismPracticeResponse,
    PhilosophyLane5Mode,
    PhilosophyLane5PlannerRequest,
    PhilosophyLane5PlannerResponse,
    DeontologyVariant,
    EthicsDeontologyTeachEntry,
    EthicsDeontologyTeachLesson,
    EthicsDeontologyPracticeRequest,
    EthicsDeontologyPracticeAnalysis,
    EthicsDeontologyPracticeResponse,
    VirtueEthicsVariant,
    EthicsVirtueTeachEntry,
    EthicsVirtueTeachLesson,
    EthicsVirtuePracticeRequest,
    EthicsVirtuePracticeAnalysis,
    EthicsVirtuePracticeResponse,
    CareEthicsVariant,
    EthicsCareTeachEntry,
    EthicsCareTeachLesson,
    EthicsCarePracticeRequest,
    EthicsCarePracticeAnalysis,
    EthicsCarePracticeResponse,
    EthicsFourLensDilemmaRequest,
    EthicsSingleLensSummary,
    EthicsFourLensResponse,
    EthicsMetaPerspectiveMode,
    EthicsMetaPerspectiveSummary,
    EthicsMetaPerspectivesResponse,
    EthicsConceptDimension,
    EthicsConceptExample,
    EthicsConceptFrameworkView,
    EthicsConcept,
    EthicsConceptDiagnosisRequest,
    EthicsConceptDiagnosisResponse,
    EthicsConceptDimensionAssessment,
    MetaPhilosophyAssessment,
    EthicsConceptLesson,
    EthicsConceptLessonProfessorView,
    EthicsConceptLessonGradView,
    EthicsConceptLessonTeacherView,
    EthicsConceptLessonTeacherStep,
    LogicConceptId,
    LogicConcept,
    LogicConceptLessonProfessorView,
    LogicConceptLessonGradView,
    LogicConceptLessonTeacherView,
    LogicConceptLessonTeacherStep,
    LogicConceptPracticeQuestion,
    LogicConceptPracticeSet,
    LogicConceptLesson,
    MethodsConceptId,
    MethodsConcept,
    MethodsConceptLesson,
    MethodsConceptLessonProfessorView,
    MethodsConceptLessonGradView,
    MethodsConceptLessonTeacherView,
    MethodsConceptLessonTeacherStep,
    MethodsConceptPracticeQuestion,
    MethodsConceptPracticeSet,
    MetaphysicsConceptId,
    MetaphysicsConcept,
    MetaphysicsConceptLesson,
    MetaphysicsConceptLessonProfessorView,
    MetaphysicsConceptLessonGradView,
    MetaphysicsConceptLessonTeacherView,
    MetaphysicsConceptLessonTeacherStep,
    MetaphysicsConceptPracticeQuestion,
    MetaphysicsConceptPracticeSet,
    ReasoningTask,
    ReasoningTaskKind,
    ReasoningCoreResponse,
    ReasoningTrace,
    ReasoningStep,
    ReasoningStepKind,
    ReasoningOutcomeQuality,
    ReasoningTraceTag,
    K8LogicPracticeItemKind,
    K8LogicPracticeRequest,
    K8LogicPracticeResponse,
    K8EthicsStoryKind,
    K8EthicsPracticeRequest,
    K8EthicsPracticeResponse,
    K8PhilosophyLane,
    K8PhilosophyPlannerRequest,
    K8PhilosophyPlannerResponse,
    K8WorldQuestionTag,
    K8WorldPracticeRequest,
    K8WorldPracticeResponse,
    K8WorldPlannerRequest,
    K8WorldPlannerResponse,
    K8MindQuestionTag,
    K8MindPracticeRequest,
    K8MindPracticeResponse,
    K8MindPlannerRequest,
    K8MindPlannerResponse,
    K8LogicPlannerRequest,
    K8LogicPlannerResponse,
    K8EthicsPlannerRequest,
    K8EthicsPlannerResponse,
    K8TeacherViewMode,
    K8TeacherLaneSummary,
)
from app.prime.reasoning.memory import save_practice_to_memory
from app.prime.curriculum.outcome_quality import compute_outcome_quality_from_answers


router = APIRouter()


class PhilosophyHelloResponse(BaseModel):
    description: str


@router.get("/hello", response_model=PhilosophyHelloResponse)
async def philosophy_hello() -> PhilosophyHelloResponse:
    """
    Minimal stub endpoint to verify PRIME's humanities/philosophy wiring.
    This will be replaced with full K–PhD philosophy lanes later.
    """
    return PhilosophyHelloResponse(
        description=(
            "PRIME humanities/philosophy spine is wired. "
            "This stub will grow into the K–PhD philosophy curriculum, "
            "starting with 'what philosophy is' and basic argument structure."
        )
    )


@router.get(
    "/l1/what-is-philosophy",
    response_model=PhilosophyLesson,
)
async def philosophy_lane1_what_is_philosophy() -> PhilosophyLesson:
    """
    Lane 1: Bare-bones 'What is philosophy?' lesson object, using the global
    Lesson/Subject/Curriculum backbone.
    """
    return PhilosophyLesson(
        id="philo.l1.what-is-philosophy",
        subject=SubjectId.PHILOSOPHY_CORE,
        title="What Is Philosophy?",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.EARLY,
        description=(
            "Philosophy is the disciplined study of very general questions "
            "about reality, knowledge, and value, using reasons and arguments "
            "rather than experiments or authority alone."
        ),
        content={
            "overview": (
                "Philosophy asks big, general questions and tries to answer them "
                "with clear reasons instead of just habit, tradition, or authority."
            ),
            "key_ideas": [
                "Philosophy asks questions like 'What is real?', 'What can we know?', and 'What should we do?'.",
                "Philosophers use arguments: reasons offered for and against claims.",
                "Different branches of philosophy focus on different kinds of questions, such as ethics, epistemology, and metaphysics.",
            ],
            "examples": [
                "Should I tell a difficult truth to my friend, or is it better to stay silent?",
                "How do I know that the world is really as it appears to me?",
                "What makes a person the same over time, even as they change?",
            ],
            "guided_questions": [
                "What is one big question you think about often?",
                "When you try to answer that question, what do you rely on most: feelings, tradition, data, or reasons?",
                "What would count as a good reason for you to change your mind about it?",
            ],
            "common_confusions": [
                "Thinking philosophy is just having opinions instead of giving reasons.",
                "Thinking philosophy only belongs to one culture or tradition.",
                "Thinking philosophy never makes progress because it rarely gives final answers.",
            ],
            "reflection_prompts": [
                "Name one belief you hold strongly. How much is it based on habit versus careful reasoning?",
                "Think of a time when someone gave you a reason that changed your mind. What made that reason powerful?",
            ],
            "next_suggestion": (
                "Next, explore basic argument structure: premises, conclusions, "
                "and how reasons support or challenge a claim."
            ),
        },
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.SCHOOL_SECONDARY,
    )

@router.get(
    "/l1/argument-structure",
    response_model=PhilosophyLesson,
)
async def philosophy_lane1_argument_structure() -> PhilosophyLesson:
    """
    Lane 1b: Basic argument structure: arguments, premises, and conclusions.
    """
    return PhilosophyLesson(
        id="philo.l1.argument-structure",
        subject=SubjectId.PHILOSOPHY_CORE,
        title="Basic Argument Structure: Premises and Conclusions",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.EARLY,
        description=(
            "An argument is a set of reasons (premises) offered to support a claim (the conclusion). "
            "Learning to see this structure is the first step toward clear thinking."
        ),
        content={
            "overview": (
                "In philosophy, an argument is not a fight. It is a set of statements where some "
                "are given as reasons (premises) for another statement (the conclusion)."
            ),
            "key_ideas": [
                "An argument consists of one or more premises and one conclusion.",
                "Premises are reasons offered in support of the conclusion.",
                "The conclusion is what the arguer wants you to accept based on those reasons.",
                "Indicator words like 'because', 'since' often introduce premises; 'so', 'therefore', 'thus' often introduce conclusions.",
            ],
            "examples": [
                "Example 1: 'You should wear a seatbelt because it reduces your risk of injury.' "
                "Premise: It reduces your risk of injury. Conclusion: You should wear a seatbelt.",
                "Example 2: 'The streets are wet, so it must have rained.' "
                "Premise: The streets are wet. Conclusion: It must have rained.",
            ],
            "guided_questions": [
                "In your own words, what is the difference between a premise and a conclusion?",
                "Can you find one sentence that states a conclusion you have, and one sentence that gives a reason for it?",
                "When someone tries to convince you of something, how can you tell what their conclusion is?",
            ],
            "common_confusions": [
                "Thinking that any strong feeling is an argument (it is not, unless reasons are given).",
                "Confusing explanations ('The streets are wet because the city washed them') with arguments "
                "('The streets are wet, so it must have rained').",
                "Assuming the conclusion always comes last; in real life, it can come first, last, or be implied.",
            ],
            "reflection_prompts": [
                "Think of a disagreement you had recently. Can you rewrite what you said as premises and a conclusion?",
                "Notice one time today when someone gave you a conclusion without any premises. How did that feel?",
            ],
            "next_suggestion": (
                "Next, practice spotting premises and conclusions in your own questions and in short passages."
            ),
        },
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.SCHOOL_SECONDARY,
    )

@router.get(
    "/k8/logic-seeds",
    response_model=PhilosophyLesson,
)
async def philosophy_k8_logic_seeds() -> PhilosophyLesson:
    """
    K–8 Lane: Logic & Critical Thinking Seeds.

    Focus: noticing 'This is what I think' vs 'This is why I think it',
    and seeing that some reasons are weak (name-calling, 'everyone does it',
    'because I said so').
    """
    return PhilosophyLesson(
        id="philo.k8.logic-seeds",
        subject=SubjectId.PHILOSOPHY_CORE,
        title="Logic Seeds: Reasons and Conclusions",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.EARLY,
        description=(
            "An early logic lane that helps you notice the difference "
            "between what you think and why you think it, and shows "
            "why some reasons are weak."
        ),
        content={
            "spine_position": (
                "K–8 seed for all later logic. "
                "Begins as noticing 'I think' vs 'I think... because', "
                "becomes informal logic and fallacies in high school, "
                "and formal logic in university (propositional/predicate), "
                "with advanced logics at graduate level."
            ),
            "prepares_for": [
                "Ethics (reasons for right and wrong).",
                "Metaphysics (reasons about what is real).",
                "Epistemology (reasons for what we know).",
                "Political philosophy (reasons about justice and power).",
                "Law, debate, media literacy, and scientific reasoning.",
            ],
            "kid_core_explanations": [
                "An argument is not a fight. It is when someone tells you what they think and gives a reason.",
                "A conclusion is what someone wants you to believe. A reason is why they say it.",
                "Sometimes people say things that sound strong but are not real reasons, "
                "like calling names or just saying 'everyone does it'.",
            ],
            "key_concepts": [
                "This is what I think vs this is why I think it.",
                "Conclusion (what you want someone to believe).",
                "Reason (why you say the conclusion is true).",
                "Name-calling instead of reasons (attacking the person).",
                "'Everyone does it' as a weak reason (popularity, not proof).",
                "'Because I said so' as an appeal to authority without support.",
            ],
            "micro_activities": [
                {
                    "name": "spot_reason_vs_conclusion",
                    "prompt": (
                        "Listen: 'You should wear a helmet because it keeps your head safe.' "
                        "Which part is the reason? Which part is the conclusion?"
                    ),
                    "expected_pattern": (
                        "Reason: 'it keeps your head safe'. "
                        "Conclusion: 'you should wear a helmet'."
                    ),
                },
                {
                    "name": "is_that_a_reason_name_calling",
                    "prompt": (
                        "Your friend says: 'You’re stupid if you don’t like my favorite game.' "
                        "Is that a reason for thinking the game is good, or just name-calling?"
                    ),
                    "expected_pattern": "This is name-calling, not a real reason.",
                },
                {
                    "name": "everyone_does_it",
                    "prompt": (
                        "Someone says: 'Everyone in my class cheats, so it’s okay.' "
                        "Does 'everyone does it' really show it is okay, or is that a weak reason?"
                    ),
                    "expected_pattern": (
                        "It is a weak reason: many people doing something does not make it right."
                    ),
                },
            ],
            "guided_questions": [
                "Can you tell me something you believe, and one reason you have for it?",
                "Think of a time someone tried to convince you of something. What did they say as a reason?",
                "When someone calls names instead of giving reasons, how does that feel? Does it help you understand?",
            ],
            "prime_internal_stance": {
                "proto_argument_template": "I think ___ because ___.",
                "silent_questions": [
                    "What is their conclusion here?",
                    "What (if anything) are they treating as a reason?",
                    "Is this more like 'I feel' or 'I think... because...'? ",
                ],
                "pattern_labels": [
                    "Attacking the person vs giving a reason.",
                    "'Everyone does it' as popularity, not proof.",
                    "'Because I said so' as unsupported authority.",
                ],
            },
            "prime_eq_style": {
                "tone": "calm, curious, non-judgmental",
                "moves": [
                    "Ask the child first before explaining.",
                    "Reflect their answer back in slightly clearer language.",
                    "Offer gentle corrections ('Good catch...', 'One more thing to notice is...').",
                    "Use very short examples (1–2 sentences).",
                    "Start with either/or questions ('reason or conclusion?') before asking 'why?'.",
                ],
                "templates": [
                    "Try this: 'I think ___ because ___'. Can you fill it in with your own belief and reason?",
                ],
            },
            "reflection_prompts": [
                "Today, notice one time when someone gives a conclusion without a reason. How did that feel?",
                "Try saying one of your beliefs to someone else using 'I think ___ because ___'. How did it change the conversation?",
            ],
            "next_suggestion": (
                "Next, you can explore simple ideas about fairness and kindness in everyday stories, "
                "and practice giving reasons for why something feels fair or unfair."
            ),
        },
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.SCHOOL_FOUNDATION,
    )

@router.get(
    "/k8/methods-m1",
    response_model=MethodsConceptLesson,
)
async def philosophy_methods_m1_concept() -> MethodsConceptLesson:
    """
    Placeholder: methods M1 concept lesson.
    Currently returns a generic 'Reading Philosophy Carefully' concept.
    """
    # You can adjust to pull a real MethodsConceptLesson from a registry later.
    return MethodsConceptLesson(
        id="methods.m1.readingphilosophy",
        concept=MethodsConcept(
            id=MethodsConceptId.READINGPHILOSOPHY,
            name="Reading Philosophy Carefully",
            workingdefinition="Learning how to read philosophical texts slowly, with attention to structure.",
            notes=[],
        ),
        subject=SubjectId.PHILOSOPHYCORE,
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.SCHOOLSECONDARY,
        professorview=None,
        gradview=None,
        teacherview=None,
        practice=None,
    )


@router.get(
    "/k8/metaphysics-b1",
    response_model=MetaphysicsConceptLesson,
)
async def philosophy_metaphysics_b1_concept() -> MetaphysicsConceptLesson:
    """
    Placeholder: metaphysics B1 concept lesson.
    Currently returns a generic 'Being and Existence' concept.
    """
    return MetaphysicsConceptLesson(
        id="metaphysics.b1.beingexistence",
        concept=MetaphysicsConcept(
            id=MetaphysicsConceptId.BEINGEXISTENCE,
            name="Being and Existence",
            workingdefinition="Basic questions about what it means for something to exist.",
            notes=[],
        ),
        subject=SubjectId.PHILOSOPHYCORE,
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.SCHOOLSECONDARY,
        professorview=None,
        gradview=None,
        teacherview=None,
        practice=None,
    )

@router.get(
    "/k8/ethics-values",
    response_model=PhilosophyLesson,
)
async def philosophy_k8_ethics_values() -> PhilosophyLesson:
    """
    K–8 Lane: Ethics & Values Seeds.

    Focus: fairness vs unfairness, harm vs help, promises, honesty,
    kindness, and responsibility in everyday situations.
    """
    return PhilosophyLesson(
        id="philo.k8.ethics-values",
        subject=SubjectId.PHILOSOPHY_CORE,
        title="Ethics Seeds: Fairness, Promises, and Honesty",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.EARLY,
        description=(
            "An early ethics lane that helps you notice fairness and harm, "
            "why promises and honesty matter, and how kindness and "
            "responsibility affect other people."
        ),
        content={
            # Genius professor view: where this sits in the ethics spine
            "spine_position": (
                "Begins in K–8 as feelings about fair vs unfair, hurt vs help, "
                "and keeping promises; becomes structured normative ethics in "
                "high school and undergrad (consequences, rules, virtues, care); "
                "and deepens into metaethics and applied ethics at grad level."
            ),
            "prepares_for": [
                "Normative ethics (consequentialism, deontology, virtue, care).",
                "Political philosophy (justice, rights, equality, power).",
                "Applied ethics (digital life, AI, environment, health).",
                "Character education and social-emotional learning.",
            ],

            # Patient teacher: kid-level anchor explanations
            "kid_core_explanations": [
                "Fairness is about treating people in a way that makes sense and does not leave someone hurt for no good reason.",
                "Harm is when someone gets hurt in their body or feelings; help is when we make things better or kinder for them.",
                "A promise is when you tell someone you will do something. Being honest means telling the truth and trying to do what you said.",
            ],

            # Key concepts seeded here
            "key_concepts": [
                "Fair vs unfair in sharing, turn-taking, and rules.",
                "Harm vs help: how actions affect others, not just yourself.",
                "Promises and trust: people rely on what you say.",
                "Honesty as more than 'not lying'—also owning up to mistakes.",
                "Kindness and responsibility as everyday ways to care.",
            ],

            # Micro-stories and "Was this fair? Why or why not?" prompts
            "micro_stories": [
                {
                    "name": "sharing_snacks",
                    "story": (
                        "Three friends bring snacks to share. Two of them give snacks to everyone, "
                        "but one keeps all of theirs and says, 'It’s mine, I don’t have to share.'"
                    ),
                    "questions": [
                        "Does this feel fair or unfair? Why?",
                        "How might the other friends feel?",
                        "What could the friend do differently to be more fair or kind?",
                    ],
                },
                {
                    "name": "test_answer",
                    "story": (
                        "You see a classmate looking at someone else’s paper during a test. "
                        "They later say, 'It’s not a big deal, everyone cheats sometimes.'"
                    ),
                    "questions": [
                        "Is 'everyone does it' a good reason here?",
                        "Who could be harmed by this choice?",
                        "What would an honest and fair choice look like in this situation?",
                    ],
                },
                {
                    "name": "broken_promise",
                    "story": (
                        "You promised a friend you would help them with a project after school, "
                        "but when the time comes you decide to play a game instead and never tell them."
                    ),
                    "questions": [
                        "How might your friend feel when you do not show up?",
                        "Does breaking this promise affect how much they trust you?",
                        "What could you do or say to repair the situation?",
                    ],
                },
            ],

            # Guided questions for the learner
            "guided_questions": [
                "Think of a time something felt unfair to you. What happened, and why did it feel unfair?",
                "Think of a time you kept a promise, even when it was hard. How did that feel afterward?",
                "When you tell the truth about a mistake, what happens to trust between you and other people?",
            ],

            # PRIME's internal stance (grad-student style)
            "prime_internal_stance": {
                "silent_questions": [
                    "Who is helped and who is hurt in this story?",
                    "What promises or expectations are in the background here?",
                    "Is the child focusing only on rules, only on feelings, or on both?",
                ],
                "pattern_labels": [
                    "Appeal to 'everyone does it' as a weak reason.",
                    "Short-term gain vs long-term trust.",
                    "Special obligations to friends, family, or teammates.",
                ],
            },

            # PRIME EQ style in this lane
            "prime_eq_style": {
                "tone": "calm, caring, non-judgmental",
                "moves": [
                    "Acknowledge feelings before analyzing fairness.",
                    "Ask the child what matters most to them in the story.",
                    "Reflect their answer in simple language to show understanding.",
                    "Offer gentle questions instead of harsh judgments.",
                ],
                "templates": [
                    "It sounds like this felt {emotion} for you. What part made it feel that way?",
                    "If you imagine being the other person in the story, how might it feel?",
                ],
            },

            # Reflection prompts: building ethical awareness
            "reflection_prompts": [
                "Today, notice one small choice where you could either help or harm someone’s feelings. What did you choose, and why?",
                "Think of one promise you want to keep this week. What can you do to make it easier to keep that promise?",
            ],

            # Next step in the K–8 ethics spine
            "next_suggestion": (
                "Next, you can explore simple digital-life dilemmas—like sharing passwords, posting pictures, "
                "or including others in group chats—and ask what is fair and kind there."
            ),
        },
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.SCHOOL_FOUNDATION,
    )

@router.get(
    "/k8/mind-self",
    response_model=PhilosophyLesson,
)
async def philosophy_k8_mind_self() -> PhilosophyLesson:
    """
    K–8 Lane: Philosophy of Mind & Self Seeds.

    Focus: thoughts, feelings, dreams, imagination, and early questions about
    what makes you "you" over time.
    """
    return PhilosophyLesson(
        id="philo.k8.mind-self",
        subject=SubjectId.PHILOSOPHY_CORE,
        title="Mind Seeds: Thoughts, Feelings, and You",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.EARLY,
        description=(
            "An early mind-and-self lane that helps you notice thoughts, feelings, "
            "dreams, imagination, and what makes you feel like the same person over time."
        ),
        content={
            # Spine / professor view
            "spine_position": (
                "Begins in K–8 as questions about thoughts, feelings, and 'me'; "
                "becomes philosophy of mind and personal identity in high school and undergrad; "
                "connects to cognitive science and consciousness studies at advanced levels."
            ),
            "prepares_for": [
                "Philosophy of mind and cognitive science.",
                "Metaphysics of personal identity and time.",
                "Moral psychology and responsibility.",
                "Psychology and social-emotional learning.",
            ],

            # Kid-level core explanations
            "kid_core_explanations": [
                "Your mind holds your thoughts, feelings, memories, and daydreams.",
                "Feelings (like happy, sad, angry, excited) are part of you, but they can change.",
                "You stay 'you' even as you grow and change, but people can disagree about what makes you the same person.",
            ],

            # Key concepts seeded here
            "key_concepts": [
                "Thoughts vs feelings (thinking something vs feeling something).",
                "Dreams and imagination as mind activity, not 'fake' or 'real' in the same way as chairs and tables.",
                "Memories as part of how you think of yourself.",
                "Body changes vs feeling like 'the same me' over time.",
            ],

            # Micro-stories / questions
            "micro_questions": [
                {
                    "name": "different_feelings",
                    "prompt": (
                        "Think about a time you felt very angry and a time you felt very calm. "
                        "Were you still the same 'you' in both moments? What was different and what was the same?"
                    ),
                },
                {
                    "name": "old_memory",
                    "prompt": (
                        "Remember something from when you were much younger. "
                        "Does it feel like it happened to 'you', even though you are different now? Why?"
                    ),
                },
                {
                    "name": "dream_vs_real",
                    "prompt": (
                        "Think of a dream that felt very real. "
                        "How did you know it was a dream when you woke up? What changed?"
                    ),
                },
            ],

            # Guided questions for the learner
            "guided_questions": [
                "When you say 'I', what do you usually mean—your body, your thoughts, your feelings, or something else?",
                "Have you ever felt two different feelings at the same time (for example, excited and nervous)? What was that like?",
                "If your body changes a lot as you grow, what makes you feel like the same person inside?",
            ],

            # PRIME's internal stance (grad-style)
            "prime_internal_stance": {
                "silent_questions": [
                    "Is the child talking more about thoughts, feelings, body, or memories?",
                    "Are they raising a personal identity question (same person over time) or a mind–world question (real vs dream)?",
                    "Which cultural or family ideas about self might be shaping this?",
                ],
                "pattern_labels": [
                    "Mind vs body focus.",
                    "Memory-based sense of self.",
                    "Feeling-based vs story-based self-descriptions.",
                ],
            },

            # PRIME EQ style in this lane
            "prime_eq_style": {
                "tone": "curious, gentle, non-intrusive",
                "moves": [
                    "Normalize all feelings as acceptable to talk about.",
                    "Avoid asking for details that feel too private; invite, don't push.",
                    "Reflect the child's way of talking about 'me' before introducing new terms.",
                ],
                "templates": [
                    "It makes sense that feeling {emotion} changed how you saw things. What stayed the same about you?",
                    "You described your memory in a very clear way. How does remembering it make you feel now?",
                ],
            },

            # Reflection prompts
            "reflection_prompts": [
                "Today, notice one time when your feeling changes but you still feel like the same 'you'. What happened?",
                "Think of one memory that feels important to who you are. Why do you think it matters so much?",
            ],

            # Next step
            "next_suggestion": (
                "Next, you can explore simple questions about 'mind and body'—for example, "
                "how thoughts, feelings, and actions connect—and how that matters for responsibility."
            ),
        },
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.SCHOOL_FOUNDATION,
    )

@router.get(
    "/k8/world-reality",
    response_model=PhilosophyLesson,
)
async def philosophy_k8_world_reality() -> PhilosophyLesson:
    """
    K–8 metaphysics / 'big world' lane:
    Reality, time, space, existence, and possibility.
    """
    return PhilosophyLesson(
        id="philo.k8.world-reality",
        subject="philosophy_core",
        title="World Seeds: Reality, Time, and Possibility",
        kind="concept",
        difficulty="early",
        description=(
            "An early metaphysics lane that helps you wonder about what is real, "
            "where things are, how time works, and whether things could have been different."
        ),
        content={
            "spine_position": (
                "Begins in K–8 as questions about what is real, where things are, "
                "and why the world is this way; becomes metaphysics and philosophy of time "
                "in high school and undergrad; connects to cosmology and philosophy of physics "
                "at advanced levels."
            ),
            "prepares_for": [
                "Metaphysics of reality, objects, and properties.",
                "Philosophy of time, space, and possibility.",
                "Cosmology and questions about the universe.",
                "Modal reasoning about what could or must be.",
            ],
            "kid_core_explanations": [
                "Some things are really there in the world, and some things are only in stories or in your mind.",
                "Time is how we talk about things happening earlier and later, but people disagree about what time really is.",
                "The world is one way, but we can imagine it being different, and that helps us think about what is possible.",
            ],
            "key_concepts": [
                "Real vs pretend (what is really there vs what is only in stories or imagination).",
                "Past, present, and future as ways of talking about time.",
                "Space as 'where things are' and how things can be in different places.",
                "Possibility: what could have happened, and what could never happen.",
            ],
            "micro_questions": [
                {
                    "name": "real_or_story",
                    "prompt": (
                        "Think of a dragon from a story and a dog you know in real life. "
                        "In what ways is the dragon 'real' and in what ways is it not?"
                    ),
                },
                {
                    "name": "time_change",
                    "prompt": (
                        "Think about your room yesterday and your room today. "
                        "What changed and what stayed the same? "
                        "Does it feel like yesterday is still 'somewhere'?"
                    ),
                },
                {
                    "name": "could_it_be_different",
                    "prompt": (
                        "Imagine if it never got dark and the sun never went down. "
                        "Could our world really be like that? Why or why not?"
                    ),
                },
            ],
            "guided_questions": [
                "When you say something is 'real', what do you usually mean?",
                "Have you ever had a dream or story that felt almost real? What made it feel that way?",
                "Can you think of something that used to be impossible for you but is possible now?",
            ],
            "prime_internal_stance": {
                "silent_questions": [
                    "Is the child talking more about objects, time, space, or possibility?",
                    "Are they raising a question about what exists, or about how the world could be different?",
                    "Which cultural or family ideas about reality (for example, spiritual or religious beliefs) might be shaping this?",
                ],
                "pattern_labels": [
                    "Concrete vs abstract sense of reality.",
                    "Time-as-story vs time-as-thing.",
                    "Imagination-rich vs rule-focused talk about possibility.",
                ],
            },
            "prime_eq_style": {
                "tone": "curious, steady, non-dismissive",
                "moves": [
                    "Treat big-world questions as serious, not silly.",
                    "Avoid quickly correcting what is 'really real'; first invite the child's own picture.",
                    "Use examples from the child's everyday world before using big cosmic examples.",
                ],
                "templates": [
                    "That is a big question about what is really real. When you picture it, what do you see in your mind?",
                    "You imagined a different way the world could be. What would be the same and what would change?",
                ],
            },
            "reflection_prompts": [
                "Today, notice one time when you wonder whether something is real or pretend. What made you wonder?",
                "Think of one way the world could have been different. How do you know it is not that way?",
            ],
            "next_suggestion": (
                "Next, you can explore questions about 'what things are made of' and 'why there is something rather than nothing,' "
                "moving toward more advanced metaphysics and cosmology."
            ),
        },
        domain="humanities",
        level="school_foundation",
    )

@router.post(
    "/k8/world-reality/practice",
    response_model=K8WorldPracticeResponse,
)
async def philosophy_k8_world_reality_practice(
    request: K8WorldPracticeRequest,
) -> K8WorldPracticeResponse:
    """
    K–8 practice for the world/reality lane.

    Takes a kid's big-world question and returns:
    - a simple tag (time, existence, space, possibility, other)
    - a short explanation
    - 3–4 gentle follow-up prompts
    """
    text = (request.question_text or "").strip()
    lowered = text.lower()

    # Simple keyword-based tagging
    time_keywords = [
        "time", "past", "future", "always", "forever", "never", "before", "after",
        "beginning", "end", "start", "eternal", "age", "old", "young",
    ]
    existence_keywords = [
        "exist", "exists", "existence", "real", "really real", "nothing", "nothingness",
        "something", "why is there something", "god", "soul", "spirit",
    ]
    space_keywords = [
        "space", "universe", "world", "planet", "galaxy", "stars", "black hole",
        "where", "far away", "infinite", "edge of the universe",
    ]
    possibility_keywords = [
        "possible", "could have", "could be", "could be different", "imagine if",
        "what if", "another world", "alternate", "multiverse",
    ]

    primary_tag = K8WorldQuestionTag.OTHER
    secondary_tags: List[K8WorldQuestionTag] = []

    def has_any(keywords: List[str]) -> bool:
        return any(word in lowered for word in keywords)

    # Determine tags
    if has_any(time_keywords):
        primary_tag = K8WorldQuestionTag.TIME
    if has_any(existence_keywords):
        if primary_tag == K8WorldQuestionTag.OTHER:
            primary_tag = K8WorldQuestionTag.EXISTENCE
        else:
            secondary_tags.append(K8WorldQuestionTag.EXISTENCE)
    if has_any(space_keywords):
        if primary_tag == K8WorldQuestionTag.OTHER:
            primary_tag = K8WorldQuestionTag.SPACE
        else:
            secondary_tags.append(K8WorldQuestionTag.SPACE)
    if has_any(possibility_keywords):
        if primary_tag == K8WorldQuestionTag.OTHER:
            primary_tag = K8WorldQuestionTag.POSSIBILITY
        else:
            secondary_tags.append(K8WorldQuestionTag.POSSIBILITY)

    # Build explanation
    if primary_tag == K8WorldQuestionTag.TIME:
        explanation = (
            "This question is mostly about time: when things begin or end, "
            "and how past, present, and future fit together."
        )
        follow_ups = [
            "When you think about the beginning or end you are asking about, what picture comes to your mind?",
            "Does it feel like the past is still 'somewhere', or does it feel like it is completely gone?",
            "If time had no beginning, how does that make you feel? If it had a beginning, how does that feel different?",
            "Is there anything in your own life that feels very long or very short, even if the clock says the same amount of time?",
        ]
    elif primary_tag == K8WorldQuestionTag.EXISTENCE:
        explanation = (
            "This question is mostly about existence: what is really there, "
            "and why there is something instead of nothing."
        )
        follow_ups = [
            "When you say something is 'real', what do you usually mean?",
            "Can you think of something that felt real in a dream or story? What changed when you woke up?",
            "If there were truly 'nothing at all', what do you picture that would be like?",
            "Does it feel different to think about people existing and things like numbers or stories existing?",
        ]
    elif primary_tag == K8WorldQuestionTag.SPACE:
        explanation = (
            "This question is mostly about space: where things are, how far they can go, "
            "and whether there is an edge or an outside to everything."
        )
        follow_ups = [
            "When you imagine the universe, do you see an edge or does it go on forever?",
            "If there were an edge to everything, what do you picture being beyond that edge?",
            "Can you think of a time when something looked very small but was actually very far away?",
            "How does it feel to think about distances that are too big to walk or even fly?",
        ]
    elif primary_tag == K8WorldQuestionTag.POSSIBILITY:
        explanation = (
            "This question is mostly about possibility: how the world could have been different, "
            "and what makes some things possible or impossible."
        )
        follow_ups = [
            "Imagine the world a little different in the way you are wondering about. What stays the same and what changes?",
            "Do you think there are rules that decide what is possible and what is not? What might some of those rules be?",
            "Can you think of something that used to feel impossible to you but now feels possible?",
            "Does imagining other possibilities make you feel excited, confused, or something else?",
        ]
    else:
        explanation = (
            "This question touches on big-world ideas but does not fit neatly into just time, "
            "existence, space, or possibility. That is okay—many questions mix all of them."
        )
        follow_ups = [
            "Which part of your question feels most important to you right now?",
            "Does your question feel more about when things happen, what is real, where things are, or what could be?",
            "Is there a story, movie, or game that makes you think about this question?",
            "If you could get one clear answer about this question, what would you want it to be about?",
        ]

    return K8WorldPracticeResponse(
        original_question=text,
        primary_tag=primary_tag,
        secondary_tags=secondary_tags,
        explanation=explanation,
        follow_up_prompts=follow_ups,
    )

@router.post(
    "/k8/mind-self/practice",
    response_model=K8MindPracticeResponse,
)
async def philosophy_k8_mind_self_practice(
    request: K8MindPracticeRequest,
) -> K8MindPracticeResponse:
    """
    K–8 practice for the mind/self lane.

    Tags a question as mainly about feelings, memory, or identity,
    and returns 3–4 gentle follow-up prompts.
    """
    text = (request.question_text or "").strip()
    lowered = text.lower()

    feelings_keywords = [
        "feel", "feeling", "feelings", "emotion", "emotions",
        "angry", "mad", "sad", "happy", "excited", "nervous",
        "scared", "afraid", "worried", "upset", "mood",
    ]
    memory_keywords = [
        "remember", "memory", "memories", "forget", "forgot",
        "past", "when i was little", "used to", "long time ago",
    ]
    identity_keywords = [
        "who i am", "who am i", "myself", "me", "same person",
        "different person", "change", "changed", "personality",
        "identity",
    ]

    primary_tag = K8MindQuestionTag.OTHER
    secondary_tags: list[K8MindQuestionTag] = []

    def has_any(keywords: list[str]) -> bool:
        return any(word in lowered for word in keywords)

    if has_any(feelings_keywords):
        primary_tag = K8MindQuestionTag.FEELINGS
    if has_any(memory_keywords):
        if primary_tag == K8MindQuestionTag.OTHER:
            primary_tag = K8MindQuestionTag.MEMORY
        else:
            secondary_tags.append(K8MindQuestionTag.MEMORY)
    if has_any(identity_keywords):
        if primary_tag == K8MindQuestionTag.OTHER:
            primary_tag = K8MindQuestionTag.IDENTITY
        else:
            secondary_tags.append(K8MindQuestionTag.IDENTITY)

    if primary_tag == K8MindQuestionTag.FEELINGS:
        explanation = (
            "This question is mostly about feelings: how emotions show up, "
            "change, and affect how you see yourself and the world."
        )
        follow_ups = [
            "When you feel the way you are asking about, where do you notice it most in your body?",
            "Does this feeling stay the same, or does it come and go in waves?",
            "Can you remember a time when you felt this way and then it changed? What helped it change?",
            "How does this feeling affect the way you see yourself or other people in that moment?",
        ]
    elif primary_tag == K8MindQuestionTag.MEMORY:
        explanation = (
            "This question is mostly about memory: how past events stay with you, "
            "and how remembering them changes how you feel and who you think you are."
        )
        follow_ups = [
            "When you remember the thing you are asking about, what is the clearest part of the memory?",
            "Does remembering it feel the same every time, or does the feeling change?",
            "Does this memory make you feel more like the same person over time, or more different?",
            "If you could talk to your past self in that memory, what would you want to say?",
        ]
    elif primary_tag == K8MindQuestionTag.IDENTITY:
        explanation = (
            "This question is mostly about identity: what makes you feel like 'you' "
            "even when your feelings, body, or situation change."
        )
        follow_ups = [
            "When you say 'me', what is the first thing you think of: your body, your thoughts, your feelings, or something else?",
            "Can you think of one thing about you that has stayed the same for a long time?",
            "Can you think of one thing about you that has changed a lot?",
            "Does feeling like a 'different person' in some moments scare you, interest you, or something else?",
        ]
    else:
        explanation = (
            "This question touches your inner world in a way that mixes feelings, "
            "memories, and identity. That is normal—many mind questions do."
        )
        follow_ups = [
            "Which part of this feels biggest to you right now: the feelings, the memory, or who you are?",
            "If your question were a picture or a short scene, what would it look like?",
            "Is there someone you trust that you would want to share this question with?",
            "What would you like to understand better about yourself from this question?",
        ]

    return K8MindPracticeResponse(
        original_question=text,
        primary_tag=primary_tag,
        secondary_tags=secondary_tags,
        explanation=explanation,
        follow_up_prompts=follow_ups,
    )

@router.post(
    "/k8/mind-self/planner",
    response_model=K8MindPlannerResponse,
)
async def philosophy_k8_mind_self_planner(
    request: K8MindPlannerRequest,
) -> K8MindPlannerResponse:
    """
    K–8 mind/self planner.

    Returns both:
    - the mind/self lesson
    - the mind practice response (feelings/memory/identity tags)
    """
    lesson = await philosophy_k8_mind_self()
    practice_req = K8MindPracticeRequest(question_text=request.question_text)
    practice_resp = await philosophy_k8_mind_self_practice(practice_req)

    return K8MindPlannerResponse(
        original_question=request.question_text,
        lesson=lesson.model_dump(),
        practice=practice_resp,
    )

@router.post(
    "/k8/world-reality/planner",
    response_model=K8WorldPlannerResponse,
)
async def philosophy_k8_world_reality_planner(
    request: K8WorldPlannerRequest,
) -> K8WorldPlannerResponse:
    """
    K–8 big world planner.

    Returns both:
    - the world/reality lesson
    - the world practice response (with time/existence/space/possibility tags)
    """
    lesson = await philosophy_k8_world_reality()
    practice_req = K8WorldPracticeRequest(question_text=request.question_text)
    practice_resp = await philosophy_k8_world_reality_practice(practice_req)

    return K8WorldPlannerResponse(
        original_question=request.question_text,
        lesson=lesson.model_dump(),
        practice=practice_resp,
    )

@router.get(
    "/k8/world-reality",
    response_model=PhilosophyLesson,
)
async def philosophy_k8_world_reality() -> PhilosophyLesson:
    """
    K–8 metaphysics / 'big world' lane:
    Reality, time, space, existence, and possibility.
    """
    return PhilosophyLesson(
        id="philo.k8.world-reality",
        subject="philosophy_core",
        title="World Seeds: Reality, Time, and Possibility",
        kind="concept",
        difficulty="early",
        description=(
            "An early metaphysics lane that helps you wonder about what is real, "
            "where things are, how time works, and whether things could have been different."
        ),
        content={
            "spine_position": (
                "Begins in K–8 as questions about what is real, where things are, "
                "and why the world is this way; becomes metaphysics and philosophy of time "
                "in high school and undergrad; connects to cosmology and philosophy of physics "
                "at advanced levels."
            ),
            "prepares_for": [
                "Metaphysics of reality, objects, and properties.",
                "Philosophy of time, space, and possibility.",
                "Cosmology and questions about the universe.",
                "Modal reasoning about what could or must be.",
            ],
            "kid_core_explanations": [
                "Some things are really there in the world, and some things are only in stories or in your mind.",
                "Time is how we talk about things happening earlier and later, but people disagree about what time really is.",
                "The world is one way, but we can imagine it being different, and that helps us think about what is possible.",
            ],
            "key_concepts": [
                "Real vs pretend (what is really there vs what is only in stories or imagination).",
                "Past, present, and future as ways of talking about time.",
                "Space as 'where things are' and how things can be in different places.",
                "Possibility: what could have happened, and what could never happen.",
            ],
            "micro_questions": [
                {
                    "name": "real_or_story",
                    "prompt": (
                        "Think of a dragon from a story and a dog you know in real life. "
                        "In what ways is the dragon 'real' and in what ways is it not?"
                    ),
                },
                {
                    "name": "time_change",
                    "prompt": (
                        "Think about your room yesterday and your room today. "
                        "What changed and what stayed the same? "
                        "Does it feel like yesterday is still 'somewhere'?"
                    ),
                },
                {
                    "name": "could_it_be_different",
                    "prompt": (
                        "Imagine if it never got dark and the sun never went down. "
                        "Could our world really be like that? Why or why not?"
                    ),
                },
            ],
            "guided_questions": [
                "When you say something is 'real', what do you usually mean?",
                "Have you ever had a dream or story that felt almost real? What made it feel that way?",
                "Can you think of something that used to be impossible for you but is possible now?",
            ],
            "prime_internal_stance": {
                "silent_questions": [
                    "Is the child talking more about objects, time, space, or possibility?",
                    "Are they raising a question about what exists, or about how the world could be different?",
                    "Which cultural or family ideas about reality (for example, spiritual or religious beliefs) might be shaping this?",
                ],
                "pattern_labels": [
                    "Concrete vs abstract sense of reality.",
                    "Time-as-story vs time-as-thing.",
                    "Imagination-rich vs rule-focused talk about possibility.",
                ],
            },
            "prime_eq_style": {
                "tone": "curious, steady, non-dismissive",
                "moves": [
                    "Treat big-world questions as serious, not silly.",
                    "Avoid quickly correcting what is 'really real'; first invite the child's own picture.",
                    "Use examples from the child's everyday world before using big cosmic examples.",
                ],
                "templates": [
                    "That is a big question about what is really real. When you picture it, what do you see in your mind?",
                    "You imagined a different way the world could be. What would be the same and what would change?",
                ],
            },
            "reflection_prompts": [
                "Today, notice one time when you wonder whether something is real or pretend. What made you wonder?",
                "Think of one way the world could have been different. How do you know it is not that way?",
            ],
            "next_suggestion": (
                "Next, you can explore questions about 'what things are made of' and 'why there is something rather than nothing,' "
                "moving toward more advanced metaphysics and cosmology."
            ),
        },
        domain="humanities",
        level="school_foundation",
    )

@router.post(
    "/k8/planner",
    response_model=K8PhilosophyPlannerResponse,
)
async def philosophy_k8_planner(
    request: K8PhilosophyPlannerRequest,
) -> K8PhilosophyPlannerResponse:
    """
    K–8 Philosophy for Kids planner.

    Takes a child's free-form question and routes to:
    - Logic seeds (reasons vs conclusions, 'everyone does it')
    - Ethics & values (fair/unfair, harm/help, promises, honesty)
    - Mind & self (thoughts, feelings, dreams, 'what makes me me')
    """
    text = (request.question_text or "").strip()
    lowered = text.lower()

    world_keywords = [
        "real", "really real", "reality", "exist", "existence", "exists",
        "pretend", "imaginary", "made up",
        "time", "past", "future", "forever", "always been",
        "space", "universe", "world", "planet", "galaxy",
        "nothing", "nothingness", "why is there something",
        "possible", "could have", "could be different",
    ]

    # Default lane and lesson: if we can't tell, start with mind/self
    chosen_lane = K8PhilosophyLane.MIND
    lesson_id = "philo.k8.mind-self"
    lesson_title = "Mind Seeds: Thoughts, Feelings, and You"
    reason = (
        "This sounds like a question about how you feel or how you see yourself, "
        "so we'll start with the mind-and-self lane."
    )
    starter_prompt = (
        "I hear that you are wondering about yourself and your inner world. "
        "Let's start by noticing your thoughts and feelings about this. "
        "Can you tell me a bit more about what is on your mind?"
    )

    world_practice = None
    mind_practice = None

    # Heuristics for ETHICS: fairness, right/wrong, promises, honesty, harm/help
    ethics_keywords = [
        "fair", "unfair", "share", "sharing", "cheat", "cheating",
        "lie", "lying", "honest", "honesty", "promise", "promises",
        "mean", "kind", "bully", "bullying", "hurt", "harm", "rule", "rules",
    ]

    # Heuristics for WORLD / METAPHYSICS: reality, time, space, existence, possibility
    world_keywords = [
        "real", "really real", "reality", "exist", "existence", "exists",
        "pretend", "imaginary", "made up",
        "time", "past", "future", "forever", "always been",
        "space", "universe", "world", "planet", "galaxy",
        "nothing", "nothingness", "why is there something",
        "possible", "could have", "could be different",
        "start of the universe", "big bang",
    ]

    # Heuristics for LOGIC: reasons, arguments, evidence, 'everyone does it'
    logic_keywords = [
        "because", "reason", "reasons", "argue", "argument",
        "evidence", "proof", "prove", "why is that true",
        "everyone does it", "all my friends", "nobody", "always", "never",
    ]

    # 1) ETHICS
    if any(word in lowered for word in ethics_keywords):
        chosen_lane = K8PhilosophyLane.ETHICS
        lesson_id = "philo.k8.ethics-values"
        lesson_title = "Ethics Seeds: Fairness, Promises, and Honesty"
        reason = (
            "Your question sounds like it is about fairness, harm, promises, "
            "or kindness, so we'll start in the ethics-and-values lane."
        )
        starter_prompt = (
            "This is a really important question about what is fair or right. "
            "Let's look at who might be helped or hurt. "
            "Can you tell me what happened and why it feels fair or unfair to you?"
        )

    # 2) WORLD / METAPHYSICS
    elif any(word in lowered for word in world_keywords):
        chosen_lane = K8PhilosophyLane.WORLD
        lesson_id = "philo.k8.world-reality"
        lesson_title = "World Seeds: Reality, Time, and Possibility"
        reason = (
            "Your question sounds like it is about what is real, how the world is, "
            "or how things could be different, so we'll start in the world-and-reality lane."
        )
        starter_prompt = (
            "You are asking a big question about what the world is really like. "
            "Let's start by noticing what feels real to you and what feels like 'just a story.' "
            "Can you tell me what you picture when you think about this question?"
        )

    # 3) LOGIC
    elif any(word in lowered for word in logic_keywords):
        chosen_lane = K8PhilosophyLane.LOGIC
        lesson_id = "philo.k8.logic-seeds"
        lesson_title = "Logic Seeds: Reasons and Conclusions"
        reason = (
            "Your question sounds like it is about reasons and conclusions, "
            "so we'll start in the logic lane."
        )
        starter_prompt = (
            "It sounds like you are wondering about reasons and whether a claim makes sense. "
            "Let's try the pattern 'I think ___ because ___.' "
            "What do you think, and what is one reason you have for it?"
        )

    # If nothing matched, we stay with the mind/self default set above.

    # Optionally attach lane-specific practice for mind or world
    if request.include_lane_practice:
        if chosen_lane == K8PhilosophyLane.WORLD:
            world_practice = await philosophy_k8_world_reality_practice(
                K8WorldPracticeRequest(question_text=text)
            )
        elif chosen_lane == K8PhilosophyLane.MIND:
            mind_practice = await philosophy_k8_mind_self_practice(
                K8MindPracticeRequest(question_text=text)
            )

    return K8PhilosophyPlannerResponse(
        original_question=text,
        chosen_lane=chosen_lane,
        lesson_id=lesson_id,
        lesson_title=lesson_title,
        reason=reason,
        starter_prompt=starter_prompt,
        world_practice=world_practice,
        mind_practice=mind_practice,
    )


@router.post(
    "/k8/ethics-values/practice",
    response_model=K8EthicsPracticeResponse,
)
async def philosophy_k8_ethics_values_practice(
    request: K8EthicsPracticeRequest,
) -> K8EthicsPracticeResponse:
    """
    K–8 ethics practice: PRIME presents or recalls a micro-story and
    responds to the child's reflection in a calm, caring, non-judgmental way.
    """
    kind = request.story_kind
    answer = (request.answer_text or "").strip()

    if kind == K8EthicsStoryKind.SHARING_SNACKS:
        story = (
            "Three friends bring snacks to share. Two of them give snacks to everyone, "
            "but one keeps all of theirs and says, 'It’s mine, I don’t have to share.'"
        )
        if not answer:
            return K8EthicsPracticeResponse(
                story_kind=kind,
                story=story,
                child_answer=None,
                prime_paraphrase="I'll wait for you to tell me what you think first.",
                prime_feedback="",
                follow_up_question="Does this feel fair or unfair to you? Why?",
            )

        prime_paraphrase = f"You said: {answer}"
        prime_feedback = (
            "You are noticing how sharing (or not sharing) affects everyone. "
            "When one friend keeps everything, others may feel left out or hurt. "
            "Fairness here is not always 'exactly equal', but it does notice how people feel."
        )
        follow_up = "If you were the friend with extra snacks, what could you do to make this feel more fair or kind?"

        return K8EthicsPracticeResponse(
            story_kind=kind,
            story=story,
            child_answer=answer,
            prime_paraphrase=prime_paraphrase,
            prime_feedback=prime_feedback,
            follow_up_question=follow_up,
        )

    if kind == K8EthicsStoryKind.TEST_ANSWER:
        story = (
            "You see a classmate looking at someone else’s paper during a test. "
            "They later say, 'It’s not a big deal, everyone cheats sometimes.'"
        )
        if not answer:
            return K8EthicsPracticeResponse(
                story_kind=kind,
                story=story,
                child_answer=None,
                prime_paraphrase="I'll wait for your first thought.",
                prime_feedback="",
                follow_up_question="Is 'everyone does it' a good reason here? Why or why not?",
            )

        prime_paraphrase = f"You said: {answer}"
        prime_feedback = (
            "Saying 'everyone does it' is usually a weak reason. "
            "Even if many people cheat, it can still be unfair to those who worked honestly, "
            "and it can harm trust between students and teachers."
        )
        follow_up = "If you wanted to explain why cheating is not okay, what reason would you give?"

        return K8EthicsPracticeResponse(
            story_kind=kind,
            story=story,
            child_answer=answer,
            prime_paraphrase=prime_paraphrase,
            prime_feedback=prime_feedback,
            follow_up_question=follow_up,
        )

    # Default: BROKEN_PROMISE
    story = (
        "You promised a friend you would help them with a project after school, "
        "but when the time comes you decide to play a game instead and never tell them."
    )
    if not answer:
        return K8EthicsPracticeResponse(
            story_kind=K8EthicsStoryKind.BROKEN_PROMISE,
            story=story,
            child_answer=None,
            prime_paraphrase="I'll wait for you to share what you think first.",
            prime_feedback="",
            follow_up_question="How might your friend feel when you do not show up? Does this seem fair to them?",
        )

    prime_paraphrase = f"You said: {answer}"
    prime_feedback = (
        "Breaking a promise can hurt trust, even if you did not mean to be unkind. "
        "Not telling your friend can make the hurt stronger, because they are left wondering what happened."
    )
    follow_up = "What could you say or do now to repair trust with your friend?"

    return K8EthicsPracticeResponse(
        story_kind=K8EthicsStoryKind.BROKEN_PROMISE,
        story=story,
        child_answer=answer,
        prime_paraphrase=prime_paraphrase,
        prime_feedback=prime_feedback,
        follow_up_question=follow_up,
    )

@router.post(
    "/k8/ethics-values/planner",
    response_model=K8EthicsPlannerResponse,
)
async def philosophy_k8_ethics_values_planner(
    request: K8EthicsPlannerRequest,
) -> K8EthicsPlannerResponse:
    """
    K–8 ethics planner.

    Returns both:
    - the ethics & values lesson
    - an ethics practice response, using the question as free-form input
    """
    lesson = await philosophy_k8_ethics_values()

    # For now, route all free-form questions into the sharing/snacks story,
    # using the child's question as their answer_text.
    practice_req = K8EthicsPracticeRequest(
        story_kind=K8EthicsStoryKind.SHARING_SNACKS,
        answer_text=request.question_text,
    )
    practice_resp = await philosophy_k8_ethics_values_practice(practice_req)

    return K8EthicsPlannerResponse(
        original_question=request.question_text,
        lesson=lesson.model_dump(),
        practice=practice_resp,
    )

@router.post(
    "/k8/teacher-view",
    response_model=K8TeacherLaneSummary,
)
async def philosophy_k8_teacher_view(
    request: K8PhilosophyPlannerRequest,
) -> K8TeacherLaneSummary:
    """
    Teacher-facing view for a K–8 question.

    Reuses the main K–8 planner (with lane practice) and enriches it with
    tags and adult guidance.
    """
    # Force include_lane_practice = True for richer data
    planner_req = K8PhilosophyPlannerRequest(
        question_text=request.question_text,
        include_lane_practice=True,
    )
    planner_resp = await philosophy_k8_planner(planner_req)

    mode = K8TeacherViewMode.LANE_SUMMARY
    world_primary_tag = None
    world_secondary_tags = None
    mind_primary_tag = None
    mind_secondary_tags = None
    suggested_teacher_moves: list[str] = []
    risk_flags: list[str] = []
    teacher_reflection_prompts: list[str] = []

    # Populate lane-specific tags and guidance
    if planner_resp.chosen_lane == K8PhilosophyLane.WORLD and planner_resp.world_practice:
        world_primary_tag = planner_resp.world_practice.primary_tag
        world_secondary_tags = planner_resp.world_practice.secondary_tags
        lesson_title = "World Seeds: Reality, Time, and Possibility"
        mode = K8TeacherViewMode.LANE_WITH_LESSON
        suggested_teacher_moves = [
            "Treat the question as serious and philosophically important, even if it sounds playful.",
            "Invite the child to describe the pictures or scenes they imagine when they ask this question.",
            "Avoid rushing to correct what is 'really real'; first listen for their own picture of the world.",
        ]
        risk_flags = [
            "Watch for signs of worry or existential anxiety (fear about nothingness, infinity, or death).",
        ]
        teacher_reflection_prompts = [
            "How comfortable are you with not having a final answer to this question?",
            "What big-world questions did you have as a child, and how were they received?",
        ]
    elif planner_resp.chosen_lane == K8PhilosophyLane.MIND and planner_resp.mind_practice:
        mind_primary_tag = planner_resp.mind_practice.primary_tag
        mind_secondary_tags = planner_resp.mind_practice.secondary_tags
        lesson_title = "Mind Seeds: Thoughts, Feelings, and You"
        mode = K8TeacherViewMode.LANE_WITH_LESSON
        suggested_teacher_moves = [
            "Normalize the feeling and the question; let the child know it is okay to talk about it.",
            "Ask where in their body they notice the feeling, and how it changes over time.",
            "Reflect their words back before introducing any new labels or explanations.",
        ]
        risk_flags = [
            "Watch for strong distress, self-blame, or language about not wanting to exist.",
        ]
        teacher_reflection_prompts = [
            "How do your own reactions to strong emotions show up when a child is sharing?",
            "Are there cultural or family ideas about self and emotion that you should respect here?",
        ]
    elif planner_resp.chosen_lane == K8PhilosophyLane.ETHICS:
        lesson_title = "Ethics Seeds: Fairness, Promises, and Honesty"
        mode = K8TeacherViewMode.LANE_WITH_LESSON
        suggested_teacher_moves = [
            "Invite the child to describe what happened in concrete terms before judging.",
            "Ask who might be helped or harmed by different options in the story.",
            "Help the child separate 'what feels fair' from 'what the rules say', and talk about both.",
        ]
        risk_flags = [
            "Watch for patterns of exclusion, bullying, or repeated unfairness in one direction.",
        ]
        teacher_reflection_prompts = [
            "Do you tend to emphasize rules, outcomes, or relationships when you talk about fairness?",
            "How can you model listening carefully before giving moral advice?",
        ]
    else:  # LOGIC or default
        lesson_title = "Logic Seeds: Reasons and Conclusions"
        mode = K8TeacherViewMode.LANE_WITH_LESSON
        suggested_teacher_moves = [
            "Encourage the child to use the pattern 'I think ___ because ___'.",
            "Ask them to notice the difference between reasons and feelings.",
            "Gently question generalizations like 'everyone does it' or 'never' and look for exceptions together.",
        ]
        risk_flags = []
        teacher_reflection_prompts = [
            "How do you respond when a child gives a weak reason? Do you correct, question, or explore?",
        ]

    return K8TeacherLaneSummary(
        mode=mode,
        original_question=planner_resp.original_question,
        chosen_lane=planner_resp.chosen_lane,
        world_primary_tag=world_primary_tag,
        world_secondary_tags=world_secondary_tags,
        mind_primary_tag=mind_primary_tag,
        mind_secondary_tags=mind_secondary_tags,
        kid_starter_prompt=planner_resp.starter_prompt,
        lesson_title=lesson_title,
        suggested_teacher_moves=suggested_teacher_moves,
        risk_flags=risk_flags,
        teacher_reflection_prompts=teacher_reflection_prompts,
    )

@router.get(
    "/l2/core-branches",
    response_model=PhilosophyLesson,
)
async def philosophy_lane2_core_branches() -> PhilosophyLesson:
    """
    Lane 2 teach: overview of core branches of philosophy.
    Ethics, epistemology, metaphysics, political philosophy, logic, and aesthetics.
    """
    return PhilosophyLesson(
        id="philo.l2.core-branches",
        subject=SubjectId.PHILOSOPHY_CORE,
        title="Core Branches of Philosophy",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.INTERMEDIATE,
        description=(
            "A map of the main branches of philosophy: ethics, epistemology, metaphysics, "
            "political philosophy, logic, and aesthetics, with the kinds of questions each one studies."
        ),
        content={
            "overview": (
                "Philosophers often group their questions into branches so they can focus on related problems. "
                "The classic core branches are ethics, epistemology, metaphysics, political philosophy, logic, and aesthetics."
            ),
            "branches": [
                {
                    "name": "Ethics",
                    "focus": "What is right or wrong, good or bad, and how we should live.",
                    "sample_questions": [
                        "Is it ever right to lie?",
                        "What do we owe to strangers, future people, or non-human animals?",
                        "Do good ends ever justify harmful means?"
                    ],
                },
                {
                    "name": "Epistemology",
                    "focus": "What knowledge is, how we get it, and how certain we can be.",
                    "sample_questions": [
                        "How can I know which sources to trust?",
                        "Is it possible that all my experiences are misleading?",
                        "When is it rational to change your mind?"
                    ],
                },
                {
                    "name": "Metaphysics",
                    "focus": "What is real and what kinds of things exist.",
                    "sample_questions": [
                        "Do we have free will, or is everything determined?",
                        "What makes a person the same over time?",
                        "Are there abstract objects like numbers?"
                    ],
                },
                {
                    "name": "Political Philosophy",
                    "focus": "Power, justice, rights, and how societies should be organized.",
                    "sample_questions": [
                        "What makes a government legitimate?",
                        "What do justice and equality require in law and policy?",
                        "When is civil disobedience justified?"
                    ],
                },
                {
                    "name": "Logic",
                    "focus": "Correct reasoning and the structure of good arguments.",
                    "sample_questions": [
                        "When does a conclusion really follow from its premises?",
                        "What makes an argument invalid or fallacious?",
                        "How can formal rules help us reason more clearly?"
                    ],
                },
                {
                    "name": "Aesthetics",
                    "focus": "Beauty, art, and the value of aesthetic experience.",
                    "sample_questions": [
                        "What makes something a work of art?",
                        "Are judgments of beauty purely subjective?",
                        "Why do tragic stories and sad music matter to us?"
                    ],
                },
            ],
            "guided_questions": [
                "When you think about your own big questions, which branch do they most often fall into?",
                "Do you find questions about value (ethics, politics, art) or questions about truth (knowledge, reality, logic) more gripping?",
                "How might work in one branch (like metaphysics) affect answers in another (like ethics)?",
            ],
            "common_confusions": [
                "Thinking each branch is isolated; in practice, many questions touch several branches at once.",
                "Assuming ethics is just personal taste, while other branches are 'real' philosophy.",
                "Forgetting that political philosophy is not just about current events but about deeper principles of justice and authority.",
            ],
            "reflection_prompts": [
                "Pick one branch and write down a real question in your life that belongs to it.",
                "Think of a belief you have that mixes branches (for example, a political belief that also depends on what you think is real and what you think we can know).",
            ],
            "next_suggestion": (
                "Next, practice classifying your own questions by branch and noticing how different branches "
                "highlight different values and uncertainties."
            ),
        },
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.SCHOOL_SECONDARY,
    )

@router.get(
    "/l3/ethics-intro",
    response_model=PhilosophyLesson,
)
async def philosophy_lane3_ethics_intro() -> PhilosophyLesson:
    """
    Lane 3 teach: introductory map of four normative ethics frameworks:
    consequentialism, deontology, virtue ethics, and care ethics.
    """
    summaries: list[EthicsIntroTeachSummary] = [
        EthicsIntroTeachSummary(
            framework=EthicsFramework.CONSEQUENTIALISM,
            headline="Consequentialism: Focus on outcomes",
            core_question="Which option will lead to the best overall results?",
            focus="Consequences of actions for all affected.",
            typical_guiding_principle="Choose the action that maximizes overall good or minimizes overall harm.",
            strengths=[
                "Makes you consider the impact on everyone affected, not just yourself.",
                "Encourages looking at long-term and indirect consequences.",
                "Fits well with many policy and cost-benefit discussions.",
            ],
            challenges=[
                "Hard to predict all consequences, especially long-term ones.",
                "Can seem to justify harming a few if it helps many.",
                "May neglect individual rights or promises if breaking them has better outcomes.",
            ],
            example_application=(
                "In deciding whether to tell a painful truth, a consequentialist asks: "
                "Which choice leads to the best overall balance of honesty, trust, and well-being "
                "for everyone involved, now and in the future?"
            ),
        ),
        EthicsIntroTeachSummary(
            framework=EthicsFramework.DEONTOLOGY,
            headline="Deontology: Focus on duties and rights",
            core_question="What are my duties here, and what must I not do, regardless of outcome?",
            focus="Moral rules, duties, rights, and respect for persons.",
            typical_guiding_principle="Act only in ways that you could will as a rule for everyone; never treat people as mere means.",
            strengths=[
                "Protects individual rights and dignity, even when breaking them might have good results.",
                "Gives clear rules in some cases (e.g., do not lie, keep promises).",
                "Allows us to say that some actions are wrong even if they turned out well.",
            ],
            challenges=[
                "Can be rigid when rules conflict or have bad consequences.",
                "Hard to decide which duties are most important when they clash.",
                "Rules need interpretation and may differ across cultures or traditions.",
            ],
            example_application=(
                "In the same truth-telling case, a deontologist asks: "
                "Do I have a duty to tell the truth here, and would lying treat my friend as a mere means?"
            ),
        ),
        EthicsIntroTeachSummary(
            framework=EthicsFramework.VIRTUE_ETHICS,
            headline="Virtue ethics: Focus on character",
            core_question="What would a good, virtuous person do in this situation?",
            focus="Character traits (virtues) like honesty, courage, compassion, and practical wisdom.",
            typical_guiding_principle="Cultivate virtues and act in ways that express good character over a whole life.",
            strengths=[
                "Connects decisions to the kind of person you are becoming.",
                "Emphasizes practical wisdom and context, not just rules or calculations.",
                "Makes sense of moral growth and role models.",
            ],
            challenges=[
                "Virtues can be interpreted differently in different cultures.",
                "Does not always give a clear yes/no answer for a single hard case.",
                "Can seem vague if not paired with more specific guidance.",
            ],
            example_application=(
                "In the truth case, a virtue ethicist asks: "
                "What would an honest and compassionate friend do here, balancing courage with kindness?"
            ),
        ),
        EthicsIntroTeachSummary(
            framework=EthicsFramework.CARE_ETHICS,
            headline="Care ethics: Focus on relationships and vulnerability",
            core_question="How can I respond with care to the needs and vulnerabilities in this relationship?",
            focus="Concrete relationships, empathy, context, and responsibilities of care.",
            typical_guiding_principle="Attend to the needs of those involved, especially the vulnerable, and maintain or repair caring relationships.",
            strengths=[
                "Centers empathy, listening, and particular relationships.",
                "Sensitive to power imbalances and vulnerability.",
                "Fits naturally with many real-world caregiving and family contexts.",
            ],
            challenges=[
                "Can risk favoritism if care for close others overrides fairness to strangers.",
                "Needs safeguards so that care does not excuse manipulation or dependency.",
                "Less standardized than rule-based or outcome-based views.",
            ],
            example_application=(
                "In the truth case, a care ethicist asks: "
                "Given our relationship and my friend's vulnerability, how can I be honest in a way that cares for their well-being?"
            ),
        ),
    ]

    # Pack into a generic PhilosophyLesson for consistency with other lanes.
    content = {
        "overview": (
            "Normative ethics offers several major frameworks for thinking about what we should do. "
            "Consequentialism focuses on outcomes, deontology on duties and rights, virtue ethics on character, "
            "and care ethics on relationships and vulnerability."
        ),
        "frameworks": [s.model_dump() for s in summaries],
        "guided_questions": [
            "Which framework feels most natural to you when you first face a moral dilemma?",
            "Which framework feels most uncomfortable or foreign to you, and why?",
            "Can you think of a case where two frameworks would clearly disagree about what to do?",
        ],
        "common_confusions": [
            "Thinking one framework must be right and the others simply wrong; in practice, many people draw on more than one.",
            "Believing that outcome-focused thinking never cares about rights, or that rule-focused thinking ignores consequences.",
            "Assuming virtues are just 'nice traits' rather than deeply connected to wise action.",
        ],
        "reflection_prompts": [
            "Recall a difficult decision you made. Looking back, which framework did you actually use?",
            "Think of someone you admire morally. Which framework best describes how they seem to reason?",
        ],
        "next_suggestion": (
            "Next, apply each framework to one of your own dilemmas and notice how their values and verdicts differ."
        ),
    }

    return PhilosophyLesson(
        id="philo.l3.ethics-intro",
        subject=SubjectId.PHILOSOPHY_CORE,
        title="Ethics I: Introductory Frameworks",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.INTERMEDIATE,
        description=(
            "An introduction to four major ethical frameworks—consequentialism, deontology, virtue ethics, and care ethics—"
            "and how they approach moral dilemmas differently."
        ),
        content=content,
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.SCHOOL_SECONDARY,
    )

@router.get(
    "/l4/ethics-digital",
    response_model=PhilosophyLesson,
)
async def philosophy_lane4_ethics_digital() -> PhilosophyLesson:
    """
    Lane 4 teach: Everyday digital & AI ethics.
    Applies the four frameworks to privacy, misinformation, bias, automation, and user–AI relationships.
    """
    content = {
        "overview": (
            "Digital and AI ethics asks how our values apply to everyday technologies such as social media, "
            "recommendation systems, data collection, automation, and AI assistants."
        ),
        "themes": [
            {
                "name": "Privacy and data",
                "focus": "Collection, use, and sharing of personal data; consent; surveillance.",
                "guiding_questions": [
                    "What data is being collected about people, and who controls it?",
                    "Who benefits and who is exposed to risk if this data is misused or leaked?",
                    "Is consent here meaningful, or buried in complexity and dark patterns?",
                ],
            },
            {
                "name": "Misinformation and attention",
                "focus": "Algorithms that shape what we see and believe; clickbait; outrage amplification.",
                "guiding_questions": [
                    "How does this system affect what people believe or how they feel over time?",
                    "Is it optimizing for user well-being, or mainly for engagement and profit?",
                    "Who is responsible when false or harmful content spreads widely?",
                ],
            },
            {
                "name": "Bias and algorithmic fairness",
                "focus": "Systems that support decisions about people (loans, hiring, policing, education, healthcare).",
                "guiding_questions": [
                    "Which groups are advantaged or disadvantaged by this system?",
                    "What data was used to train it, and whose experience is missing or distorted?",
                    "Who can contest or appeal decisions, and how transparent is the process?",
                ],
            },
            {
                "name": "Automation and work",
                "focus": "Jobs, deskilling, and shifting burdens between humans and machines.",
                "guiding_questions": [
                    "Who gains time, money, or power from this automation, and who loses security or dignity?",
                    "Are new forms of work, support, or education being created for those displaced?",
                    "Is the technology serving human purposes, or are people serving the technology?",
                ],
            },
            {
                "name": "User–AI relationships",
                "focus": "Trust, dependence, persuasion, emotional attachment to AI.",
                "guiding_questions": [
                    "Is the AI nudging people in ways they fully understand and endorse?",
                    "Is it honest about its limits, sources, and non-human status?",
                    "Does it encourage reflection and agency, or just make choices easy and automatic?",
                ],
            },
        ],
        "framework_views": [
            {
                "framework": EthicsFramework.CONSEQUENTIALISM.value,
                "headline": "Consequentialism: Outcomes of digital systems",
                "focus": "Total harms and benefits of AI and digital platforms at the scale of many users and long time periods.",
            },
            {
                "framework": EthicsFramework.DEONTOLOGY.value,
                "headline": "Deontology: Rights, duties, and constraints for tech",
                "focus": "Rights to privacy, informed consent, non-discrimination, and truthful communication, regardless of outcomes.",
            },
            {
                "framework": EthicsFramework.VIRTUE_ETHICS.value,
                "headline": "Virtue ethics: Character in online life and design",
                "focus": "What kind of people and organizations we are becoming through our digital habits and designs.",
            },
            {
                "framework": EthicsFramework.CARE_ETHICS.value,
                "headline": "Care ethics: Vulnerability and relationships online",
                "focus": "How systems treat vulnerable users and affect real relationships and communities.",
            },
        ],
        "guided_questions": [
            "Think of one digital product you use daily. What values does it quietly encourage in you?",
            "When you feel uneasy about a tech feature, is it because of outcomes, rights, character, or care for someone vulnerable?",
            "Where do different ethical frameworks pull in different directions about a tech issue you care about?",
        ],
        "common_confusions": [
            "Thinking digital ethics is only about following the law, not about deeper questions of good and harm.",
            "Assuming algorithms are neutral or objective because they are made of code.",
            "Treating 'user choice' as free and informed when designs heavily steer behavior.",
        ],
        "reflection_prompts": [
            "Describe one tech product you use that makes you better—and one that makes you worse.",
            "If PRIME had to choose, would you rather it be slightly less helpful but more honest and careful with your data, or the reverse?",
        ],
        "next_suggestion": (
            "Next, apply the four ethical frameworks to specific digital and AI dilemmas "
            "from your own life or work."
        ),
    }

    return PhilosophyLesson(
        id="philo.l4.ethics-digital",
        subject=SubjectId.PHILOSOPHY_CORE,
        title="Ethics II: Everyday Digital & AI Ethics",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.INTERMEDIATE,
        description=(
            "An introduction to everyday digital and AI ethics, using the four major ethical frameworks "
            "to think about privacy, misinformation, bias, automation, and user–AI relationships."
        ),
        content=content,
        domain=DomainId.HUMANITIES,
        level=CurriculumLevel.SCHOOL_SECONDARY,
    )

@router.post(
    "/l4/ethics-digital/practice",
    response_model=EthicsDigitalPracticeResponse,
)
async def philosophy_lane4_ethics_digital_practice(
    request: EthicsDigitalPracticeRequest,
) -> EthicsDigitalPracticeResponse:
    """
    Lane 4 practice: apply the four ethical frameworks to a digital/AI dilemma,
    surfacing their different emphases, values, and risks.
    """
    dilemma = request.dilemma_text.strip()
    tags = request.context_tags

    evaluations: list[EthicsDigitalFrameworkEvaluation] = []

    # Consequentialism lens
    evaluations.append(
        EthicsDigitalFrameworkEvaluation(
            framework=EthicsFramework.CONSEQUENTIALISM,
            digital_focus=(
                "Short- and long-term impacts of this system or decision on users, "
                "bystanders, and society at scale."
            ),
            main_question=(
                "If we look at overall harms and benefits for everyone affected, which option "
                "leads to the best balance of well-being over harm?"
            ),
            tentative_take=(
                "Consequentialism tends to favor options that reduce large-scale harms "
                "(such as widespread misinformation, discrimination, or exploitation), "
                "even if they are inconvenient or costly in the short term."
            ),
            values_highlighted=[
                "Overall outcomes",
                "Harm reduction",
                "Collective well-being",
            ],
            risks_ignored=[
                "Violating individual rights or expectations if doing so improves overall outcomes",
                "Overconfidence in our ability to predict complex digital consequences",
            ],
        )
    )

    # Deontology lens
    evaluations.append(
        EthicsDigitalFrameworkEvaluation(
            framework=EthicsFramework.DEONTOLOGY,
            digital_focus=(
                "Respecting users' rights to privacy, informed consent, fair treatment, "
                "and truthful communication, regardless of outcomes."
            ),
            main_question=(
                "Which options respect users as ends in themselves, honoring their rights and "
                "dignity, and which options treat them as mere data points or means?"
            ),
            tentative_take=(
                "Deontology tends to reject practices that involve deception, non-consensual "
                "data use, or unfair discrimination, even when those practices might bring "
                "efficiency or profit."
            ),
            values_highlighted=[
                "Rights and duties",
                "Honesty and transparency",
                "Non-discrimination",
            ],
            risks_ignored=[
                "Potentially missing ways to sharply reduce harm because of rigid rules",
                "Difficulty resolving conflicts between different rights or duties",
            ],
        )
    )

    # Virtue ethics lens
    evaluations.append(
        EthicsDigitalFrameworkEvaluation(
            framework=EthicsFramework.VIRTUE_ETHICS,
            digital_focus=(
                "Character and culture: what kind of people, teams, and organizations we become "
                "through our digital design and usage choices."
            ),
            main_question=(
                "What would an honest, just, and compassionate person or organization do in "
                "designing or using this system?"
            ),
            tentative_take=(
                "Virtue ethics tends to favor options that cultivate integrity, humility, "
                "courage to resist harmful incentives, and a sense of responsibility for users."
            ),
            values_highlighted=[
                "Character and integrity",
                "Practical wisdom",
                "Responsibility for long-term culture",
            ],
            risks_ignored=[
                "Lack of precise yes/no answers in complex technical policy decisions",
                "Ambiguity when different virtues (e.g., honesty vs. kindness) seem to conflict",
            ],
        )
    )

    # Care ethics lens
    evaluations.append(
        EthicsDigitalFrameworkEvaluation(
            framework=EthicsFramework.CARE_ETHICS,
            digital_focus=(
                "How the system treats vulnerable users and affects real relationships and "
                "communities over time."
            ),
            main_question=(
                "How can we respond to this situation in a way that attends to vulnerability and "
                "maintains or repairs trust and care in relationships?"
            ),
            tentative_take=(
                "Care ethics tends to favor options that protect and support vulnerable users "
                "(such as children, isolated people, or marginalized groups), even when those "
                "options reduce engagement or profit."
            ),
            values_highlighted=[
                "Empathy and responsiveness",
                "Protection of the vulnerable",
                "Trust and relationship quality",
            ],
            risks_ignored=[
                "Impartial fairness when care for one group disadvantages others",
                "Clear boundaries when 'caring' practices become intrusive or paternalistic",
            ],
        )
    )

    comparison_questions = [
        "Do the four frameworks point in the same direction here, or do any of them strongly disagree?",
        "Which lens makes you most uneasy about the 'easy' or default option in this dilemma?",
        "If you had to prioritize one value in this case (e.g., privacy, fairness, well-being, trust), which would it be and why?",
    ]

    wisdom_prompts = [
        "If PRIME is involved in this situation, what concrete limits or disclosures should PRIME adopt to avoid harm?",
        "What process (review, oversight, user feedback) could make similar digital/AI decisions wiser over time?",
        "What would it look like for you, personally, to use or design this technology in a way you would be proud to explain to someone you respect?",
    ]

    return EthicsDigitalPracticeResponse(
        original_dilemma=dilemma,
        context_tags=tags,
        evaluations=evaluations,
        comparison_questions=comparison_questions,
        wisdom_prompts=wisdom_prompts,
    )

@router.get(
    "/l3/care",
    response_model=EthicsCareTeachLesson,
)
async def philosophy_ethics_l3_care_teach() -> EthicsCareTeachLesson:
    """
    Ethics Lane 3 teach: Care / relational ethics in depth.
    Blends analytic clarity with a relational, reflective voice.
    """
    overview = (
        "Care and relational ethics start from the fact that we are vulnerable, interdependent beings "
        "who live in webs of relationship. Instead of asking only 'What rule applies?' or 'What maximizes "
        "overall good?', this approach asks 'Who is involved here, who is vulnerable, and what would it look "
        "like to respond with good care in this situation?'"
    )

    historical_roots = [
        "Feminist care ethics, which highlighted care, dependency, and emotion as morally significant in a way that earlier theories often overlooked.",
        "Confucian and other relational traditions that place relationships, roles, and mutual responsibilities at the center of a good life.",
        "Contemporary work on care as a political and structural value, not just a private virtue, including debates about global care chains and social vulnerability.",
    ]

    core_principles = [
        "Relationality: Persons are understood through their relationships and dependencies, not as completely independent atoms.",
        "Care practices: Attentiveness, responsibility, competence, and responsiveness in meeting needs are central moral activities, not afterthoughts.",
        "Vulnerability and power: Ethical analysis must track who is vulnerable, who holds power, and how care can both support and unintentionally control others.",
        "Context and particularity: What good care requires is highly context-dependent; it resists simple one-size-fits-all rules.",
    ]

    variants: list[dict[str, Any]] = [
        EthicsCareTeachEntry(
            title="Feminist Ethics of Care",
            description=(
                "Feminist care ethics emphasizes the moral significance of caring relationships, emotional responsiveness, "
                "and the often invisible labor of care. It challenges approaches that focus only on abstract rights or "
                "impartial rules, arguing that real moral life is rooted in concrete relationships and dependency."
            ),
            examples=[
                "Noticing that an overworked colleague is struggling and quietly redistributing tasks or offering support, even if no rule requires it.",
                "Re-examining family or workplace expectations when one person is always doing the emotional or caregiving labor.",
            ],
            strengths=[
                "Makes visible forms of care work and emotional labor that traditional theories have often ignored.",
                "Takes seriously vulnerability, dependence, and the role of emotion in good moral judgment.",
            ],
            classic_objections=[
                "Risk of reinforcing traditional gender roles if care expectations fall mostly on women or marginalized people.",
                "Concerns that a focus on close relationships might slide into favoritism or neglect of distant others and structural injustice.",
            ],
        ).model_dump(),
        EthicsCareTeachEntry(
            title="Confucian and Role-Based Relational Ethics",
            description=(
                "Confucian and related relational traditions understand morality through roles and relationships "
                "child and parent, friend and friend, leader and community. Virtues like ren (humaneness, care) "
                "and li (ritual propriety) guide how people should care for one another within these roles."
            ),
            examples=[
                "Seeing leadership as a role of caring responsibility for the well-being and growth of those you lead.",
                "Balancing loyalty to family with wider responsibilities to community or society when they come into tension.",
            ],
            strengths=[
                "Provides a rich picture of how specific roles carry responsibilities of care and respect.",
                "Highlights the importance of rituals, practices, and everyday gestures that sustain relationships over time.",
            ],
            classic_objections=[
                "Historical role structures can encode hierarchy and gender inequality, which need critical examination.",
                "Tension between role-based partiality and more egalitarian or rights-based ideals.",
            ],
        ).model_dump(),
        EthicsCareTeachEntry(
            title="Global and Structural Care Ethics",
            description=(
                "Global and structural care ethics examine how care is organized in societies and across borders. "
                "They ask who receives good care, who does the caring work, and how institutions, laws, and economies "
                "can better reflect care as a central value rather than a private matter."
            ),
            examples=[
                "Noticing that migrant workers or low-paid caregivers support essential services while lacking secure care for themselves.",
                "Designing policies or workplace structures that give caregivers time, resources, and recognition rather than treating care as invisible.",
            ],
            strengths=[
                "Connects personal relationships of care to questions of justice, labor, and social design.",
                "Highlights that everyone is dependent and vulnerable at different times, challenging ideals of complete independence.",
            ],
            classic_objections=[
                "Can seem broad and hard to translate into precise policy rules.",
                "Needs to guard against paternalism: helping in ways that override the voices and agency of those receiving care.",
            ],
        ).model_dump(),
    ]

    strengths = [
        "Brings vulnerability, dependency, and emotional life into ethical reflection instead of treating them as private matters.",
        "Encourages attention to concrete people and relationships, not just abstract agents or anonymous beneficiaries.",
        "Connects everyday care to larger questions of power, justice, and how institutions are designed.",
    ]

    objections = [
        "May provide less precise action-guidance in highly novel or large-scale dilemmas.",
        "Needs to balance partiality to close relationships with concern for distant or marginalized others.",
        "Risk of reinforcing unequal care burdens if structural and gender dynamics are not critically examined.",
    ]

    reflection_questions = [
        "In your own life, who do you feel most responsible for caring for right now, and who cares for you?",
        "Are there relationships where you feel you are giving much more care than you receive, or the reverse?",
        "When you make hard decisions, how often do you explicitly think about vulnerability and power in the relationships involved?",
    ]

    return EthicsCareTeachLesson(
        overview=overview,
        historical_roots=historical_roots,
        core_principles=core_principles,
        variants=variants,
        strengths=strengths,
        objections=objections,
        reflection_questions=reflection_questions,
    )

@router.post(
    "/l3/care/practice",
    response_model=EthicsCarePracticeResponse,
)
async def philosophy_ethics_l3_care_practice(
    request: EthicsCarePracticeRequest,
) -> EthicsCarePracticeResponse:
    """
    Ethics Lane 3 practice: apply care / relational ethics to a case,
    blending analytic structure with a reflective, relational tone.
    """
    dilemma = request.dilemma_text.strip()

    relationship_focused_summary = (
        "From a care and relational ethics perspective, the first question is: who is involved here, "
        "how are they connected, and who is most vulnerable in this situation? Instead of starting from "
        "abstract rules or overall totals, this view invites you to look closely at the relationships, "
        "needs, and emotions already in play, and to ask what a caring response would look like for each person."
    )

    care_obligations_and_needs = [
        "Identify whose needs are most urgent right now, and whether those needs are physical, emotional, social, or financial.",
        "Notice any ongoing patterns of care: who usually steps in, who is often overlooked, and whether anyone (including you) is approaching exhaustion.",
        "Ask what forms of care are realistic for you to offer without erasing your own basic needs or boundaries.",
    ]

    power_and_vulnerability_analysis = [
        "Consider who has more power, voice, or resources in this situation, and who might feel they have little say.",
        "Ask how dependency or vulnerability might make it hard for someone to speak up about what they truly need.",
        "Reflect on ways to offer care that support the other person's agency, rather than quietly deciding for them what is best.",
    ]

    tensions_with_other_frameworks = [
        "A purely outcome-focused view may push for whatever seems to help the greatest number, even if it strains or damages particular relationships.",
        "A strictly rule-focused view may insist on treating everyone the same, while a care perspective sometimes asks you to give extra attention to those who are especially vulnerable or close to you.",
        "Virtue ethics overlaps with care in focusing on character, but a care lens keeps relationships, dependency, and power dynamics at the center of the picture.",
    ]

    self_check_questions = [
        "In this dilemma, whose vulnerability or quiet needs might be easiest to overlook if you only focused on rules or outcomes?",
        "Is there anyone including you who is giving more care than they can sustainably offer right now?",
        "What would a response look like that feels caring both to others involved and to yourself, even if it is not perfect?",
    ]

    meta_reflection_prompts = [
        "How much do you want PRIME to factor in existing relationships, attachment, and vulnerability when giving you ethical guidance?",
        "When rules, outcomes, and relationships pull in different directions, which do you want to carry the most weight in your own decision-making?",
        "Are there structural or power issues in your life family, workplace, community that you would like PRIME to help you notice when you are thinking about care?",
    ]

    analysis = EthicsCarePracticeAnalysis(
        relationship_focused_summary=relationship_focused_summary,
        care_obligations_and_needs=care_obligations_and_needs,
        power_and_vulnerability_analysis=power_and_vulnerability_analysis,
        tensions_with_other_frameworks=tensions_with_other_frameworks,
    )

    return EthicsCarePracticeResponse(
        original_dilemma=dilemma,
        analysis=analysis,
        self_check_questions=self_check_questions,
        meta_reflection_prompts=meta_reflection_prompts,
    )

@router.post(
    "/l3/ethics-intro/practice",
    response_model=EthicsIntroPracticeResponse,
)
async def philosophy_lane3_ethics_intro_practice(
    request: EthicsIntroPracticeRequest,
) -> EthicsIntroPracticeResponse:
    """
    Lane 3 practice: take a user's dilemma and run it through four frameworks,
    surfacing how their values and tentative judgments differ.
    """
    dilemma = request.dilemma_text.strip()

    evaluations: list[EthicsFrameworkEvaluation] = []

    # Consequentialism
    evaluations.append(
        EthicsFrameworkEvaluation(
            framework=EthicsFramework.CONSEQUENTIALISM,
            main_question="What overall pattern of consequences will each option have for everyone affected?",
            suggested_focus=(
                "Map out the main options and list likely short- and long-term benefits and harms "
                "for all key stakeholders."
            ),
            tentative_judgment=(
                "Consequentialism tends to favor the option that produces the best overall balance "
                "of good over harm, even if it is personally difficult."
            ),
            what_it_values_most=["Overall outcomes", "Harm reduction", "Total or average welfare"],
            what_it_risks_or_downplays=[
                "Individual rights or promises when they conflict with overall good",
                "The difficulty of predicting complex consequences",
            ],
        )
    )

    # Deontology
    evaluations.append(
        EthicsFrameworkEvaluation(
            framework=EthicsFramework.DEONTOLOGY,
            main_question="What duties, rights, or rules are at stake, and what must not be done even for good results?",
            suggested_focus=(
                "Identify promises, explicit and implicit agreements, rights, and moral rules that apply, "
                "and ask what you would be willing to make a universal rule."
            ),
            tentative_judgment=(
                "Deontology tends to favor the option that respects duties and rights, even if the "
                "immediate outcome is harder or less efficient."
            ),
            what_it_values_most=["Respect for persons", "Duties and obligations", "Consistency and fairness"],
            what_it_risks_or_downplays=[
                "Flexibility when rules conflict with serious harms",
                "Contextual details that are not captured by general rules",
            ],
        )
    )

    # Virtue ethics
    evaluations.append(
        EthicsFrameworkEvaluation(
            framework=EthicsFramework.VIRTUE_ETHICS,
            main_question="What would a wise and virtuous person do here, given the kind of character they aim to embody?",
            suggested_focus=(
                "Consider which virtues are most relevant (e.g., honesty, courage, compassion, justice) "
                "and how each option would shape your character over time."
            ),
            tentative_judgment=(
                "Virtue ethics tends to favor the option that expresses and cultivates good character, "
                "even if it is messy to describe in simple rules."
            ),
            what_it_values_most=["Character and integrity", "Practical wisdom", "Moral growth over time"],
            what_it_risks_or_downplays=[
                "Precise action-guidance in highly specific cases",
                "Clear answers when different virtues pull in different directions",
            ],
        )
    )

    # Care ethics
    evaluations.append(
        EthicsFrameworkEvaluation(
            framework=EthicsFramework.CARE_ETHICS,
            main_question="How can I respond with care to the concrete needs and vulnerabilities in this situation?",
            suggested_focus=(
                "Look closely at the relationships involved, who is most vulnerable, and how trust and "
                "care can be maintained or repaired."
            ),
            tentative_judgment=(
                "Care ethics tends to favor the option that best sustains or repairs caring relationships "
                "while attending to vulnerability."
            ),
            what_it_values_most=["Empathy and responsiveness", "Particular relationships", "Vulnerability and dependence"],
            what_it_risks_or_downplays=[
                "Impartiality and fairness between close others and strangers",
                "Clear limits when care for one person harms others unjustly",
            ],
        )
    )

    comparison_questions = [
        "Do the four frameworks give the same verdict on your dilemma, or do any of them conflict?",
        "Which framework's way of looking at your situation feels most natural to you? Which feels most challenging?",
        "If two frameworks disagree, which values are in tension (e.g., overall good vs. individual rights vs. loyalty vs. character)?",
    ]

    wisdom_prompts = [
        "If you had to explain your choice to someone you respect, which framework would you lean on to justify it?",
        "Are there values you are tempted to ignore because they make the decision harder, even though they matter?",
        "What small action could you take now that honors the most important values across more than one framework?",
    ]

    return EthicsIntroPracticeResponse(
        original_dilemma=dilemma,
        evaluations=evaluations,
        comparison_questions=comparison_questions,
        wisdom_prompts=wisdom_prompts,
    )

@router.get(
    "/l3/consequentialism",
    response_model=EthicsConsequentialismTeachLesson,
)
async def philosophy_ethics_l3_consequentialism_teach() -> EthicsConsequentialismTeachLesson:
    """
    Ethics Lane 3 teach: Consequentialism in depth.
    Covers core principles, main variants, strengths, and classic objections.
    """
    overview = (
        "Consequentialism is the family of ethical theories that judge actions primarily by their consequences. "
        "On this view, the right action is the one that produces the best overall results, compared to the alternatives. "
        "Utilitarianism is the most famous version, focusing on overall happiness or welfare."
    )

    historical_roots = [
        "Ancient roots in thinkers who linked ethics to human flourishing and outcomes (e.g., some Greek and Indian traditions).",
        "Modern development in classical utilitarianism (Jeremy Bentham, John Stuart Mill) with focus on pleasure, pain, and overall welfare.",
        "Contemporary expansions to include preferences, well-being, and broader conceptions of 'the good'.",
    ]

    core_principles = [
        "Consequential focus: What ultimately matters ethically is the pattern of outcomes produced by actions, rules, or policies.",
        "Impartiality: Each person's good counts equally, at least in principle; nobody's welfare is inherently worth more.",
        "Maximization: We should, as far as possible, choose the option that produces the best overall balance of good over bad.",
    ]

    variants: list[dict[str, Any]] = [
        EthicsConsequentialismTeachEntry(
            title="Act Consequentialism",
            description=(
                "Act consequentialism (including act utilitarianism) evaluates each individual action directly "
                "by its consequences: an action is right if it produces at least as much overall good as any "
                "available alternative."
            ),
            examples=[
                "A doctor considers whether to break a minor rule to save a patient's life because the immediate outcome is much better.",
                "A person lies in a specific case if doing so prevents serious harm and no better option is available.",
            ],
            strengths=[
                "Flexibility: can respond sensitively to particular circumstances rather than rigid rules.",
                "Clarity: gives a single decision procedure—choose the option with the best overall consequences.",
            ],
            classic_objections=[
                "May seem to permit sacrificing innocent individuals if doing so maximizes overall good.",
                "Can undermine trust if people suspect rules and promises will be broken whenever it seems beneficial.",
                "Very demanding: seems to require constant calculation and great personal sacrifice.",
            ],
        ).model_dump(),
        EthicsConsequentialismTeachEntry(
            title="Rule Consequentialism",
            description=(
                "Rule consequentialism evaluates rules by their consequences: the right action is the one that "
                "follows the set of rules whose general acceptance would lead to the best outcomes."
            ),
            examples=[
                "A society adopts and follows rules like 'do not punish the innocent' or 'keep promises' because these rules make things better overall.",
                "Even if breaking a rule would help in one case, people follow the rule to preserve trust and long-term benefits.",
            ],
            strengths=[
                "Can protect important rules (e.g., against punishing innocents) that support trust and rights.",
                "Less demanding in everyday life: people can follow stable rules rather than calculate each act.",
            ],
            classic_objections=[
                "Risk of 'rule worship': following rules even when breaking them would clearly improve outcomes.",
                "Difficult questions about which set of rules really maximizes overall good.",
            ],
        ).model_dump(),
        EthicsConsequentialismTeachEntry(
            title="Two-Level or 'Softened' Consequentialism",
            description=(
                "Two-level views suggest that we usually follow simple moral rules and habits (intuitive level), "
                "but in hard or exceptional cases we step back and think in full consequentialist terms (critical level)."
            ),
            examples=[
                "In daily life, someone follows ordinary rules about honesty and fairness without constant calculation.",
                "In rare high-stakes situations, they deliberately weigh overall consequences before deciding.",
            ],
            strengths=[
                "Acknowledges human limits: we cannot compute all consequences all the time.",
                "Explains why common-sense rules and virtues are still valuable within a consequentialist outlook.",
            ],
            classic_objections=[
                "Unclear when to switch from intuitive to critical level.",
                "May still inherit classic objections if critical-level reasoning approves troubling actions.",
            ],
        ).model_dump(),
    ]

    strengths = [
        "Encourages wide empathy: asks us to care about the impact of our actions on all affected, not just ourselves.",
        "Fits many real-world decision contexts (policy, public health, business) where outcomes are central.",
        "Provides a clear way to compare options when rules or intuitions conflict.",
    ]

    objections = [
        "Demandingness: seems to require large sacrifices of time, money, and comfort whenever doing so would increase overall good.",
        "Justice and rights: may appear to justify harming a few if it benefits many, raising concerns about rights and fairness.",
        "Prediction: we often cannot reliably predict all consequences, especially long-term or indirect ones.",
        "Integrity: may require people to act against their deepest commitments if that maximizes overall welfare.",
    ]

    reflection_questions = [
        "When you think about hard decisions, do you naturally think in consequentialist terms (weighing outcomes), or do other considerations come first?",
        "Can you think of a case where a purely outcome-focused choice would feel clearly wrong to you? Why?",
        "Would a rule-based or two-level version of consequentialism answer some of your worries, or do they remain?",
    ]

    return EthicsConsequentialismTeachLesson(
        overview=overview,
        historical_roots=historical_roots,
        core_principles=core_principles,
        variants=variants,
        strengths=strengths,
        objections=objections,
        reflection_questions=reflection_questions,
    )

@router.get(
    "/l3/deontology",
    response_model=EthicsDeontologyTeachLesson,
)
async def philosophy_ethics_l3_deontology_teach() -> EthicsDeontologyTeachLesson:
    """
    Ethics Lane 3 teach: Deontology in depth.
    Focus on duties, rights, and constraints (especially Kantian-style deontology).
    """
    overview = (
        "Deontological ethics judges actions primarily by whether they respect duties, rights, and moral rules, "
        "rather than by their consequences. On a deontological view, some actions are wrong in themselves—such as "
        "lying, killing the innocent, or breaking serious promises—even if they might lead to better outcomes."
    )

    historical_roots = [
        "Roots in ideas of moral law and divine commandments in religious and philosophical traditions.",
        "Kant's development of a secular, rational account of duty, universal law, and respect for persons.",
        "Later developments in rights-based theories and rule-focused approaches that emphasize constraints on action.",
    ]

    core_principles = [
        "Duty and rightness: Some actions are right or wrong regardless of their outcomes; we have obligations we must not violate.",
        "Universalizability: Moral rules should be principles that any rational agent could will as a law for everyone.",
        "Respect for persons: We must treat people as ends in themselves, not merely as means to our own goals.",
    ]

    variants: list[dict[str, Any]] = [
        EthicsDeontologyTeachEntry(
            title="Kantian Deontology (Duty and Categorical Imperative)",
            description=(
                "Kantian ethics grounds morality in rational duties expressed through the categorical imperative. "
                "One formulation asks us to act only on maxims we can will as universal laws; another demands that we "
                "treat humanity, in ourselves and others, always as an end and never merely as a means."
            ),
            examples=[
                "Refusing to lie even when a lie could bring short-term benefits, because a universal permission to lie would destroy trust.",
                "Rejecting the idea of using an innocent person as a mere tool, even to achieve large benefits for others.",
            ],
            strengths=[
                "Provides clear constraints that protect individuals from being sacrificed for others.",
                "Emphasizes the importance of intention, consistency, and respect for rational agency.",
            ],
            classic_objections=[
                "Can seem too rigid in extreme cases (e.g., lying to a would-be murderer).",
                "Struggles with conflicting duties (e.g., promise-keeping vs. preventing harm).",
            ],
        ).model_dump(),
        EthicsDeontologyTeachEntry(
            title="Rule Deontology and Common-Sense Morality",
            description=(
                "Rule-focused deontological views emphasize a set of moral rules (do not kill the innocent, keep promises, "
                "respect property, tell the truth) that apply generally and are not easily overridden by good outcomes."
            ),
            examples=[
                "Believing it is wrong to break a serious promise even when doing so would help you or others.",
                "Holding that certain rules, like 'do not torture', must be respected regardless of benefits.",
            ],
            strengths=[
                "Fits many ordinary moral intuitions about promises, rights, and fairness.",
                "Gives relatively clear guidance in many everyday situations.",
            ],
            classic_objections=[
                "Can be unclear which rules are truly fundamental and how to resolve conflicts between them.",
                "May seem insensitive to context when strict rule-following leads to bad outcomes.",
            ],
        ).model_dump(),
        EthicsDeontologyTeachEntry(
            title="Rights-Based Deontology",
            description=(
                "Rights-based deontological approaches focus on protecting moral rights (to life, liberty, privacy, etc.) "
                "that place strong constraints on what can be done to individuals, even for good ends."
            ),
            examples=[
                "Insisting that people have a right not to be killed or coerced, even if harming them would save others.",
                "Defending privacy rights against intrusive surveillance, regardless of possible benefits of more data.",
            ],
            strengths=[
                "Provides a powerful language for protecting individuals and minorities from being used or sacrificed.",
                "Connects easily to legal and political ideas about human rights.",
            ],
            classic_objections=[
                "Can lead to 'rights conflicts' where different rights pull in different directions.",
                "May still require some view about which consequences matter when rights conflict.",
            ],
        ).model_dump(),
    ]

    strengths = [
        "Protects individuals from being treated merely as tools for others' purposes.",
        "Captures the sense that intentions, promises, and commitments matter morally, not just outcomes.",
        "Provides firm constraints ('moral side-constraints') that can guide action in hard cases.",
    ]

    objections = [
        "Rigidity: strict rules can seem inhuman or counterintuitive in extreme cases (e.g., not lying to prevent serious harm).",
        "Conflict: different duties or rights can clash, and deontology does not always clearly say which should win.",
        "Outcome blindness: ignoring consequences entirely can feel irresponsible when harms are very large and predictable.",
    ]

    reflection_questions = [
        "When you think about moral rules (e.g., 'do not lie', 'keep promises'), do you see them as absolute, or do you make exceptions?",
        "Can you think of a case where you would break a deontological rule (like not lying) because the consequences are too serious?",
        "Do you think people have rights that must never be violated, no matter what good could be achieved?",
    ]

    return EthicsDeontologyTeachLesson(
        overview=overview,
        historical_roots=historical_roots,
        core_principles=core_principles,
        variants=variants,
        strengths=strengths,
        objections=objections,
        reflection_questions=reflection_questions,
    )

@router.post(
    "/l3/deontology/practice",
    response_model=EthicsDeontologyPracticeResponse,
)
async def philosophy_ethics_l3_deontology_practice(
    request: EthicsDeontologyPracticeRequest,
) -> EthicsDeontologyPracticeResponse:
    """
    Ethics Lane 3 practice: apply deontology to a hard case,
    highlighting duties, rights, and constraints, and where they feel too rigid.
    """
    dilemma = request.dilemma_text.strip()

    duty_focused_summary = (
        "From a deontological perspective, the first questions are: what duties and rights are at stake here, "
        "and what must not be done, even for good results? We ask what promises, roles, or moral rules apply "
        "to your situation (for example, duties not to lie, not to kill the innocent, or to respect consent) and "
        "whether any option clearly violates these obligations, regardless of the outcome."
    )

    humanity_formula_summary = (
        "Kantian-style deontology adds a specific test: does this option treat any person merely as a means to an end, "
        "rather than also as an end in themselves? If an option uses someone purely as a tool—ignoring their own "
        "rational agency, consent, or dignity—a strict Kantian view will reject that option, even if it could bring "
        "greater overall benefits."
    )

    key_conflicts_between_duties = [
        "Conflicts between duties to tell the truth and duties to protect others from harm.",
        "Conflicts between keeping promises and preventing serious wrongs or suffering.",
        "Conflicts between loyalty to particular people (family, friends, colleagues) and duties to treat everyone fairly.",
    ]

    limits_on_tradeoffs = [
        "Deontological views often set 'red lines'—actions (such as torturing or killing innocents) that are not to be crossed, regardless of benefits.",
        "Rights-focused approaches may say that some interests (like basic bodily integrity or freedom from coercion) cannot simply be traded off against gains for others.",
        "Even when deontologists allow exceptions, they usually require strong justification, not just small gains in overall welfare.",
    ]

    self_check_questions = [
        "In your dilemma, which duties or rights feel absolutely central to you?",
        "Is there any action you would refuse to take in this situation, no matter how good the consequences might be?",
        "Do you feel more disturbed by the idea of breaking a key duty, or by the idea of allowing bad consequences to occur?",
    ]

    meta_reflection_prompts = [
        "Do you want your own ethics to include absolute 'no-go' lines, or only strong but overridable rules?",
        "When duties conflict in your life, how do you usually decide which one to follow?",
        "If PRIME is helping you, how much weight should it give to duties and rights compared to outcomes in its advice?",
    ]

    analysis = EthicsDeontologyPracticeAnalysis(
        duty_focused_summary=duty_focused_summary,
        humanity_formula_summary=humanity_formula_summary,
        key_conflicts_between_duties=key_conflicts_between_duties,
        limits_on_tradeoffs=limits_on_tradeoffs,
    )

    return EthicsDeontologyPracticeResponse(
        original_dilemma=dilemma,
        analysis=analysis,
        self_check_questions=self_check_questions,
        meta_reflection_prompts=meta_reflection_prompts,
    )

@router.get(
    "/l3/virtue",
    response_model=EthicsVirtueTeachLesson,
)
async def philosophy_ethics_l3_virtue_teach() -> EthicsVirtueTeachLesson:
    """
    Ethics Lane 3 teach: Virtue ethics in depth.
    Focus on character, habituation, role models, and flourishing.
    """
    overview = (
        "Virtue ethics focuses on the kind of person you are becoming, not just on isolated actions. "
        "Instead of asking only 'What should I do?', it asks 'What would a good, virtuous person do here?' "
        "and 'What kind of life am I shaping through my choices?'"
    )

    historical_roots = [
        "Ancient Greek philosophy, especially Aristotle, with emphasis on virtues, habituation, and flourishing (eudaimonia).",
        "Revival in the 20th century as a response to perceived limits of rule-based and outcome-focused theories.",
        "Connections to Confucian, Aristotelian, and other traditions that stress character and role ethics.",
    ]

    core_principles = [
        "Character-centered: Ethics is about developing stable virtues (like honesty, courage, justice, compassion) and avoiding vices.",
        "Habituation and practice: We become virtuous by repeatedly acting in certain ways and reflecting on what we are becoming.",
        "Flourishing: The goal is a whole life that goes well in a deep sense, not just momentary pleasure or rule-following.",
        "Practical wisdom: Good judgment (phronesis) is required to balance virtues in concrete situations.",
    ]

    variants: list[dict[str, Any]] = [
        EthicsVirtueTeachEntry(
            title="Aristotelian Virtue Ethics",
            description=(
                "Aristotelian virtue ethics understands virtues as excellences of character that lie between extremes "
                "(e.g., courage between cowardice and recklessness). Virtue is developed through habit and guided by "
                "practical wisdom toward human flourishing (eudaimonia)."
            ),
            examples=[
                "Practicing honesty in many small situations so that truthfulness becomes part of your character.",
                "Acting with courage by facing a difficult truth or risk when it is appropriate, not rushing into danger for no reason.",
            ],
            strengths=[
                "Connects ethics to personal growth and the shape of an entire life.",
                "Recognizes the importance of context and judgment rather than rigid rules.",
            ],
            classic_objections=[
                "Can seem vague: does not always give a clear answer in specific cases.",
                "Depends heavily on a particular view of human nature and flourishing.",
            ],
        ).model_dump(),
        EthicsVirtueTeachEntry(
            title="Care of Self and Practices of Character",
            description=(
                "Some approaches focus on deliberate practices of self-care and self-formation: reflecting on one's habits, "
                "emotions, and relationships, and using routines, communities, and disciplines to cultivate virtues."
            ),
            examples=[
                "Keeping a journal to reflect on when you acted bravely or failed to act, and adjusting your habits.",
                "Joining a community that supports honesty and accountability in speech and decision-making.",
            ],
            strengths=[
                "Highlights the practical work of becoming virtuous, not just abstract principles.",
                "Invites ongoing self-examination and change.",
            ],
            classic_objections=[
                "Risk of becoming self-focused or moralistic if not guided by concern for others.",
                "Can underplay structural injustices that shape individual character.",
            ],
        ).model_dump(),
        EthicsVirtueTeachEntry(
            title="Contemporary Character and Moral Psychology",
            description=(
                "Contemporary virtue approaches often engage with psychology, asking how real people form and change character, "
                "and how situations and social structures influence virtue and vice."
            ),
            examples=[
                "Recognizing that stress, power, or anonymity can tempt even well-meaning people into wrongdoing.",
                "Designing environments that support honesty and courage, not just expecting individuals to be virtuous in isolation.",
            ],
            strengths=[
                "Connects ethics to empirical insights about human behavior.",
                "Acknowledges the role of environment, not just individual willpower.",
            ],
            classic_objections=[
                "Some empirical findings suggest people are more influenced by situations than stable character traits.",
                "Raises questions about how stable and reliable virtues really are.",
            ],
        ).model_dump(),
    ]

    strengths = [
        "Connects ethical questions to personal growth, identity, and long-term patterns of life.",
        "Acknowledges that good judgment is needed to balance competing values in real situations.",
        "Resonates with the way people naturally think about role models and moral exemplars.",
    ]

    objections = [
        "Can lack precise action-guidance in specific, novel, or high-stakes cases.",
        "Different cultures may disagree about which traits count as virtues.",
        "Can seem to underplay rules and large-scale consequences.",
    ]

    reflection_questions = [
        "Who are your moral role models, and what virtues do they embody?",
        "Looking back at your choices over the last year, what kind of person are you becoming?",
        "Are there patterns in your life where you regularly fall short of the virtues you admire?",
    ]

    return EthicsVirtueTeachLesson(
        overview=overview,
        historical_roots=historical_roots,
        core_principles=core_principles,
        variants=variants,
        strengths=strengths,
        objections=objections,
        reflection_questions=reflection_questions,
    )

@router.post(
    "/l3/virtue/practice",
    response_model=EthicsVirtuePracticeResponse,
)
async def philosophy_ethics_l3_virtue_practice(
    request: EthicsVirtuePracticeRequest,
) -> EthicsVirtuePracticeResponse:
    """
    Ethics Lane 3 practice: apply virtue ethics to a case,
    focusing on character, habits, and long-term self-shaping.
    """
    dilemma = request.dilemma_text.strip()

    character_focused_summary = (
        "From a virtue ethics perspective, the key question is: what would a wise and virtuous person do here, "
        "and what kind of person will you become if you act in each possible way? Rather than only counting outcomes "
        "or checking rules, this view asks how each option expresses or damages traits like honesty, courage, compassion, "
        "justice, and practical wisdom over time."
    )

    relevant_virtues_and_vices = [
        "Honesty vs. dishonesty",
        "Courage vs. cowardice or rashness",
        "Compassion vs. indifference or sentimentality",
        "Justice vs. favoritism or unfairness",
        "Practical wisdom vs. thoughtlessness or over-analysis",
    ]

    long_term_self_shaping = [
        "Repeated actions, even in small situations, slowly build habits that make certain choices easier or harder.",
        "Choosing convenience or comfort over virtue many times can erode your sense of integrity.",
        "Acting with courage or honesty in hard cases can strengthen your character, making future good actions more likely.",
    ]

    tensions_with_other_frameworks = [
        "Consequentialists may focus on total outcomes and underplay the importance of character and integrity.",
        "Deontologists may focus on rules and duties without attending to how a person grows or shrinks morally through repeated actions.",
        "Virtue ethics can agree that outcomes and duties matter, but insists that 'Who are you becoming?' is also a central ethical question.",
    ]

    self_check_questions = [
        "In your dilemma, which virtues feel most at stake for you personally?",
        "If someone saw only how you handled this case, what would they reasonably infer about your character?",
        "If you repeated this pattern of action many times, would you be proud of the person you would become?",
    ]

    meta_reflection_prompts = [
        "Do you want PRIME to help you mainly with short-term decisions, or also to reflect on your long-term character and habits?",
        "Which virtues do you most want to cultivate over the next five years, and how might that affect choices like this?",
        "Are there environments or relationships you should seek out or avoid because of how they shape your character?",
    ]

    analysis = EthicsVirtuePracticeAnalysis(
        character_focused_summary=character_focused_summary,
        relevant_virtues_and_vices=relevant_virtues_and_vices,
        long_term_self_shaping=long_term_self_shaping,
        tensions_with_other_frameworks=tensions_with_other_frameworks,
    )

    return EthicsVirtuePracticeResponse(
        original_dilemma=dilemma,
        analysis=analysis,
        self_check_questions=self_check_questions,
        meta_reflection_prompts=meta_reflection_prompts,
    )

@router.post(
    "/l3/consequentialism/practice",
    response_model=EthicsConsequentialismPracticeResponse,
)
async def philosophy_ethics_l3_consequentialism_practice(
    request: EthicsConsequentialismPracticeRequest,
) -> EthicsConsequentialismPracticeResponse:
    """
    Ethics Lane 3 practice: apply consequentialism to a hard case,
    and surface where it feels strong and where it feels wrong or limited.
    """
    dilemma = request.dilemma_text.strip()

    act_style_summary = (
        "From an act consequentialist perspective, the central question is: which available option will, in fact, "
        "produce the best overall balance of good over harm for everyone affected? In this mode, we imagine comparing "
        "each option in your case by its likely short- and long-term consequences, and then selecting the option with "
        "the highest expected overall welfare, even if it is personally difficult or conflicts with some common rules."
    )

    rule_or_softened_summary = (
        "A rule or two-level consequentialist asks a slightly different question: which stable rules or patterns of "
        "behavior, if generally followed in similar cases, would lead to the best outcomes over time? Instead of only "
        "asking what maximizes good right now, they also consider trust, rights, and institutions. This can lead them "
        "to keep strong rules (for example, against punishing innocents or breaking serious promises) because such "
        "rules usually make life go better for almost everyone in the long run."
    )

    key_tradeoffs = [
        "Between maximizing overall good in this specific case and respecting rules that protect trust and rights.",
        "Between being flexible and responsive to particular circumstances and having stable, predictable moral guidelines.",
        "Between asking 'What should I do now?' and 'What kind of person, and what kind of practices, make life go better over time?'",
    ]

    places_it_feels_wrong = [
        "Act consequentialism can feel wrong when it seems to permit using an innocent person purely as a means to help others.",
        "Even softened consequentialism can feel unsettling if it asks for very large sacrifices from individuals whenever they could help many others.",
        "Basing everything on predicted outcomes can feel unstable when we know our predictions are limited or biased.",
    ]

    self_check_questions = [
        "When you read a consequentialist analysis of your dilemma, which part feels most intuitive or attractive to you?",
        "Where do you feel a strong 'no' inside, even if the outcome-focused reasoning says 'yes'?",
        "If you adjust the case slightly (more people helped, or more harm to one person), does your judgment change? Why?",
    ]

    meta_reflection_prompts = [
        "Do you want your own ethics to be mostly consequentialist, or do you want strong side-constraints (rights, duties) that hold even when outcomes look tempting?",
        "In your real life, do you more often under-estimate the importance of consequences, or over-focus on them?",
        "If PRIME used consequentialist reasoning to advise you, what safeguards would you want in place so that it does not ignore rights, integrity, or uncertainty?",
    ]

    analysis = EthicsConsequentialismPracticeAnalysis(
        act_style_summary=act_style_summary,
        rule_or_softened_summary=rule_or_softened_summary,
        key_tradeoffs=key_tradeoffs,
        places_it_feels_wrong=places_it_feels_wrong,
    )

    return EthicsConsequentialismPracticeResponse(
        original_dilemma=dilemma,
        analysis=analysis,
        self_check_questions=self_check_questions,
        meta_reflection_prompts=meta_reflection_prompts,
    )

@router.post(
    "/l3/four-lens",
    response_model=EthicsFourLensResponse,
)
async def philosophy_ethics_l3_four_lens(
    request: EthicsFourLensDilemmaRequest,
) -> EthicsFourLensResponse:
    """
    Orchestration endpoint: run a single dilemma through all four deep ethics lanes
    (Consequentialism, Deontology, Virtue Ethics, Care / Relational) and return a combined view.
    """
    dilemma = request.dilemma_text.strip()

    # Call each lane's practice function directly.
    conseq_result = await philosophy_ethics_l3_consequentialism_practice(
        EthicsConsequentialismPracticeRequest(dilemma_text=dilemma)
    )
    deont_result = await philosophy_ethics_l3_deontology_practice(
        EthicsDeontologyPracticeRequest(dilemma_text=dilemma)
    )
    virtue_result = await philosophy_ethics_l3_virtue_practice(
        EthicsVirtuePracticeRequest(dilemma_text=dilemma)
    )
    care_result = await philosophy_ethics_l3_care_practice(
        EthicsCarePracticeRequest(dilemma_text=dilemma)
    )

    summaries = [
        EthicsSingleLensSummary(
            framework="consequentialism",
            headline="Consequentialism L3: outcomes and trade-offs",
            key_question="Which option leads to the best overall outcomes, and where do the trade-offs start to feel disturbing?",
            notes=[
                "Focuses on benefits and harms across all affected parties, including large-scale impacts.",
                "Highlights places where maximizing good might ask you to accept heavy costs for a few.",
            ],
        ),
        EthicsSingleLensSummary(
            framework="deontology",
            headline="Deontology L3: duties, rights, and red lines",
            key_question="Which actions are ruled out or required by duties and rights, even if breaking them could improve outcomes?",
            notes=[
                "Emphasizes moral rules and rights that set limits on what may be done.",
                "Explores conflicts between duties (e.g., truth-telling vs. protection from harm).",
            ],
        ),
        EthicsSingleLensSummary(
            framework="virtue",
            headline="Virtue Ethics L3: character and self-shaping",
            key_question="Who are you becoming if you act this way, and which virtues or vices are you strengthening?",
            notes=[
                "Looks at long-term patterns of action and the kind of person they help you become.",
                "Connects single choices to habits, role models, and a flourishing life.",
            ],
        ),
        EthicsSingleLensSummary(
            framework="care",
            headline="Care / Relational Ethics L3: relationships, vulnerability, and power",
            key_question="Who is involved, who is most vulnerable, and what would caring well for them and yourself look like here?",
            notes=[
                "Attends to relationships, dependency, and emotional life, not just abstract agents.",
                "Tracks power imbalances and care burdens, asking how to respond without erasing anyone's needs.",
            ],
        ),
    ]

    return EthicsFourLensResponse(
        original_dilemma=dilemma,
        summaries=summaries,
        consequentialism=conseq_result,
        deontology=deont_result,
        virtue=virtue_result,
        care=care_result,
    )

def analyze_four_lens_meta(
    four_lens: EthicsFourLensResponse,
) -> dict[str, list[str]]:
    """
    Meta-analysis over the four deep ethics lenses for a single dilemma.

    Returns a dict with:
      - consensus_points: places where all lenses lean in the same direction conceptually
      - disagreement_points: where at least one lens pulls differently
      - pressure_points: key tensions between values (e.g., outcomes vs duties)
    """
    consensus_points: list[str] = []
    disagreement_points: list[str] = []
    pressure_points: list[str] = []

    # Very simple, content-agnostic meta rules for now, based on framework roles.
    # As you add richer signals to the practice responses, you can make this sharper.

    # 1) Consensus heuristic: All four frameworks are engaged and none is "empty".
    if len(four_lens.summaries) == 4:
        consensus_points.append(
            "All four deep ethics frameworks see this as a morally significant dilemma, "
            "not a trivial or purely technical choice."
        )

    # 2) Pressure point: outcomes vs duties
    pressure_points.append(
        "Tension between maximizing good outcomes (consequentialism) and respecting duties/rights that set red lines (deontology)."
    )

    # 3) Pressure point: impartial good vs special relationships
    pressure_points.append(
        "Tension between impartial concern for overall good (consequentialism) and special obligations in close relationships (care ethics)."
    )

    # 4) Pressure point: external actions vs inner character
    pressure_points.append(
        "Tension between focusing on what happens (outcomes and rules) and focusing on who you are becoming (virtue ethics)."
    )

    # 5) Disagreement heuristic: frameworks emphasize different primary questions.
    disagreement_points.append(
        "Frameworks disagree on what should carry the most weight: outcomes, duties, character, or relationships."
    )

    # You can enrich this later using more detailed fields from each practice analysis.
    return {
        "consensus_points": consensus_points,
        "disagreement_points": disagreement_points,
        "pressure_points": pressure_points,
    }

def build_meta_perspectives(
    four_lens: EthicsFourLensResponse,
    meta: dict[str, list[str]],
) -> EthicsMetaPerspectivesResponse:
    """
    Build legalistic and relational meta-perspectives on top of the four deep ethics lenses.
    Legalistic: rules, rights, institutional duties, precedence.
    Relational: relationships, vulnerability, care, and character.
    """
    tension_points = meta.get("pressure_points", [])

    legalistic = EthicsMetaPerspectiveSummary(
        mode=EthicsMetaPerspectiveMode.LEGALISTIC,
        headline="Legalistic view: prioritize rules, rights, and institutional duties.",
        key_concerns=[
            "Which rights or duties must not be violated?",
            "What do relevant laws, contracts, or policies require?",
            "How should similar cases be treated for consistency and fairness?",
        ],
        alignment_with_frameworks=["deontology", "consequentialism"],
        points_of_tension=tension_points,
    )

    relational = EthicsMetaPerspectiveSummary(
        mode=EthicsMetaPerspectiveMode.RELATIONAL,
        headline="Relational view: prioritize relationships, care, and lived context.",
        key_concerns=[
            "Who is most vulnerable or dependent in this situation?",
            "How will this choice affect trust and long-term relationships?",
            "What forms of care, recognition, or repair are owed here?",
        ],
        alignment_with_frameworks=["care", "virtue"],
        points_of_tension=tension_points,
    )

    return EthicsMetaPerspectivesResponse(
        original_dilemma=four_lens.original_dilemma,
        legalistic=legalistic,
        relational=relational,
    )

@router.post(
    "/l2/core-branches/practice",
    response_model=PhilosophyBranchPracticeResponse,
)
async def philosophy_lane2_core_branches_practice(
    request: PhilosophyBranchPracticeRequest,
) -> PhilosophyBranchPracticeResponse:
    """
    Lane 2 practice: classify a user's question by branch and return
    branch-specific prompts that surface values, trade-offs, and uncertainty.
    """
    text = request.question_text.lower()

    # Simple heuristics to classify by branch.
    if any(word in text for word in ["should i", "ought", "right", "wrong", "good", "bad", "moral", "ethical"]):
        branch = PhilosophyBranch.ETHICS
        rationale = "The question uses language about what is right, wrong, good, bad, or what you should do."
        summary = "Ethics studies what is right or wrong, what is good or bad, and how we should live."
        key_questions = [
            "Who is impacted by this choice, and in what ways?",
            "What are the main options, and what are the best reasons for and against each?",
            "Which values are central here (e.g., harm, fairness, loyalty, honesty, autonomy)?",
        ]
        value_prompts = [
            "If two values conflict here, which one are you most willing to sacrifice, and why?",
            "What kind of person are you trying to be in this situation?",
        ]
        next_step = "Try framing your dilemma in terms of concrete options and the values each option honors or threatens."
    elif any(word in text for word in ["government", "policy", "law", "state", "election", "tax", "rights", "democracy", "justice", "equality"]):
        branch = PhilosophyBranch.POLITICAL
        rationale = "The question concerns laws, policies, institutions, or collective justice."
        summary = "Political philosophy studies power, authority, rights, justice, and how societies should be organized."
        key_questions = [
            "Which groups are most affected by this policy or arrangement?",
            "What kind of injustice or risk worries you most here?",
            "Are you prioritizing freedom, equality, stability, security, or something else?",
        ]
        value_prompts = [
            "If a policy benefits many but seriously harms a minority, how should that be weighed?",
            "How would this question look from the perspective of the least advantaged people affected?",
        ]
        next_step = "Try stating the strongest reasonable argument for a position you disagree with on this issue."
    elif any(word in text for word in ["know", "knowledge", "evidence", "certain", "doubt", "prove", "truth", "true", "false"]):
        branch = PhilosophyBranch.EPISTEMOLOGY
        rationale = "The question focuses on knowledge, evidence, or certainty."
        summary = "Epistemology studies what knowledge is, how we get it, and how confident we can be."
        key_questions = [
            "What would you count as good enough evidence on this question?",
            "Are you more afraid of believing something false or of missing an important truth?",
            "Which sources do you trust or distrust here, and why?",
        ]
        value_prompts = [
            "In this domain, is it wiser to be more skeptical or more trusting? Why?",
            "Could any of your trust or distrust be driven by identity or emotion rather than evidence?",
        ]
        next_step = "Write down what you currently believe, your main reasons, and what kind of new information would move you."
    elif any(word in text for word in ["real", "exist", "existence", "reality", "free will", "soul", "time", "identity", "consciousness"]):
        branch = PhilosophyBranch.METAPHYSICS
        rationale = "The question concerns what is real, what exists, or features like time, identity, or free will."
        summary = "Metaphysics studies what is real, what exists, and the basic structure of reality."
        key_questions = [
            "Are you asking mainly what exists, or how some feature of reality (like time or identity) works?",
            "Does your question depend on how we define key terms (like 'self', 'mind', or 'reality')?",
            "Would different answers to this question change how you actually live?",
        ]
        value_prompts = [
            "What are you hoping this question will give you: comfort, clarity, challenge, or something else?",
            "Is there a practical decision in your life that this metaphysical question might influence?",
        ]
        next_step = "Connect the metaphysical question to one concrete life choice it might affect, even indirectly."
    elif any(word in text for word in ["argue", "argument", "logic", "valid", "fallacy", "reasoning", "premise", "conclusion"]):
        branch = PhilosophyBranch.LOGIC
        rationale = "The question is about arguments themselves and whether reasoning is good or bad."
        summary = "Logic studies correct reasoning and the structure of good and bad arguments."
        key_questions = [
            "What is the main conclusion you or someone else is trying to argue for?",
            "What are the explicit premises, and are there hidden assumptions?",
            "Does the conclusion follow from the premises, or could they all be true while the conclusion is false?",
        ]
        value_prompts = [
            "Where are you most tempted to accept weak arguments because you like the conclusion?",
            "Are you holding yourself and others to the same standard of reasoning?",
        ]
        next_step = "Try rewriting the argument you care about in premise–conclusion form and check whether the support is strong."
    elif any(word in text for word in ["art", "beauty", "beautiful", "ugly", "music", "painting", "novel", "movie", "aesthetic"]):
        branch = PhilosophyBranch.AESTHETICS
        rationale = "The question concerns art, beauty, style, or aesthetic experience."
        summary = "Aesthetics studies beauty, art, and the value and meaning of aesthetic experiences."
        key_questions = [
            "Are you asking what makes something art, or what makes it good art?",
            "Do you think judgments of beauty or artistic value are objective, subjective, or something in between?",
            "How does this work of art affect the way you see yourself or others?",
        ]
        value_prompts = [
            "What role do art and beauty play in the kind of life you want to lead?",
            "Can art reveal truths or possibilities that straightforward facts cannot?",
        ]
        next_step = "Pick one artwork or aesthetic experience and describe what you think it reveals or changes for you."
    else:
        branch = PhilosophyBranch.OTHER
        rationale = "The question did not clearly match a single branch; it may mix several areas."
        summary = "Some philosophical questions cut across several branches or do not fit neatly into one category."
        key_questions = [
            "If you had to choose, is your question more about what is true, what is real, what is right, or something else?",
            "Does your question have a strong ethical, political, epistemic, or metaphysical dimension?",
            "Is there a concrete situation in your life that makes this question urgent?",
        ]
        value_prompts = [
            "Which part of this question feels most live and important to you right now?",
            "If you could get a clear answer to only one aspect of this question, which would it be?",
        ]
        next_step = "Try restating your question in a way that makes clear whether it is mainly ethical, political, epistemic, or metaphysical."

    return PhilosophyBranchPracticeResponse(
        original_question=request.question_text,
        branch=branch,
        rationale=rationale,
        branch_summary=summary,
        key_questions=key_questions,
        value_or_epistemic_prompts=value_prompts,
        next_step_suggestion=next_step,
    )

@router.post(
    "/l1/argument-structure/practice",
    response_model=PhilosophyArgumentPracticeResponse,
)
async def philosophy_lane1_argument_practice(
    request: PhilosophyArgumentPracticeRequest,
) -> PhilosophyArgumentPracticeResponse:
    """
    Lane 1b practice: attempt a simple premises/conclusion breakdown of a short text.
    This is heuristic and gentle: it invites the user to refine the breakdown.
    """
    text = request.text.strip()

    # Very simple heuristic: look for common conclusion indicators.
    lower = text.lower()
    conclusion = None

    conclusion_markers = ["therefore", "so ", "so,", "thus", "hence", "consequently"]
    for marker in conclusion_markers:
        if marker in lower:
            idx = lower.find(marker)
            # everything after the marker is treated as conclusion
            conclusion = text[idx + len(marker):].strip(" ,.:;")
            premises_part = text[:idx].strip()
            break
    else:
        # No explicit marker; guess last sentence as conclusion, rest as premises.
        parts = [p.strip() for p in text.replace("?", ".").split(".") if p.strip()]
        if len(parts) >= 2:
            conclusion = parts[-1]
            premises_part = ". ".join(parts[:-1])
        else:
            conclusion = None
            premises_part = text

    # Split premises_part into smaller premises by simple separators.
    raw_premises = []
    for sep in [" because ", " since ", " and ", " but "]:
        if sep in premises_part.lower():
            # crude split, just to get something premise-like
            raw_premises = [p.strip(" ,.:;") for p in premises_part.split(sep) if p.strip()]
            break
    if not raw_premises:
        raw_premises = [premises_part.strip(" ,.:;")] if premises_part.strip() else []

    # Explanation text.
    if conclusion:
        explanation = (
            "I treated the conclusion as the main claim the text seems to be aiming at, "
            "and the premises as the reasons that support it. This is a first guess for you to refine."
        )
    else:
        explanation = (
            "I could not clearly identify a separate conclusion, so I treated the whole text "
            "as a mixture of reasons and claims. You can refine which part you see as the main conclusion."
        )

    refinement_questions = [
        "Does the guessed conclusion match what you were really trying to argue for?",
        "Are any of the guessed premises actually just background information rather than reasons?",
        "Is there an important unstated premise that should be made explicit?",
    ]

    return PhilosophyArgumentPracticeResponse(
        original_text=text,
        guessed_premises=raw_premises,
        guessed_conclusion=conclusion,
        explanation=explanation,
        refinement_questions=refinement_questions,
    )

@router.post(
    "/l1/planner",
    response_model=PhilosophyLane1PlannerResponse,
)
async def philosophy_lane1_planner(
    request: PhilosophyLane1PlannerRequest,
) -> PhilosophyLane1PlannerResponse:
    """
    Simple planner for Lane 1: routes between 'what is philosophy?' teach/practice
    and argument-structure teach/practice, based on mode.
    """

    mode = request.mode

    if mode == PhilosophyLane1Mode.TEACH_WHAT_IS_PHILOSOPHY:
        lesson = await philosophy_lane1_what_is_philosophy()
        return PhilosophyLane1PlannerResponse(
            mode=mode,
            result=lesson.model_dump(),
        )

    if mode == PhilosophyLane1Mode.PRACTICE_QUESTION_KIND:
        payload = request.payload or {}
        question_text = payload.get("question_text", "")
        practice_req = PhilosophyPracticeRequest(question_text=question_text)
        practice_resp = await philosophy_lane1_practice(practice_req)
        return PhilosophyLane1PlannerResponse(
            mode=mode,
            result=practice_resp.model_dump(),
        )

    if mode == PhilosophyLane1Mode.TEACH_ARGUMENT_STRUCTURE:
        lesson = await philosophy_lane1_argument_structure()
        return PhilosophyLane1PlannerResponse(
            mode=mode,
            result=lesson.model_dump(),
        )

    if mode == PhilosophyLane1Mode.PRACTICE_ARGUMENT_STRUCTURE:
        payload = request.payload or {}
        text = payload.get("text", "")
        practice_req = PhilosophyArgumentPracticeRequest(text=text)
        practice_resp = await philosophy_lane1_argument_practice(practice_req)
        return PhilosophyLane1PlannerResponse(
            mode=mode,
            result=practice_resp.model_dump(),
        )

    # Fallback (should not happen if enum is exhaustive)
    return PhilosophyLane1PlannerResponse(
        mode=mode,
        result={"error": "Unsupported mode"},
    )

@router.post(
    "/l2/planner",
    response_model=PhilosophyLane2PlannerResponse,
)
async def philosophy_lane2_planner(
    request: PhilosophyLane2PlannerRequest,
) -> PhilosophyLane2PlannerResponse:
    """
    Simple planner for Lane 2: routes between core-branches teach and practice
    based on mode.
    """
    mode = request.mode

    if mode == PhilosophyLane2Mode.TEACH_CORE_BRANCHES:
        lesson = await philosophy_lane2_core_branches()
        return PhilosophyLane2PlannerResponse(
            mode=mode,
            result=lesson.model_dump(),
        )

    if mode == PhilosophyLane2Mode.PRACTICE_CORE_BRANCHES:
        payload = request.payload or {}
        question_text = payload.get("question_text", "")
        practice_req = PhilosophyBranchPracticeRequest(question_text=question_text)
        practice_resp = await philosophy_lane2_core_branches_practice(practice_req)
        return PhilosophyLane2PlannerResponse(
            mode=mode,
            result=practice_resp.model_dump(),
        )

    return PhilosophyLane2PlannerResponse(
        mode=mode,
        result={"error": "Unsupported mode"},
    )

@router.post(
    "/l3/planner",
    response_model=PhilosophyLane3PlannerResponse,
)
async def philosophy_lane3_planner(
    request: PhilosophyLane3PlannerRequest,
) -> PhilosophyLane3PlannerResponse:
    """
    Simple planner for Lane 3 (Ethics I): routes between ethics-intro teach and practice.
    """
    mode = request.mode

    if mode == PhilosophyLane3Mode.TEACH_ETHICS_INTRO:
        lesson = await philosophy_lane3_ethics_intro()
        return PhilosophyLane3PlannerResponse(
            mode=mode,
            result=lesson.model_dump(),
        )

    if mode == PhilosophyLane3Mode.PRACTICE_ETHICS_INTRO:
        payload = request.payload or {}
        dilemma_text = payload.get("dilemma_text", "")
        practice_req = EthicsIntroPracticeRequest(dilemma_text=dilemma_text)
        practice_resp = await philosophy_lane3_ethics_intro_practice(practice_req)
        return PhilosophyLane3PlannerResponse(
            mode=mode,
            result=practice_resp.model_dump(),
        )

    return PhilosophyLane3PlannerResponse(
        mode=mode,
        result={"error": "Unsupported mode"},
    )

@router.post(
    "/l5/planner",
    response_model=PhilosophyLane5PlannerResponse,
)
async def philosophy_lane5_planner(
    request: PhilosophyLane5PlannerRequest,
) -> PhilosophyLane5PlannerResponse:
    """
    Planner for Lane 5 (deep normative ethics).
    Supports Consequentialism L3, Deontology L3, Virtue Ethics L3, and Care / Relational Ethics L3
    in both teach and practice modes.
    """
    mode = request.mode

    if mode == PhilosophyLane5Mode.TEACH_CONSEQUENTIALISM_L3:
        lesson = await philosophy_ethics_l3_consequentialism_teach()
        return PhilosophyLane5PlannerResponse(
            mode=mode,
            result=lesson.model_dump(),
        )

    if mode == PhilosophyLane5Mode.PRACTICE_CONSEQUENTIALISM_L3:
        payload = request.payload or {}
        dilemma_text = payload.get("dilemma_text", "")
        practice_req = EthicsConsequentialismPracticeRequest(dilemma_text=dilemma_text)
        practice_resp = await philosophy_ethics_l3_consequentialism_practice(practice_req)
        return PhilosophyLane5PlannerResponse(
            mode=mode,
            result=practice_resp.model_dump(),
        )

    if mode == PhilosophyLane5Mode.TEACH_DEONTOLOGY_L3:
        lesson = await philosophy_ethics_l3_deontology_teach()
        return PhilosophyLane5PlannerResponse(
            mode=mode,
            result=lesson.model_dump(),
        )

    if mode == PhilosophyLane5Mode.PRACTICE_DEONTOLOGY_L3:
        payload = request.payload or {}
        dilemma_text = payload.get("dilemma_text", "")
        practice_req = EthicsDeontologyPracticeRequest(dilemma_text=dilemma_text)
        practice_resp = await philosophy_ethics_l3_deontology_practice(practice_req)
        return PhilosophyLane5PlannerResponse(
            mode=mode,
            result=practice_resp.model_dump(),
        )

    if mode == PhilosophyLane5Mode.TEACH_VIRTUE_L3:
        lesson = await philosophy_ethics_l3_virtue_teach()
        return PhilosophyLane5PlannerResponse(
            mode=mode,
            result=lesson.model_dump(),
        )

    if mode == PhilosophyLane5Mode.PRACTICE_VIRTUE_L3:
        payload = request.payload or {}
        dilemma_text = payload.get("dilemma_text", "")
        practice_req = EthicsVirtuePracticeRequest(dilemma_text=dilemma_text)
        practice_resp = await philosophy_ethics_l3_virtue_practice(practice_req)
        return PhilosophyLane5PlannerResponse(
            mode=mode,
            result=practice_resp.model_dump(),
        )

    if mode == PhilosophyLane5Mode.TEACH_CARE_L3:
        lesson = await philosophy_ethics_l3_care_teach()
        return PhilosophyLane5PlannerResponse(
            mode=mode,
            result=lesson.model_dump(),
        )

    if mode == PhilosophyLane5Mode.PRACTICE_CARE_L3:
        payload = request.payload or {}
        dilemma_text = payload.get("dilemma_text", "")
        practice_req = EthicsCarePracticeRequest(dilemma_text=dilemma_text)
        practice_resp = await philosophy_ethics_l3_care_practice(practice_req)
        return PhilosophyLane5PlannerResponse(
            mode=mode,
            result=practice_resp.model_dump(),
        )

    return PhilosophyLane5PlannerResponse(
        mode=mode,
        result={"error": "Unsupported mode"},
    )

@router.post(
    "/l4/planner",
    response_model=PhilosophyLane4PlannerResponse,
)
async def philosophy_lane4_planner(
    request: PhilosophyLane4PlannerRequest,
) -> PhilosophyLane4PlannerResponse:
    """
    Simple planner for Lane 4 (Ethics II: digital & AI ethics).
    """
    mode = request.mode

    if mode == PhilosophyLane4Mode.TEACH_ETHICS_DIGITAL:
        lesson = await philosophy_lane4_ethics_digital()
        return PhilosophyLane4PlannerResponse(
            mode=mode,
            result=lesson.model_dump(),
        )

    if mode == PhilosophyLane4Mode.PRACTICE_ETHICS_DIGITAL:
        payload = request.payload or {}
        dilemma_text = payload.get("dilemma_text", "")
        raw_tags = payload.get("context_tags", None)

        context_tags = None
        if raw_tags is not None:
            # Map raw strings to enum values where possible, ignore unknowns.
            mapped = []
            for t in raw_tags:
                try:
                    mapped.append(EthicsDigitalContextTag(t))
                except ValueError:
                    continue
            context_tags = mapped or None

        practice_req = EthicsDigitalPracticeRequest(
            dilemma_text=dilemma_text,
            context_tags=context_tags,
        )
        practice_resp = await philosophy_lane4_ethics_digital_practice(practice_req)
        return PhilosophyLane4PlannerResponse(
            mode=mode,
            result=practice_resp.model_dump(),
        )

    return PhilosophyLane4PlannerResponse(
        mode=mode,
        result={"error": "Unsupported mode"},
    )

# ============================================================
# Ethics conceptual engineering: harm, coercion, etc.
# ============================================================


def _load_ethics_concepts() -> list[EthicsConcept]:
    """
    Initial hard-coded set of ethics concepts.
    We start with harm, coercion, consent, autonomy, fairness, loyalty, and respect.
    """
    harm = EthicsConcept(
        id="ethics.concept.harm",
        name="Harm",
        working_definition=(
            "Harm is a setback to a person's important interests or well-being, "
            "such as physical injury, psychological damage, serious loss of opportunities, "
            "or violations of dignity."
        ),
        dimensions=[
            EthicsConceptDimension(
                name="Magnitude",
                description="How serious is the setback to well-being?"
            ),
            EthicsConceptDimension(
                name="Directness",
                description="Is the harm directly caused, or mediated through others or systems?"
            ),
            EthicsConceptDimension(
                name="Temporal_Scope",
                description="Is the harm short-term, long-term, or intergenerational?"
            ),
        ],
        contrast_concepts=["offense", "mere_discomfort", "pure_risk_without_realization"],
        notes=[
            "Not every offense or discomfort counts as harm.",
            "Risk of harm can matter ethically even before harm occurs.",
        ],
    )

    coercion = EthicsConcept(
        id="ethics.concept.coercion",
        name="Coercion",
        working_definition=(
            "Coercion is using threats or control to leave someone with no reasonable alternative "
            "but to comply, undermining the voluntariness of their choice."
        ),
        dimensions=[
            EthicsConceptDimension(
                name="Threat_or_Control",
                description="Presence of a threat, penalty, or controlling condition that pressures compliance."
            ),
            EthicsConceptDimension(
                name="Alternatives",
                description="Whether the person has any reasonable alternative options."
            ),
            EthicsConceptDimension(
                name="Intention_or_Structure",
                description="Whether the situation is structured to force compliance rather than invite consent."
            ),
        ],
        contrast_concepts=["persuasion", "offer", "manipulation"],
        notes=[
            "Offers can become coercive if background conditions remove real alternatives.",
        ],
    )

    consent = EthicsConcept(
        id="ethics.concept.consent",
        name="Consent",
        working_definition=(
            "Consent is a person's voluntary, informed, and competent agreement to a proposal "
            "or arrangement, given without coercion or significant deception."
        ),
        dimensions=[
            EthicsConceptDimension(
                name="Information",
                description="Whether the person has relevant, understandable information about what they are agreeing to."
            ),
            EthicsConceptDimension(
                name="Voluntariness",
                description="Whether the agreement is free from coercion, manipulation, or undue pressure."
            ),
            EthicsConceptDimension(
                name="Competence",
                description="Whether the person has the capacity to understand and decide."
            ),
        ],
        contrast_concepts=["mere_acquiescence", "coerced_agreement", "uninformed_agreement"],
        notes=[
            "Consent can be defective if any of information, voluntariness, or competence is missing.",
            "Power imbalances can quietly undermine voluntariness even when words of agreement are spoken.",
        ],
    )

    autonomy = EthicsConcept(
        id="ethics.concept.autonomy",
        name="Autonomy",
        working_definition=(
            "Autonomy is a person's ability to govern their own life and decisions in line with their "
            "values and reasons, free from controlling interference and severe ignorance."
        ),
        dimensions=[
            EthicsConceptDimension(
                name="Self_Governance",
                description="Whether the person can set and pursue their own goals."
            ),
            EthicsConceptDimension(
                name="Freedom_From_Control",
                description="Whether others or systems are unduly controlling their options or choices."
            ),
            EthicsConceptDimension(
                name="Reflective_Endorsement",
                description="Whether the person can reflect on and endorse their own motives and plans."
            ),
        ],
        contrast_concepts=["paternalism", "manipulation", "mere_preference_satisfaction"],
        notes=[
            "Respecting autonomy often requires supporting informed, reflective choice, not just non-interference.",
        ],
    )

    fairness = EthicsConcept(
        id="ethics.concept.fairness",
        name="Fairness",
        working_definition=(
            "Fairness is the impartial and consistent treatment of people according to relevant reasons, "
            "including how benefits and burdens are distributed and how rules are applied."
        ),
        dimensions=[
            EthicsConceptDimension(
                name="Procedural_Fairness",
                description="Whether processes and rules are applied consistently and transparently."
            ),
            EthicsConceptDimension(
                name="Distributive_Fairness",
                description="Whether benefits and burdens are allocated in a justifiable way."
            ),
            EthicsConceptDimension(
                name="Recognition_Respect",
                description="Whether people are treated as equals in status and voice."
            ),
        ],
        contrast_concepts=["bias", "nepotism", "pure_efficiency_without_justice"],
        notes=[
            "Different theories of justice give different tests for when a distribution is fair.",
        ],
    )

    loyalty = EthicsConcept(
        id="ethics.concept.loyalty",
        name="Loyalty",
        working_definition=(
            "Loyalty is a stable commitment to stand by a person, group, or cause, especially when it is "
            "costly, while still bounded by broader moral constraints."
        ),
        dimensions=[
            EthicsConceptDimension(
                name="Commitment",
                description="Depth and stability of the bond over time."
            ),
            EthicsConceptDimension(
                name="Priority",
                description="How much weight the relationship gets compared to other duties and interests."
            ),
            EthicsConceptDimension(
                name="Moral_Bounds",
                description="Whether loyalty stays within limits set by broader justice and respect for others."
            ),
        ],
        contrast_concepts=["favoritism", "blind_loyalty", "mere_affection"],
        notes=[
            "Loyalty can conflict with impartial fairness; part of conceptual work is deciding where its limits lie.",
        ],
    )

    respect = EthicsConcept(
        id="ethics.concept.respect",
        name="Respect",
        working_definition=(
            "Respect is recognizing and responding to the moral standing of persons, including their rights, "
            "dignity, and perspective, in how we treat and speak about them."
        ),
        dimensions=[
            EthicsConceptDimension(
                name="Status_Recognition",
                description="Seeing others as having equal basic moral standing."
            ),
            EthicsConceptDimension(
                name="Rights_and_Boundaries",
                description="Honoring personal boundaries, rights, and legitimate expectations."
            ),
            EthicsConceptDimension(
                name="Attitude_and_Expression",
                description="Whether tone, language, and behavior express regard rather than contempt."
            ),
        ],
        contrast_concepts=["contempt", "instrumentalization", "mere_politeness_without_real_regard"],
        notes=[
            "Respect has both action-level and attitude-level components.",
        ],
    )

    return [harm, coercion, consent, autonomy, fairness, loyalty, respect]

_ETHICS_CONCEPTS: dict[str, EthicsConcept] = {c.id: c for c in _load_ethics_concepts()}

class PhilosophyFoundationsOverview(BaseModel):
    """
    High-level overview of PRIME's philosophy foundations lanes:
    logic, methods, metaphysics, ethics.

    We represent each lane at the concept level; detailed professor/grad/teacher
    views and practice sets are available through the specific endpoints.
    """
    logic_concepts: list[LogicConcept]
    methods_concepts: list[MethodsConcept]
    metaphysics_concepts: list[MetaphysicsConcept]

# =========================================
# Logic & Argumentation core concepts (Lane L1)
# =========================================

_LOGIC_CONCEPTS: dict[LogicConceptId, LogicConcept] = {
    LogicConceptId.ARGUMENT_STRUCTURE: LogicConcept(
        id=LogicConceptId.ARGUMENT_STRUCTURE,
        name="Argument Structure",
        working_definition=(
            "An argument is a set of reasons (premises) offered to support a claim (conclusion), "
            "with structure that can be made explicit and evaluated for strength or validity."
        ),
        notes=[
            "Distinguish explanation vs argument; not every set of sentences is an argument.",
            "Structure underlies both informal reasoning and formal logic.",
        ],
    ),
    LogicConceptId.FALLACIES: LogicConcept(
        id=LogicConceptId.FALLACIES,
        name="Common Fallacies",
        working_definition=(
            "A fallacy is a recurring pattern of poor reasoning that can make an argument "
            "persuasive in appearance while weak or defective in support."
        ),
        notes=[
            "Includes informal fallacies (ad hominem, straw man, slippery slope, etc.) [web:121][web:124]",
            "Fallacies are tools for diagnosis, not mere labels for people.",
        ],
    ),
    LogicConceptId.VALIDITY_SOUNDNESS: LogicConcept(
        id=LogicConceptId.VALIDITY_SOUNDNESS,
        name="Validity and Soundness",
        working_definition=(
            "A deductive argument is valid if, assuming its premises were true, its conclusion "
            "would have to be true; it is sound if it is valid and its premises are in fact true."
        ),
        notes=[
            "Validity is about form; soundness adds truth of premises. [web:119][web:122]",
            "Valid arguments can have false premises and false conclusions; sound arguments cannot have false conclusions.",
        ],
    ),
    LogicConceptId.PROOF_METHODS: LogicConcept(
        id=LogicConceptId.PROOF_METHODS,
        name="Proof Methods",
        working_definition=(
            "Proof methods are systematic ways of showing that a conclusion follows from premises, "
            "including direct proof, proof by contradiction, and proof by cases."
        ),
        notes=[
            "Proofs connect everyday reasons to formal systems. [web:119][web:125]",
            "Different systems: natural deduction, axiomatic systems, sequent calculi.",
        ],
    ),
    LogicConceptId.PREDICATE_LOGIC: LogicConcept(
        id=LogicConceptId.PREDICATE_LOGIC,
        name="Predicate Logic and Quantifiers",
        working_definition=(
            "Predicate logic extends propositional logic with quantifiers (like 'all', 'some') "
            "and predicates, allowing finer analysis of argument structure in natural language."
        ),
        notes=[
            "Captures arguments involving 'all', 'some', 'none' that propositional logic cannot.",
            "Foundation for formal semantics and much of analytic philosophy. [web:119][web:125]",
        ],
    ),
    LogicConceptId.MODAL_NONCLASSICAL: LogicConcept(
        id=LogicConceptId.MODAL_NONCLASSICAL,
        name="Modal and Non-Classical Logics",
        working_definition=(
            "Modal and non-classical logics extend or modify classical logic to reason about "
            "necessity, possibility, time, obligation, knowledge, or to alter basic principles "
            "like excluded middle."
        ),
        notes=[
            "Modal logics for necessity/possibility, knowledge, obligation. [web:123][web:126]",
            "Non-classical families: intuitionistic, many-valued, paraconsistent.",
        ],
    ),
}

def _build_logic_concept_lesson(concept: LogicConcept) -> "LogicConceptLesson":
    """
    Construct a triple-role logic lesson for a single concept.
    Content is concrete and can be deepened later.
    """
    cid = concept.id

    # ARGUMENT STRUCTURE
    if cid == LogicConceptId.ARGUMENT_STRUCTURE:
        level = CurriculumLevel.SCHOOL_SECONDARY
        professor_view = LogicConceptLessonProfessorView(
            spine_position=(
                "Begins in K–8 as giving reasons for opinions; "
                "becomes explicit in high-school critical thinking; "
                "is formalized in undergrad logic and advanced in grad-level proof theory."
            ),
            connections_to_other_areas=[
                "philosophical reading and writing",
                "legal reasoning and case analysis",
                "scientific explanation and hypothesis testing",
            ],
            deeper_theories=[
                "theory of argument schemes and defeasible reasoning",
                "formal argumentation frameworks in AI",
            ],
        )
        grad_view = LogicConceptLessonGradView(
            core_tensions=[
                "Where is the line between an explanation and an argument?",
                "How much implicit structure can we add when reconstructing arguments charitably?",
            ],
            edge_cases=[
                "Texts that mix narrative, rhetoric, and scattered reasons.",
                "Arguments with suppressed or culturally assumed premises.",
            ],
            open_questions=[
                "How should large language models represent argument structure for robust reasoning?",
            ],
        )
        teacher_steps = [
            LogicConceptLessonTeacherStep(
                order=1,
                prompt="First, find the sentence that looks most like the main point.",
                example="\"Therefore, we should start school later in the morning.\"",
                check_question="What is the main conclusion in this example?"
            ),
            LogicConceptLessonTeacherStep(
                order=2,
                prompt="Next, look for sentences that give reasons for that main point.",
                example="\"Students are very tired early in the morning\"; \"Extra sleep improves learning.\"",
                check_question="Name one reason that supports the conclusion."
            ),
            LogicConceptLessonTeacherStep(
                order=3,
                prompt="Put it together as: premises → conclusion in your own words.",
                example="Because students are tired and extra sleep helps learning, we should start school later.",
                check_question="Can you restate this argument as 'Because X and Y, therefore Z'?"
            ),
        ]
        practice_questions = [
            LogicConceptPracticeQuestion(
                prompt=(
                    "Take a short paragraph from a news article or post you read recently. "
                    "Write one sentence as the conclusion and list 1–3 sentences as its premises."
                ),
                expected_shape="argument_outline",
            ),
            LogicConceptPracticeQuestion(
                prompt="Write one argument of your own about a school or work policy, clearly labeling premises and conclusion.",
                expected_shape="short_text",
            ),
        ]

    # FALLACIES
    elif cid == LogicConceptId.FALLACIES:
        level = CurriculumLevel.SCHOOL_SECONDARY
        professor_view = LogicConceptLessonProfessorView(
            spine_position=(
                "Appears informally in K–8 as 'that’s not a good reason'; "
                "is named in high-school critical thinking; "
                "is systematized in undergrad logic and debated in grad-level philosophy of argument."
            ),
            connections_to_other_areas=[
                "rhetoric and communication",
                "media literacy and misinformation analysis",
                "political argument and public discourse",
            ],
            deeper_theories=[
                "informal logic and argumentation theory",
                "pragmatic theories of fallacies as dialogue moves",
            ],
        )
        grad_view = LogicConceptLessonGradView(
            core_tensions=[
                "Are fallacies best understood as structural defects or as context-dependent dialogue missteps?",
                "When does strong rhetoric cross the line into fallacious reasoning?",
            ],
            edge_cases=[
                "Personal attacks that are relevant to credibility vs irrelevant ad hominem.",
                "Slippery slope arguments that are well-supported vs purely speculative.",
            ],
            open_questions=[
                "How can AI systems flag fallacies without oversimplifying complex arguments?",
            ],
        )
        teacher_steps = [
            LogicConceptLessonTeacherStep(
                order=1,
                prompt="Start with a simple pattern: attacking a person instead of their reasons.",
                example="\"You’re just a kid, so your argument about climate policy doesn’t matter.\"",
                check_question="What is being attacked here: the person or the reasons?"
            ),
            LogicConceptLessonTeacherStep(
                order=2,
                prompt="Now spot when someone misrepresents another’s view to make it easier to attack.",
                example="\"She said we should fund education more, so she clearly wants to ignore healthcare.\"",
                check_question="What important part of the original position was left out or distorted?"
            ),
            LogicConceptLessonTeacherStep(
                order=3,
                prompt="Connect fallacies to real-life decisions: ask 'Would this still be convincing if I didn’t like or dislike the person?'",
                example="A social media post that gets many likes because it mocks a group instead of addressing their reasons.",
                check_question="If you remove the jokes or insults, is there still a strong argument left?"
            ),
        ]
        practice_questions = [
            LogicConceptPracticeQuestion(
                prompt="Write one example of an ad hominem attack and then rewrite it into a version that focuses on reasons instead.",
                expected_shape="short_text",
            ),
            LogicConceptPracticeQuestion(
                prompt="Find a short online post and identify whether it contains a straw man or not. Explain your judgment.",
                expected_shape="short_text",
            ),
        ]

    # VALIDITY & SOUNDNESS
    elif cid == LogicConceptId.VALIDITY_SOUNDNESS:
        level = CurriculumLevel.UNDERGRAD_INTRO
        professor_view = LogicConceptLessonProfessorView(
            spine_position=(
                "Introduced gently in high school as 'good form' of reasoning; "
                "made precise in undergrad logic; "
                "becomes part of meta-theory in grad work on soundness and completeness."
            ),
            connections_to_other_areas=[
                "mathematical proof and theorem provers",
                "legal reasoning and burden of proof",
                "formal verification in computer science",
            ],
            deeper_theories=[
                "soundness and completeness theorems for proof systems",
                "non-monotonic and defeasible logics",
            ],
        )
        grad_view = LogicConceptLessonGradView(
            core_tensions=[
                "How well does the formal notion of validity capture intuitive good reasoning?",
                "What to do with arguments that are strong but not strictly valid (inductive arguments)?",
            ],
            edge_cases=[
                "Arguments with obviously true premises and conclusion but invalid structure.",
                "Arguments that are valid but intuitively misleading or question-begging.",
            ],
            open_questions=[
                "How should AI balance strict validity with probabilistic and defeasible reasoning?",
            ],
        )
        teacher_steps = [
            LogicConceptLessonTeacherStep(
                order=1,
                prompt="Start with the idea: if the premises were true, would the conclusion have to be true?",
                example="\"All humans are mortal. Socrates is a human. So, Socrates is mortal.\"",
                check_question="If the two premises are true, can the conclusion be false?"
            ),
            LogicConceptLessonTeacherStep(
                order=2,
                prompt="Show a similar-looking argument that fails that test.",
                example="\"All dogs are animals. My pet is an animal. So, my pet is a dog.\"",
                check_question="Could the premises be true while the conclusion is false here?"
            ),
            LogicConceptLessonTeacherStep(
                order=3,
                prompt="Explain soundness: valid form plus actually true premises.",
                example="If it were true that \"All students in this class live on Mars\", then valid reasoning could still give false conclusions about real people.",
                check_question="Can an argument be valid but unsound? Why?"
            ),
        ]
        practice_questions = [
            LogicConceptPracticeQuestion(
                prompt="Construct one valid but unsound argument (false premise, true conclusion) and explain why it is valid but unsound.",
                expected_shape="short_text",
            ),
            LogicConceptPracticeQuestion(
                prompt="Given a short argument you care about, rewrite it in premise–conclusion form and ask whether it is valid, sound, both, or neither.",
                expected_shape="short_text",
            ),
        ]

    # PROOF METHODS
    elif cid == LogicConceptId.PROOF_METHODS:
        level = CurriculumLevel.UNDERGRAD_CORE
        professor_view = LogicConceptLessonProfessorView(
            spine_position=(
                "Appears implicitly in algebra as 'show your work'; "
                "becomes explicit in undergrad proof courses; "
                "forms the backbone of grad-level mathematics and logic."
            ),
            connections_to_other_areas=[
                "undergraduate and graduate mathematics",
                "computer science (program verification, type systems)",
                "formal epistemology and meta-logic",
            ],
            deeper_theories=[
                "proof theory and normalization",
                "connections between proofs and programs (Curry–Howard)",
            ],
        )
        grad_view = LogicConceptLessonGradView(
            core_tensions=[
                "Is proof primarily a formal object or a communicative practice between humans?",
                "How do informal proofs relate to fully formal derivations?",
            ],
            edge_cases=[
                "Proof sketches that experts find convincing but are not fully detailed.",
                "Computer-assisted proofs that humans cannot easily check line by line.",
            ],
            open_questions=[
                "What counts as an acceptable proof for AI systems used in safety-critical contexts?",
            ],
        )
        teacher_steps = [
            LogicConceptLessonTeacherStep(
                order=1,
                prompt="Begin with a very simple direct proof pattern.",
                example="To prove: If a number is even, then its square is even. Reason: an even number is 2k, so its square is 4k², which is again even.",
                check_question="What assumption did we start with, and what did we show?"
            ),
            LogicConceptLessonTeacherStep(
                order=2,
                prompt="Introduce proof by contradiction with a friendly example.",
                example="Assume √2 is rational, then derive a contradiction about parity of a and b in its supposed fraction form.",
                check_question="What does it mean to prove something by assuming the opposite and reaching a contradiction?"
            ),
            LogicConceptLessonTeacherStep(
                order=3,
                prompt="Show how argument structure in prose can be turned into a numbered proof outline.",
                example="Numbered steps: 1) Suppose n is even. 2) Then n = 2k. 3) So n² = 4k². 4) Thus n² is even.",
                check_question="How does the numbered outline make the reasoning clearer than a single paragraph?"
            ),
        ]
        practice_questions = [
            LogicConceptPracticeQuestion(
                prompt="Take a short argument you like and rewrite it as a step-by-step proof outline with numbered steps.",
                expected_shape="argument_outline",
            ),
            LogicConceptPracticeQuestion(
                prompt="Write a simple proof by contradiction of your own (for example, about divisibility or parity) and label the assumption that leads to contradiction.",
                expected_shape="short_text",
            ),
        ]

    # PREDICATE LOGIC
    elif cid == LogicConceptId.PREDICATE_LOGIC:
        level = CurriculumLevel.UNDERGRAD_CORE
        professor_view = LogicConceptLessonProfessorView(
            spine_position=(
                "Informal 'all' and 'some' talk appears early; "
                "formal quantifiers surface in high school for strong students; "
                "fully developed in undergrad logic and essential for grad-level semantics and meta-logic."
            ),
            connections_to_other_areas=[
                "philosophy of language and formal semantics",
                "foundations of mathematics and set theory",
                "knowledge representation in AI",
            ],
            deeper_theories=[
                "first-order vs higher-order logic",
                "completeness and compactness theorems",
            ],
        )
        grad_view = LogicConceptLessonGradView(
            core_tensions=[
                "Limits of first-order logic for capturing intuitive concepts like 'finiteness' or 'truth'.",
                "Trade-offs between expressive power and meta-theoretic properties (completeness, decidability).",
            ],
            edge_cases=[
                "Sentences that look similar in natural language but differ in formalization scope ambiguity.",
                "\"Everyone loves someone\" vs \"There is someone whom everyone loves.\"",
            ],
            open_questions=[
                "How should large-scale AI systems represent quantification to align with human reasoning?",
            ],
        )
        teacher_steps = [
            LogicConceptLessonTeacherStep(
                order=1,
                prompt="Start with everyday 'all' and 'some' statements.",
                example="\"All dogs are mammals.\" \"Some students like math.\"",
                check_question="Can you point to one case that makes 'All dogs are mammals' false?"
            ),
            LogicConceptLessonTeacherStep(
                order=2,
                prompt="Show how we can use simple symbols to capture these patterns.",
                example="Let D(x) mean 'x is a dog' and M(x) mean 'x is a mammal'; then 'All dogs are mammals' becomes ∀x(D(x) → M(x)).",
                check_question="In words, what does ∀x(D(x) → M(x)) say?"
            ),
            LogicConceptLessonTeacherStep(
                order=3,
                prompt="Contrast two similar but different quantified sentences.",
                example="\"Everyone loves someone\" vs \"There is someone whom everyone loves.\"",
                check_question="Can you describe a situation where the first is true but the second is false?"
            ),
        ]
        practice_questions = [
            LogicConceptPracticeQuestion(
                prompt="Formalize two everyday sentences involving 'all' or 'some' into predicate-logic form, then explain in plain language what each formalization means.",
                expected_shape="short_text",
            ),
            LogicConceptPracticeQuestion(
                prompt="Give an example where 'Everyone loves someone' is true but 'There is someone whom everyone loves' is false.",
                expected_shape="short_text",
            ),
        ]

    # MODAL & NON-CLASSICAL
    else:  # LogicConceptId.MODAL_NONCLASSICAL
        level = CurriculumLevel.GRAD_PHD_CORE
        professor_view = LogicConceptLessonProfessorView(
            spine_position=(
                "Hints appear in fiction and everyday speech (could, must, might); "
                "formal modal logic is usually undergrad/grad; "
                "non-classical logics are grad-level specializations."
            ),
            connections_to_other_areas=[
                "metaphysics (possibility, necessity, possible worlds)",
                "epistemology and doxastic logic (knowledge, belief)",
                "ethics and deontic logic (obligation, permission)",
                "computer science (temporal logic, program logics)",
            ],
            deeper_theories=[
                "Kripke semantics for modal logics",
                "intuitionistic and many-valued logics",
                "paraconsistent logics and inconsistency-tolerant reasoning",
            ],
        )
        grad_view = LogicConceptLessonGradView(
            core_tensions=[
                "How literally should we take 'possible worlds' talk in modal metaphysics?",
                "Should logic reflect idealized reasoning or actual human reasoning under limitations?",
            ],
            edge_cases=[
                "Reasoning under vague possibility and changing evidence.",
                "Handling inconsistent but non-trivial theories with paraconsistent logics.",
            ],
            open_questions=[
                "Which non-classical logics, if any, should be built into AI systems for robust reasoning under inconsistency?",
            ],
        )
        teacher_steps = [
            LogicConceptLessonTeacherStep(
                order=1,
                prompt="Begin with everyday modal language: could, must, might.",
                example="\"It must be raining\" vs \"It might be raining.\"",
                check_question="In your own words, what is the difference between 'must' and 'might' here?"
            ),
            LogicConceptLessonTeacherStep(
                order=2,
                prompt="Show that we can treat these as extra operators on top of ordinary claims.",
                example="We can think of □P as 'P must be true' and ◇P as 'P might be true.'",
                check_question="If □P is true, what does that say about P in all the cases we consider possible?"
            ),
            LogicConceptLessonTeacherStep(
                order=3,
                prompt="Connect to other kinds of 'must' and 'may' such as rules, knowledge, and time.",
                example="\"You must stop at a red light\" (obligation) vs \"This must be the right key\" (inference).",
                check_question="How are these two uses of 'must' similar and how are they different?"
            ),
        ]
        practice_questions = [
            LogicConceptPracticeQuestion(
                prompt="Write three sentences using 'must', 'might', and 'may' and say whether each is about rules, knowledge, or possibility.",
                expected_shape="short_text",
            ),
            LogicConceptPracticeQuestion(
                prompt="Describe, in simple terms, what it would mean for □P to be true in a possible-worlds picture.",
                expected_shape="short_text",
            ),
        ]

    teacher_view = LogicConceptLessonTeacherView(steps=teacher_steps)
    practice_set = LogicConceptPracticeSet(
        concept_id=concept.id,
        level=level,
        questions=practice_questions,
    )

    return LogicConceptLesson(
        id=f"philo.logic.{concept.id}",
        concept=concept,
        subject=SubjectId.PHILOSOPHY_CORE,
        domain=DomainId.HUMANITIES,
        level=level,
        professor_view=professor_view,
        grad_view=grad_view,
        teacher_view=teacher_view,
        practice=practice_set,
    )


@router.get(
    "/l1/logic-concepts/overview",
    response_model=list[LogicConceptLesson],
)
async def logic_concepts_overview_l1() -> list[LogicConceptLesson]:
    """
    Lane 1 overview: core logic & argumentation concepts with triple-role lessons.
    """
    lessons: list[LogicConceptLesson] = []
    for concept in _LOGIC_CONCEPTS.values():
        lessons.append(_build_logic_concept_lesson(concept))
    return lessons


@router.get(
    "/l1/logic-concepts/{concept_id}",
    response_model=LogicConceptLesson,
)
async def logic_concept_detail_l1(concept_id: LogicConceptId) -> LogicConceptLesson:
    """
    Lane 1 detail: one logic concept with professor, grad, teacher, and practice views.
    """
    concept = _LOGIC_CONCEPTS.get(concept_id)
    if concept is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unknown logic concept")
    return _build_logic_concept_lesson(concept)


class LogicConceptPracticeAnswer(BaseModel):
    """
    One answer from the learner for a practice question.
    PRIME will log and later use this to adapt teaching.
    """
    question_index: int
    response_text: str


class LogicConceptPracticeSubmission(BaseModel):
    """
    Submission of practice answers for a given concept at a given level.
    """
    concept_id: LogicConceptId
    level: CurriculumLevel
    answers: list[LogicConceptPracticeAnswer]


class LogicConceptPracticeFeedback(BaseModel):
    """
    Minimal but concrete feedback loop; no placeholder 'todo'.
    """
    concept_id: LogicConceptId
    level: CurriculumLevel
    reflections: list[str]
    suggestions_for_next_steps: list[str]


@router.post(
    "/l1/logic-concepts/{concept_id}/practice",
    response_model=LogicConceptPracticeFeedback,
)
async def logic_concept_practice_l1(
    concept_id: LogicConceptId,
    submission: LogicConceptPracticeSubmission,
) -> LogicConceptPracticeFeedback:
    """
    Lane 1 practice: PRIME reads the learner's answers, reflects like a grad student,
    and responds with concrete suggestions for what to practice next.
    """
    concept = _LOGIC_CONCEPTS.get(concept_id)
    if concept is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unknown logic concept")

    # Simple, concrete reflection based on concept, no stubs.
    reflections: list[str] = []
    suggestions: list[str] = []

    if concept_id == LogicConceptId.ARGUMENT_STRUCTURE:
        reflections.append(
            "Focus on clearly separating premises from the conclusion. "
            "Make sure each premise directly supports the conclusion you chose."
        )
        suggestions.append(
            "Next, try rewriting one of your arguments so that each premise is a separate numbered line."
        )
    elif concept_id == LogicConceptId.FALLACIES:
        reflections.append(
            "Pay attention to whether your examples attack the person or their reasons, "
            "and whether any position is simplified into an easier but distorted target."
        )
        suggestions.append(
            "Next, take a real argument you care about and check whether you can describe it without any fallacy labels at all—just by explaining what feels weak about the reasoning."
        )
    elif concept_id == LogicConceptId.VALIDITY_SOUNDNESS:
        reflections.append(
            "Check whether your 'valid but unsound' example truly cannot have true premises and a false conclusion. "
            "If it can, then it is not valid."
        )
        suggestions.append(
            "Next, take one argument from your life and ask: if the premises were true, could the conclusion still be false?"
        )
    elif concept_id == LogicConceptId.PROOF_METHODS:
        reflections.append(
            "Look at how your steps follow one another. Each step should be justified by the previous ones or by a clear rule."
        )
        suggestions.append(
            "Next, try writing a proof both as a paragraph and as a numbered list, and compare which one makes the structure clearer."
        )
    elif concept_id == LogicConceptId.PREDICATE_LOGIC:
        reflections.append(
            "Be careful with the scope of 'all' and 'some' when you formalize. Small changes in order can change the meaning."
        )
        suggestions.append(
            "Next, formalize two different readings of a sentence with 'everyone' and 'someone', and explain in words how they differ."
        )
    else:  # MODAL_NONCLASSICAL
        reflections.append(
            "Notice whether you are using 'must' and 'might' for rules, for knowledge, or for possibility. "
            "Distinguishing these helps you understand different modal logics."
        )
        suggestions.append(
            "Next, list two sentences where 'must' expresses a rule and two where it expresses a strong guess about the world."
        )

    # TODO: later you can log `submission` to a file or DB so PRIME 'learns' from practice.
    # For now, we return concrete, concept-specific feedback.
    return LogicConceptPracticeFeedback(
        concept_id=concept_id,
        level=submission.level,
        reflections=reflections,
        suggestions_for_next_steps=suggestions,
    )

class MetaPhilosophyAssessmentRequest(BaseModel):
    dilemma_text: str
    framework_summaries: list[str] = []

# =========================================
# Methods & Writing Lane M1
# =========================================

_METHODS_CONCEPTS: dict[MethodsConceptId, MethodsConcept] = {
    MethodsConceptId.READING_PHILOSOPHY: MethodsConcept(
        id=MethodsConceptId.READING_PHILOSOPHY,
        name="Reading Philosophy",
        working_definition=(
            "Reading philosophy is the skill of extracting the main question, thesis, "
            "and structure of a philosophical text through active, multi-pass engagement."
        ),
        notes=[
            "Skim first to locate the main conclusion and rough structure. [web:143][web:149]",
            "Then read slowly, identify key terms, distinctions, and arguments. [web:143][web:145][web:148]",
        ],
    ),
    MethodsConceptId.ARGUMENT_RECONSTRUCTION: MethodsConcept(
        id=MethodsConceptId.ARGUMENT_RECONSTRUCTION,
        name="Argument Reconstruction",
        working_definition=(
            "Argument reconstruction is rewriting what an author (or speaker) is "
            "arguing in a clear premise–conclusion form, making implicit structure explicit "
            "while interpreting the author charitably."
        ),
        notes=[
            "Identify conclusion(s), supporting premises, and key distinctions. [web:141][web:139]",
            "Add plausible suppressed premises when needed, without distorting the view. [web:141][web:149]",
        ],
    ),
    MethodsConceptId.EVALUATION: MethodsConcept(
        id=MethodsConceptId.EVALUATION,
        name="Argument Evaluation",
        working_definition=(
            "Argument evaluation is assessing whether an argument's premises are acceptable, "
            "whether they support the conclusion well, and how it compares to alternative views."
        ),
        notes=[
            "Ask: Are premises true or well supported? Is the reasoning valid/strong? [web:143][web:141]",
            "Consider objections, counterexamples, and rival explanations. [web:130][web:152]",
        ],
    ),
    MethodsConceptId.PHILOSOPHICAL_PROSE: MethodsConcept(
        id=MethodsConceptId.PHILOSOPHICAL_PROSE,
        name="Philosophical Prose",
        working_definition=(
            "Philosophical prose is writing that presents a clear thesis and argument, "
            "uses precise terms, anticipates objections, and responds charitably and logically."
        ),
        notes=[
            "A philosophy paper is a reasoned defense of a claim, not a report of opinions. [web:154]",
            "Good prose is clear, structured, and up-front about what it will argue. [web:154][web:130]",
        ],
    ),
}

def _build_methods_concept_lesson(concept: MethodsConcept) -> MethodsConceptLesson:
    cid = concept.id

    # READING PHILOSOPHY
    if cid == MethodsConceptId.READING_PHILOSOPHY:
        level = CurriculumLevel.SCHOOL_SECONDARY
        professor_view = MethodsConceptLessonProfessorView(
            spine_position=(
                "Begins in middle school as careful reading and summarizing; "
                "develops in high school as identifying thesis and reasons; "
                "becomes a core undergrad and grad skill for engaging complex texts."
            ),
            connections_to_other_areas=[
                "history of philosophy survey courses",
                "ethics, metaphysics, and logic seminars",
                "reading in law, theology, and critical theory",
            ],
            deeper_theories=[
                "interpretation and hermeneutics",
                "adversarial vs cooperative reading strategies [web:142][web:143]",
            ],
        )
        grad_view = MethodsConceptLessonGradView(
            core_tensions=[
                "How adversarial should one be when reading: seeking flaws vs seeking the best version of a view? [web:142]",
                "How to balance charitable interpretation with intellectual honesty about weaknesses.",
            ],
            edge_cases=[
                "Texts with unclear structure or conflicting passages.",
                "Authors who shift positions across works or even within one paper.",
            ],
            open_questions=[
                "How can AI be trained to read philosophy in a way that respects nuance without over-simplifying?",
            ],
        )
        teacher_steps = [
            MethodsConceptLessonTeacherStep(
                order=1,
                prompt="Start by skimming to find the main question and conclusion before reading every sentence.",
                example="Look at the introduction and conclusion to see what claim the author is defending.",
                check_question="In one sentence, what do you think the author is trying to show or argue for?"
            ),
            MethodsConceptLessonTeacherStep(
                order=2,
                prompt="On a slower pass, underline key sentences that state the thesis or major steps in the argument.",
                example="Mark sentences that begin with 'In this paper I will argue...' or 'Thus, we should conclude...'.",
                check_question="Can you point to one sentence that clearly states the author’s main thesis?"
            ),
            MethodsConceptLessonTeacherStep(
                order=3,
                prompt="Make a rough outline of the paper’s parts: setup, main argument, objections, replies.",
                example="Write: 1) Section 1 sets up the problem; 2) Section 2 gives argument A; 3) Section 3 replies to B.",
                check_question="Can you list three stages of the text’s discussion in your own words?"
            ),
        ]
        practice_questions = [
            MethodsConceptPracticeQuestion(
                prompt=(
                    "Take a short philosophical passage (5–10 sentences). "
                    "Write: (a) the main question, (b) the main thesis, and "
                    "(c) a 3‑point outline of the structure."
                ),
                expected_shape="outline",
            ),
            MethodsConceptPracticeQuestion(
                prompt="Identify one key term in the passage and write how the author seems to be using or defining it.",
                expected_shape="short_text",
            ),
        ]

    # ARGUMENT RECONSTRUCTION
    elif cid == MethodsConceptId.ARGUMENT_RECONSTRUCTION:
        level = CurriculumLevel.UNDERGRAD_INTRO
        professor_view = MethodsConceptLessonProfessorView(
            spine_position=(
                "Introduced informally in high school when students are asked to 'explain the reasoning'; "
                "systematically taught in undergrad logic and critical thinking; "
                "refined in grad seminars where precise reconstructions drive debate."
            ),
            connections_to_other_areas=[
                "logic and argumentation lane",
                "ethics and political philosophy (policy arguments)",
                "legal reasoning (briefs and opinions)",
            ],
            deeper_theories=[
                "argument diagramming and structure [web:141][web:152]",
                "burden of proof and dialectical context [web:152]",
            ],
        )
        grad_view = MethodsConceptLessonGradView(
            core_tensions=[
                "How far can we go in 'improving' a sloppy argument before we change the author’s view?",
                "How to represent arguments that rely heavily on examples or narratives.",
            ],
            edge_cases=[
                "Passages that mix multiple conclusions and subarguments.",
                "Arguments where crucial assumptions are cultural or tacit.",
            ],
            open_questions=[
                "Can AI reliably perform charitable reconstruction without introducing bias?",
            ],
        )
        teacher_steps = [
            MethodsConceptLessonTeacherStep(
                order=1,
                prompt="Find one sentence that best expresses the main conclusion.",
                example="\"Therefore, we should ban this policy.\"",
                check_question="Write just the conclusion of the argument in one clear sentence."
            ),
            MethodsConceptLessonTeacherStep(
                order=2,
                prompt="List the reasons the author gives that directly support that conclusion.",
                example="\"It harms group X\"; \"There are better alternatives\"; \"It violates principle Y.\"",
                check_question="Can you list at least two distinct reasons that support the conclusion?"
            ),
            MethodsConceptLessonTeacherStep(
                order=3,
                prompt="Rewrite the argument as numbered premises leading to the conclusion.",
                example="1) If a policy causes serious unjust harm and has better alternatives, it should be rejected. 2) This policy causes serious unjust harm. 3) There are better alternatives. So, this policy should be rejected.",
                check_question="Does each premise clearly contribute to the conclusion, or is any line just commentary?"
            ),
        ]
        practice_questions = [
            MethodsConceptPracticeQuestion(
                prompt="Reconstruct a short paragraph you choose into a numbered premise–conclusion argument. Label the conclusion explicitly.",
                expected_shape="outline",
            ),
            MethodsConceptPracticeQuestion(
                prompt="Identify one plausible unstated premise in your reconstruction and explain why adding it is charitable rather than distortive.",
                expected_shape="short_text",
            ),
        ]

    # EVALUATION
    elif cid == MethodsConceptId.EVALUATION:
        level = CurriculumLevel.UNDERGRAD_INTRO
        professor_view = MethodsConceptLessonProfessorView(
            spine_position=(
                "Begins as 'is this a good reason?' in early grades; "
                "becomes structured evaluation (validity, truth, strength) in high school and undergrad; "
                "turns into detailed objection–reply practice in grad seminars."
            ),
            connections_to_other_areas=[
                "ethics, politics, and metaphysics debates",
                "decision-making in law, policy, and science",
                "critical writing and peer review",
            ],
            deeper_theories=[
                "norms of argument quality (relevance, sufficiency, acceptability) [web:130]",
                "fallacies and burden of proof [web:152]",
            ],
        )
        grad_view = MethodsConceptLessonGradView(
            core_tensions=[
                "How to weigh competing arguments that each have some strengths and weaknesses.",
                "When is it acceptable to rely on intuitive judgments vs demanding formal rigor.",
            ],
            edge_cases=[
                "Arguments based on thought experiments or controversial intuitions.",
                "Cases where empirical evidence is incomplete or heavily disputed.",
            ],
            open_questions=[
                "What standards of argument quality should AI apply when assisting with high‑stakes decisions?",
            ],
        )
        teacher_steps = [
            MethodsConceptLessonTeacherStep(
                order=1,
                prompt="Start by asking if the premises are believable, given what you already know.",
                example="If an argument assumes 'All media are untrustworthy', you can question that premise.",
                check_question="Is there at least one premise you think is clearly false or too strong?"
            ),
            MethodsConceptLessonTeacherStep(
                order=2,
                prompt="Ask whether, if the premises were true, they really support the conclusion strongly.",
                example="Premise: 'Some people cheat on tests'; conclusion: 'Grading is useless.' The support is weak.",
                check_question="Can you imagine the premises being true while the conclusion is still false?"
            ),
            MethodsConceptLessonTeacherStep(
                order=3,
                prompt="Consider at least one serious objection or alternative explanation.",
                example="Maybe the policy has bad side effects that the argument ignores.",
                check_question="What is one reasonable alternative view or objection to this argument?"
            ),
        ]
        practice_questions = [
            MethodsConceptPracticeQuestion(
                prompt="Take one reconstructed argument of yours and write: (a) one premise you challenge, and (b) one objection that accepts the premises but questions the conclusion.",
                expected_shape="short_text",
            ),
            MethodsConceptPracticeQuestion(
                prompt="Compare two arguments for different positions on the same issue and briefly say which is stronger and why.",
                expected_shape="short_text",
            ),
        ]

    # PHILOSOPHICAL PROSE
    else:  # MethodsConceptId.PHILOSOPHICAL_PROSE
        level = CurriculumLevel.UNDERGRAD_CORE
        professor_view = MethodsConceptLessonProfessorView(
            spine_position=(
                "Begins as structured paragraphs in school; "
                "becomes thesis‑driven essays in high school; "
                "is formalized in undergrad and grad as clear, rigorous philosophy papers."
            ),
            connections_to_other_areas=[
                "logic and argumentation",
                "all content areas (ethics, metaphysics, epistemology, etc.)",
                "publishing and peer review in philosophy and related fields",
            ],
            deeper_theories=[
                "genre and audience in philosophical writing [web:154][web:130]",
                "uses and limits of formalization in prose",
            ],
        )
        grad_view = MethodsConceptLessonGradView(
            core_tensions=[
                "Balancing precision with readability and accessibility.",
                "How much background to explain vs assume for an expert audience.",
            ],
            edge_cases=[
                "Very dense, technical papers that sacrifice readability.",
                "Highly accessible essays that risk oversimplifying complex positions.",
            ],
            open_questions=[
                "How should AI help draft philosophical writing without flattening style or argument nuance?",
            ],
        )
        teacher_steps = [
            MethodsConceptLessonTeacherStep(
                order=1,
                prompt="Begin by writing one clear sentence stating your main claim.",
                example="\"In this paper I argue that...\" followed by a simple, direct statement.",
                check_question="Can someone who reads only this sentence see what you are trying to defend?"
            ),
            MethodsConceptLessonTeacherStep(
                order=2,
                prompt="Add a short roadmap: the main reasons or steps you will use.",
                example="\"First, I explain X. Second, I argue that Y. Third, I respond to Z.\"",
                check_question="Does your roadmap tell the reader what to expect in the rest of the piece?"
            ),
            MethodsConceptLessonTeacherStep(
                order=3,
                prompt="Write one paragraph that presents a single reason with a clear connection back to your main claim.",
                example="Begin the paragraph with a sentence that states the reason, then support it with explanation or examples.",
                check_question="If you read only this paragraph, can you tell how it supports your main claim?"
            ),
        ]
        practice_questions = [
            MethodsConceptPracticeQuestion(
                prompt="Write a short paragraph stating a philosophical claim you care about and give one clear reason for it.",
                expected_shape="paragraph",
            ),
            MethodsConceptPracticeQuestion(
                prompt="Add one objection to your claim and one brief reply, in your own words.",
                expected_shape="paragraph",
            ),
        ]

    teacher_view = MethodsConceptLessonTeacherView(steps=teacher_steps)
    practice_set = MethodsConceptPracticeSet(
        concept_id=concept.id,
        level=level,
        questions=practice_questions,
    )

    return MethodsConceptLesson(
        id=f"philo.methods.{concept.id}",
        concept=concept,
        subject=SubjectId.PHILOSOPHY_CORE,
        domain=DomainId.HUMANITIES,
        level=level,
        professor_view=professor_view,
        grad_view=grad_view,
        teacher_view=teacher_view,
        practice=practice_set,
    )

@router.get(
    "/m1/methods-concepts/overview",
    response_model=list[MethodsConceptLesson],
)
async def methods_concepts_overview_m1() -> list[MethodsConceptLesson]:
    """
    Methods & Writing Lane M1: overview of core methodological skills.
    """
    lessons: list[MethodsConceptLesson] = []
    for concept in _METHODS_CONCEPTS.values():
        lessons.append(_build_methods_concept_lesson(concept))
    return lessons


@router.get(
    "/m1/methods-concepts/{concept_id}",
    response_model=MethodsConceptLesson,
)
async def methods_concept_detail_m1(concept_id: MethodsConceptId) -> MethodsConceptLesson:
    concept = _METHODS_CONCEPTS.get(concept_id)
    if concept is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unknown methods concept")
    return _build_methods_concept_lesson(concept)


class MethodsConceptPracticeAnswer(BaseModel):
    question_index: int
    response_text: str


class MethodsConceptPracticeSubmission(BaseModel):
    concept_id: MethodsConceptId
    level: CurriculumLevel
    answers: list[MethodsConceptPracticeAnswer]


class MethodsConceptPracticeFeedback(BaseModel):
    concept_id: MethodsConceptId
    level: CurriculumLevel
    reflections: list[str]
    suggestions_for_next_steps: list[str]


@router.post(
    "/m1/methods-concepts/{concept_id}/practice",
    response_model=MethodsConceptPracticeFeedback,
)
async def methods_concept_practice_m1(
    concept_id: MethodsConceptId,
    submission: MethodsConceptPracticeSubmission,
) -> MethodsConceptPracticeFeedback:
    concept = _METHODS_CONCEPTS.get(concept_id)
    if concept is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unknown methods concept")

    reflections: list[str] = []
    suggestions: list[str] = []

    if concept_id == MethodsConceptId.READING_PHILOSOPHY:
        reflections.append(
            "Focus on stating the main thesis in your own words and outlining the structure "
            "before worrying about every detail sentence."
        )
        suggestions.append(
            "Next time, try writing a 3–4 line outline that labels each part of the text as setup, argument, objection, or reply."
        )
    elif concept_id == MethodsConceptId.ARGUMENT_RECONSTRUCTION:
        reflections.append(
            "Check that each premise in your reconstruction is a genuine reason, not just a "
            "restatement or example."
        )
        suggestions.append(
            "For your next reconstruction, explicitly label which premises are added by you as implicit assumptions."
        )
    elif concept_id == MethodsConceptId.EVALUATION:
        reflections.append(
            "Notice whether you are challenging premises, the connection between premises and conclusion, "
            "or both."
        )
        suggestions.append(
            "Choose one argument you evaluated and write a short paragraph comparing it with a plausible rival argument for the opposing view."
        )
    else:  # PHILOSOPHICAL_PROSE
        reflections.append(
            "Check that each paragraph you write has one main job and begins with a sentence "
            "that signals that job clearly."
        )
        suggestions.append(
            "Next, try rewriting one of your paragraphs so that the first sentence clearly announces its role in your argument."
        )

    return MethodsConceptPracticeFeedback(
        concept_id=concept_id,
        level=submission.level,
        reflections=reflections,
        suggestions_for_next_steps=suggestions,
    )

# =========================================
# Metaphysics Lane B1
# =========================================

_METAPHYSICS_CONCEPTS: dict[MetaphysicsConceptId, MetaphysicsConcept] = {
    MetaphysicsConceptId.BEING_EXISTENCE: MetaphysicsConcept(
        id=MetaphysicsConceptId.BEING_EXISTENCE,
        name="Being and Existence",
        working_definition=(
            "Being and existence concern what it is for something to be at all, "
            "and what sorts of things exist or are real."
        ),
        notes=[
            "Questions: Why is there something rather than nothing? What kinds of things exist? [web:123][web:131][web:144]",
            "Distinctions: existence vs essence; concrete vs abstract; dependence vs independence. [web:123]",
        ],
    ),
    MetaphysicsConceptId.OBJECTS_PROPERTIES: MetaphysicsConcept(
        id=MetaphysicsConceptId.OBJECTS_PROPERTIES,
        name="Objects and Properties",
        working_definition=(
            "Objects are individual things; properties are ways those things are, "
            "like being red or being square. Metaphysics asks how objects and properties relate."
        ),
        notes=[
            "Are properties universals or particular tropes? [web:123]",
            "How do objects 'have' properties across change?",
        ],
    ),
    MetaphysicsConceptId.IDENTITY_PERSISTENCE: MetaphysicsConcept(
        id=MetaphysicsConceptId.IDENTITY_PERSISTENCE,
        name="Identity and Persistence",
        working_definition=(
            "Identity and persistence concern when something is the same object over time, "
            "despite change, and what makes it that very thing."
        ),
        notes=[
            "Examples: Ship of Theseus, personal identity through memory or body. [web:123]",
        ],
    ),
    MetaphysicsConceptId.CAUSATION: MetaphysicsConcept(
        id=MetaphysicsConceptId.CAUSATION,
        name="Causation",
        working_definition=(
            "Causation concerns how one event or state brings about another, and what it is "
            "for one thing to be a cause of another."
        ),
        notes=[
            "Regularity, counterfactual, and mechanistic accounts of causation. [web:123][web:153]",
            "Questions about simultaneous causation and temporal order. [web:153]",
        ],
    ),
    MetaphysicsConceptId.TIME_SPACE: MetaphysicsConcept(
        id=MetaphysicsConceptId.TIME_SPACE,
        name="Time and Space",
        working_definition=(
            "Time and space are the basic frameworks of events and objects. Metaphysics asks "
            "what they are like and how they relate to change and motion."
        ),
        notes=[
            "Presentism vs eternalism; A‑series vs B‑series views of time. [web:123][web:131]",
            "Absolute vs relational space and time.",
        ],
    ),
    MetaphysicsConceptId.MODALITY: MetaphysicsConcept(
        id=MetaphysicsConceptId.MODALITY,
        name="Possibility and Necessity",
        working_definition=(
            "Modality is about what is possible, impossible, necessary, or contingent, "
            "often analyzed using possible worlds."
        ),
        notes=[
            "Metaphysical vs logical vs physical possibility. [web:123][web:131]",
            "Possible worlds semantics and debates about their reality.",
        ],
    ),
    MetaphysicsConceptId.FREE_WILL_AND_DETERMINISM: MetaphysicsConcept(
        id=MetaphysicsConceptId.FREE_WILL_AND_DETERMINISM,
        name="Free Will and Determinism",
        working_definition=(
            "Free will and determinism concerns whether our choices are genuinely up to us "
            "or fully determined by prior causes and laws of nature, and what that means for "
            "responsibility, praise, and blame."
        ),
        notes=[
            "Classic positions include hard determinism, libertarianism, and compatibilism.",
            "Connects to questions about causation, laws of nature, responsibility, and moral desert.",
        ],
    ),
}

def _build_metaphysics_concept_lesson(concept: MetaphysicsConcept) -> MetaphysicsConceptLesson:
    cid = concept.id

    # BEING & EXISTENCE
    if cid == MetaphysicsConceptId.BEING_EXISTENCE:
        level = CurriculumLevel.UNDERGRAD_INTRO
        professor_view = MetaphysicsConceptLessonProfessorView(
            spine_position=(
                "Appears early as 'what is real and what is pretend'; "
                "becomes explicit in undergrad metaphysics; "
                "is deepened in grad work on ontology, fundamentality, and dependence."
            ),
            connections_to_other_areas=[
                "philosophy of religion (existence of God)",
                "philosophy of science (realism vs anti‑realism)",
                "logic and ontology in AI (what entities to represent)",
            ],
            deeper_theories=[
                "ontological commitment and quantification [web:123]",
                "fundamentality and grounding",
            ],
        )
        grad_view = MetaphysicsConceptLessonGradView(
            core_tensions=[
                "Are there objective facts about what exists, or is it theory‑relative?",
                "Are abstract objects (numbers, properties) as real as concrete objects?",
            ],
            edge_cases=[
                "Fictional entities (Sherlock Holmes, Hogwarts).",
                "Borderline cases (clouds, social groups, corporations).",
            ],
            open_questions=[
                "What ontology should AI systems adopt when modeling the world for reasoning?",
            ],
        )
        teacher_steps = [
            MetaphysicsConceptLessonTeacherStep(
                order=1,
                prompt="Begin with a simple question: what kinds of things do you think really exist?",
                example="People, trees, cars, numbers, stories, laws.",
                check_question="Name three things you think are real and one thing you think is not real."
            ),
            MetaphysicsConceptLessonTeacherStep(
                order=2,
                prompt="Ask whether things like numbers or fictional characters are 'real' in the same way as tables and chairs.",
                example="Is 'the number 2' real? Is 'Batman' real? In what sense?",
                check_question="Pick one case (like 'the number 2') and explain in one sentence how it is or is not real."
            ),
            MetaphysicsConceptLessonTeacherStep(
                order=3,
                prompt="Introduce the idea that philosophers sometimes talk about what we must count as existing to make our best theories true.",
                example="If physics talks about electrons, many philosophers say our ontology includes electrons.",
                check_question="Can you give an example of a theory and one kind of thing it seems to commit us to?"
            ),
        ]
        practice_questions = [
            MetaphysicsConceptPracticeQuestion(
                prompt="Make a list with two columns: things you think are 'definitely real' and things you are unsure about. Explain one item in the 'unsure' column.",
                expected_shape="short_text",
            ),
            MetaphysicsConceptPracticeQuestion(
                prompt="Pick a scientific or everyday theory (e.g. about the economy) and say what kinds of things it treats as existing.",
                expected_shape="short_text",
            ),
        ]

    # OBJECTS & PROPERTIES
    elif cid == MetaphysicsConceptId.OBJECTS_PROPERTIES:
        level = CurriculumLevel.UNDERGRAD_INTRO
        professor_view = MetaphysicsConceptLessonProfessorView(
            spine_position=(
                "Shows up early as 'things' and their 'features'; "
                "undergrad metaphysics makes the object–property distinction explicit; "
                "grad work explores universals, tropes, and bundle theories."
            ),
            connections_to_other_areas=[
                "philosophy of science (laws and natural kinds)",
                "philosophy of mind (mental properties vs physical properties)",
                "formal ontology in AI (classes, instances, attributes)",
            ],
            deeper_theories=[
                "realism vs nominalism about universals [web:123]",
                "bundle vs substance theories of objects",
            ],
        )
        grad_view = MetaphysicsConceptLessonGradView(
            core_tensions=[
                "Are properties repeatable universals or particular tropes?",
                "Does an object have a 'bare particular' substratum beyond its properties?",
            ],
            edge_cases=[
                "Objects that share all properties (indiscernibles).",
                "Vague objects (clouds, heaps).",
            ],
            open_questions=[
                "How should we represent objects and properties in knowledge graphs and ontologies?",
            ],
        )
        teacher_steps = [
            MetaphysicsConceptLessonTeacherStep(
                order=1,
                prompt="Start with an everyday object and list some of its properties.",
                example="A red ball: round, red, made of rubber, fits in your hand.",
                check_question="Choose one object near you and list at least three of its properties."
            ),
            MetaphysicsConceptLessonTeacherStep(
                order=2,
                prompt="Ask whether two different objects can share exactly the same property.",
                example="Two cars might both be red and both be the same model.",
                check_question="Can two different things share the same color or shape? Give an example."
            ),
            MetaphysicsConceptLessonTeacherStep(
                order=3,
                prompt="Notice that properties help explain how we group and describe things.",
                example="We call things 'chairs' because they share certain shapes and functions.",
                check_question="Name a group of things that we treat as the same kind and one property they share."
            ),
        ]
        practice_questions = [
            MetaphysicsConceptPracticeQuestion(
                prompt="Pick one object and write a short description that clearly separates the object from its properties.",
                expected_shape="short_text",
            ),
            MetaphysicsConceptPracticeQuestion(
                prompt="Describe a case where you are unsure if two things are different objects or the same object with changing properties.",
                expected_shape="short_text",
            ),
        ]

    # IDENTITY & PERSISTENCE
    elif cid == MetaphysicsConceptId.IDENTITY_PERSISTENCE:
        level = CurriculumLevel.UNDERGRAD_INTRO
        professor_view = MetaphysicsConceptLessonProfessorView(
            spine_position=(
                "Begins in childhood questions about 'same toy' after change; "
                "becomes Ship‑of‑Theseus and personal identity puzzles in high school and undergrad; "
                "is systematized in grad work on perdurance, endurantism, and personhood."
            ),
            connections_to_other_areas=[
                "ethics and responsibility (same person over time)",
                "philosophy of mind (self and consciousness)",
                "law (liability, identity of institutions over time)",
            ],
            deeper_theories=[
                "endurantism vs perdurantism [web:123]",
                "psychological vs bodily criteria of personal identity",
            ],
        )
        grad_view = MetaphysicsConceptLessonGradView(
            core_tensions=[
                "Is identity over time a matter of strict numerical sameness or looser continuity?",
                "What matters for survival: being the same person, or psychological continuity?",
            ],
            edge_cases=[
                "Ship of Theseus: replacing parts gradually.",
                "Teleportation or brain‑splitting thought experiments.",
            ],
            open_questions=[
                "How should AI reason about identity of persons and institutions through time when advising on ethics or law?",
            ],
        )
        teacher_steps = [
            MetaphysicsConceptLessonTeacherStep(
                order=1,
                prompt="Begin with a simple case of change: your favorite toy gets scratched or repainted.",
                example="A blue bike gets repainted red.",
                check_question="After repainting, is it still the same bike? Why?"
            ),
            MetaphysicsConceptLessonTeacherStep(
                order=2,
                prompt="Introduce the Ship of Theseus idea: replacing parts one by one.",
                example="Imagine a ship where each plank is replaced over many years.",
                check_question="If all planks are replaced, do you think it is the same ship? Explain your intuition."
            ),
            MetaphysicsConceptLessonTeacherStep(
                order=3,
                prompt="Connect identity to what matters for responsibility and relationships.",
                example="If a person forgets many things but keeps their character, do you treat them as the same person?",
                check_question="Name one thing you think is important for a person to be 'the same' over time."
            ),
        ]
        practice_questions = [
            MetaphysicsConceptPracticeQuestion(
                prompt="Describe your own version of the Ship of Theseus with an everyday object and explain what your intuition says about identity in that case.",
                expected_shape="short_text",
            ),
            MetaphysicsConceptPracticeQuestion(
                prompt="Write a short reflection on what you think matters most for personal identity over time.",
                expected_shape="short_text",
            ),
        ]

    # CAUSATION
    elif cid == MetaphysicsConceptId.CAUSATION:
        level = CurriculumLevel.UNDERGRAD_CORE
        professor_view = MetaphysicsConceptLessonProfessorView(
            spine_position=(
                "Starts as 'this made that happen' in childhood; "
                "undergrad metaphysics introduces regularity and counterfactual views; "
                "grad work explores laws, mechanisms, and probabilistic causation."
            ),
            connections_to_other_areas=[
                "science (experiments, explanations)",
                "law (causation in responsibility and negligence)",
                "AI and statistics (causal inference)",
            ],
            deeper_theories=[
                "Humean regularity theory; counterfactual theories; interventionist accounts [web:123][web:153]",
                "simultaneous vs temporally ordered causation [web:153]",
            ],
        )
        grad_view = MetaphysicsConceptLessonGradView(
            core_tensions=[
                "Are causal relations fundamental or reducible to patterns in events?",
                "Can there be simultaneous causation, or must causes precede effects?",
            ],
            edge_cases=[
                "Backward causation or time‑travel scenarios.",
                "Highly complex causal webs where no single factor seems 'the cause'.",
            ],
            open_questions=[
                "What causal notions are most useful and safe for AI systems performing causal inference?",
            ],
        )
        teacher_steps = [
            MetaphysicsConceptLessonTeacherStep(
                order=1,
                prompt="Start with simple cause–effect stories.",
                example="Pressing a light switch causes the light to turn on.",
                check_question="Give one example from your day where one thing caused another."
            ),
            MetaphysicsConceptLessonTeacherStep(
                order=2,
                prompt="Ask whether the cause had to come before the effect in time.",
                example="You push a glass, and then it falls and breaks.",
                check_question="In your example, does the cause always happen before the effect?"
            ),
            MetaphysicsConceptLessonTeacherStep(
                order=3,
                prompt="Introduce the idea that causation often involves patterns, not just single events.",
                example="Smoking is linked to higher rates of lung disease.",
                check_question="Is this case about one single event or about a pattern across many cases?"
            ),
        ]
        practice_questions = [
            MetaphysicsConceptPracticeQuestion(
                prompt="Describe one simple causal chain (A causes B causes C) and say where you think the main cause lies.",
                expected_shape="short_text",
            ),
            MetaphysicsConceptPracticeQuestion(
                prompt="Give an example where you are unsure whether one thing really caused another, and explain why it is unclear.",
                expected_shape="short_text",
            ),
        ]

    # TIME & SPACE
    elif cid == MetaphysicsConceptId.TIME_SPACE:
        level = CurriculumLevel.UNDERGRAD_CORE
        professor_view = MetaphysicsConceptLessonProfessorView(
            spine_position=(
                "Begins as basic sense of before/after and here/there; "
                "later becomes explicit debates about A‑series vs B‑series time and absolute vs relational space in undergrad; "
                "grad work draws on physics and metaphysics together."
            ),
            connections_to_other_areas=[
                "physics and cosmology",
                "philosophy of mind (experience of time)",
                "philosophy of religion (eternity, timelessness)",
            ],
            deeper_theories=[
                "presentism vs eternalism; growing block theories [web:123][web:131]",
                "relational vs substantival space‑time",
            ],
        )
        grad_view = MetaphysicsConceptLessonGradView(
            core_tensions=[
                "Is only the present real, or are past and future equally real?",
                "Is time fundamentally different from space, or similar in structure?",
            ],
            edge_cases=[
                "Time dilation in relativity.",
                "Experiences of time slowing or speeding up subjectively.",
            ],
            open_questions=[
                "How should long‑term planning AI systems think about time and future generations?",
            ],
        )
        teacher_steps = [
            MetaphysicsConceptLessonTeacherStep(
                order=1,
                prompt="Start with simple ordering of events: yesterday, today, tomorrow.",
                example="You ate breakfast before you read this; you will do something after reading it.",
                check_question="Name two events from today and say which came first."
            ),
            MetaphysicsConceptLessonTeacherStep(
                order=2,
                prompt="Ask whether past and future events are in any sense 'real' now.",
                example="Is your birthday next year already real, or not yet?",
                check_question="Do you think the future exists right now? Explain briefly."
            ),
            MetaphysicsConceptLessonTeacherStep(
                order=3,
                prompt="Connect to space: here vs there, and how objects relate in space.",
                example="You and a tree are both real now, but in different places.",
                check_question="How is the difference between here/there similar to or different from now/then?"
            ),
        ]
        practice_questions = [
            MetaphysicsConceptPracticeQuestion(
                prompt="Describe how you experience time passing in a boring situation vs an exciting one, and say what that suggests about time.",
                expected_shape="short_text",
            ),
            MetaphysicsConceptPracticeQuestion(
                prompt="Write a short thought about whether the past still 'exists' in any sense.",
                expected_shape="short_text",
            ),
        ]

    # MODALITY
    else:  # MetaphysicsConceptId.MODALITY
        level = CurriculumLevel.GRAD_PHD_CORE
        professor_view = MetaphysicsConceptLessonProfessorView(
            spine_position=(
                "Begins in everyday talk about could, must, and might; "
                "is formalized in modal logic and metaphysics of possible worlds in advanced undergrad; "
                "grad work explores modal realism, essentialism, and the basis of necessity."
            ),
            connections_to_other_areas=[
                "logic and modal logics",
                "metaphysics of essence and laws",
                "epistemology and knowledge of possibility",
            ],
            deeper_theories=[
                "possible worlds semantics for modal logic [web:123]",
                "metaphysical vs epistemic vs deontic modality",
            ],
        )
        grad_view = MetaphysicsConceptLessonGradView(
            core_tensions=[
                "Are possible worlds real entities or just useful fictions?",
                "Are modal truths grounded in essences, laws, or something else?",
            ],
            edge_cases=[
                "Borderline possibilities (e.g., logically possible but physically impossible scenarios).",
                "Debates about whether some things could not have failed to exist.",
            ],
            open_questions=[
                "How should AI represent and reason about possibilities and necessities without confusing them with certainties?",
            ],
        )
        teacher_steps = [
            MetaphysicsConceptLessonTeacherStep(
                order=1,
                prompt="Start with 'could', 'must', and 'cannot' in everyday speech.",
                example="\"I could have taken another route\"; \"You must stop at red lights\"; \"Humans cannot breathe underwater unaided.\"",
                check_question="Give one example each of something you think is possible, necessary, and impossible."
            ),
            MetaphysicsConceptLessonTeacherStep(
                order=2,
                prompt="Notice different kinds of 'must': logical, physical, and rule‑based.",
                example="\"2+2 must be 4\" (logical); \"The glass must fall if pushed off the table\" (physical); \"You must pay taxes\" (rule‑based).",
                check_question="Classify one 'must' sentence you know as logical, physical, or rule‑based."
            ),
            MetaphysicsConceptLessonTeacherStep(
                order=3,
                prompt="Introduce the idea of possible worlds as ways things could have been.",
                example="There is a possible world where you chose a different career.",
                check_question="Describe one way the world could have been different and still be 'like ours' in many respects."
            ),
        ]
        practice_questions = [
            MetaphysicsConceptPracticeQuestion(
                prompt="List three things you think are metaphysically possible but not actual, and one thing you think is metaphysically impossible.",
                expected_shape="short_text",
            ),
            MetaphysicsConceptPracticeQuestion(
                prompt="Write a brief explanation of what you think it means to say that something is 'necessary'.",
                expected_shape="short_text",
            ),
        ]

    teacher_view = MetaphysicsConceptLessonTeacherView(steps=teacher_steps)
    practice_set = MetaphysicsConceptPracticeSet(
        concept_id=concept.id,
        level=level,
        questions=practice_questions,
    )

    return MetaphysicsConceptLesson(
        id=f"philo.metaphysics.{concept.id}",
        concept=concept,
        subject=SubjectId.PHILOSOPHY_CORE,
        domain=DomainId.HUMANITIES,
        level=level,
        professor_view=professor_view,
        grad_view=grad_view,
        teacher_view=teacher_view,
        practice=practice_set,
    )


@router.get(
    "/l1/logic-concepts/{concept_id}",
    response_model=LogicConceptLesson,
)
async def philosophy_logic_l1_concept(
    concept_id: LogicConceptId,
) -> LogicConceptLesson:
    """
    Retrieve a single Logic foundation concept as a triple-role lesson.
    """
    concept = _LOGIC_CONCEPTS.get(concept_id)
    if concept is None:
        raise HTTPException(status_code=404, detail="Unknown LogicConceptId")
    return _build_logic_concept_lesson(concept)


@router.get(
    "/m1/methods-concepts/{concept_id}",
    response_model=MethodsConceptLesson,
)
async def philosophy_methods_m1_concept(
    concept_id: MethodsConceptId,
) -> MethodsConceptLesson:
    """
    Retrieve a single Methods & Writing foundation concept as a triple-role lesson.
    """
    concept = _METHODS_CONCEPTS.get(concept_id)
    if concept is None:
        raise HTTPException(status_code=404, detail="Unknown MethodsConceptId")
    return _build_methods_concept_lesson(concept)


@router.get(
    "/b1/metaphysics-concepts/{concept_id}",
    response_model=MetaphysicsConceptLesson,
)
async def philosophy_metaphysics_b1_concept(
    concept_id: MetaphysicsConceptId,
) -> MetaphysicsConceptLesson:
    """
    Retrieve a single Metaphysics foundation concept as a triple-role lesson.
    """
    concept = _METAPHYSICS_CONCEPTS.get(concept_id)
    if concept is None:
        raise HTTPException(status_code=404, detail="Unknown MetaphysicsConceptId")
    return _build_metaphysics_concept_lesson(concept)

@router.get(
    "/b1/metaphysics-concepts/overview",
    response_model=list[MetaphysicsConceptLesson],
)
async def metaphysics_concepts_overview_b1() -> list[MetaphysicsConceptLesson]:
    """
    Metaphysics Lane B1: overview of core metaphysical concepts.
    """
    lessons: list[MetaphysicsConceptLesson] = []
    for concept in _METAPHYSICS_CONCEPTS.values():
        lessons.append(_build_metaphysics_concept_lesson(concept))
    return lessons


@router.get(
    "/b1/metaphysics-concepts/{concept_id}",
    response_model=MetaphysicsConceptLesson,
)
async def metaphysics_concept_detail_b1(concept_id: MetaphysicsConceptId) -> MetaphysicsConceptLesson:
    concept = _METAPHYSICS_CONCEPTS.get(concept_id)
    if concept is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unknown metaphysics concept")
    return _build_metaphysics_concept_lesson(concept)


class MetaphysicsConceptPracticeAnswer(BaseModel):
    question_index: int
    response_text: str


class MetaphysicsConceptPracticeSubmission(BaseModel):
    concept_id: MetaphysicsConceptId
    level: CurriculumLevel
    answers: list[MetaphysicsConceptPracticeAnswer]


class MetaphysicsConceptPracticeFeedback(BaseModel):
    concept_id: MetaphysicsConceptId
    level: CurriculumLevel
    reflections: list[str]
    suggestions_for_next_steps: list[str]


@router.post(
    "/b1/metaphysics-concepts/{concept_id}/practice",
    response_model=MetaphysicsConceptPracticeFeedback,
)
async def metaphysics_concept_practice_b1(
    concept_id: MetaphysicsConceptId,
    submission: MetaphysicsConceptPracticeSubmission,
) -> MetaphysicsConceptPracticeFeedback:
    concept = _METAPHYSICS_CONCEPTS.get(concept_id)
    if concept is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unknown metaphysics concept")

    reflections: list[str] = []
    suggestions: list[str] = []

    if concept_id == MetaphysicsConceptId.BEING_EXISTENCE:
        reflections.append(
            "Notice which cases you find hard to classify as 'real' or 'not real'—those often "
            "reveal interesting metaphysical questions."
        )
        suggestions.append(
            "Next, pick one 'borderline' case and write two different ways of thinking about its reality."
        )
    elif concept_id == MetaphysicsConceptId.OBJECTS_PROPERTIES:
        reflections.append(
            "Pay attention to how you separate objects from their properties and how this "
            "affects your description of change."
        )
        suggestions.append(
            "Try describing an object before and after a change and highlight which parts of your description are properties."
        )
    elif concept_id == MetaphysicsConceptId.IDENTITY_PERSISTENCE:
        reflections.append(
            "Compare your intuitions across different identity cases (objects, persons, institutions) and see if one principle fits them all."
        )
        suggestions.append(
            "Write down a simple principle you think governs identity over time and test it against two new cases."
        )
    elif concept_id == MetaphysicsConceptId.CAUSATION:
        reflections.append(
            "Note whether you focus on single 'trigger' causes or on broader conditions and patterns."
        )
        suggestions.append(
            "For one example, list at least three background conditions that were needed in addition to the main cause."
        )
    elif concept_id == MetaphysicsConceptId.TIME_SPACE:
        reflections.append(
            "Observe how your thinking about time (only the present vs past and future also real) "
            "shapes your views about long‑term decisions."
        )
        suggestions.append(
            "Write a short note on how your view of time might affect how far into the future you plan."
        )
    else:  # MODALITY
        reflections.append(
            "Pay attention to how you distinguish 'could happen' from 'will happen' and from 'must happen'."
        )
        suggestions.append(
            "List three scenarios you think are possible but unlikely, and explain why you still count them as possible."
        )

    feedback = MetaphysicsConceptPracticeFeedback(
        concept_id=concept_id,
        level=submission.level,
        reflections=reflections,
        suggestions_for_next_steps=suggestions,
    )

    # --- Log this practice episode into reasoning memory ---
    # Build a synthetic ReasoningTask and ReasoningCoreResponse so it fits the schema.
    practice_task = ReasoningTask(
        task_id=f"metaphysics_practice::{concept_id.value}",
        natural_language_task=(
            f"Metaphysics concept practice: {concept.name} at level {submission.level}."
        ),
        domain_tag="philosophy",
        subdomain_tag="metaphysics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.PRACTICE if hasattr(ReasoningTaskKind, "PRACTICE") else ReasoningTaskKind.EXPLANATION,
        allowed_tools=[],
    )

    practice_step = ReasoningStep(
        index=0,
        kind=ReasoningStepKind.SUMMARIZE,
        description="Metaphysics concept practice feedback.",
        inputs=[],
        outputs=[
            f"Concept id: {concept_id.value}",
            f"Level: {submission.level}",
            f"Reflections: {reflections}",
            f"Suggestions: {suggestions}",
        ],
        warnings=[],
        confidence=None,
    )

    practice_trace = ReasoningTrace(
        steps=[practice_step],
        overall_confidence=None,
        detected_contradictions=[],
        notes=[],
    )

    practice_response = ReasoningCoreResponse(
        task_id=practice_task.task_id,
        trace=practice_trace,
        key_conclusions=[
            f"Metaphysics practice completed for concept {concept_id.value} at level {submission.level}."
        ],
        open_questions=[],
    )

    # Outcome quality: for now, mark UNKNOWN; later you can infer from answers.
    entry_id = f"metaphysics_practice::{concept_id.value}::{submission.level}"
    user_id = "raymond"  # TODO: thread real user id once you have auth

    num_questions = len(submission.answers)
    num_correct = num_questions  # for now, treat all as correct reflection; adjust when you add marking

    outcome_quality = compute_outcome_quality_from_answers(
        num_questions=num_questions,
        num_correct=num_correct,
    )

    save_practice_to_memory(
        entry_id=entry_id,
        user_id=user_id,
        domain="philosophy",
        subdomain="metaphysics",
        theme=f"concept_id={concept_id.value}",
        practice_task=practice_task,
        practice_response=practice_response,
        outcome_quality=ReasoningOutcomeQuality.UNKNOWN,
    )

    return feedback

@router.get(
    "/foundations/overview",
    response_model=PhilosophyFoundationsOverview,
)
async def philosophy_foundations_overview() -> PhilosophyFoundationsOverview:
    """
    Unified overview of PRIME's philosophy foundations:
    Logic (L1), Methods & Writing (M1), and Metaphysics (B1).

    We return the core concept definitions here; clients can call
    specific concept-lesson endpoints for full professor/grad/teacher views.
    """
    logic_concepts: list[LogicConcept] = []
    for concept in _LOGIC_CONCEPTS.values():
        logic_concepts.append(concept)

    methods_concepts: list[MethodsConcept] = []
    for concept in _METHODS_CONCEPTS.values():
        methods_concepts.append(concept)

    metaphysics_concepts: list[MetaphysicsConcept] = []
    for concept in _METAPHYSICS_CONCEPTS.values():
        metaphysics_concepts.append(concept)

    return PhilosophyFoundationsOverview(
        logic_concepts=logic_concepts,
        methods_concepts=methods_concepts,
        metaphysics_concepts=metaphysics_concepts,
    )

@router.post(
    "/meta/assess",
    response_model=MetaPhilosophyAssessment,
)
async def philosophy_meta_assess(
    request: MetaPhilosophyAssessmentRequest,
) -> MetaPhilosophyAssessment:
    """
    Rough meta-ethical assessment: how underdetermined is this question,
    and should PRIME hand final judgment back to the human?
    """
    text = request.dilemma_text.lower()

    life_direction_signals = [
        "life purpose",
        "meaning of my life",
        "who i should be",
        "what kind of person i should be",
        "my calling",
    ]
    is_life_direction = any(sig in text for sig in life_direction_signals)

    under_level = "medium"
    reasons: list[str] = []

    if is_life_direction:
        under_level = "high"
        reasons.append(
            "This question concerns life direction or meaning, which cannot be settled by ethics frameworks alone."
        )

    if len(request.framework_summaries) >= 2:
        reasons.append(
            "Multiple serious frameworks offer differing recommendations; choosing among them involves value judgment."
        )

    should_escalate = under_level == "high" or bool(reasons)

    return MetaPhilosophyAssessment(
        question_kind="ethical_life_mixed" if is_life_direction else "ethical",
        underdetermination_level=under_level,
        frameworks_in_play=request.framework_summaries,
        should_escalate_to_human=should_escalate,
        reasons_to_escalate=reasons,
        notes=[
            "This is a first-pass meta assessment; PRIME should map options and hand final choice to the human when underdetermination is high."
        ],
    )

@router.get(
    "/ethics/concepts",
    response_model=list[EthicsConcept],
)
async def ethics_list_concepts() -> list[EthicsConcept]:
    """
    List core ethics concepts PRIME has explicit working definitions for.
    """
    return list(_ETHICS_CONCEPTS.values())


@router.post(
    "/ethics/concepts/diagnose",
    response_model=EthicsConceptDiagnosisResponse,
)
async def ethics_concept_diagnose(
    request: EthicsConceptDiagnosisRequest,
) -> EthicsConceptDiagnosisResponse:
    """
    Diagnose how well a case fits a given ethics concept, dimension by dimension.
    For now, this is a heuristic scaffold; later, deeper analysis tools will refine it.
    """
    concept = _ETHICS_CONCEPTS.get(request.concept_id)
    if concept is None:
        from fastapi import HTTPException  # local import to avoid circular issues
        raise HTTPException(status_code=404, detail="Unknown ethics concept")

    dimension_assessments: list[EthicsConceptDimensionAssessment] = []

    # For now, apply all dimensions with generic explanatory notes.
    for dim in concept.dimensions:
        dimension_assessments.append(
            EthicsConceptDimensionAssessment(
                dimension_name=dim.name,
                applies=True,
                explanation=(
                    f"This case may involve the dimension '{dim.name}'. "
                    "A richer analysis tool will later examine specific facts."
                ),
            )
        )

    return EthicsConceptDiagnosisResponse(
        concept_id=concept.id,
        concept_name=concept.name,
        overall_match="borderline",
        dimension_assessments=dimension_assessments,
        pressures_on_definition=[
            "Diagnosis logic is generic. Use this as scaffolding to refine the concept and definition."
        ],
        notes=[
            "This response is part of conceptual engineering, not a final moral verdict."
        ],
    )

# ============================================================
# Philosophy Lane 6: Ethics concepts (teach + practice, triple role)
# ============================================================


def _build_ethics_concept_lesson(concept: EthicsConcept) -> EthicsConceptLesson:
    """
    Construct a triple-role lesson object for a single ethics concept.
    For now, we hard-code content patterns for the seven core concepts.
    """
    if concept.id == "ethics.concept.harm":
        level = CurriculumLevel.UNDERGRAD_INTRO
        professor_view = EthicsConceptLessonProfessorView(
            spine_position=(
                "Seeds in K–8 (fair vs unfair, hurt vs help); "
                "explicit in high-school ethics; "
                "formalized in undergrad ethics, law, and political philosophy."
            ),
            connections_to_other_areas=[
                "tort law and negligence",
                "public health and safety regulation",
                "AI safety and risk assessment",
            ],
            deeper_theories=[
                "interest-based theories of harm",
                "rights-based accounts of wrongful harm",
            ],
        )
        grad_view = EthicsConceptLessonGradView(
            core_tensions=[
                "Is harm always a setback to interests, or can 'harms' sometimes be good for long-term flourishing?",
                "How do we weigh small harms to many vs large harms to a few?",
            ],
            edge_cases=[
                "Psychological harm from truthful but painful information.",
                "Harms that are inseparable from necessary social change.",
            ],
            open_questions=[
                "How should AI systems reason about low-probability, high-impact harms?",
            ],
        )
        teacher_steps = [
            EthicsConceptLessonTeacherStep(
                order=1,
                prompt="Start with a simple question: When someone gets hurt, what does that mean?",
                example="A classmate pushes another and they fall and scrape their knee.",
                check_question="In this example, what is the harm?"
            ),
            EthicsConceptLessonTeacherStep(
                order=2,
                prompt="Introduce non-physical harms: feelings, opportunities, and dignity.",
                example="A rumor spreads that makes a student feel ashamed and left out.",
                check_question="Is there harm here even if no one is physically hurt? Why?"
            ),
            EthicsConceptLessonTeacherStep(
                order=3,
                prompt="Connect to bigger systems: rules and designs that increase or reduce harm.",
                example="A company skips safety checks to save money, increasing risk for workers.",
                check_question="Who might be harmed if something goes wrong, and how?"
            ),
        ]
    elif concept.id == "ethics.concept.coercion":
        level = CurriculumLevel.UNDERGRAD_INTRO
        professor_view = EthicsConceptLessonProfessorView(
            spine_position=(
                "Appears early as 'being forced' in K–8; "
                "becomes a central topic in high-school and undergrad ethics and political philosophy."
            ),
            connections_to_other_areas=[
                "political legitimacy and state coercion",
                "contracts and consent in law",
                "manipulation vs autonomy in AI and tech design",
            ],
            deeper_theories=[
                "coercion vs exploitation in political philosophy",
                "threats vs offers in moral theory",
            ],
        )
        grad_view = EthicsConceptLessonGradView(
            core_tensions=[
                "When do background injustices make an apparently 'free' choice coercive?",
                "Are all threats coercive, or only some?",
            ],
            edge_cases=[
                "A doctor says: 'If you do not take this treatment, your condition will worsen.'",
                "A platform makes it very hard to opt out of data collection.",
            ],
            open_questions=[
                "How should AI-driven choice architectures avoid crossing into coercion?",
            ],
        )
        teacher_steps = [
            EthicsConceptLessonTeacherStep(
                order=1,
                prompt="Start with the idea of being forced to do something.",
                example="Someone says: 'If you don’t give me your lunch, I’ll hit you.'",
                check_question="Is this a free choice or are you being pushed to do something?"
            ),
            EthicsConceptLessonTeacherStep(
                order=2,
                prompt="Show that sometimes people say 'yes' but do not really feel free.",
                example="A boss hints that staying late is 'optional', but workers fear losing their job.",
                check_question="Does this feel like a real choice? Why or why not?"
            ),
            EthicsConceptLessonTeacherStep(
                order=3,
                prompt="Connect coercion to systems and designs, not just individuals.",
                example="An app makes it very hard to refuse tracking without losing key features.",
                check_question="How could designers make this feel less coercive?"
            ),
        ]
    elif concept.id == "ethics.concept.consent":
        level = CurriculumLevel.UNDERGRAD_INTRO
        professor_view = EthicsConceptLessonProfessorView(
            spine_position=(
                "Appears as 'asking permission' in K–8; "
                "formalizes into consent in high school; "
                "legally and ethically analyzed in undergrad and grad work."
            ),
            connections_to_other_areas=[
                "bioethics and informed consent",
                "privacy and data protection",
                "contract law and agreements",
            ],
            deeper_theories=[
                "informed consent in medical ethics",
                "relational theories of consent under power imbalance",
            ],
        )
        grad_view = EthicsConceptLessonGradView(
            core_tensions=[
                "Can consent be fully valid under large power differences?",
                "How much understanding is enough for consent to be informed?",
            ],
            edge_cases=[
                "Agreeing to terms of service no one realistically reads.",
                "Agreeing under emotional pressure rather than explicit threats.",
            ],
            open_questions=[
                "How should AI interfaces support real, not merely formal, consent?",
            ],
        )
        teacher_steps = [
            EthicsConceptLessonTeacherStep(
                order=1,
                prompt="Start with asking before you use or take something from someone.",
                example="You ask a friend, 'Can I borrow your book?' and they say yes.",
                check_question="Why is asking first important here?"
            ),
            EthicsConceptLessonTeacherStep(
                order=2,
                prompt="Show that for consent to be real, the person needs to understand.",
                example="A long, complicated pop-up asks you to accept new rules for your data.",
                check_question="If you do not understand the rules, is your 'yes' strong consent?"
            ),
            EthicsConceptLessonTeacherStep(
                order=3,
                prompt="Highlight that people must feel free to say no.",
                example="A student agrees to share personal information because they fear being left out.",
                check_question="Does this feel like free consent? Why or why not?"
            ),
        ]
    elif concept.id == "ethics.concept.autonomy":
        level = CurriculumLevel.UNDERGRAD_CORE
        professor_view = EthicsConceptLessonProfessorView(
            spine_position=(
                "Begins as 'making your own choices' in K–8; "
                "develops into autonomy and self-governance in high-school ethics; "
                "becomes central in undergrad and grad ethics, bioethics, and political theory."
            ),
            connections_to_other_areas=[
                "Kantian ethics and respect for persons",
                "bioethics and patient autonomy",
                "AI systems that support or undermine human agency",
            ],
            deeper_theories=[
                "Kantian autonomy and the moral law",
                "relational autonomy in feminist ethics",
            ],
        )
        grad_view = EthicsConceptLessonGradView(
            core_tensions=[
                "Is autonomy just non-interference, or does it require support and resources?",
                "How do social structures shape what choices feel real?",
            ],
            edge_cases=[
                "Someone chooses under heavy misinformation.",
                "A person 'freely' chooses options shaped by manipulative design.",
            ],
            open_questions=[
                "How should AI be designed to respect and enhance, not replace, human autonomy?",
            ],
        )
        teacher_steps = [
            EthicsConceptLessonTeacherStep(
                order=1,
                prompt="Begin with everyday choices people make for themselves.",
                example="Choosing what to wear or what hobby to try.",
                check_question="What makes these choices feel like 'your own'?"
            ),
            EthicsConceptLessonTeacherStep(
                order=2,
                prompt="Show that sometimes others make choices for us, for better or worse.",
                example="Parents decide a bedtime that you do not like.",
                check_question="When might it be okay for someone else to decide for you?"
            ),
            EthicsConceptLessonTeacherStep(
                order=3,
                prompt="Connect autonomy to having good information and not being pushed.",
                example="An app nudges you to keep scrolling, even when you wanted to stop.",
                check_question="Does this support your autonomy or pull against it?"
            ),
        ]
    elif concept.id == "ethics.concept.fairness":
        level = CurriculumLevel.SCHOOL_SECONDARY
        professor_view = EthicsConceptLessonProfessorView(
            spine_position=(
                "Fair vs unfair is central in K–8; "
                "ties into justice and equality in high school; "
                "becomes part of political philosophy and law in undergrad and grad work."
            ),
            connections_to_other_areas=[
                "distributive justice in political philosophy",
                "anti-discrimination law",
                "algorithmic fairness in AI",
            ],
            deeper_theories=[
                "Rawlsian justice and fairness",
                "luck egalitarianism and desert-based views",
            ],
        )
        grad_view = EthicsConceptLessonGradView(
            core_tensions=[
                "Should fairness focus on equal treatment, equal outcomes, or equal opportunities?",
                "How do we handle trade-offs between fairness and efficiency?",
            ],
            edge_cases=[
                "Policies that are formally equal but worsen existing inequalities.",
                "Randomization (lotteries) as a way to be fair when not everyone can get a benefit.",
            ],
            open_questions=[
                "What does fairness require when AI systems allocate limited opportunities?",
            ],
        )
        teacher_steps = [
            EthicsConceptLessonTeacherStep(
                order=1,
                prompt="Start from playground fairness: turns, sharing, and rules.",
                example="A game where only some kids ever get a turn.",
                check_question="Would this feel fair to you? Why or why not?"
            ),
            EthicsConceptLessonTeacherStep(
                order=2,
                prompt="Introduce that sometimes equal is not the same as fair.",
                example="Everyone gets the same size shoes, no matter their foot size.",
                check_question="Is this equal? Is it fair?"
            ),
            EthicsConceptLessonTeacherStep(
                order=3,
                prompt="Connect fairness to bigger systems like schools or jobs.",
                example="A scholarship process that favors people from certain backgrounds.",
                check_question="What questions would you ask to see if this is fair?"
            ),
        ]
    elif concept.id == "ethics.concept.loyalty":
        level = CurriculumLevel.SCHOOL_SECONDARY
        professor_view = EthicsConceptLessonProfessorView(
            spine_position=(
                "Shows up early as friendship and sticking by someone; "
                "becomes a theme in high-school ethics and literature; "
                "is analyzed in undergrad ethics and political theory as a partial value."
            ),
            connections_to_other_areas=[
                "virtue ethics and character",
                "nationalism and group loyalty in political philosophy",
                "conflicts between loyalty and justice in business and law",
            ],
            deeper_theories=[
                "special obligations to family, friends, and co-nationals",
            ],
        )
        grad_view = EthicsConceptLessonGradView(
            core_tensions=[
                "When does loyalty become moral blindness?",
                "How should loyalty be balanced against impartial justice?",
            ],
            edge_cases=[
                "Covering for a friend who cheated.",
                "Whistleblowing against your own organization.",
            ],
            open_questions=[
                "What kinds of loyalty should AI avoid reinforcing (e.g., to unhealthy groups)?",
            ],
        )
        teacher_steps = [
            EthicsConceptLessonTeacherStep(
                order=1,
                prompt="Begin with what it means to be a good friend or teammate.",
                example="Standing by a friend when they are being unfairly criticized.",
                check_question="What feels loyal in this situation?"
            ),
            EthicsConceptLessonTeacherStep(
                order=2,
                prompt="Show that loyalty can pull against other values like honesty or fairness.",
                example="A friend asks you to lie for them so they avoid trouble.",
                check_question="Is saying yes loyal, fair, both, or neither?"
            ),
            EthicsConceptLessonTeacherStep(
                order=3,
                prompt="Connect loyalty to groups and causes, not just individuals.",
                example="Feeling loyal to a school, team, or country even when it makes mistakes.",
                check_question="When should loyalty push you to speak up rather than stay silent?"
            ),
        ]
    else:  # ethics.concept.respect and any others
        level = CurriculumLevel.SCHOOL_SECONDARY
        professor_view = EthicsConceptLessonProfessorView(
            spine_position=(
                "Respect language appears very early (K–8); "
                "becomes tied to rights and dignity in high school; "
                "is central in undergrad ethics, political philosophy, and human rights theory."
            ),
            connections_to_other_areas=[
                "Kantian respect for persons",
                "human rights law",
                "anti-discrimination and dignity in social policy",
            ],
            deeper_theories=[
                "recognition theories in political philosophy",
                "Kantian and post-Kantian accounts of dignity",
            ],
        )
        grad_view = EthicsConceptLessonGradView(
            core_tensions=[
                "What do we owe people we strongly disagree with?",
                "Is respect mainly about actions, attitudes, or both?",
            ],
            edge_cases=[
                "Responding to hate speech while respecting persons.",
                "Respecting privacy vs intervening to prevent harm.",
            ],
            open_questions=[
                "How should AI systems signal respect in language and behavior?",
            ],
        )
        teacher_steps = [
            EthicsConceptLessonTeacherStep(
                order=1,
                prompt="Start from everyday respect: how we talk and listen to others.",
                example="Letting someone finish speaking before you respond.",
                check_question="Why does this feel respectful?"
            ),
            EthicsConceptLessonTeacherStep(
                order=2,
                prompt="Show respect as recognizing that others matter like you do.",
                example="Not sharing an embarrassing photo of someone without their permission.",
                check_question="What does this say about how you see that person?"
            ),
            EthicsConceptLessonTeacherStep(
                order=3,
                prompt="Connect respect to rules and structures, not just manners.",
                example="A rule that some students always get better resources than others.",
                check_question="What might be disrespectful about this rule?"
            ),
        ]

    teacher_view = EthicsConceptLessonTeacherView(steps=teacher_steps)

    return EthicsConceptLesson(
        id=f"philo.ethics.concept.{concept.id}",
        concept=concept,
        subject=SubjectId.PHILOSOPHY_CORE,
        domain=DomainId.HUMANITIES,
        level=level,
        professor_view=professor_view,
        grad_view=grad_view,
        teacher_view=teacher_view,
    )


@router.get(
    "/l6/ethics-concepts/overview",
    response_model=list[EthicsConceptLesson],
)
async def ethics_concepts_overview_l6() -> list[EthicsConceptLesson]:
    """
    Lane 6 overview: map the seven core ethics concepts along the K–PhD spine,
    with triple-role lesson views for each.
    """
    lessons: list[EthicsConceptLesson] = []
    for concept in _ETHICS_CONCEPTS.values():
        lessons.append(_build_ethics_concept_lesson(concept))
    return lessons


@router.get(
    "/l6/ethics-concepts/{concept_id}",
    response_model=EthicsConceptLesson,
)
async def ethics_concept_detail_l6(concept_id: str) -> EthicsConceptLesson:
    """
    Lane 6: detailed triple-role lesson for a single ethics concept.
    """
    concept = _ETHICS_CONCEPTS.get(concept_id)
    if concept is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unknown ethics concept")
    return _build_ethics_concept_lesson(concept)


@router.post(
    "/l6/ethics-concepts/{concept_id}/practice",
    response_model=EthicsConceptDiagnosisResponse,
)
async def ethics_concept_practice_l6(
    concept_id: str,
    request: EthicsConceptDiagnosisRequest,
) -> EthicsConceptDiagnosisResponse:
    """
    Lane 6 practice: reuse diagnosis for a concept, but framed as
    a teach/practice step. For now we call the same logic; later
    we can enrich this with targeted reflection prompts.
    """
    # Trust concept_id from path if not set in body
    effective_request = request
    if effective_request.concept_id != concept_id:
        effective_request = EthicsConceptDiagnosisRequest(
            concept_id=concept_id,
            case_id=request.case_id,
            case_description=request.case_description,
        )
    return await ethics_concept_diagnose(effective_request)

@router.post(
    "/k8/logic-seeds/practice",
    response_model=K8LogicPracticeResponse,
)
async def philosophy_k8_logic_seeds_practice(
    request: K8LogicPracticeRequest,
) -> K8LogicPracticeResponse:
    """
    K–8 Lane 1 practice: micro-exercises in spotting reasons vs conclusions
    and noticing weak reasons like name-calling or 'everyone does it'.
    PRIME always responds in a calm, non-judgmental, kid-friendly tone.
    """
    kind = request.item_kind
    answer = (request.answer_text or "").strip()

    if kind == K8LogicPracticeItemKind.SPOT_REASON_VS_CONCLUSION:
        prompt = (
            "Listen: 'You should wear a helmet because it keeps your head safe.' "
            "Which part is the reason? Which part is the conclusion?"
        )
        if not answer:
            return K8LogicPracticeResponse(
                item_kind=kind,
                prompt=prompt,
                child_answer=None,
                prime_paraphrase="I'll wait for you to tell me which part you think is the reason and which is the conclusion.",
                prime_feedback="",
                follow_up_question="What do you think? Which part is the reason, and which part is the conclusion?",
            )

        prime_paraphrase = f"So you think: {answer}"
        prime_feedback = (
            "In this sentence, 'it keeps your head safe' is the reason, "
            "and 'you should wear a helmet' is the conclusion. "
            "You noticed there are two parts—good work spotting them."
        )
        follow_up = "Can you think of another example where someone gives a reason and then a conclusion?"

        return K8LogicPracticeResponse(
            item_kind=kind,
            prompt=prompt,
            child_answer=answer,
            prime_paraphrase=prime_paraphrase,
            prime_feedback=prime_feedback,
            follow_up_question=follow_up,
        )

    if kind == K8LogicPracticeItemKind.IS_THAT_A_REASON:
        prompt = (
            "Your friend says: 'You're stupid if you don't like my favorite game.' "
            "Is that a reason for thinking the game is good, or just name-calling?"
        )
        if not answer:
            return K8LogicPracticeResponse(
                item_kind=kind,
                prompt=prompt,
                child_answer=None,
                prime_paraphrase="I'll wait for you to tell me what you think first.",
                prime_feedback="",
                follow_up_question="What do you think: is that a real reason, or just name-calling?",
            )

        prime_paraphrase = f"You answered: {answer}"
        prime_feedback = (
            "This sentence is name-calling, not a real reason. "
            "It does not explain what is good about the game. "
            "You can still like or dislike the game, but good reasons talk about the game, not about calling people names."
        )
        follow_up = "Can you think of a better reason someone could give for liking a game?"

        return K8LogicPracticeResponse(
            item_kind=kind,
            prompt=prompt,
            child_answer=answer,
            prime_paraphrase=prime_paraphrase,
            prime_feedback=prime_feedback,
            follow_up_question=follow_up,
        )

    if kind == K8LogicPracticeItemKind.EVERYONE_DOES_IT:
        prompt = (
            "Someone says: 'Everyone in my class cheats, so it's okay.' "
            "Does 'everyone does it' really show it is okay, or is that a weak reason?"
        )
        if not answer:
            return K8LogicPracticeResponse(
                item_kind=kind,
                prompt=prompt,
                child_answer=None,
                prime_paraphrase="I'll wait for your first thought.",
                prime_feedback="",
                follow_up_question="Does 'everyone does it' make something right, or could a lot of people be doing something wrong together?",
            )

        prime_paraphrase = f"You answered: {answer}"
        prime_feedback = (
            "Saying 'everyone does it' is usually a weak reason. "
            "Many people can do something and still be wrong. "
            "Stronger reasons talk about harm, fairness, or honesty, not just how many people do it."
        )
        follow_up = "If you wanted to explain why cheating is not okay, what reason could you give?"

        return K8LogicPracticeResponse(
            item_kind=kind,
            prompt=prompt,
            child_answer=answer,
            prime_paraphrase=prime_paraphrase,
            prime_feedback=prime_feedback,
            follow_up_question=follow_up,
        )

    prompt = (
        "Can you tell me something you believe, and one reason you have for it? "
        "You can start with: 'I think ___ because ___.'"
    )
    if not answer:
        return K8LogicPracticeResponse(
            item_kind=K8LogicPracticeItemKind.FREE_FORM_BELIEF_AND_REASON,
            prompt=prompt,
            child_answer=None,
            prime_paraphrase="I'll wait for you to try filling in the blanks.",
            prime_feedback="",
            follow_up_question="What is one belief you have, and what is one reason for it?",
        )

    prime_paraphrase = f"You said: {answer}"
    prime_feedback = (
        "Thank you for sharing that. You are practicing the habit of saying both what you think "
        "and why you think it. That is the first step in clear thinking."
    )
    follow_up = "If you wanted to change your mind about this belief, what kind of reason would you need to hear?"

    return K8LogicPracticeResponse(
        item_kind=K8LogicPracticeItemKind.FREE_FORM_BELIEF_AND_REASON,
        prompt=prompt,
        child_answer=answer,
        prime_paraphrase=prime_paraphrase,
        prime_feedback=prime_feedback,
        follow_up_question=follow_up,
    )

@router.post(
    "/k8/logic-seeds/planner",
    response_model=K8LogicPlannerResponse,
)
async def philosophy_k8_logic_seeds_planner(
    request: K8LogicPlannerRequest,
) -> K8LogicPlannerResponse:
    """
    K–8 logic planner.

    Returns both:
    - the logic seeds lesson
    - a logic practice response, using the question as free-form input
    """
    # Reuse the existing logic lesson endpoint
    lesson = await philosophy_k8_logic_seeds()

    # For now, treat the child's question as a free-form belief/reason item
    practice_req = K8LogicPracticeRequest(
        item_kind=K8LogicPracticeItemKind.FREE_FORM_BELIEF_AND_REASON,
        answer_text=request.question_text,
    )
    practice_resp = await philosophy_k8_logic_seeds_practice(practice_req)

    return K8LogicPlannerResponse(
        original_question=request.question_text,
        lesson=lesson.model_dump(),
        practice=practice_resp,
    )

@router.post(
    "/l1/what-is-philosophy/practice",
    response_model=PhilosophyPracticeResponse,
)
async def philosophy_lane1_practice(request: PhilosophyPracticeRequest) -> PhilosophyPracticeResponse:
    """
    Lane 1 practice: classify the user's question by philosophical kind and
    return clarifying and value-surfacing questions, instead of direct advice.
    """

    text = request.question_text.lower()

    # Very simple heuristic classification for now.
    if any(word in text for word in ["fair", "should i", "right", "wrong", "good", "bad", "ought", "responsible"]):
        kind = PhilosophyQuestionKind.ETHICS
        rationale = "Question mentions fairness, what someone should do, or right/wrong language."
    elif any(word in text for word in ["justice", "government", "law", "policy", "rights", "freedom", "equality", "power"]):
        kind = PhilosophyQuestionKind.POLITICAL_SOCIAL
        rationale = "Question refers to justice, law, government, or social structures."
    elif any(word in text for word in ["real", "exist", "reality", "free will", "identity", "soul", "mind", "consciousness", "time"]):
        kind = PhilosophyQuestionKind.METAPHYSICS
        rationale = "Question concerns what is real, identity, or features of reality like time and mind."
    elif any(word in text for word in ["know", "knowledge", "evidence", "certain", "doubt", "prove", "true", "truth"]):
        kind = PhilosophyQuestionKind.EPISTEMOLOGY
        rationale = "Question focuses on knowledge, evidence, or certainty."
    else:
        kind = PhilosophyQuestionKind.GENERAL
        rationale = "Question is broad or mixed; treating it as a general philosophical concern."

    # Clarifying questions tailored by kind.
    if kind == PhilosophyQuestionKind.ETHICS:
        clarifying = [
            "Who is affected by this decision, and in what ways?",
            "What do you see as the main options you are choosing between?",
            "Which outcomes or principles matter most to you here (e.g., harm, fairness, loyalty, honesty)?",
        ]
        value_prompts = [
            "If you imagine looking back on this choice in 10 years, what would you most want to be true about how you acted?",
            "Are you more worried about causing harm, breaking a rule, or betraying a relationship in this situation?",
        ]
        reflection = "Try to write your own rough argument: your main conclusion, two or three reasons, and one worry you have about those reasons."
    elif kind == PhilosophyQuestionKind.POLITICAL_SOCIAL:
        clarifying = [
            "Which groups or stakeholders are most affected by this issue?",
            "What do you see as the main kinds of injustice or risk here?",
            "Are you focusing more on individual freedom, collective welfare, or something else?",
        ]
        value_prompts = [
            "If a policy helped your preferred group but hurt a more vulnerable group, how would you weigh that trade-off?",
            "What kind of society are you implicitly aiming at when you think about this question?",
        ]
        reflection = "Try to state the strongest reasonable argument for a view you disagree with on this issue, as fairly as you can."
    elif kind == PhilosophyQuestionKind.METAPHYSICS:
        clarifying = [
            "Are you mainly asking what exists, or how things like time or identity work?",
            "Does your question depend on how we define key terms (like 'self', 'soul', or 'reality')?",
            "Is there a concrete example from your own life that makes this question feel pressing?",
        ]
        value_prompts = [
            "How would an answer to this question change the way you actually live, if at all?",
            "Are you hoping for comfort, clarity, or challenge from thinking about this?",
        ]
        reflection = "Describe one concrete decision in your life that this metaphysical question might influence, even indirectly."
    elif kind == PhilosophyQuestionKind.EPISTEMOLOGY:
        clarifying = [
            "What would you count as good enough evidence on this question?",
            "Are you more worried about believing something false or missing out on a truth?",
            "Do you trust some sources (people, institutions, methods) more than others here? Why?",
        ]
        value_prompts = [
            "In this area, do you think it is wiser to be cautious and skeptical, or to act confidently on limited evidence?",
            "Whose testimony or experience are you inclined to discount, and could that be a bias?",
        ]
        reflection = "Write down what you currently believe, why you believe it, and what kind of new information would most likely change your mind."
    else:
        # GENERAL
        clarifying = [
            "Can you restate your question in one sentence, as clearly as possible?",
            "Is your question mainly about what is true, what is real, what is right, or something else?",
            "Is there a particular decision or situation in your life that makes this question important now?",
        ]
        value_prompts = [
            "What do you most hope to gain from exploring this question: guidance, understanding, peace, motivation, something else?",
            "If someone you respect deeply answered this question differently than you, how open would you be to revising your view?",
        ]
        reflection = "Try to sort your question into parts: what is factual, what is conceptual, and what is about values."

    return PhilosophyPracticeResponse(
        original_question=request.question_text,
        inferred_kind=kind,
        rationale=rationale,
        clarifying_questions=clarifying,
        value_prompts=value_prompts,
        reflection_prompt=reflection,
    )

