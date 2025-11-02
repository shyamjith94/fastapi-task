from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from app.core import settings
from fastapi.middleware.cors import CORSMiddleware
from app.api.depends import Database
from app.api.routes import auth_router, chat_router
import logging
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette import status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from typing import Union
from app.logs import logger



# app events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Simple DB connection check
    try:
        Database(check_connection=True)
    except Exception as e:
        print("Database connection failed:", e)
        raise e

    # Run the app
    yield

    # Shutdown logic


    

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_TAG}/openapi.json",
    docs_url="/docs",
    readoc_url="/readdoc",
    lifespan=lifespan,  # modern startup/shutdown handler
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Exception handlers
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    error_msg = str(exc)
    if isinstance(exc, IntegrityError):
        status_code = status.HTTP_409_CONFLICT
        message = "Database integrity error"
    elif isinstance(exc, OperationalError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        message = "Database connection error"
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = "Database error occurred"
    
    logger.error(f"Database error: {error_msg}")
    return JSONResponse(
        status_code=status_code,
        content={"detail": message, "type": exc.__class__.__name__}
    )



app.include_router(router=auth_router, prefix=f"{settings.API_TAG}/v1", tags=["auth"])
app.include_router(router=chat_router, prefix=f"{settings.API_TAG}/v1", tags=["chat"])


@app.get("/")
def home():
    return {"message": "Hello, FastAPI with VS Code!"}

