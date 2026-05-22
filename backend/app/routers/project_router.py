from fastapi import APIRouter

from app.services.project_info_service import get_project_info


router = APIRouter(prefix="/api", tags=["project"])


@router.get("/project-info")
def project_info() -> dict:
    return get_project_info()
