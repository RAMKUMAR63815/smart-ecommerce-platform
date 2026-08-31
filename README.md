# 🛒 Smart E-Commerce Platform

A full-stack **Smart E-Commerce Platform** developed using **FastAPI, Django, MySQL, SQLAlchemy, JWT, Auth0, React/Next.js, Stripe, WebSockets, Email Notifications, and Postman**.

The platform provides secure authentication, role-based access control, product management, shopping cart management, order processing, Stripe payment integration, notifications, email notifications, real-time updates, **user-side return/refund requests**, Django administration, dashboard analytics, reporting, Swagger/OpenAPI documentation, and Postman API testing.

---

# 📌 1. Project Overview

The Smart E-Commerce Platform follows a modular architecture separating the application into:

* FastAPI backend
* Django Admin Panel
* MySQL database
* Authentication
* Authorization
* Product management
* Shopping cart management
* Order management
* Payment management
* **Return & Refund Request Management**
* Notification system
* Email notification system
* Real-time WebSocket updates
* Dashboard
* Analytics
* Reporting
* Frontend
* API testing

The application supports three main user roles:

* **Admin**
* **Staff**
* **Customer**

---

# 🎯 2. Project Objective

The main objective of the project is to develop a secure, modular, and user-friendly e-commerce platform that supports the complete shopping workflow.

The platform covers:

* User registration and authentication
* Product browsing and management
* Shopping cart management
* Order creation and tracking
* Payment processing
* Return and refund request management
* Notifications
* Email communication
* Real-time order updates
* Administrative management
* Analytics and reporting

---

# 🚀 3. Main Features

## 🔐 Authentication

* User registration
* User login
* Password hashing
* JWT access token
* JWT refresh token
* Current user authentication
* Protected API endpoints
* Auth0 social login
* Google Login
* Facebook Login

---

## 🛡️ Authorization

* Role-Based Access Control (RBAC)
* Admin role
* Staff role
* Customer role
* Protected APIs
* Role-based administrative operations

---

## 📦 Product Management

* Create product
* Get all products
* Get product by ID
* Get products by category
* Update product
* Delete product
* Category filtering
* Minimum price filtering
* Maximum price filtering
* Popularity filtering
* Stock filtering
* Product stock management
* Product image information

---

## 🛒 Shopping Cart

* Add product to cart
* View cart
* Update cart quantity
* Increase quantity
* Decrease quantity
* Remove cart item
* Stock validation
* Cart calculation
* Item total calculation
* Cart subtotal
* Tax calculation
* Grand total calculation

---

## 📋 Order Management

* Create order
* View orders
* View individual order
* Update order status
* Track payment status
* Payment success
* Payment failure
* Order processing
* Order shipping
* Order delivery
* **Return request**
* **Return request status tracking**

---

# 🔄 4. User-side Refund & Return Request Flow

The project implements a **User-side Refund & Return Request Flow** to allow customers to request a return for an eligible delivered order.

## Return Request Feature

A **Request Return** option is available on the user's Orders page when the order is eligible for return.

A return request is allowed only when:

* Order status is **Delivered**
* The order is within the configured return window
* Example return window: **7 days**
* The authenticated user owns the order

The user can provide:

* Return reason
* Optional comment

---

## Return Request Flow

```text
Customer
    ↓
Orders Page
    ↓
Select Delivered Order
    ↓
Request Return
    ↓
Enter Reason
    ↓
Optional Comment
    ↓
Submit Return Request
    ↓
Backend Validation
    ↓
Check Order Ownership
    ↓
Check Order Status
    ↓
Check Return Window
    ↓
Create ReturnRequest
    ↓
Order Status = Return Requested
    ↓
Admin/Staff Reviews Request
    ↓
Approve / Reject
```

---

# 📝 5. Return Request Feature – User Panel

The user can access the return functionality from the **Orders page**.

## User Flow

```text
Orders
   ↓
Delivered Order
   ↓
Request Return
   ↓
Select Reason
   ↓
Enter Optional Comment
   ↓
Submit
```

The system validates the request before creating it.

