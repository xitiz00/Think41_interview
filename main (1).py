from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MySQL database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'ecommerce_db'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# FastAPI app
app = FastAPI(
    title="E-commerce AI Backend API",
    description="Advanced e-commerce backend with AI-powered recommendations and analytics",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection helper
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Pydantic models
class DistributionCenter(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    age: Optional[int]
    gender: Optional[str]
    state: Optional[str]
    city: Optional[str]
    created_at: datetime

class Product(BaseModel):
    id: int
    name: str
    category: str
    brand: Optional[str]
    cost: float
    retail_price: float
    department: Optional[str]
    sku: Optional[str]
    distribution_center_id: Optional[int]

class Order(BaseModel):
    id: int
    user_id: int
    status: str
    created_at: datetime
    num_of_item: int

class AIRecommendationRequest(BaseModel):
    user_id: int
    category: Optional[str] = None
    max_price: Optional[float] = None
    limit: int = 5

# API Routes
@app.get("/")
async def root():
    return {
        "message": "E-commerce AI Backend API",
        "version": "2.0.0",
        "database": "MySQL",
        "features": ["AI Recommendations", "Real-time Analytics", "Product Management"],
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        connection.close()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "api": "online",
                "database": "online",
                "ai_engine": "active"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# Distribution Centers endpoints
@app.get("/distribution-centers")
async def get_distribution_centers():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM distribution_centers ORDER BY id")
        centers = cursor.fetchall()
        cursor.close()
        connection.close()
        return centers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/distribution-centers/{center_id}")
async def get_distribution_center(center_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM distribution_centers WHERE id = %s", (center_id,))
        center = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not center:
            raise HTTPException(status_code=404, detail="Distribution center not found")
        return center
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Users endpoints
@app.get("/users")
async def get_users(skip: int = 0, limit: int = 100):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users ORDER BY id LIMIT %s OFFSET %s", (limit, skip))
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Products endpoints
@app.get("/products")
async def get_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 100
):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if category:
            query += " AND category LIKE %s"
            params.append(f"%{category}%")
        
        if brand:
            query += " AND brand LIKE %s"
            params.append(f"%{brand}%")
        
        if min_price:
            query += " AND retail_price >= %s"
            params.append(min_price)
        
        if max_price:
            query += " AND retail_price <= %s"
            params.append(max_price)
        
        query += " ORDER BY id LIMIT %s OFFSET %s"
        params.extend([limit, skip])
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        cursor.close()
        connection.close()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Orders endpoints
@app.get("/orders")
async def get_orders(
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM orders WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = %s"
            params.append(user_id)
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, skip])
        
        cursor.execute(query, params)
        orders = cursor.fetchall()
        cursor.close()
        connection.close()
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI-powered recommendation endpoint
@app.post("/ai/recommendations")
async def get_ai_recommendations(request: AIRecommendationRequest):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user's order history for personalization
        user_orders_query = """
            SELECT DISTINCT p.category, p.brand, AVG(oi.sale_price) as avg_spent
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.user_id = %s
            GROUP BY p.category, p.brand
            ORDER BY COUNT(*) DESC
        """
        
        cursor.execute(user_orders_query, (request.user_id,))
        user_history = cursor.fetchall()
        
        # Build recommendation query based on user preferences
        rec_query = """
            SELECT p.*, 
                   CASE 
                       WHEN p.category IN (
                           SELECT DISTINCT category 
                           FROM order_items oi 
                           JOIN products pr ON oi.product_id = pr.id 
                           WHERE oi.user_id = %s
                       ) THEN 2
                       WHEN p.brand IN (
                           SELECT DISTINCT brand 
                           FROM order_items oi 
                           JOIN products pr ON oi.product_id = pr.id 
                           WHERE oi.user_id = %s
                       ) THEN 1
                       ELSE 0
                   END as preference_score
            FROM products p
            WHERE p.id NOT IN (
                SELECT DISTINCT product_id FROM order_items WHERE user_id = %s
            )
        """
        
        params = [request.user_id, request.user_id, request.user_id]
        
        if request.category:
            rec_query += " AND p.category LIKE %s"
            params.append(f"%{request.category}%")
        
        if request.max_price:
            rec_query += " AND p.retail_price <= %s"
            params.append(request.max_price)
        
        rec_query += " ORDER BY preference_score DESC, p.retail_price ASC LIMIT %s"
        params.append(request.limit)
        
        cursor.execute(rec_query, params)
        recommendations = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return {
            "user_id": request.user_id,
            "recommendations": recommendations,
            "user_preferences": user_history,
            "algorithm": "hybrid_collaborative_content_based",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.get("/analytics/sales-summary")
async def get_sales_summary():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT 
                COUNT(DISTINCT o.id) as total_orders,
                COUNT(DISTINCT o.user_id) as unique_customers,
                COALESCE(SUM(oi.sale_price), 0) as total_revenue,
                COALESCE(AVG(oi.sale_price), 0) as avg_order_value,
                COUNT(DISTINCT p.category) as product_categories
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.status != 'returned'
        """
        
        cursor.execute(query)
        summary = cursor.fetchone()
        cursor.close()
        connection.close()
        
        return summary if summary else {}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/top-products")
async def get_top_products(limit: int = 10):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT 
                p.id,
                p.name,
                p.category,
                p.brand,
                COUNT(oi.id) as order_count,
                COALESCE(SUM(oi.sale_price), 0) as total_revenue,
                COALESCE(AVG(oi.sale_price), 0) as avg_price
            FROM products p
            JOIN order_items oi ON p.id = oi.product_id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status != 'returned'
            GROUP BY p.id, p.name, p.category, p.brand
            ORDER BY order_count DESC, total_revenue DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        top_products = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return top_products
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
