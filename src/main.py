# type: ignore

from datetime import datetime
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from contexts.sample.infrastructure.api.entrypoints import router as sample_router
from contexts.auth.infrastructure.api.endpoints import router as auth_router
from composite_root.graphql import (
    graphql_app,
)
from composite_root.bootstrapper import bootstrap

description = """
Sample REST API
"""

app = FastAPI(
    root_path="/",
    title="Sample API",
    description=description,
    version="0.0.1",
    docs_url="/openapi",
    redoc_url="/redoc",
    contact={
        "name": "David Jiménez",
        "email": "davigetto@gmail.com@gmail.com",
    },
)

app.include_router(sample_router)
app.include_router(auth_router)
router = APIRouter()
app.include_router(graphql_app, prefix="/graphql")
router.add_websocket_route("/graphql/", graphql_app)

app.include_router(router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    expose_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    bootstrap()


@app.get("/hc")
def get_status():
    return JSONResponse(content={"time": str(datetime.utcnow())})
