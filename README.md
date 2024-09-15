# Investment Account Management API

## Table of Contents
1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Permissions](#permissions)
4. [Endpoints](#endpoints)
   - [Users](#users)
   - [Accounts](#accounts)
   - [Permissions](#permissions-1)
   - [Transactions](#transactions)
5. [Models](#models)
6. [Error Handling](#error-handling)
7. [Testing](#testing)

## Introduction

This API provides a comprehensive system for managing investment accounts, users, permissions, and transactions. It is designed with a robust permission system to ensure secure and controlled access to financial data.

## Authentication

The API uses token-based authentication. Include the token in the Authorization header of your requests:

```
Authorization: Token <your-token-here>
```

To obtain a token, use the login endpoint:

```
POST /api/token/
{
    "username": "your_username",
    "password": "your_password"
}
```

## Permissions

The system uses a custom permission model with four levels:

- `view`: Can view account details and transactions
- `post`: Can create new transactions, but cannot view existing ones
- `crud`: Can perform all operations on transactions
- `admin`: Has full access, including user management and permission assignment

Only admin users can create new users, investment accounts, and assign permissions.

## Endpoints

### Users

- `GET /users/`: List all users (Admin only)
- `POST /users/`: Create a new user (Admin only)
- `GET /users/{id}/`: Retrieve a specific user
- `PUT /users/{id}/`: Update a user
- `DELETE /users/{id}/`: Delete a user (Admin only)

### Accounts

- `GET /accounts/`: List all accounts
- `POST /accounts/`: Create a new account (Admin only)
- `GET /accounts/{id}/`: Retrieve a specific account
- `PUT /accounts/{id}/`: Update an account (Admin only)
- `DELETE /accounts/{id}/`: Delete an account (Admin only)

### Permissions

- `GET /permissions/`: List all permissions
- `POST /permissions/`: Create a new permission (Admin only)
- `GET /permissions/{id}/`: Retrieve a specific permission
- `PUT /permissions/{id}/`: Update a permission (Admin only)
- `DELETE /permissions/{id}/`: Delete a permission (Admin only)

### Transactions

- `GET /transactions/`: List transactions (filtered based on user's permissions)
- `POST /transactions/`: Create a new transaction
- `GET /transactions/{id}/`: Retrieve a specific transaction
- `PUT /transactions/{id}/`: Update a transaction
- `DELETE /transactions/{id}/`: Delete a transaction

## Models

### User
- Standard Django User model

### InvestmentAccount
- `name`: CharField
- `balance`: DecimalField

### UserAccountPermission
- `user`: ForeignKey(User)
- `account`: ForeignKey(InvestmentAccount)
- `permission`: CharField(choices=['view', 'post', 'crud', 'admin'])

### Transaction
- `account`: ForeignKey(InvestmentAccount)
- `amount`: DecimalField
- `description`: TextField
- `date`: DateTimeField

## Error Handling

The API uses standard HTTP status codes:

- 200: OK
- 201: Created
- 204: No Content
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Errors will return a JSON object with a `detail` key explaining the error.

## Testing

To run the test suite:

```
python manage.py test
```

The test suite covers:
- Permission levels (view, post, crud)
- Admin functionalities
- CRUD operations on transactions
- Access control for non-admin users

## Development

To set up the development environment:

1. Clone the repository
2. Create a virtual environment: `python -m venv env`
3. Activate the virtual environment:
   - On Windows: `env\Scripts\activate`
   - On Unix or MacOS: `source env/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create a superuser: `python manage.py createsuperuser`
7. Run the development server: `python manage.py runserver`

## Deployment

For production deployment, ensure you:
1. Set `DEBUG = False` in settings
2. Use a production-grade web server like Gunicorn
3. Set up a reverse proxy like Nginx
4. Use environment variables for sensitive information
5. Set up proper database backups
