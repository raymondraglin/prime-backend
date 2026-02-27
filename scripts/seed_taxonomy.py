"""
PRIME Taxonomy Seed — All 14 Domains + Full Math First Wave
File: scripts/seed_taxonomy.py

Usage:
    python scripts/seed_taxonomy.py

Requires DATABASE_URL in environment or .env
"""

import os
import sys
from pathlib import Path

# ── make sure app is importable ──────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL, echo=False)


# ─────────────────────────────────────────────────────────────
# SEED DATA
# ─────────────────────────────────────────────────────────────

DOMAINS = [
    {"code": "math_formal",         "name": "Mathematics and Formal Sciences",       "sort_order": 1,  "description": "Full ladder K-5 through PhD/Innovator. Arithmetic, analysis, algebra, topology, logic, set theory, category theory, theoretical computer science, mathematical finance."},
    {"code": "cs_ict",              "name": "Computer Science and ICT",               "sort_order": 2,  "description": "Binary, logic gates, all programming languages, data structures, algorithms, systems, AI, distributed computing, networks, cybersecurity."},
    {"code": "language_linguistics","name": "Language and Linguistics",               "sort_order": 3,  "description": "All natural languages (living, ancient, dead, dialectal), all formal and programming languages. Latin, Hebrew, Aramaic, Sanskrit, every ISO 639 language, every coding language."},
    {"code": "natural_sciences",    "name": "Natural Sciences",                       "sort_order": 4,  "description": "Physics, Chemistry, Biology, Earth Sciences, Astronomy, Oceanography, Environmental Science, Forensic Science, Zoology, Botany."},
    {"code": "engineering_tech",    "name": "Engineering and Technology",             "sort_order": 5,  "description": "Civil, mechanical, electrical, chemical, biomedical, computer, environmental, industrial/systems engineering. Robotics, materials science."},
    {"code": "humanities",          "name": "Humanities",                             "sort_order": 6,  "description": "Philosophy, Ethics, Literature, History, Linguistics, Religious Studies, Art History, Classical Studies, Cultural Studies."},
    {"code": "social_sciences",     "name": "Social Sciences",                        "sort_order": 7,  "description": "Psychology, Sociology, Political Science, Anthropology, Economics (applied), Geography, Civics, Media Studies, International Relations."},
    {"code": "business_finance",    "name": "Business, Finance, and Management",      "sort_order": 8,  "description": "Accounting, Finance, Marketing, Management, Operations, Supply Chain, Entrepreneurship, Investment, Portfolio Theory, Risk, Derivatives, MBA-level and Doctoral."},
    {"code": "health_life_sci",     "name": "Health and Life Sciences",               "sort_order": 9,  "description": "Nursing, Public Health, Epidemiology, Anatomy and Physiology, Health Policy, Global Health, Medicine (foundational), Biostatistics."},
    {"code": "education_study",     "name": "Education and Study Skills",             "sort_order": 10, "description": "Curriculum design, pedagogy, learning science, higher ed leadership, study skills, test preparation, instructional design."},
    {"code": "arts_media_design",   "name": "Arts, Media, and Design",                "sort_order": 11, "description": "Visual arts, Music, Theatre, Film, Photography, Graphic Design, Digital Media, Journalism, Communication Studies."},
    {"code": "law_policy_gov",      "name": "Law, Policy, and Governance",            "sort_order": 12, "description": "Law (constitutional, criminal, civil, international), Public Policy, Public Administration, Governance theory, Civics."},
    {"code": "env_agri_earth",      "name": "Environment, Agriculture, and Earth Systems", "sort_order": 13, "description": "Environmental Science, Earth Science, Geology, Agricultural Sciences, Sustainability, Climate Systems, Ecology."},
    {"code": "interdisciplinary",   "name": "Interdisciplinary and Research Skills",  "sort_order": 14, "description": "Research methodology, statistics for research, systems thinking, innovation theory, cross-domain synthesis, failure analysis."},
]


# ── Math subjects — full ladder ──────────────────────────────
# level_tag values:
#   SCHOOL_BASIC | SCHOOL_SEC | UG_CORE | GRAD_CORE | PHD_CORE | INNOVATOR

