# 🛒 Smart E-Commerce Platform

A full-stack **Smart E-Commerce Platform** developed using **FastAPI, Django, MySQL, SQLAlchemy, JWT, Auth0, React/Next.js, Stripe, WebSockets, Email Notifications, and Postman**.

The platform provides secure authentication, role-based access control, product management, shopping cart management, order processing, Stripe payment integration, notifications, email notifications, real-time updates, customer return/refund requests, admin-side return processing, inventory restoration, Stripe refunds, Django administration, dashboard analytics, reporting, Swagger/OpenAPI documentation, and Postman API testing.

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
* Return and refund management
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

The main objective of the project is to develop a secure, modular, and user-friendly e-commerce platform supporting the complete shopping lifecycle.

The platform covers:

* User registration and authentication
* Product browsing and management
* Shopping cart management
* Order creation and tracking
* Payment processing
* Stripe Checkout
* Stripe webhook processing
* Customer return requests
* Return eligibility validation
* Admin return approval/rejection
* Inventory restoration
* Stripe refund processing
* Payment status updates
* In-app notifications
* Email notifications
* Real-time updates
* Administrative management
* Dashboard analytics
* Reporting

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

The application implements Role-Based Access Control (RBAC).

Supported roles:

* Admin
* Staff
* Customer

Role-based authorization protects administrative and operational APIs.

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

# 📋 4. Order Management

The order module manages the complete customer order lifecycle.

Features include:

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
* Return request
* Return request status tracking
* Refund processing

Example order lifecycle:

```text
Pending
   ↓
Processing
   ↓
Shipped
   ↓
Delivered
   ↓
Return Requested
   ↓
Returned
   ↓
Refunded
```

---

# 🔄 5. Customer Return & Refund Request Flow

Customers can request a return for eligible delivered orders.

A return request is allowed only when:

* The order exists
* The authenticated user owns the order
* The order status is `Delivered`
* The order is within the configured return window
* A valid return reason is provided
* A duplicate/ineligible return request does not already exist

Example return window:

```text
7 Days
```

Customers can provide:

* Return reason
* Optional comment

---

# 📝 6. User-Side Return Request

The customer accesses the return functionality from the **Orders page**.

User flow:

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
   ↓
Backend Validation
   ↓
Return Request Created
```

Example return reasons:

* Damaged product
* Product not working
* Wrong product
* Product not as described
* Missing item
* Other

---

# 🔌 7. Customer Return Request API

## Create Return Request

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

The `comment` field is optional.

---

## API Validation

The backend validates:

1. Order existence
2. User ownership
3. Order status
4. Return window
5. Return reason
6. Existing return request
7. Request validity

If validation succeeds:

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

# 🗄️ 8. ReturnRequest Database Model

The `ReturnRequest` model stores customer return requests and their processing status.

| Field        | Description                                         |
| ------------ | --------------------------------------------------- |
| `id`         | Unique return request ID                            |
| `order_id`   | Related order ID                                    |
| `user_id`    | Customer who requested the return                   |
| `reason`     | Return reason                                       |
| `comment`    | Optional customer comment                           |
| `status`     | Pending / Approved / Rejected / Returned / Refunded |
| `created_at` | Request creation date                               |

---

# 🔄 9. Return Request Status

The return lifecycle supports:

```text
Pending
   ↓
Approved
   ↓
Returned
   ↓
Refunded
```

Or:

```text
Pending
   ↓
Rejected
```

### Pending

The customer has submitted the request and it is waiting for admin/staff review.

### Approved

The administrator has approved the return.

### Returned

The return has been approved and the order is considered returned.

### Refunded

The payment refund has been successfully completed.

### Rejected

The administrator has rejected the return request.

---

# 🔗 10. ReturnRequest Relationships

The `ReturnRequest` model is related to the user and order.

```text
User
 │
 └── ReturnRequest

Order
 │
 └── ReturnRequest
