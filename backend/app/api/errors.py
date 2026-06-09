from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import AppError

def register_error_handlers(app: FastAPI) -> None: 
    @app.exception_handler(AppError) 
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse: 
        return JSONResponse(
            status_code=exc.status_code, 
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message, 
                }, 
            }
        )