### Example reasons

* Damaged product
* Product not working
* Wrong product
* Product not as described
* Missing item
* Other

---

# 🔌 6. Return Request API

The backend provides an API for creating return requests.

## Create Return Request

```http
POST /orders/{order_id}/return
```

### Request

The request contains:

```json
{
    "reason": "Damage Product",
    "comment": "The product was received with visible damage and is not in usable condition"
}
```

The `comment` field is optional.

---

## API Processing

When the API receives the request, it validates:

1. The order exists
2. The authenticated user owns the order
3. The order status is `Delivered`
4. The order is within the return window
5. A valid return reason is provided
6. A return request can be created

If all validations pass:

```text
ReturnRequest
      ↓
Created
      ↓
status = pending
      ↓
Order status = Return Requested
```

---

# 🗄️ 7. ReturnRequest Database Model

A dedicated `ReturnRequest` model is used to store customer return requests.

## ReturnRequest Fields

| Field        | Description                       |
| ------------ | --------------------------------- |
| `id`         | Unique return request ID          |
| `order_id`   | Related order ID                  |
| `user_id`    | Customer who requested the return |
| `reason`     | Reason for returning the order    |
| `comment`    | Optional customer comment         |
| `status`     | Pending / Approved / Rejected     |
| `created_at` | Return request creation date      |

---

## Return Request Status

The return request supports three main statuses:

```text
pending
approved
rejected
```

### Pending

The request has been submitted by the customer and is waiting for administrative review.

### Approved

The return request has been accepted.

### Rejected

The return request has been rejected.

---

# 🔗 8. ReturnRequest Relationships

The `ReturnRequest` model is related to:

```text
User
  │
  └── ReturnRequest

Order
  │
  └── ReturnRequest
```

This allows the system to identify:

* Which user requested the return
* Which order is being returned
* The reason for the return
* The current return request status

---

# 🔄 9. Order Status Update for Returns

When a valid return request is created, the corresponding order status is updated.

Before return request:

```text
Delivered
```

After return request:

```text
Return Requested
```

Flow:

```text
Delivered
    ↓
User Requests Return
    ↓
Return Request Created
    ↓
Order Status Updated
    ↓
Return Requested
```

This allows administrators and users to identify orders that are currently under return processing.

---

# 👨‍💼 10. Return Request Approval Workflow

After the customer submits a return request, the request remains:

```text
Pending
```

The administrator or authorized staff member can review the request.

## Approval Flow

```text
Pending
   ↓
Admin Review
   ↓
 ┌───────────────┐
 ↓               ↓
Approve        Reject
 ↓               ↓
Approved       Rejected
```

The return request status is displayed to the user.

Example:

```text
Return Request #7
Order ID: #84
Reason: Damage
Status: Approved
```

---

# 💰 11. Refund Workflow

The return request and refund process are logically connected.

The customer first submits a return request.

```text
Customer
   ↓
Return Request
   ↓
Admin Review
   ↓
Approved
   ↓
Return Processing
   ↓
Refund Processing
```

The return request records whether the return has been:

* Pending
* Approved
* Rejected

The actual payment refund can then be processed according to the application's payment/refund implementation.

> **Note:** The current return-request implementation handles the customer return request and approval/rejection workflow. A separate automated Stripe refund operation can be added if required.

---

# 📦 12. Order APIs

## Create Order

```http
POST /orders/create?user_id=1
```

---

## Get Orders

```http
GET /orders/?user_id=1
```

---

## Get Individual Order

```http
GET /orders/{order_id}
```

---

## Payment Success

```http
PUT /orders/{order_id}/pay
```

Example:

```http
PUT /orders/1/pay
```

---

## Update Order Status

```http
PUT /orders/{order_id}/status?status=shipped
```

Example:

```http
PUT /orders/1/status?status=shipped
```

---

## Request Return

```http
POST /orders/{order_id}/return
```

Example:

```http
POST /orders/84/return
```

Request body:

```json
{
    "reason": "Damage",
    "comment": "Product received with visible damage"
}
```

---

# 💳 13. Payment Management

