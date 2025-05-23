from fastapi import FastAPI
from sqlalchemy.orm import (
    Session,
)  # Only needed if get_db is defined here, which it is not anymore.

# Import DB related items
from app.db import session as db_session
from app.api.endpoints import auth as auth_router  # Import the auth router
from app.api.endpoints import bots as bots_router  # Import the new bots router

app = FastAPI(
    title="Freqtrade SaaS API",
    description="API for managing Freqtrade bot instances.",
    version="0.1.0",
)


# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    db_session.init_db()


# No global orchestrator instance here, it's instantiated within bots.py router or per-call if needed.


@app.get("/")
async def root():
    return {"message": "Welcome to Freqtrade SaaS API. See /docs for endpoint details."}


# Include the authentication router
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Authentication"])
# Include the new bots router
app.include_router(bots_router.router, prefix="/api/v1/bots", tags=["Bots"])


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# If you want to run this directly using `python main.py` for simple testing:
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
