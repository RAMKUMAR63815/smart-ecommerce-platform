# Smart E-Commerce Platform

A full-stack Smart E-Commerce Platform developed as part of a backend/full-stack development assignment. The system provides user authentication, JWT-based authorization, social login integration, role-based access control, product management, cart management, order processing, payments, dashboard analytics, and API testing using Postman.

---

## 1. Project Overview

The Smart E-Commerce Platform is designed with a modular architecture that separates backend services, administration, frontend functionality, and API testing.

### Main Features

* User registration and login
* Secure password hashing
* JWT access token authentication
* JWT refresh token authentication
* User profile authentication
* Auth0 social login integration
* Role-Based Access Control (RBAC)
* Admin, Staff, and Customer roles
* Product management
* Shopping cart management
* Order creation and management
* Payment status management
* Dashboard statistics
* Analytics APIs
* Swagger/OpenAPI documentation
* Postman API collection

---

## 2. Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* JWT
* Python-Jose
* MySQL

### Authentication

* JWT Access Token
* JWT Refresh Token
* Password Hashing
* Auth0
* Google Login
* Facebook Login

### API Testing

* Swagger UI
* Postman

### Database

* MySQL

### Additional Technologies

* Django
* React / Next.js
* Git

---

## 3. Project Architecture

```text
smart_ecommerce/
│
├── fastapi_backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── auth/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── django_admin/
│
├── frontend/
│
├── Postman/
│   ├── Smart_Ecommerce_Postman_Collection.json
│   └── Smart_Ecommerce_Environment.json
│
└── README.md
```

> Folder names may vary depending on the final project structure.

---

# 4. Database Design

The application uses MySQL as the primary database.

## User

Stores registered users and their roles.

| Field      | Description              |
| ---------- | ------------------------ |
| id         | Unique user ID           |
| name       | User name                |
| email      | Unique email address     |
| password   | Hashed password          |
| role       | admin / staff / customer |
| created_at | Account creation date    |

## Product

Stores product information.

| Field       | Description         |
| ----------- | ------------------- |
| id          | Unique product ID   |
| name        | Product name        |
| description | Product description |
| price       | Product price       |
| stock       | Available stock     |
| images      | Product image URL   |

## Cart

Stores products added to a user's cart.

| Field      | Description      |
| ---------- | ---------------- |
| id         | Cart item ID     |
| user_id    | User ID          |
| product_id | Product ID       |
| quantity   | Product quantity |

## Order

Stores customer orders.

| Field        | Description          |
| ------------ | -------------------- |
| id           | Order ID             |
| user_id      | Customer ID          |
| total_amount | Total order amount   |
| status       | Order/payment status |

---

# 5. Authentication System

The authentication system is implemented using JWT.

## Registration

```text
POST /auth/register
```

Creates a new customer account.

Example request:

```json
{
  "name": "Postman User",
  "email": "postmanuser@gmail.com",
  "password": "Test@12345"
}
```

---

## Login

```text
POST /auth/login
```

Authenticates the user and generates JWT tokens.

Example request:

```json
{
  "email": "postmanuser@gmail.com",
  "password": "Test@12345"
}
```

The response contains an access token and refresh token.

---

## Refresh Token

```text
POST /auth/refresh
```

Generates a new access token using the refresh token.

---

## Current User

```text
GET /auth/me
```

Returns the currently authenticated user's information.

Requires:

```text
Authorization: Bearer <access_token>
```

---

# 6. Social Login

Auth0 is integrated for social authentication.

Supported providers:

* Google
* Facebook

Social login flow:

```text
User
  ↓
Google / Facebook
  ↓
Auth0
  ↓
Token Verification
  ↓
Create / Find User
  ↓
Application JWT
  ↓
Authenticated User
```

Endpoint:

```text
POST /auth/social-login
```

---

# 7. Role-Based Access Control

The application implements three roles.

### Admin

Administrators can:

* Manage products
* View users
* View analytics
* Access administrative APIs

### Staff

Staff users can access permitted operational functionality according to their assigned permissions.

### Customer

Customers can:

* View products
* Add products to cart
* Update cart
* Remove cart items
* Create orders
* Make/complete payments
* View their orders

Protected endpoints validate the JWT token and user role before allowing access.

---

# 8. Product APIs

### Get Products

```text
GET /products/
```

### Create Product

```text
POST /products/
```

### Get Product

```text
GET /products/{product_id}
```

### Delete Product

```text
DELETE /products/{product_id}
```

Product creation and administrative operations are protected using role-based authorization.

---

# 9. Cart APIs

### Add to Cart

```text
POST /cart/add
```

### View Cart

```text
GET /cart/
```

### Update Cart

```text
PUT /cart/update/{cart_id}
```

### Remove from Cart

```text
DELETE /cart/remove/{cart_id}
```