The Payment module manages payment-related information associated with orders.

Payment functionality includes:

* Payment information
* Payment success
* Payment failure
* Payment status tracking
* Stripe Checkout
* Stripe webhook
* Return/refund workflow support

---

# 💰 14. Stripe Integration

The project integrates Stripe Checkout for payment processing.

## Stripe Checkout Flow

```text
Customer
   ↓
Create Order
   ↓
Checkout
   ↓
Stripe Checkout
   ↓
Customer Payment
   ↓
Stripe
   ↓
Webhook
   ↓
Payment Status Update
   ↓
Order Updated
   ↓
Notification
```

---

## Stripe Webhook

```http
POST /stripe/webhook
```

The webhook validates the Stripe signature before processing the event.

### Important

The Stripe webhook cannot be tested by simply sending an empty POST request.

If the endpoint returns:

```json
{
    "detail": "Missing Stripe signature"
}
```

the request does not contain the required Stripe signature header.

Stripe test events or a properly configured Stripe webhook should be used for webhook testing.

---

# 🔔 15. Notification System

The notification system provides application notifications for users.

Notifications can be generated for:

* Order confirmation
* Payment success
* Payment failure
* Shipping updates
* Delivery updates
* Return request events
* Return approval
* Return rejection

---

## Get Notifications

```http
GET /notifications/?user_id=1
```

---

## Create Notification

```http
POST /notifications/?user_id=1&type=order&message=Order%20confirmed
```

---

## Mark Notification as Read

```http
POST /notifications/read?notification_id=1
```

---

# 📧 16. Email Notifications

The application supports email notifications for important events.

Examples:

* Order confirmation
* Payment successful
* Payment failed
* Order shipped
* Order delivered
* **Return request submitted**
* **Return request approved**
* **Return request rejected**

Email credentials should be stored in environment variables.

---

# ⚡ 17. Real-Time WebSocket Updates

WebSockets are used to provide real-time application updates.

Supported events can include:

```text
order_status_updated
cart_updated
return_request_updated
notification_created
```

Example return flow:

```text
Return Request Status Changed
          ↓
Backend Event
          ↓
WebSocket
          ↓
Connected Client
          ↓
Real-Time UI Update
```

---

# 📊 18. Dashboard

Dashboard endpoint:

```http
GET /dashboard/
```

Provides high-level application statistics.

Examples:

* Total users
* Total products
* Total cart items
* Total orders
* Total sales
* Application information

Return-related dashboard information can also be extended to include:

* Total return requests
* Pending returns
* Approved returns
* Rejected returns

---

# 📈 19. Analytics

Analytics endpoint:

```http
GET /analytics/
```

Admin analytics:

```http
GET /admin/analytics
```

Analytics can include:

* Total sales
* Revenue trends
* Top-selling products
* Low-stock products
* User statistics
* Product statistics
* Order statistics
* Return request statistics

---

# 🧑‍💼 20. Django Admin Panel

The Django Admin Panel provides administrative management functionality.

Start Django:

```powershell
python manage.py runserver 8001
```

Open:

```text
http://127.0.0.1:8001/admin/
```

The administrator can manage:

* Users
* Roles
* Products
* Stock
* Orders
* Payment status
* Return requests
* Return request status
* Dashboard information
* Reports
* Analytics

---

# 🔄 21. Return Request Admin Management

The administrator can review return requests.

Example:

```text
Return Request #7
-------------------------
Order ID: 84
User ID: 6
Reason: Damage
Comment: No comment
Status: Approved
Created At: 8/31/2026
```

Possible actions:

```text
Pending
   ↓
Approve
   ↓
Approved
```

or:

```text
Pending
   ↓
Reject
   ↓
Rejected
```

---

# 📄 22. Reports

Administrative reports include:

## Orders Report

Contains:

* Order ID
* User
* Amount
* Order status
* Payment status
* Date

## Sales Report

Contains:

* Sales totals
* Revenue
* Order information
* Product sales

## User Report

Contains:

* User ID
* Name
* Email
* Role
* Account information

## Return Report

Can contain:

* Return Request ID
* Order ID
* User ID
* Reason
* Comment
* Status
* Created date

Supported formats:

* CSV
* PDF

---

# 🛠️ 23. Technology Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* MySQL
* Alembic
* Uvicorn

## Authentication & Security

* JWT
* Python-Jose
* Password hashing
* OAuth2
* Auth0
* Google Login
* Facebook Login
* Role-Based Access Control

## Admin Panel

* Django
* Django Admin

## Payment

* Stripe

## Real-Time Communication

* WebSockets

## Email

* SMTP
* Email notification integration

## Frontend

* React.js
* Next.js
* Axios
* React Router

## Analytics

* Chart.js
* Plotly

## API Testing

* Swagger UI
* OpenAPI
* Postman

## Database

* MySQL

## Database Migration

* Alembic
* Django Migrations

## Development Tools

* Git
* GitHub
* Visual Studio Code

---

# 📁 24. Project Architecture

```text
smart_ecommerce/

│
├── fastapi_backend/
│   │
│   ├── app/
│   │   │
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── products.py
│   │   │   ├── cart.py
│   │   │   ├── orders.py
│   │   │   ├── payment.py
│   │   │   ├── dashboard.py
│   │   │   ├── analytics.py
│   │   │   ├── notifications.py
│   │   │   └── stripe.py
│   │   │
│   │   ├── auth/
│   │   │   ├── jwt_handler.py
│   │   │   ├── security.py
│   │   │   └── auth0.py
│   │   │
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── main.py
│   │
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env
│
├── django_admin/
│   │
│   ├── manage.py
│   ├── django_admin/
│   └── ...
│
├── frontend/
│   │
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   └── ...
│   │
│   └── package.json
│
├── postman/
│   ├── collections/
│   ├── environments/
│   └── globals/
│
├── screenshots/
│
├── .env.example
├── .gitignore
└── README.md
```

> The exact folder and file structure may vary depending on the final project configuration.

---

# 🗄️ 25. Database Design

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

---

## Product

Stores product information.

| Field         | Description               |
| ------------- | ------------------------- |
| `id`          | Unique product ID         |
| `name`        | Product name              |
| `description` | Product description       |
| `price`       | Product price             |
| `category`    | Product category          |
| `stock`       | Available stock           |
| `images`      | Product image information |

---

## Cart

Stores products added to a user's cart.

| Field        | Description      |
| ------------ | ---------------- |
| `id`         | Cart item ID     |
| `user_id`    | User ID          |
| `product_id` | Product ID       |
| `quantity`   | Product quantity |

---

## Order

Stores customer orders.

| Field            | Description        |
| ---------------- | ------------------ |
| `id`             | Order ID           |
| `user_id`        | Customer ID        |
| `total_amount`   | Total order amount |
| `status`         | Order status       |
| `payment_status` | Payment status     |

---

## Notification

Stores user notifications.

| Field         | Description            |
| ------------- | ---------------------- |
| `id`          | Notification ID        |
| `user_id`     | User ID                |
| `type`        | Notification type      |
| `message`     | Notification message   |
| `read_status` | Read/unread status     |
| `timestamp`   | Notification timestamp |

---

## ReturnRequest

Stores customer return requests.

| Field        | Description                   |
| ------------ | ----------------------------- |
| `id`         | Return request ID             |
| `order_id`   | Related order ID              |
| `user_id`    | Customer ID                   |
| `reason`     | Return reason                 |
| `comment`    | Optional comment              |
| `status`     | Pending / Approved / Rejected |
| `created_at` | Request creation date         |

---

# 🔐 26. Authentication System

The authentication system uses JWT-based authentication with access and refresh tokens.

## Registration

```http
POST /auth/register
```

Example:

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

Required fields:

```text
username
password
```

---

## Refresh Token

```http
POST /auth/refresh?refresh_token=YOUR_REFRESH_TOKEN
```

---

## Current User

```http
GET /auth/me
```

Protected endpoint:

```http
Authorization: Bearer <access_token>
```

---

# 🌐 27. Social Login

