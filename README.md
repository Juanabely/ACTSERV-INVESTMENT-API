# Investment Account Management API

## Table of Contents
1. [Introduction && Flow](#introduction)
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

## Introduction && Flow

This API provides a comprehensive system for managing investment accounts, users, permissions, and transactions. It is designed with a robust permission system to ensure secure and controlled access to financial data.
A user is created by an admin or superuser
An admin is supposed to be authinticated by sending a post request to 'api_auth_token/' 
{
   username : abel,
   password : Abel12345
}
After auth the admin can now add other users with there role field ,these new users have different permission levels according to there roles 
Admins - can get all investment accounts ,with all there users and roles 
         can create new accounts
         can add users to accounts and assign permissions to them
Managers - can get accounts
          can create accounts
          cannot get transactions
Investors - Default role && has basic permissions    

Once a user has been added to an investment account they can now perform different crud operations according to the permissions they were assigned to.

## Authentication

The API uses token-based authentication. Include the token in the Authorization header of your requests:

(docs/authheader.png)

```

Authorization: Token <your-token-here>
```
![Screenshot 2024-09-19 135744](https://github.com/user-attachments/assets/f4871585-a489-4f80-84f7-ebd434a05263)

To obtain a token, use the login endpoint:

```
POST /api-token-auth/
{
    "username": "your_username",
    "password": "your_password"
}
```
![Screenshot 2024-09-19 143925](https://github.com/user-attachments/assets/77ef9fd7-9b71-4fbe-8247-c16936548e57)


## Permissions

The system uses a custom permission model with four levels:

- `can_view`: Can view account details and transactions
- `can_create`: Can create new transactions, but cannot view existing ones
- `can_change`: Can perform all operations on transactions
- `admin`: Has full access, including user management and permission assignment

Only admin users can create new users and if you can_create_account perm, investment accounts, and assign permissions.
Mangers can add investment accounts but cannot delete them

## Endpoints

### Users

- `GET /customusers/`: List all users (Admin only)
- `POST /customusers/`: Create a new user (Admin only)
- `GET /customusers/{id}/`: Retrieve a specific user
- `PUT /customusers/{id}/`: Update a user
- `DELETE /customusers/{id}/`: Delete a user (Admin only)

### Accounts

- `GET /accounts/`: List all accounts
- `POST /accounts/`: Create a new account (Admin only)
- `GET /accounts/{id}/`: Retrieve a specific account
- `PUT /accounts/{id}/`: Update an account (Admin only)
- `DELETE /accounts/{id}/`: Delete an account (Admin only)

### Permissions,and assigning users to accounts

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
- Abstracted the django base model and created a custom manager to handle creating users and super users
-`username`-username - unique
-`Email`-email - unique
-`password` - password
-`role` - has a default value of investor used for group creations and assigning permissions
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
