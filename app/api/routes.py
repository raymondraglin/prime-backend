from fastapi import APIRouter


from app.prime.endpoints import router as prime_router
from app.prime.math.endpoints import router as prime_math_router
from app.prime.curriculum.endpoints import router as curriculum_router
from app.prime.money.history_endpoints import router as money_history_router
from app.prime.humanities.philosophy.endpoints import router as philosophy_router
from app.prime.history.philosophy.endpoints import router as philosophy_history_router
from app.prime.reasoning.endpoints import router as reasoning_router
from app.prime.humanities.philosophy.endpoints_hs import router as philosophy_hs_router
from app.prime.humanities.philosophy.endpoints_core import router as philosophy_core_router


router = APIRouter()


# Core PRIME endpoints
router.include_router(prime_router, prefix="/prime", tags=["prime"])

# Math-related endpoints
router.include_router(prime_math_router, prefix="/prime/math", tags=["prime-math"])

# Curriculum snapshot endpoints (math + money history subjects)
router.include_router(curriculum_router, prefix="/prime/curriculum", tags=["prime-curriculum"])

# Money history curriculum endpoints
router.include_router(money_history_router, prefix="/prime", tags=["prime-money-history"])

# Humanities / philosophy endpoints
router.include_router(philosophy_router, prefix="/prime")

# Philosophy history endpoints
router.include_router(philosophy_history_router, prefix="/prime")

# Domain-agnostic reasoning core endpoints
router.include_router(reasoning_router, prefix="/prime", tags=["reasoning-core"])

router.include_router(philosophy_hs_router)

router.include_router(philosophy_core_router)
