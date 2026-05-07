from fastapi import FastAPI
from app.api.routes.users import router as user_router
from app.api.routes.products import router as product_router
from app.database import engine, Base
from app.models.user import User
from app.models.product import Product,Category
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="User API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your React/Vite frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Create tables on startup
@app.on_event("startup")
def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

app.include_router(user_router)
app.include_router(product_router)
@app.get("/")
def root():
    return {"message": "Welcome to User API", "docs": "/docs"}