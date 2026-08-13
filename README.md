# Smart E-Commerce Platform

## Project Overview

Smart E-Commerce Platform is a full-stack e-commerce application designed to provide secure product management, customer authentication, shopping cart, order processing, payment handling, and administrative management.

The project uses FastAPI for backend APIs, MySQL for database management, Django for administration, and a modern frontend for the customer interface.

## Technologies Used

* Python
* FastAPI
* SQLAlchemy
* MySQL
* JWT Authentication
* Auth0 Social Login
* Django
* React / Next.js
* Postman
* Git & GitHub

## Main Features

### Authentication

* User registration
* User login
* JWT access token
* JWT refresh token
* Current user information
* Auth0 social login
* Role-based access control

### Product Management

* Create products
* View products
* View individual product
* Update product information
* Delete products
* Stock management

### Shopping Cart

* View cart
* Add products to cart
* Update product quantity
* Remove products from cart

### Orders

* Create orders
* View orders
* View individual order
* Order status management

### Payment

* Payment processing
* Payment status handling
* Order-payment integration

### Administration

* User management
* Product management
* Order management
* Dashboard and analytics

## Project Structure

```text
smart_ecommerce/
│
├── fastapi_backend/
│   ├── app/
│   ├── alembic/
│   ├── requirements.txt
│   └── ...
│
├── django_admin/
│   └── ...
│
├── frontend/
│   └── ...
│
├── postman/
│   ├── collections/
│   ├── environments/
│   └── globals/
│
├── .env.example
├── .gitignore
└── README.md
```

## Backend API

The FastAPI backend provides REST APIs for authentication, products, cart, orders, payments, and user management.

### Run Backend

Open a terminal in the backend folder:

```bash
cd fastapi_backend
```

Activate the virtual environment if required and install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

## Authentication APIs

Important authentication endpoints include:

```text
POST /auth/register
POST /auth/login
POST /auth/refresh
GET  /auth/me
POST /auth/social-login
```

## Postman Testing

A Postman collection is included in the project:

```text
postman/
```

The collection contains requests for the main application APIs.

The environment uses:

```text
baseUrl = http://127.0.0.1:8000
```

## Database

The application uses MySQL as the primary database.

Database configuration should be stored in the local `.env` file.

**Do not commit the real `.env` file to GitHub.**

Use `.env.example` as a template for configuring the application.

## Security

The project uses:

* Password hashing
* JWT authentication
* Access and refresh tokens
* Role-based authorization
* Environment variables for sensitive configuration

Sensitive credentials and secret keys should never be committed to the repository.

## Testing

API testing can be performed using:

* FastAPI Swagger UI
* Postman

Swagger:

```text
http://127.0.0.1:8000/docs
```

## GitHub

Project repository:

https://github.com/RAMKUMAR63815/smart-ecommerce-platform

## Author

**Ram Kumar**

Smart E-Commerce Platform — Full Stack Assignment
