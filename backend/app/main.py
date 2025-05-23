from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import (
    Session,
)  # Only needed if get_db is defined here, which it is not anymore.

# Import DB related items
from app.db import session as db_session
from app.api.endpoints import auth as auth_router  # Import the auth router
from app.api.endpoints import bots as bots_router  # Import the new bots router
from app.api.endpoints import websocket as websocket_router  # Import WebSocket router
from app.api.endpoints import external_bots as external_bots_router  # Import external bots router
from app.api.endpoints import shared_bots as shared_bots_router  # Import shared bots router

# Import logging
from app.core.logging import setup_logging, get_logger
from app.middleware.logging import RequestLoggingMiddleware

# Setup logging before anything else
setup_logging()
logger = get_logger("main")

app = FastAPI(
    title="TradeWise API",
    description="API for managing automated trading bot instances.",
    version="0.1.0",
)

# Add logging middleware first
app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
)


# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    logger.info("Starting TradeWise API", extra={"event_type": "application_startup"})
    db_session.init_db()
    logger.info("Database initialized", extra={"event_type": "database_initialized"})


# No global orchestrator instance here, it's instantiated within bots.py router or per-call if needed.


@app.get("/")
async def root():
    return {"message": "Welcome to Freqtrade SaaS API. See /docs for endpoint details."}


# Include the authentication router
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Authentication"])
# Include the new bots router
app.include_router(bots_router.router, prefix="/api/v1/bots", tags=["Bots"])
# Include external bots router
app.include_router(external_bots_router.router, prefix="/api/v1/external-bots", tags=["External Bots"])
# Include shared bots router
app.include_router(shared_bots_router.router, prefix="/api/v1/shared-bots", tags=["Shared Bots"])
# Include WebSocket router
app.include_router(websocket_router.router, prefix="/api/v1", tags=["WebSocket"])


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# If you want to run this directly using `python main.py` for simple testing:
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
