import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors import EntityNotFoundError, BusinessRuleError, ExternalAPIError, AuthenticationError
from app.routes import users_router, spotify_router
from app.settings import get_settings

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title="Users & Spotify API", version="2.5")


@app.exception_handler(EntityNotFoundError)
async def entity_not_found_handler(request: Request, exc: EntityNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Not Found", "message": exc.message}
    )


@app.exception_handler(BusinessRuleError)
async def business_rule_handler(request: Request, exc: BusinessRuleError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error": "Business Rule Violation", "message": exc.message}
    )


@app.exception_handler(AuthenticationError)
async def auth_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error": "Unauthorized", "message": exc.message}
    )


@app.exception_handler(ExternalAPIError)
async def external_api_handler(request: Request, exc: ExternalAPIError):
    logger.error(f"External API Error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"error": "External Service Error", "message": exc.message}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error['loc'][1:])
        msg = error['msg']
        errors.append(f"{field}: {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation Error", "details": errors}
    )


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(spotify_router)
