import pandas as pd
import mysql.connector
from mysql.connector import Error
import requests
from io import StringIO
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EcommerceDataLoader:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        
    def connect_db(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            logger.info("Connected to MySQL database successfully")
        except Error as e:
            logger.error(f"Error connecting to MySQL database: {e}")
            raise
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL database connection closed")
    
    def fetch_csv_data(self, url):
        """Fetch CSV data from URL"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return pd.read_csv(StringIO(response.text))
        except Exception as e:
            logger.error(f"Error fetching CSV from {url}: {e}")
            return None
    
    def load_distribution_centers(self):
        """Load distribution centers data"""
        url = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/distribution_centers-uSjpFrqP0stuGtTlXRowr1zITPT2yY.csv"
        df = self.fetch_csv_data(url)
        
        if df is None:
            logger.error("Failed to fetch distribution centers data")
            return
        
        cursor = self.connection.cursor()
        
        try:
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO distribution_centers (id, name, latitude, longitude)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        name = VALUES(name),
                        latitude = VALUES(latitude),
                        longitude = VALUES(longitude),
                        updated_at = CURRENT_TIMESTAMP
                """, (int(row['id']), row['name'], float(row['latitude']), float(row['longitude'])))
            
            self.connection.commit()
            logger.info(f"Loaded {len(df)} distribution centers")
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error loading distribution centers: {e}")
        finally:
            cursor.close()
    
    def generate_sample_data(self):
        """Generate sample data for other tables since CSV files are empty"""
        cursor = self.connection.cursor()
        
        try:
            # Sample users
            users_data = [
                ('John', 'Doe', 'john.doe@email.com', 30, 'M', 'CA', '123 Main St', '90210', 'Los Angeles', 'USA', 34.0522, -118.2437, 'google'),
                ('Jane', 'Smith', 'jane.smith@email.com', 25, 'F', 'NY', '456 Broadway', '10001', 'New York', 'USA', 40.7128, -74.0060, 'facebook'),
                ('Bob', 'Johnson', 'bob.johnson@email.com', 35, 'M', 'TX', '789 Oak Ave', '75201', 'Dallas', 'USA', 32.7767, -96.7970, 'organic'),
                ('Alice', 'Brown', 'alice.brown@email.com', 28, 'F', 'FL', '321 Pine St', '33101', 'Miami', 'USA', 25.7617, -80.1918, 'email'),
                ('Charlie', 'Wilson', 'charlie.wilson@email.com', 42, 'M', 'WA', '654 Cedar Rd', '98101', 'Seattle', 'USA', 47.6062, -122.3321, 'google')
            ]
            
            for user in users_data:
                cursor.execute("""
                    INSERT INTO users (first_name, last_name, email, age, gender, state, street_address, postal_code, city, country, latitude, longitude, traffic_source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, user)
            
            # Sample products
            products_data = [
                (15.50, 'Electronics', 'Wireless Headphones', 'TechBrand', 79.99, 'Audio', 'WH001', 1),
                (25.00, 'Clothing', 'Cotton T-Shirt', 'FashionCo', 29.99, 'Apparel', 'TS001', 2),
                (45.00, 'Home & Garden', 'Coffee Maker', 'KitchenPro', 89.99, 'Kitchen', 'CM001', 1),
                (8.50, 'Books', 'Programming Guide', 'TechBooks', 24.99, 'Education', 'PG001', 3),
                (35.00, 'Sports', 'Running Shoes', 'SportMax', 119.99, 'Footwear', 'RS001', 2),
                (12.00, 'Electronics', 'Phone Case', 'TechBrand', 19.99, 'Accessories', 'PC001', 1),
                (18.00, 'Clothing', 'Jeans', 'FashionCo', 59.99, 'Apparel', 'JN001', 2),
                (30.00, 'Home & Garden', 'Desk Lamp', 'HomePro', 49.99, 'Furniture', 'DL001', 3),
                (5.50, 'Books', 'Novel', 'BookWorld', 14.99, 'Fiction', 'NV001', 1),
                (28.00, 'Sports', 'Yoga Mat', 'FitLife', 39.99, 'Fitness', 'YM001', 2)
            ]
            
            for product in products_data:
                cursor.execute("""
                    INSERT INTO products (cost, category, name, brand, retail_price, department, sku, distribution_center_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, product)
            
            # Sample inventory items
            cursor.execute("SELECT id, cost, category, name, brand, retail_price, department, sku, distribution_center_id FROM products")
            products = cursor.fetchall()
            
            for product in products:
                # Create 3-5 inventory items per product
                for i in range(3, 6):
                    cursor.execute("""
                        INSERT INTO inventory_items (product_id, cost, product_category, product_name, product_brand, product_retail_price, product_department, product_sku, product_distribution_center_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (product[0], product[1], product[2], product[3], product[4], product[5], product[6], product[7], product[8]))
            
            # Sample orders
            orders_data = [
                (1, 'completed', 'M', '2024-01-15 10:30:00', None, '2024-01-16 14:20:00', '2024-01-18 16:45:00', 2),
                (2, 'shipped', 'F', '2024-01-20 09:15:00', None, '2024-01-21 11:30:00', None, 1),
                (3, 'pending', 'M', '2024-01-25 14:45:00', None, None, None, 3),
                (4, 'completed', 'F', '2024-01-28 16:20:00', None, '2024-01-29 10:15:00', '2024-01-31 13:30:00', 1),
                (5, 'returned', 'M', '2024-02-01 11:00:00', '2024-02-10 09:30:00', '2024-02-02 15:45:00', '2024-02-05 12:20:00', 2)
            ]
            
            for order in orders_data:
                cursor.execute("""
                    INSERT INTO orders (user_id, status, gender, created_at, returned_at, shipped_at, delivered_at, num_of_item)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, order)
            
            # Sample order items
            order_items_data = [
                (1, 1, 1, 1, 'completed', '2024-01-15 10:30:00', '2024-01-16 14:20:00', '2024-01-18 16:45:00', None, 79.99),
                (1, 1, 3, 3, 'completed', '2024-01-15 10:30:00', '2024-01-16 14:20:00', '2024-01-18 16:45:00', None, 89.99),
                (2, 2, 2, 4, 'shipped', '2024-01-20 09:15:00', '2024-01-21 11:30:00', None, None, 29.99),
                (3, 3, 4, 7, 'pending', '2024-01-25 14:45:00', None, None, None, 24.99),
                (3, 3, 5, 8, 'pending', '2024-01-25 14:45:00', None, None, None, 119.99),
                (3, 3, 6, 9, 'pending', '2024-01-25 14:45:00', None, None, None, 19.99),
                (4, 4, 7, 10, 'completed', '2024-01-28 16:20:00', '2024-01-29 10:15:00', '2024-01-31 13:30:00', None, 59.99),
                (5, 5, 8, 11, 'returned', '2024-02-01 11:00:00', '2024-02-02 15:45:00', '2024-02-05 12:20:00', '2024-02-10 09:30:00', 49.99),
                (5, 5, 9, 12, 'returned', '2024-02-01 11:00:00', '2024-02-02 15:45:00', '2024-02-05 12:20:00', '2024-02-10 09:30:00', 14.99)
            ]
            
            for order_item in order_items_data:
                cursor.execute("""
                    INSERT INTO order_items (order_id, user_id, product_id, inventory_item_id, status, created_at, shipped_at, delivered_at, returned_at, sale_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, order_item)
            
            self.connection.commit()
            logger.info("Generated sample data successfully")
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error generating sample data: {e}")
        finally:
            cursor.close()
    
    def load_all_data(self):
        """Load all data into the database"""
        self.connect_db()
        try:
            self.load_distribution_centers()
            self.generate_sample_data()
            logger.info("All data loaded successfully")
        finally:
            self.close_connection()

if __name__ == "__main__":
    # MySQL database configuration
    db_config = {
        'host': 'localhost',
        'database': 'ecommerce_db',
        'user': 'root',
        'password': 'password',
        'port': 3306,
        'autocommit': False
    }
    
    loader = EcommerceDataLoader(db_config)
    loader.load_all_data()