```

This allows the system to identify:

* Which customer requested the return
* Which order is being returned
* Return reason
* Return comment
* Return status
* Return creation time

---

# 🔄 11. Order Status Update

When a valid customer return request is created:

```text
Delivered
    ↓
User Requests Return
    ↓
ReturnRequest Created
    ↓
Order Status
    ↓
Return Requested
```

After admin approval:

```text
Return Requested
       ↓
Admin Approves
       ↓
Returned
```

After successful refund:

```text
Returned
   ↓
Refund Completed
   ↓
Refunded
```

If rejected:

```text
Return Requested
       ↓
Admin Rejects
       ↓
Rejected
```

---

# 👨‍💼 12. Admin Return Management

Administrators can review and process customer return requests.

The admin-side workflow provides:

* View return requests
* Review return details
* Approve return
* Reject return
* Update return status
* Restore inventory
* Process payment refund
* Update payment status
* Send notifications
* Send email notifications

---

# 🔌 13. Admin Return APIs

## Get All Return Requests

```http
GET /admin/returns
```

This endpoint allows authorized administrators/staff to view return requests.

---

## Approve Return

```http
POST /admin/returns/{id}/approve
```

Example:

```http
POST /admin/returns/7/approve
```

The approval workflow performs the required return-processing operations.

Flow:

```text
Pending
   ↓
Admin Approves
   ↓
Return Approved
   ↓
Order = Returned
   ↓
Inventory Restored
   ↓
Refund Processing
   ↓
Payment Status Updated
   ↓
Notification
   ↓
Email
```

---

## Reject Return

```http
POST /admin/returns/{id}/reject
```

Example:

```http
POST /admin/returns/7/reject
```

Flow:

```text
Pending
   ↓
Admin Rejects
   ↓
Return = Rejected
   ↓
Notification
   ↓
Email
```

---

# 💰 14. Complete Refund Workflow

The refund workflow connects the customer return request with admin approval and payment processing.

```text
Customer
   ↓
Delivered Order
   ↓
Request Return
   ↓
ReturnRequest Created
   ↓
Pending
   ↓
Admin Review
   ↓
Approve
   ↓
Returned
   ↓
Inventory Increased
   ↓
Stripe Refund
   ↓
Payment Status Updated
   ↓
Refunded
   ↓
Notification
   ↓
Email
```

---

# 💳 15. Stripe Payment Integration

Stripe is used for payment processing.

Payment features include:

* Stripe Checkout
* Payment status tracking
* Stripe webhook
* Payment success handling
* Payment failure handling
* Stripe refund processing
* Refund status tracking

---

# 💰 16. Stripe Checkout Flow

```text
Customer
   ↓
Cart
   ↓
Create Order
   ↓
Stripe Checkout
   ↓
Customer Payment
   ↓
Stripe
   ↓
Stripe Webhook
   ↓
Verify Signature
   ↓
Update Payment Status
   ↓
Update Order
   ↓
Notification
```

---

# 🔄 17. Stripe Refund Processing

After an administrator approves an eligible return, the system processes the refund through Stripe.

Flow:

```text
Return Approved
      ↓
Order Returned
      ↓
Find Payment
      ↓
Get Stripe Payment Information
      ↓
Create Stripe Refund
      ↓
Refund Successful
      ↓
Update Payment Status
      ↓
Return Status = Refunded
      ↓
Notification
      ↓
Email
```

The refund workflow helps maintain consistency between:

* Return request status
* Order status
* Inventory
* Payment status
* Stripe refund status
* Customer notifications

---

# 📦 18. Inventory Management During Return

When an administrator approves a return, the returned product quantity is added back to inventory.

Example:

```text
Before Return:

Product Stock = 5

Returned Quantity = 2
```

After successful return processing:

```text
Product Stock = 7
```

Flow:

```text
Return Approved
      ↓
Identify Returned Products
      ↓
Get Returned Quantity
      ↓
