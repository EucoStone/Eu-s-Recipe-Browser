from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import settings
from app.api.v1.endpoints.calculate import router as calculate_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.recipes import router as recipes_router
from app.api.v1.endpoints.upload import router as upload_router
from app.core.database import close_db, init_db
from app.core.translations import load_translation_file


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    upload_dir = Path(settings().upload_dir)
    if upload_dir.exists():
        for translation_file in upload_dir.rglob("zh_cn.json"):
            load_translation_file(translation_file)
    yield
    await close_db()


cfg = settings()
app = FastAPI(title=cfg.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(recipes_router, prefix="/api/v1")
app.include_router(calculate_router, prefix="/api/v1")
