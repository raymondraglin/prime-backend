from fastapi import APIRouter

router = APIRouter()

from . import routes  # noqa: F401