Increase Product Stock
      ↓
Save Inventory
```

This prevents inventory from remaining incorrectly reduced after a returned product is processed.

---

# 💳 19. Payment Status Handling

Payment status is updated according to the payment/refund lifecycle.

Example:

```text
Payment Successful
       ↓
Paid
       ↓
Return Approved
       ↓
Refund Processing
       ↓
Refund Completed
       ↓
Refunded
```

This allows administrators to distinguish between:

* Pending payment
* Successful payment
* Failed payment
* Refund processing
* Refunded payment

---

# 🔔 20. Notification System

The notification system provides in-app notifications to users.

Notifications can be generated for:

* Order confirmation
* Payment success
* Payment failure
* Order shipped
* Order delivered
* Return request submitted
* Return approved
* Return rejected
* Refund completed

---

# 🔔 21. Return & Refund Notifications

The return workflow generates notifications for important events.

### Return Approved

```text
Return Request Approved
```

### Return Rejected

```text
Return Request Rejected
```

### Refund Completed

```text
Refund Completed Successfully
```

These notifications allow customers to track their return/refund progress.

---

# 📧 22. Email Notification System

The application also supports email notifications.

Email events include:

* Order confirmation
* Payment successful
* Payment failed
* Order shipped
* Order delivered
* Return request submitted
* Return request approved
* Return request rejected
* Refund completed

Example:

```text
Return Approved
      ↓
Create Notification
      ↓
Send Email
      ↓
Customer Receives Email
```

Email credentials and configuration should be stored in environment variables.

---

# 🔔 23. Notification APIs

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

# ⚡ 24. Real-Time WebSocket Updates

WebSockets are used to provide real-time updates to connected users.

Supported events can include:

```text
order_status_updated
cart_updated
return_request_updated
notification_created
refund_completed
```

Example:

```text
Return Status Changed
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

# 📋 25. Complete Return Lifecycle

The complete return lifecycle is:

```text
Delivered
    ↓
Customer Requests Return
    ↓
Return Requested
    ↓
Pending
    ↓
Admin Review
    ↓
 ┌───────────────┐
 ↓               ↓
Approve        Reject
 ↓               ↓
Returned       Rejected
 ↓
Inventory Updated
 ↓
Stripe Refund
 ↓
Payment Updated
 ↓
Refunded
 ↓
Notification
 ↓
Email
 ↓
Customer
```

---

# 📊 26. Dashboard

Dashboard endpoint:

```http
GET /dashboard/
```

Provides application statistics such as:

* Total users
* Total products
* Total cart items
* Total orders
* Total sales
* Application information

Return-related statistics can include:

* Total return requests
* Pending returns
* Approved returns
* Rejected returns
* Returned orders
* Refunded orders

---

# 📈 27. Analytics

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
* Return statistics
* Approved returns
* Rejected returns
* Refund statistics

---

# 🧑‍💼 28. Django Admin Panel

The Django Admin Panel provides administrative management functionality.

Start Django:

```powershell
python manage.py runserver 8001
```

Admin:

```text
http://127.0.0.1:8001/admin/
```

Administrators can manage:

* Users
* Roles
* Products
* Stock
* Orders
* Payment status
* Return requests
* Return request status
* Refund information
* Dashboard information
* Reports
* Analytics

---

# 🔄 29. Admin Return Management

Example:

```text
Return Request #7
-------------------------
Order ID: 84
User ID: 6
Reason: Damage
Comment: Product received with visible damage
Status: Pending
Created At: 09/03/2026
```

Admin actions:

```text
Pending
   ↓
 ┌───────────┐
 ↓           ↓
Approve    Reject
 ↓           ↓
Returned   Rejected
 ↓
Refund
 ↓
Refunded
```

---

# 📄 30. Reports

Administrative reports include:

## Orders Report

* Order ID
* User
* Amount
* Order status
* Payment status
* Date

## Sales Report