MATH_SUBJECTS = [
    # ── School Basic ────────────────────────────────────────
    {"code": "arithmetic",              "name": "Arithmetic and Number Sense",          "level_tag": "SCHOOL_BASIC", "sort_order": 1,  "description": "Counting, place value, operations, factors, primes, fractions, decimals, percentages, ratios."},
    {"code": "pre_algebra",             "name": "Pre-Algebra",                           "level_tag": "SCHOOL_BASIC", "sort_order": 2,  "description": "Variables, expressions, order of operations, linear equations in one variable, coordinate plane basics."},

    # ── School Secondary ────────────────────────────────────
    {"code": "algebra_1",               "name": "Algebra I",                             "level_tag": "SCHOOL_SEC",   "sort_order": 3,  "description": "Linear and quadratic functions, systems, polynomials, factoring, exponential functions intro."},
    {"code": "geometry_school",         "name": "Geometry (School)",                     "level_tag": "SCHOOL_SEC",   "sort_order": 4,  "description": "Shapes, proofs, similarity, congruence, Pythagorean theorem, circles, transformations."},
    {"code": "algebra_2",               "name": "Algebra II and Functions",              "level_tag": "SCHOOL_SEC",   "sort_order": 5,  "description": "Polynomial, rational, exponential, logarithmic functions; sequences and series; complex numbers."},
    {"code": "precalculus",             "name": "Trigonometry and Precalculus",          "level_tag": "SCHOOL_SEC",   "sort_order": 6,  "description": "Trig functions, unit circle, identities, vectors, parametric equations, limits intro."},
    {"code": "calculus_school",         "name": "Calculus (School Level)",               "level_tag": "SCHOOL_SEC",   "sort_order": 7,  "description": "Limits, derivatives, basic integration, Fundamental Theorem of Calculus. AP Calculus AB/BC scope."},
    {"code": "prob_stats_school",       "name": "Probability and Statistics (School)",  "level_tag": "SCHOOL_SEC",   "sort_order": 8,  "description": "Descriptive stats, basic probability, distributions, sampling, regression intro."},
    {"code": "consumer_financial_math", "name": "Consumer and Financial Math",           "level_tag": "SCHOOL_SEC",   "sort_order": 9,  "description": "Interest, loans, budgets, wages, taxes, cost-benefit, basic risk."},

    # ── Undergraduate Core ──────────────────────────────────
    {"code": "real_analysis_ug",        "name": "Real Analysis (Undergraduate)",         "level_tag": "UG_CORE",      "sort_order": 10, "description": "Epsilon-delta limits, sequences, series, Riemann integration, metric spaces intro."},
    {"code": "linear_algebra_ug",       "name": "Linear Algebra (Proof-Based)",          "level_tag": "UG_CORE",      "sort_order": 11, "description": "Vector spaces, linear maps, eigenvalues, inner product spaces, spectral theorem intro."},
    {"code": "abstract_algebra_ug",     "name": "Abstract Algebra (Undergraduate)",      "level_tag": "UG_CORE",      "sort_order": 12, "description": "Groups, rings, fields, homomorphisms, quotients, polynomial rings."},
    {"code": "topology_ug",             "name": "Topology and Intro Geometry (UG)",      "level_tag": "UG_CORE",      "sort_order": 13, "description": "Metric spaces, compactness, connectedness, intro point-set topology, curves/surfaces intro."},
    {"code": "discrete_math_ug",        "name": "Discrete Mathematics",                  "level_tag": "UG_CORE",      "sort_order": 14, "description": "Logic, sets, combinatorics, graph theory, recurrence relations."},
    {"code": "prob_stats_ug",           "name": "Probability and Statistics (UG)",       "level_tag": "UG_CORE",      "sort_order": 15, "description": "Probability spaces, random variables, distributions, CLT, estimation, hypothesis testing."},
    {"code": "diff_eq_ug",              "name": "Differential Equations and Numerical Methods", "level_tag": "UG_CORE", "sort_order": 16, "description": "ODEs, systems, Laplace transforms, PDE classification intro, Euler/RK numerical methods."},
    {"code": "multivariable_calc",      "name": "Multivariable Calculus",                "level_tag": "UG_CORE",      "sort_order": 17, "description": "Partial derivatives, gradient, divergence, curl, multiple integrals, Stokes/Green/Divergence theorems."},

    # ── Graduate Core ───────────────────────────────────────
    {"code": "measure_theory",          "name": "Measure Theory and Lebesgue Integration","level_tag": "GRAD_CORE",   "sort_order": 18, "description": "Sigma-algebras, measures, Lebesgue integral, convergence theorems, L^p spaces."},
    {"code": "functional_analysis",     "name": "Functional Analysis",                   "level_tag": "GRAD_CORE",    "sort_order": 19, "description": "Banach spaces, Hilbert spaces, bounded operators, spectral theory intro, distributions."},
    {"code": "complex_analysis_grad",   "name": "Complex Analysis (Graduate)",           "level_tag": "GRAD_CORE",    "sort_order": 20, "description": "Holomorphic functions, Cauchy theorem, residues, conformal maps, analytic continuation."},
    {"code": "algebra_grad",            "name": "Algebra (Graduate)",                    "level_tag": "GRAD_CORE",    "sort_order": 21, "description": "Sylow theorems, Galois theory, modules, Noetherian rings, homological algebra intro."},
    {"code": "topology_grad",           "name": "Topology (Graduate)",                   "level_tag": "GRAD_CORE",    "sort_order": 22, "description": "Point-set topology, fundamental group, covering spaces, intro homology/cohomology."},
    {"code": "diff_geometry_grad",      "name": "Differential Geometry (Graduate)",      "level_tag": "GRAD_CORE",    "sort_order": 23, "description": "Manifolds, tangent spaces, Riemannian metrics, connections, curvature."},
    {"code": "prob_stochastic_grad",    "name": "Probability and Stochastic Processes",  "level_tag": "GRAD_CORE",    "sort_order": 24, "description": "Measure-theoretic probability, modes of convergence, martingales, Markov chains, Brownian motion."},

    # ── PhD Core ────────────────────────────────────────────
    {"code": "phd_analysis",            "name": "PhD Analysis",                          "level_tag": "PHD_CORE",     "sort_order": 25, "description": "Advanced functional analysis, operator theory, harmonic analysis, distribution theory, PDE theory."},
    {"code": "phd_algebra",             "name": "PhD Algebra and Number Theory",         "level_tag": "PHD_CORE",     "sort_order": 26, "description": "Commutative algebra, algebraic geometry intro, representation theory, analytic number theory."},
    {"code": "phd_topology_geometry",   "name": "PhD Topology and Geometry",             "level_tag": "PHD_CORE",     "sort_order": 27, "description": "Algebraic topology, differential topology, Lie groups, symplectic geometry, characteristic classes."},
    {"code": "phd_probability",         "name": "PhD Probability and Stochastic Calculus","level_tag": "PHD_CORE",   "sort_order": 28, "description": "Stochastic calculus, Ito formula, SDE theory, Markov processes, ergodic theory."},
    {"code": "phd_numerical",           "name": "PhD Numerical Analysis and Optimization","level_tag": "PHD_CORE",   "sort_order": 29, "description": "Finite element/volume methods, iterative solvers, convex optimization, optimal control."},
    {"code": "logic_foundations",       "name": "Mathematical Logic and Foundations",    "level_tag": "PHD_CORE",     "sort_order": 30, "description": "Set theory, model theory, computability, proof theory, category theory, topos theory."},
    {"code": "math_finance",            "name": "Mathematical Finance",                  "level_tag": "PHD_CORE",     "sort_order": 31, "description": "Stochastic calculus for finance, Black-Scholes, term-structure models, portfolio optimization, risk measures (VaR, CVaR)."},

    # ── Innovator ───────────────────────────────────────────
    {"code": "math_innovator",          "name": "Mathematics: Innovator Layer",          "level_tag": "INNOVATOR",    "sort_order": 32, "description": "Open problems, cross-domain synthesis, mathematical modeling of unsolved societal challenges. Where math meets the future."},
    {"code": "math_history_philosophy", "name": "History and Philosophy of Mathematics", "level_tag": "INNOVATOR",    "sort_order": 33, "description": "Development of number systems, calculus wars, Hilbert's program, Godel, Turing, and the philosophical foundations of math."},
]


