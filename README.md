# Smart E-Commerce Platform

A full-stack **Smart E-Commerce Platform** developed as part of a backend/full-stack development assignment. The application provides secure user authentication, JWT-based authorization, Auth0 social login, role-based access control, product management, cart management, order processing, payment handling, dashboard and analytics APIs, and API testing using Postman.

---

## 1. Project Overview

The Smart E-Commerce Platform follows a modular architecture that separates backend services, administration, frontend functionality, database operations, authentication, and API testing.

### Main Features

* User registration and login
* Secure password hashing
* JWT access token authentication
* JWT refresh token authentication
* Current user authentication
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
* MySQL database integration

---

# 2. Technology Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* Python-Jose
* JWT
* MySQL

## Authentication

* JWT Access Token
* JWT Refresh Token
* Password Hashing
* Auth0
* Google Login
* Facebook Login

## API Testing

* Swagger UI
* Postman

## Additional Technologies

* Django
* React / Next.js
* Git
* GitHub

---

# 3. Project Architecture

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
│   └── ...
│
├── django_admin/
│
├── frontend/
│
├── postman/
│   ├── collections/
│   │   └── Smart E-Commerce Platform/
│   ├── environments/
│   └── globals/
│
├── .env.example
├── .gitignore
└── README.md
```

> The exact folder structure may vary depending on the final project configuration.

---

# 4. Database Design

The application uses **MySQL** as the primary database.

## User

Stores registered users and their roles.

| Field        | Description              |
| ------------ | ------------------------ |
| `id`         | Unique user ID           |
| `name`       | User name                |
| `email`      | Unique email address     |
| `password`   | Hashed password          |
| `role`       | Admin / Staff / Customer |
| `created_at` | Account creation date    |

## Product

Stores product information.

| Field         | Description               |
| ------------- | ------------------------- |
| `id`          | Unique product ID         |
| `name`        | Product name              |
| `description` | Product description       |
| `price`       | Product price             |
| `stock`       | Available stock           |
| `images`      | Product image information |

## Cart

Stores products added to a user's cart.

| Field        | Description      |
| ------------ | ---------------- |
| `id`         | Cart item ID     |
| `user_id`    | User ID          |
| `product_id` | Product ID       |
| `quantity`   | Product quantity |

## Order

Stores customer orders.

| Field          | Description          |
| -------------- | -------------------- |
| `id`           | Order ID             |
| `user_id`      | Customer ID          |
| `total_amount` | Total order amount   |
| `status`       | Order/payment status |

---

# 5. Authentication System

The authentication system uses **JWT-based authentication** with access and refresh tokens.

## Registration

```http
POST /auth/register
```

Creates a new customer account.

Example request:

```json
{
  "name": "Postman User",
  "email": "example@gmail.com",
  "password": "your_password"
}
```

---

## Login

```http
POST /auth/login
```

Authenticates the user and generates JWT tokens.

Example request:

```json
{
  "email": "example@gmail.com",
  "password": "your_password"
}
```

The response provides authentication tokens used to access protected APIs.

---

## Refresh Token

```http
POST /auth/refresh
```

Generates a new access token using a valid refresh token.

---

## Current User

```http
GET /auth/me
```

Returns information about the currently authenticated user.

Protected request:

```http
Authorization: Bearer <access_token>
```

---

# 6. Social Login

Auth0 is integrated to support social authentication.

Supported providers include:

* Google
* Facebook

### Social Login Flow

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
Application Authentication
  ↓
Authenticated User
```

Endpoint:

```http
POST /auth/social-login
```

---

# 7. Role-Based Access Control

The application implements three main roles.

## Admin

Administrators can:

* Manage products
* Manage users
* Access administrative APIs
* View dashboard information
* Access analytics

## Staff

Staff users can access permitted operational functionality according to their assigned role and permissions.

## Customer

Customers can:

* View products
* Add products to cart
* Update cart items
* Remove cart items
* Create orders
* Complete payment operations
* View their orders

Protected endpoints validate the user's JWT and role before allowing access.

---

# 8. Product APIs

### Get Products

```http
GET /products/
```

### Create Product

```http
POST /products/
```

### Get Product

```http
GET /products/{product_id}
```

### Delete Product

```http
DELETE /products/{product_id}
```

Product creation and administrative operations are protected using role-based authorization.

---

# 9. Cart APIs

### Add Product to Cart

```http
POST /cart/add
```

### View Cart

```http
GET /cart/
```

### Update Cart

```http
PUT /cart/update/{cart_id}
```

### Remove Cart Item

```http
DELETE /cart/remove/{cart_id}
```

---

# 10. Order APIs

### Create Order

```http
POST /orders/create
```

### Get Orders

```http
GET /orders/
```

### Get Individual Order

```http
GET /orders/{order_id}
```

### Payment Success

