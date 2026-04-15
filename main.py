from fastapi import FastAPI
from app.api.routes.users import router as user_router
from app.database import engine, Base
from app.models.user import User  # Import to ensure table is created

app = FastAPI(title="User API", version="1.0")

# Create tables on startup
@app.on_event("startup")
def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

app.include_router(user_router)

@app.get("/")
def root():
    return {"message": "Welcome to User API", "docs": "/docs"}