"""
API routes package
"""

from fastapi import APIRouter
from .routes import policy, webpage

router = APIRouter()

router.include_router(policy.router, prefix="/policy", tags=["policy"])