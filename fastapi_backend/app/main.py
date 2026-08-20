from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from .models import Base

from .auth.router import router as auth_router
from .product.router import router as product_router
from .cart.router import router as cart_router
from .order.router import router as order_router
from .dashboard.router import router as dashboard_router
from .payment.router import router as payment_router
from .analytics.router import router as analytics_router
from .admin.router import router as admin_router
from .checkout.router import router as checkout_router

# IMPORTANT
from .stripe.router import router as stripe_router


app = FastAPI(
    title="Smart E-Commerce Platform"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# DATABASE TABLES
# =========================================================

Base.metadata.create_all(
    bind=engine
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(auth_router)

app.include_router(product_router)

app.include_router(cart_router)

app.include_router(order_router)

app.include_router(dashboard_router)

app.include_router(payment_router)

app.include_router(analytics_router)

app.include_router(admin_router)

app.include_router(checkout_router)

# IMPORTANT
app.include_router(stripe_router)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "Smart Ecommerce Running"
    }