* Sales totals
* Revenue
* Order information
* Product sales

## User Report

* User ID
* Name
* Email
* Role
* Account information

## Return Report

* Return Request ID
* Order ID
* User ID
* Reason
* Comment
* Status
* Created date

## Refund Report

* Refund ID
* Order ID
* Payment ID
* Refund amount
* Refund status
* Refund date

Supported formats:

* CSV
* PDF

---

# 🛠️ 31. Technology Stack

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
* Stripe Checkout
* Stripe Webhook
* Stripe Refund API

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

# 📁 32. Project Architecture

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
│   │   │   ├── returns.py
│   │   │   ├── admin_returns.py
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
├── .env.example
├── .gitignore
└── README.md
```

> The exact folder and file structure may vary depending on the final project configuration.

---

# 🗄️ 33. Database Design

The application uses **MySQL** as the primary database.

## User

| Field        | Description              |
| ------------ | ------------------------ |
| `id`         | Unique user ID           |
| `name`       | User name                |
| `email`      | Unique email             |
| `password`   | Hashed password          |
| `role`       | Admin / Staff / Customer |
| `created_at` | Account creation date    |

---

## Product

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

| Field        | Description      |
| ------------ | ---------------- |
| `id`         | Cart item ID     |
| `user_id`    | User ID          |
| `product_id` | Product ID       |
| `quantity`   | Product quantity |

---

## Order

| Field            | Description        |
| ---------------- | ------------------ |
| `id`             | Order ID           |
| `user_id`        | Customer ID        |
| `total_amount`   | Total order amount |
| `status`         | Order status       |
| `payment_status` | Payment status     |

---

## Payment

The payment entity stores payment-related information.

Possible information includes:

* Payment ID
* Order ID
* Amount
* Payment method
* Payment status
* Stripe payment identifier
* Refund status
* Refund identifier

---

## Notification

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

| Field        | Description                                         |
| ------------ | --------------------------------------------------- |
| `id`         | Return request ID                                   |
| `order_id`   | Related order ID                                    |
| `user_id`    | Customer ID                                         |
| `reason`     | Return reason                                       |
| `comment`    | Optional comment                                    |
| `status`     | Pending / Approved / Rejected / Returned / Refunded |
| `created_at` | Request creation date                               |

---

# 🔐 34. Authentication System

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

Protected request:

```text
Authorization: Bearer <access_token>
```

---

# 🌐 35. Social Login

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

# 🛡️ 36. Role-Based Access Control

## Admin

Administrators can:

* Manage users
* Manage products
* Manage orders
* Manage returns
* Approve returns
* Reject returns
* Process refunds
* Manage stock
* View dashboard
* View analytics
* Access reports
* Access administrative APIs

## Staff

Staff users can access permitted operational functionality according to assigned permissions.

## Customer

Customers can:

* View products
* Filter products
* Add products to cart
* Update cart
* Remove cart items
* Create orders
* Complete payment
* View orders
* Request returns
* Track return status
* Receive notifications
* Receive email updates

---

# 📦 37. Product APIs

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

## Get Product

```http
GET /products/{product_id}
```

## Update Product

```http
PUT /products/{product_id}
```

## Delete Product

```http
DELETE /products/{product_id}
```

---

# 🛒 38. Cart APIs

## Add Product to Cart

```http
POST /cart/add
```

## View Cart

```http
GET /cart/?user_id=1
```

## Update Cart

```http
PUT /cart/update/{cart_id}?quantity=2
```

## Remove Cart Item

```http
DELETE /cart/remove/{cart_id}
```

---

# 📋 39. Order APIs

## Create Order

```http
POST /orders/create?user_id=1
```

## Get Orders

```http
GET /orders/?user_id=1
```

## Get Individual Order

```http
GET /orders/{order_id}
```

## Payment Success

```http
PUT /orders/{order_id}/pay
```

Example:

```http
PUT /orders/1/pay
```

## Update Order Status

```http
PUT /orders/{order_id}/status?status=shipped
```

## Request Return

```http
POST /orders/{order_id}/return
```

---

# 👨‍💼 40. Admin Return APIs

## Get Returns

```http
GET /admin/returns
```

## Approve Return

```http
POST /admin/returns/{id}/approve
```

## Reject Return

```http
POST /admin/returns/{id}/reject
```

Admin endpoints require appropriate authentication and authorization.

---

# 💳 41. Stripe APIs

## Stripe Checkout

The application creates Stripe Checkout sessions for customer payments.

## Stripe Webhook

```http
POST /stripe/webhook
```

The webhook validates the Stripe signature before processing events.

## Stripe Refund

The admin refund workflow uses the Stripe refund operation after an eligible return is approved.

Refund flow:

```text
Approved Return
      ↓