Auth0 is integrated for social authentication.

Supported providers:

* Google
* Facebook

Flow:

```text
User
  ↓
Google / Facebook
  ↓
Auth0
  ↓
Verify Token
  ↓
Create / Find User
  ↓
Application JWT
  ↓
Authenticated User
```

Endpoint:

```http
POST /auth/social-login
```

---

# 🛡️ 28. Role-Based Access Control

The application implements three main roles.

## Admin

Administrators can:

* Manage users
* Manage products
* Manage orders
* Manage return requests
* Approve/reject return requests
* View dashboard
* View analytics
* Access administrative APIs
* Manage stock
* Access reports

## Staff

Staff users can access permitted operational functionality according to their assigned permissions.

## Customer

Customers can:

* View products
* Filter products
* Add products to cart
* Update cart items
* Remove cart items
* Create orders
* Complete payment operations
* View their orders
* Request returns for eligible orders
* View return request status
* Receive notifications

---

# 📦 29. Product APIs

## Get Products

```http
GET /products/
```

Supports:

```text
category
min_price
max_price
min_popularity
in_stock
```

Example:

```http
GET /products/?category=Electronics
```

---

## Create Product

```http
POST /products/
```

Example:

```json
{
    "name": "Test Laptop",
    "description": "Test laptop for ecommerce",
    "price": 50000,
    "category": "Electronics",
    "stock": 10,
    "images": "laptop.jpg"
}
```

---

## Get Product

```http
GET /products/{product_id}
```

---

## Update Product

```http
PUT /products/{product_id}
```

---

## Delete Product

```http
DELETE /products/{product_id}
```

---

# 🛒 30. Cart APIs

## Add Product to Cart

```http
POST /cart/add
```

---

## View Cart

```http
GET /cart/?user_id=1
```

---

## Update Cart

```http
PUT /cart/update/{cart_id}?quantity=2
```

---

## Remove Cart Item

```http
DELETE /cart/remove/{cart_id}
```

---

# 🔔 31. Complete Customer Order-to-Return Flow

The complete customer workflow is:

```text
Register
   ↓
Login
   ↓
Browse Products
   ↓
Add Product to Cart
   ↓
Checkout
   ↓
Create Order
   ↓
Stripe Payment
   ↓
Payment Success
   ↓
Order Processing
   ↓
Shipped
   ↓
Delivered
   ↓
Request Return
   ↓
Return Request Created
   ↓
Order = Return Requested
   ↓
Admin Review
   ↓
Approve / Reject
   ↓
Refund Processing
   ↓
Customer Notification
```

---

# 🔄 32. Return Eligibility Logic

The return request is allowed only when the required conditions are satisfied.

```text
Is order available?
       ↓
      Yes
       ↓
Does user own order?
       ↓
      Yes
       ↓
Is order Delivered?
       ↓
      Yes
       ↓
Is order within return window?
       ↓
      Yes
       ↓
Create Return Request
```

If any condition fails, the API returns an appropriate error response.

Examples:

```text
Order not found
Unauthorized order access
Order is not delivered
Return window expired
Invalid request
```

---

# 🧪 33. API Testing

The application APIs are tested using:

* Swagger UI
* Postman

Testing covers:

* Registration
* Login
* JWT authentication
* JWT refresh
* Current user
* Product APIs
* Product filtering
* Cart APIs
* Order APIs
* Payment APIs
* Stripe Checkout
* Notifications
* Dashboard
* Analytics
* Admin APIs
* **Return Request API**
* **Return eligibility validation**
* **Return request status**
* Authorization
* Error responses
* Validation responses

---

# 📮 34. Postman Testing – Return Request

## Request

```http
POST /orders/{order_id}/return
```

Example:

```http
POST /orders/84/return
```

Authorization:

```text
Bearer Token
```

Body:

```json
{
    "reason": "Damage",
    "comment": "Product received with visible damage"
}
```

Expected successful result:

```text
Return Request Created
```

The request is initially:

```text
status = pending
```

and the order becomes:

```text
Return Requested
```

---

# 🧪 35. Swagger API Testing

