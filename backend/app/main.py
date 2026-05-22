from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import data_router, project_router, staging_router


app = FastAPI(
    title="一汽绿运：备车优化与短驳方案展示平台",
    description="面向简历展示和面试讲解的整车出库备车优化 Web Demo。",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "message": "FAW staging shuttle backend is running."}


app.include_router(data_router.router)
app.include_router(staging_router.router)
app.include_router(project_router.router)