Stripe Refund API
      ↓
Refund Successful
      ↓
Payment Status = Refunded
      ↓
Return Status = Refunded
```

---

# 🔔 42. Complete Customer Order-to-Return Flow

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
Returned / Rejected
   ↓
Refund Processing
   ↓
Payment Updated
   ↓
Refunded
   ↓
Notification
   ↓
Email
```

---

# 🔄 43. Return Eligibility Logic

```text
Is Order Available?
       ↓
      Yes
       ↓
Does User Own Order?
       ↓
      Yes
       ↓
Is Order Delivered?
       ↓
      Yes
       ↓
Is Return Within 7 Days?
       ↓
      Yes
       ↓
Valid Return Reason?
       ↓
      Yes
       ↓
Create Return Request
```

Possible errors:

```text
Order not found
Unauthorized order access
Order is not delivered
Return window expired
Invalid request
Return already requested
```

---

# 🧪 44. API Testing

The APIs are tested using:

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
* Stripe webhook
* Stripe refund
* Notifications
* Notification read
* Dashboard
* Analytics
* Admin APIs
* Return request API
* Return eligibility validation
* Return request approval
* Return request rejection
* Inventory update
* Payment refund
* Refund status
* Authorization
* Error responses
* Validation responses

---

# 📮 45. Postman Testing – Return Request

## Customer Request

```http
POST /orders/84/return
```

Authorization:

```text
Bearer <access_token>
```

Body:

```json
{
    "reason": "Damage",
    "comment": "Product received with visible damage"
}
```

Expected result:

```text
Return Request Created
```

Initial status:

```text
pending
```

Order status:

```text
Return Requested
```

---

# 📮 46. Postman Testing – Admin Approval

## Approve

```http
POST /admin/returns/7/approve
```

Expected workflow:

```text
Pending
   ↓
Approved
   ↓
Returned
   ↓
Inventory Increased
   ↓
Stripe Refund
   ↓
Payment Updated
   ↓
Refunded
   ↓
Notification
   ↓
Email
```

---

# 📮 47. Postman Testing – Admin Rejection

## Reject

```http
POST /admin/returns/7/reject
```

Expected workflow:

```text
Pending
   ↓
Rejected
   ↓
Notification
   ↓
Email
```

---

# 🧪 48. Swagger API Testing

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
Admin Returns
   ↓
Approve / Reject
   ↓
Refund
   ↓
Notifications
   ↓
Analytics
```

---

# 🗄️ 49. MySQL Setup

Create database:

```sql
CREATE DATABASE smart_ecommerce;
```

Check databases:

```sql
SHOW DATABASES;
```

Select database:

```sql
USE smart_ecommerce;
```

Check tables:

```sql
SHOW TABLES;
```

---

# 🔄 50. Alembic Database Migrations

Navigate to backend:

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

Check migration history:

```powershell
python -m alembic history
```

---

# 🐍 51. Django Migrations

Check migrations:

```powershell
python manage.py showmigrations
```

Create migrations:

```powershell
python manage.py makemigrations
```

Apply migrations:

```powershell
python manage.py migrate
```

---

# 🚀 52. Running FastAPI Backend

Navigate to backend:

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

# 🧑‍💼 53. Running Django Admin

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

Start Django:

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

# 📸 54. Screenshots / Demo

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
├── admin-returns.png
├── return-request.png
├── return-request-form.png
├── return-request-pending.png
├── return-request-approved.png
├── return-request-rejected.png
├── refund-completed.png
├── inventory-updated.png
├── swagger.png
├── postman.png
└── stripe-checkout.png
```