```http
PUT /orders/{order_id}/pay
```

---

# 11. Payment APIs

### Get Payment Information

```http
GET /payment/{order_id}
```

### Complete Payment

```http
POST /payment/{order_id}/pay
```

Payment operations update the corresponding order/payment status.

---

# 12. Dashboard and Analytics

## Dashboard

```http
GET /dashboard/
```

Provides high-level application statistics such as:

* Total users
* Total products
* Total cart items
* Total orders

## Analytics

```http
GET /analytics/
```

Provides application analytics.

## Admin Users

```http
GET /admin/users
```

## Admin Analytics

```http
GET /admin/analytics
```

Administrative APIs are protected using role-based authorization.

---

# 13. API Documentation

FastAPI automatically provides Swagger/OpenAPI documentation.

After starting the backend, open:

```text
http://127.0.0.1:8000/docs
```

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
```

Swagger UI can be used to interactively test the API endpoints.

---

# 14. Running the Backend

## Step 1 — Navigate to Backend

```powershell
cd fastapi_backend
```

## Step 2 — Activate Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If the virtual environment has a different name, activate the corresponding environment.

## Step 3 — Install Dependencies

```powershell
pip install -r requirements.txt
```

## Step 4 — Configure Environment Variables

Create a local `.env` file in the backend directory.

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

If Auth0 is configured, add the required Auth0 configuration values to the local environment.

> **Important:** Never commit real passwords, database credentials, secret keys, Auth0 secrets, or other sensitive credentials to GitHub.

## Step 5 — Start FastAPI

```powershell
uvicorn app.main:app --reload
```

The API will normally be available at:

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

The Postman files are stored under:

```text
postman/
```

The collection includes API requests for:

```text
Authentication
Products
Cart
Orders
Payment
Dashboard
Analytics
Admin
```

### Authentication Requests

```http
POST /auth/register
POST /auth/login
POST /auth/refresh
GET  /auth/me
POST /auth/social-login
```

The Postman environment uses:

```text
baseUrl = http://127.0.0.1:8000
```

The collection can be opened in Postman and used to test the backend APIs.

---

# 16. Authentication Testing Flow

Recommended authentication testing sequence:

```text
1. Register
      ↓
2. Login
      ↓
3. Receive access token
      ↓
4. Call /auth/me
      ↓
5. Use refresh token
      ↓
6. Call /auth/refresh
      ↓
7. Test protected APIs
```

For protected APIs:

```http
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
* Auth0 authentication
* Environment-based configuration

Sensitive configuration is kept outside the source code.

The real `.env` file should remain local and should not be uploaded to GitHub.

---

# 18. Testing

The APIs can be tested using:

## Swagger UI

```text
http://127.0.0.1:8000/docs
```

## Postman

The Postman collection contains requests for the application's major API modules.

Testing includes:

* User registration
* User login
* JWT token generation
* JWT token refresh
* Current user authentication
* Social login
* Product operations
* Cart operations
* Order operations
* Payment operations
* Role-based authorization
* Dashboard APIs
* Analytics APIs

---

# 19. Authentication Flow

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
                 │    JWT Tokens    │
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
              Cart/Orders     Products/
                              Analytics
```

---

# 20. Project Deliverables

The completed assignment includes:

* FastAPI backend
* MySQL database integration
* User registration and login
* JWT access token authentication
* JWT refresh token authentication
* Current user authentication
* Auth0 social login integration
* Role-Based Access Control
* Admin, Staff, and Customer roles
* Product APIs
* Cart APIs
* Order APIs
* Payment APIs
* Dashboard APIs
* Analytics APIs
* Swagger/OpenAPI documentation
* Postman API collection
* Postman environment
* `.gitignore`
* `.env.example`
* Project documentation
* GitHub repository

---

# 21. Future Enhancements

Possible future improvements include:

* Razorpay or Stripe payment gateway integration
* Product image upload using cloud storage
* Product categories
* Product search and filtering
* Pagination
* Email notifications
* Docker deployment
* CI/CD pipeline
* Automated API testing
* Production database configuration
* Frontend integration
* Cloud deployment

---

# 22. GitHub Repository

The project source code and documentation are available on GitHub:

**Smart E-Commerce Platform**

https://github.com/RAMKUMAR63815/smart-ecommerce-platform

---

# 23. Author

**Ram Kumar**

Smart E-Commerce Platform
Python | FastAPI | SQLAlchemy | MySQL | JWT | Auth0 | Postman | GitHub

---

# Conclusion

The Smart E-Commerce Platform demonstrates a modular and secure e-commerce backend architecture with authentication, authorization, database management, product management, cart and order processing, payment handling, social login, analytics, API documentation, and Postman-based API testing.

The project provides a strong foundation for a complete full-stack e-commerce application and has been prepared as a complete assignment submission.