After starting FastAPI:

```text
http://127.0.0.1:8000/docs
```

Recommended testing sequence:

```text
Register
   ↓
Login
   ↓
Get Access Token
   ↓
Authorize
   ↓
Products
   ↓
Cart
   ↓
Orders
   ↓
Payment
   ↓
Delivered Order
   ↓
Request Return
   ↓
Notifications
   ↓
Analytics
   ↓
Admin
```

---

# 🗄️ 36. MySQL Setup

Create database:

```sql
CREATE DATABASE smart_ecommerce;
```

Check:

```sql
SHOW DATABASES;
```

Select:

```sql
USE smart_ecommerce;
```

Check tables:

```sql
SHOW TABLES;
```

---

# 🔄 37. Alembic Database Migrations

Navigate to the backend:

```powershell
cd "C:\Fullstack developer\smart_ecommerce\fastapi_backend"
```

Activate environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Create migration:

```powershell
python -m alembic revision --autogenerate -m "update database schema"
```

Apply migration:

```powershell
python -m alembic upgrade head
```

Check current migration:

```powershell
python -m alembic current
```

Check history:

```powershell
python -m alembic history
```

---

# 🐍 38. Django Migrations

Check migrations:

```powershell
python manage.py showmigrations
```

Apply:

```powershell
python manage.py migrate
```

Create:

```powershell
python manage.py makemigrations
```

Apply again:

```powershell
python manage.py migrate
```

---

# 🚀 39. Running FastAPI Backend

Navigate:

```powershell
cd "C:\Fullstack developer\smart_ecommerce\fastapi_backend"
```

Activate virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Install requirements:

```powershell
pip install -r requirements.txt
```

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

---

# 🧑‍💼 40. Running Django Admin

Open another PowerShell:

```powershell
cd "C:\Fullstack developer\smart_ecommerce\django_admin"
```

Run migrations:

```powershell
python manage.py migrate
```

Create superuser:

```powershell
python manage.py createsuperuser
```

Start:

```powershell
python manage.py runserver 8001
```

Django:

```text
http://127.0.0.1:8001
```

Admin:

```text
http://127.0.0.1:8001/admin/
```

---

# 📸 41. Screenshots / Demo

Project screenshots can be stored in:

```text
screenshots/
```

Recommended screenshots:

```text
screenshots/

├── login.png
├── register.png
├── products.png
├── product-management.png
├── cart.png
├── orders.png
├── payment.png
├── notifications.png
├── dashboard.png
├── analytics.png
├── admin-users.png
├── admin-products.png
├── admin-orders.png
├── reports.png
├── return-request.png
├── return-request-form.png
├── return-request-pending.png
├── return-request-approved.png
├── return-request-rejected.png
├── swagger.png
├── postman.png
└── stripe-checkout.png
```

The return-request screenshots demonstrate:

1. Delivered order
2. Request Return button
3. Return request form
4. Submitted return request
5. Pending status
6. Approved status
7. Rejected status

---

# 📦 42. Final Deliverables

The completed project includes:

* FastAPI backend
* Django Admin Panel
* MySQL database
* SQLAlchemy
* Alembic migrations
* Django migrations
* User authentication
* JWT access tokens
* JWT refresh tokens
* Auth0 social login
* Google Login
* Facebook Login
* Role-Based Access Control
* Admin role
* Staff role
* Customer role
* Product management
* Product filtering
* Cart management
* Order management
* Payment processing
* Stripe integration
* Stripe webhook
* Notification system
* Email notifications
* WebSocket real-time updates
* Dashboard
* Analytics
* Reporting
* **User-side return request**
* **Return eligibility validation**
* **ReturnRequest database model**
* **Return request API**
* **Return request status management**
* **Order status update to Return Requested**
* **Admin approval/rejection workflow**
* Swagger/OpenAPI documentation
* Postman API testing
* Postman collection
* Setup documentation
* GitHub repository

---

# 🔐 43. Security

The application implements:

* Password hashing
* JWT authentication
* Access token expiration
* Refresh token support
* Protected routes
* OAuth2 authentication
* Role-based authorization
* Auth0 authentication
* Environment-based configuration
* Stripe webhook signature validation
* User ownership validation for orders
* Return eligibility validation

Sensitive values must be stored in environment variables.

Never upload:

```text
.env
passwords
database credentials
JWT secret keys
Auth0 secrets
Stripe secret keys
API keys
```

to GitHub.

---

# 🔒 44. .gitignore

The project should ignore:

```text
.env
venv/
__pycache__/
*.pyc
node_modules/
*.log
```

An `.env.example` file can be committed with placeholder values.

---

# 🔄 45. Complete Application Flow

```text
                         USER
                           │
                           ▼
                    Authentication
                           │
              ┌────────────┴────────────┐
              │                         │
          Customer                    Admin
              │                         │
              ▼                         ▼
          Products                Django Admin
              │                         │
              ▼                         ▼
            Cart                Users / Products
              │                  Orders / Returns
              ▼                         │
          Checkout                      │
              │                         │
              ▼                         ▼
            Stripe                  Analytics
              │                         │
              ▼                         │
          Payment                      │
              │                         │
              ▼                         │
         Order Update ◄────────────────┘
              │
              ▼
           Delivered
              │
              ▼
        Request Return
              │
              ▼
       Return Requested
              │
              ▼
        Admin Review
          /       \
         /         \
    Approved      Rejected
       │              │
       ▼              ▼
 Refund Process     Return Closed
       │
       ▼
 Notification
       │
       ▼
    Email
       │
       ▼
  WebSocket
       │
       ▼
 Real-Time User
```

---

# 📈 46. Analytics Flow

```text
Database
   ↓
Orders
   ↓
Sales Data
   ↓
Return Data
   ↓
Analytics API
   ↓
Dashboard
   ↓
Charts
```

Analytics include:

```text
Total Sales
Revenue Trends
Top-Selling Products
Low-Stock Products
Return Requests
Approved Returns
Rejected Returns
```

---

# 💳 47. Payment Flow

```text
Customer
   ↓
Cart
   ↓
Create Order
   ↓
Checkout
   ↓
Stripe
   ↓
Payment
   ↓
Stripe Webhook
   ↓
Verify Signature
   ↓
Update Payment Status
   ↓
Update Order Status
   ↓
Create Notification
   ↓
Send Email
```

---

# 🔄 48. Return & Refund Flow

```text
Delivered Order
       ↓
Customer Requests Return
       ↓
Validate Order
       ↓
Validate User
       ↓
Validate Return Window
       ↓
Create ReturnRequest
       ↓
Status = Pending
       ↓
Order = Return Requested
       ↓
Admin Review
       ↓
 ┌───────────────┐
 │               │
 ▼               ▼
Approved       Rejected
 │               │
 ▼               ▼
Refund          Request Closed
Processing
 │
 ▼
Notification
 │
 ▼
Email
 │
 ▼
Customer
```

---

# 🔔 49. Notification Flow

```text
Order Event
     ↓
Backend
     ↓
Create Notification
     ↓
Database
     ↓
Email Notification
     ↓
WebSocket Event
     ↓
User Interface
```

Return events can also generate notifications:

```text
Return Requested
Return Approved
Return Rejected
```

---

# 🧪 50. API Testing Status

The API endpoints have been manually tested using Postman and Swagger.

Testing covers:

* User registration
* User login
* JWT authentication
* JWT refresh
* Current user
* Product APIs
* Product filtering
* Cart APIs
* Order APIs
* Payment APIs
* Stripe checkout
* Notifications
* Notification read
* Dashboard
* Analytics
* Admin APIs
* Authorization
* Error responses
* Validation responses
* **Return Request API**
* **Return eligibility**
* **Return request creation**
* **Pending return status**
* **Approved return status**
* **Rejected return status**
* **Order status update**

Expected successful responses include:

```text
200 OK
201 Created
```

