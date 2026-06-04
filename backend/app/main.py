from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.features.agents.router import router as agents_router
from app.features.auth.router import router as auth_router
from app.features.jobs.router import router as jobs_router
from app.features.leaderboard.router import router as leaderboard_router
from app.features.projects.router import router as projects_router
from app.features.reviews.router import router as reviews_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.api_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
    app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])
    app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
    app.include_router(reviews_router, prefix="/api", tags=["reviews"])
    app.include_router(leaderboard_router, prefix="/api/leaderboard", tags=["leaderboard"])

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return app


app = create_app()
