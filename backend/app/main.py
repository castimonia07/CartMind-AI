from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import shopping, conversation, ws, products, recommendations

app = FastAPI(
    title="CartMind AI API",
    description="Context-Aware Voice Shopping & Decision Agent",
    version="1.0.0",
)

# Allow all common local development origins
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to CartMind AI API", "status": "running"}

# Mount routers under /api prefix
app.include_router(shopping.router, prefix="/api")
app.include_router(conversation.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")

# Mount WebSocket router directly (ws paths handle their own route)
app.include_router(ws.router)