Expected error responses may include:

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
422 Validation Error
```

---

# 🐳 51. Optional Docker Deployment

Docker deployment can be added as a future enhancement.

Possible services:

```text
FastAPI
Django
MySQL
Frontend
Nginx
```

Example:

```text
Docker
│
├── FastAPI Container
├── Django Container
├── MySQL Container
└── Frontend Container
```

---

# 🔮 52. Future Enhancements

Possible future improvements include:

* Automated Stripe refunds
* Docker deployment
* Cloud deployment
* CI/CD pipeline
* Automated API testing
* Advanced analytics
* Product search
* Pagination
* Cloud image storage
* Production email service
* Production payment configuration
* Redis caching
* Background task processing
* Monitoring and logging
* Return pickup tracking
* Return shipment tracking
* Refund transaction tracking

---

# 🧑‍💻 53. Installation Summary

For a new machine:

```text
1. Clone the repository
2. Install Python
3. Install MySQL
4. Create the database
5. Navigate to FastAPI backend
6. Create/activate virtual environment
7. Install requirements
8. Configure .env
9. Run Alembic migrations
10. Start FastAPI
11. Navigate to Django Admin
12. Install Django dependencies
13. Run Django migrations
14. Create superuser
15. Start Django
16. Open Swagger
17. Import/test Postman collection
18. Configure Stripe test credentials if required
19. Test order workflow
20. Test return request workflow
```

---

# 📥 54. GitHub Setup

Clone the project:

```powershell
git clone https://github.com/RAMKUMAR63815/smart-ecommerce-platform.git
```

Navigate:

```powershell
cd smart-ecommerce-platform
```

Check status:

```powershell
git status
```

---

# 📤 55. GitHub Update

After making changes:

```powershell
git add .
```

Commit:

```powershell
git commit -m "Add user return and refund request flow"
```

Push:

```powershell
git push
```

---

# 🌐 56. GitHub Repository

**Smart E-Commerce Platform**

Repository:

```text
https://github.com/RAMKUMAR63815/smart-ecommerce-platform
```

---

# 👨‍💻 57. Author

**Ram Kumar**

Smart E-Commerce Platform

```text
Python
FastAPI
Django
SQLAlchemy
MySQL
JWT
Auth0
Stripe
React
Next.js
WebSockets
Postman
GitHub
```

---

# ✅ 58. Project Completion

The Smart E-Commerce Platform has been developed as a full-stack e-commerce project demonstrating:

* Secure authentication
* Role-based authorization
* Product management
* Shopping cart management
* Order processing
* Payment integration
* Stripe Checkout
* Notifications
* Email notifications
* Real-time WebSocket updates
* Django Admin Panel
* Dashboard
* Analytics
* Reporting
* Database migrations
* API documentation
* Postman API testing
* **User-side Return Request**
* **ReturnRequest database model**
* **Return Request API**
* **Return eligibility validation**
* **7-day return window validation**
* **Order status update to Return Requested**
* **Admin return approval/rejection**
* **Return request status tracking**
* GitHub version control

The project provides a complete foundation for a production-oriented full-stack e-commerce application with customer return management.

---

# 🏁 59. Conclusion

The Smart E-Commerce Platform demonstrates a modular full-stack architecture combining **FastAPI for backend APIs, Django for administration, MySQL for data storage, JWT/Auth0 for authentication, Stripe for payments, WebSockets for real-time communication, email notifications for user communication, and Postman/Swagger for API testing**.

The project covers the complete e-commerce workflow from user authentication and product browsing to cart management, order creation, payment processing, delivery, and **user-side return request management**.

The newly implemented **Refund & Return Request Flow** allows customers to request a return for eligible delivered orders within the configured return window. The system validates the order and user, creates a `ReturnRequest`, updates the order status to **Return Requested**, and provides an administrative workflow for approving or rejecting the request.

The project therefore combines:

```text
Authentication
      +
Authorization
      +
Products
      +
Cart
      +
Orders
      +
Payments
      +
Returns
      +
Refund Workflow
      +
Notifications
      +
Email
      +
WebSockets
      +
Django Admin
      +
Dashboard
      +
Analytics
      +
Reports
      +
API Testing
```

**Project Status: Completed** ✅