---

# 10. Order APIs

### Create Order

```text
POST /orders/create
```

### Get Orders

```text
GET /orders/
```

### Get Order

```text
GET /orders/{order_id}
```

### Payment Success

```text
PUT /orders/{order_id}/pay
```

---

# 11. Payment APIs

### Get Payment Order

```text
GET /payment/{order_id}
```

### Complete Payment

```text
POST /payment/{order_id}/pay
```

The payment functionality updates the corresponding order/payment status.

---

# 12. Dashboard and Analytics

### Dashboard

```text
GET /dashboard/
```

Provides high-level application statistics such as:

* Total users
* Total products
* Total cart items
* Total orders

### Analytics

```text
GET /analytics/
```

Provides application analytics.

### Admin Users

```text
GET /admin/users
```

### Admin Analytics

```text
GET /admin/analytics
```

Administrative endpoints are protected using role-based authorization.

---

# 13. API Documentation

FastAPI automatically provides Swagger UI.

After starting the backend, open:

```text
http://127.0.0.1:8000/docs
```

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
```

Swagger can be used to test the APIs directly from the browser.

---

# 14. Running the Backend

## Step 1 — Navigate to Backend

```powershell
cd fastapi_backend
```

## Step 2 — Activate Virtual Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If the virtual environment has a different name, activate the corresponding environment.

## Step 3 — Install Dependencies

```powershell
pip install -r requirements.txt
```

## Step 4 — Configure Environment Variables

Create a `.env` file in the backend directory.

Example:

```env
DB_USER=root
DB_PASSWORD=your_database_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=smart_ecommerce

SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> Never commit real passwords, secret keys, Auth0 secrets, or other credentials to Git.

## Step 5 — Start FastAPI

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 15. Postman Collection

A Postman collection has been created for testing the application's APIs.

### Authentication requests included

```text
POST /auth/register
POST /auth/login
POST /auth/refresh
GET  /auth/me
POST /auth/social-login
```

### Other API groups

```text
Products
Cart
Orders
Payment
Dashboard
Analytics
Admin
```

The Postman environment uses:

```text
baseUrl = http://127.0.0.1:8000
```

The collection can be imported into Postman for API testing.

---

# 16. Authentication Testing Flow

Recommended testing sequence:

```text
1. Register
      ↓
2. Login
      ↓
3. Copy access_token
      ↓
4. Call /auth/me
      ↓
5. Copy refresh_token
      ↓
6. Call /auth/refresh
      ↓
7. Test protected APIs
```

For protected APIs, use:

```text
Authorization: Bearer <access_token>
```

---

# 17. Security

The application implements several security mechanisms:

* Password hashing
* JWT authentication
* Access token expiration
* Refresh token support
* Protected API routes
* Role-based authorization
* Auth0 token verification
* Environment-based configuration

Sensitive configuration should be stored in environment variables rather than source code.

---

# 18. Testing

The APIs can be tested using:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### Postman

The provided Postman collection contains requests for the authentication and application APIs.

Testing covers:

* User registration
* User login
* Token generation
* Token refresh
* Current user authentication
* Social login
* Product operations
* Cart operations
* Order operations
* Payment operations
* Admin authorization
* Analytics

---

# 19. Example Authentication Flow

```text
                 ┌──────────────────┐
                 │      User        │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │    Register      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │      Login       │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │    JWT Token     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Protected APIs   │
                 └────────┬─────────┘
                          │
                  ┌───────┴────────┐
                  ▼                ▼
              Customer           Admin
                  │                │
                  ▼                ▼
               Orders          Products/
               Cart            Analytics
```

---

# 20. Project Deliverables

The completed assignment includes:

* FastAPI authentication implementation
* Database models
* JWT access token authentication
* JWT refresh token authentication
* Auth0 social login integration
* Role-Based Access Control
* Product APIs
* Cart APIs
* Order APIs
* Payment APIs
* Dashboard and analytics APIs
* Swagger/OpenAPI documentation
* Postman collection
* Postman environment
* Project source code

---

# 21. Future Enhancements

Possible future improvements include:

* Razorpay/Stripe payment gateway integration
* Product image upload using cloud storage
* Order item table
* Product categories
* Product search and filtering
* Pagination
* Email notifications
* Docker deployment
* CI/CD pipeline
* Production database configuration
* Automated API testing
* Frontend integration
* Deployment to cloud infrastructure

---

# 22. Author

**Ram Kumar**

Smart E-Commerce Platform
Python / FastAPI / MySQL / JWT / Auth0

---

## Conclusion

The Smart E-Commerce Platform demonstrates a production-oriented backend architecture with authentication, authorization, database management, product management, cart and order processing, payment handling, social login, analytics, and API testing.

The project is designed to provide a secure and scalable foundation for a complete full-stack e-commerce application.