# ─────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────

def upsert_domains(session: Session) -> dict:
    """Insert domains, return code→id map."""
    from app.prime.models import Domain
    code_to_id = {}
    for d in DOMAINS:
        existing = session.query(Domain).filter_by(code=d["code"]).first()
        if not existing:
            obj = Domain(**d)
            session.add(obj)
            session.flush()
            code_to_id[d["code"]] = obj.id
            print(f"  + Domain: {d['code']}")
        else:
            code_to_id[d["code"]] = existing.id
            print(f"  ~ Domain exists: {d['code']}")
    return code_to_id


def upsert_math_subjects(session: Session, math_domain_id: int):
    """Insert math subjects under the math_formal domain."""
    from app.prime.models import Subject
    for s in MATH_SUBJECTS:
        existing = session.query(Subject).filter_by(
            domain_id=math_domain_id, code=s["code"]
        ).first()
        if not existing:
            obj = Subject(domain_id=math_domain_id, **s)
            session.add(obj)
            print(f"    + Subject: {s['code']} [{s['level_tag']}]")
        else:
            print(f"    ~ Subject exists: {s['code']}")


def seed():
    with Session(engine) as session:
        print("\n── Seeding domains ──────────────────────────────────")
        code_to_id = upsert_domains(session)

        math_id = code_to_id.get("math_formal")
        if math_id:
            print(f"\n── Seeding math subjects (domain_id={math_id}) ──────")
            upsert_math_subjects(session, math_id)
        else:
            print("ERROR: math_formal domain not found")

        session.commit()
        print("\n✓ Seed complete.")
        print(f"  Domains:       {len(DOMAINS)}")
        print(f"  Math subjects: {len(MATH_SUBJECTS)}")


if __name__ == "__main__":
    seed()