Return/refund screenshots should demonstrate:

1. Delivered order
2. Request Return button
3. Return request form
4. Submitted return request
5. Pending status
6. Admin return list
7. Admin approval
8. Admin rejection
9. Returned status
10. Inventory update
11. Stripe refund
12. Refunded status
13. Notification
14. Email notification

---

# 📦 55. Final Deliverables

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
* Stripe Checkout
* Stripe webhook
* Stripe refund processing
* Notification system
* Email notifications
* WebSocket real-time updates
* Dashboard
* Analytics
* Reporting
* User-side return request
* Return eligibility validation
* ReturnRequest database model
* Return request API
* Return request status management
* Order status update
* Admin return API
* Admin return approval
* Admin return rejection
* Inventory restoration
* Payment status update
* Refund workflow
* Refund completed status
* Return/refund notifications
* Email notifications for return/refund events
* Swagger/OpenAPI documentation
* Postman API testing
* Postman collection
* Setup documentation
* GitHub version control

---

# 🔐 56. Security

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
* User ownership validation
* Return eligibility validation
* Admin authorization
* Payment/refund validation

Sensitive values must be stored in environment variables.

Never upload the following to GitHub:

```text
.env
passwords
database credentials
JWT secret keys
Auth0 secrets
Stripe secret keys
API keys
```

---

# 🔒 57. .gitignore

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

# 🔄 58. Complete Application Flow

```text
                         USER
                           │
                           ▼
                    Authentication
                           │
             ┌─────────────┴─────────────┐
             │                           │
         Customer                      Admin
             │                           │
             ▼                           ▼
         Products                  Django Admin
             │                           │
             ▼                           ▼
           Cart                    Users / Products
             │                    Orders / Returns
             ▼                           │
         Checkout                        │
             │                           │
             ▼                           ▼
          Stripe                    Analytics
             │
             ▼
          Payment
             │
             ▼
        Order Update
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
    Approve       Reject
       │              │
       ▼              ▼
   Returned        Rejected
       │
       ▼
Inventory Updated
       │
       ▼
Stripe Refund
       │
       ▼
Payment Refunded
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

# 📈 59. Analytics Flow

```text
Database
   ↓
Orders
   ↓
Sales Data
   ↓
Return Data
   ↓
Refund Data
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
Refunded Orders
Refund Statistics
```

---

# 💳 60. Payment Flow

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

# 🔄 61. Complete Return & Refund Flow

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
Approve        Reject
 │               │
 ▼               ▼
Returned       Rejected
 │
 ▼
Inventory Increased
 │
 ▼
Stripe Refund
 │
 ▼
Payment Status = Refunded
 │
 ▼
Return Status = Refunded
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
Customer
```

---

# 🔔 62. Notification Flow

```text
Order / Return / Refund Event
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

Return events include:

```text
Return Requested
Return Approved
Return Rejected
Refund Completed
```

---

# 🧪 63. API Testing Status

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
* Stripe Checkout
* Stripe webhook
* Stripe refund workflow
* Notifications
* Notification read
* Dashboard
* Analytics
* Admin APIs
* Authorization
* Error responses
* Validation responses
* Return Request API
* Return eligibility
* Return request creation
* Pending return status
* Admin approval
* Admin rejection
* Returned status
* Inventory update
* Refund processing
* Refunded status
* Payment status update
* Notification triggering
* Email notification triggering

Expected successful responses may include:

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

# 🐳 64. Optional Docker Deployment

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

# 🔮 65. Future Enhancements

Possible future improvements include:

* Docker deployment
* Cloud deployment
* CI/CD pipeline
* Automated API testing
* Advanced analytics
* Product search
* Pagination
* Cloud image storage
* Production email service
* Production Stripe configuration
* Redis caching
* Background task processing
* Monitoring and logging
* Return pickup tracking
* Return shipment tracking
* Refund transaction tracking
* Advanced refund reconciliation

---

# 🧑‍💻 66. Installation Summary

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
18. Configure Stripe test credentials
19. Test order workflow
20. Test return request workflow
21. Test admin approval/rejection
22. Test inventory restoration
23. Test Stripe refund
24. Test notifications
25. Test email notifications
```

---

# 📥 67. GitHub Setup

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

# 📤 68. GitHub Update

After making changes:

```powershell
git add .
```

Commit:

```powershell
git commit -m "Complete admin return refund workflow and notifications"
```

Push:

```powershell
git push
```

---

# 🌐 69. GitHub Repository

**Smart E-Commerce Platform**

Repository:

```text
https://github.com/RAMKUMAR63815/smart-ecommerce-platform
```

---

# 👨‍💻 70. Author

**Ram Kumar**

Smart E-Commerce Platform

Technology used:

```text
Python
FastAPI
Django
SQLAlchemy
MySQL
Alembic
JWT
Auth0
Stripe
React
Next.js
WebSockets
Email Notifications
Postman
Swagger
Git
GitHub
```

---

# ✅ 71. Project Completion

The Smart E-Commerce Platform has been developed as a full-stack e-commerce project demonstrating:

* Secure authentication
* Role-based authorization
* Product management
* Shopping cart management
* Order processing
* Payment integration
* Stripe Checkout
* Stripe webhook
* Stripe refund processing
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
* User-side Return Request
* ReturnRequest database model
* Return Request API
* Return eligibility validation
* 7-day return window validation
* Order status update to Return Requested
* Admin return APIs
* Admin return approval
* Admin return rejection
* Inventory restoration
* Payment status update
* Refund workflow
* Refunded status
* Return/refund notifications
* Email notifications
* GitHub version control

The project provides a complete foundation for a production-oriented full-stack e-commerce application with customer return management and administrator-controlled refund processing.

---

# 🏁 72. Conclusion

The Smart E-Commerce Platform demonstrates a modular full-stack architecture combining **FastAPI for backend APIs, Django for administration, MySQL for data storage, JWT/Auth0 for authentication, Stripe for payments and refunds, WebSockets for real-time communication, email notifications for user communication, and Postman/Swagger for API testing**.

The platform covers the complete e-commerce workflow from user authentication and product browsing to cart management, order creation, payment processing, delivery, customer return requests, administrative return processing, inventory restoration, payment refunds, and customer notifications.

The implemented **Return & Refund Management System** allows customers to request returns for eligible delivered orders within the configured return window.

The system validates:

```text
Order
 ↓
User Ownership
 ↓
Delivered Status
 ↓
Return Window
 ↓
Return Request
```

After the customer submits a request, the administrator can review it through the admin return APIs.

The completed admin workflow is:

```text
Pending
   ↓
Admin Review
   ↓
Approve / Reject
```

For an approved return:

```text
Approved
   ↓
Returned
   ↓
Inventory Increased
   ↓
Stripe Refund
   ↓
Payment Status Updated
   ↓
Refunded
   ↓
Notification
   ↓
Email
   ↓
Real-Time Update
```

For a rejected return:

```text
Pending
   ↓
Rejected
   ↓
Notification
   ↓
Email
```

Therefore, the project now provides an end-to-end e-commerce lifecycle covering:

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
Admin Return Management
      +
Inventory Management
      +
Stripe Refunds
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

# 🎉 Project Status: Completed ✅
