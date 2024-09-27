"""
Authentication API Endpoints

This module defines the FastAPI route for user authentication. It allows users to obtain an
OAuth2-compliant token for accessing protected endpoints. The token is generated upon successful
authentication of the user's credentials.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta

from schemas import Token, User, UserRequest, ChangePassword
from services.auth import (
    authenticate_user, 
    register_user,
    create_access_token,
    get_current_active_user,
    update_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# APIRouter object to define all routes for Authentication
auth_router = APIRouter()


@auth_router.post("/register", response_model=Token, tags=["Authentication"])
async def register_new_user(
    new_user: UserRequest,  # Define el esquema del nuevo usuario
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Register a new user (accessible only to authenticated users).
    
    Args:
        new_user (CreateUser): The new user's data (username and password).
        db (Session): The database session.
        token (str): The OAuth2 token of the authenticated user.

    Returns:
        dict: A dictionary containing the access token and token type (bearer).
    
    Raises:
        HTTPException:
            - 400 Bad Request if the username is already taken.
    """
    user = register_user(new_user)
    if not user:
            # Raise an HTTP 401 Unauthorized error if authentication fails
            raise HTTPException(
                status_code=400,
                detail="User already exists",
                headers={"WWW-Authenticate": "Bearer"},
            )
    # Generate token for the new user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.put("/change-password", tags=["Authentication"])
async def change_password(
    new_password_data: ChangePassword,  # Esquema para la nueva contraseña
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Endpoint para que un usuario cambie su propia contraseña.

    Args:
        new_password_data (ChangePassword): La nueva contraseña.
        db (Session): Sesión de la base de datos.
        token (str): El token de autenticación del usuario.

    Returns:
        dict: Un mensaje indicando que la contraseña ha sido actualizada.
    
    Raises:
        HTTPException:
            - 400 Bad Request si las contraseñas no son válidas.
    """
    user = authenticate_user(current_user.username, new_password_data.old_password)
    if not user:
        # Raise an HTTP 401 Unauthorized error if authentication fails
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    update_password(current_user.username, new_password_data.new_password)
 
    return {"message": "Password successfully updated"}

@auth_router.post("/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    Authenticate the user and provide an OAuth2 access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.
        db (Session): The database session (injected by FastAPI dependency).

    Returns:
        dict: A dictionary containing the access token and token type (bearer).
    
    Raises:
        HTTPException: 
            - 401 Unauthorized if the username or password is incorrect.
    """
    # Verify user credentials
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        # Raise an HTTP 401 Unauthorized error if authentication fails
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Calculate the expiration time for the access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Create the access token using the user's username as the subject (sub)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Return the token and its type (bearer) as a JSON response
    return {"access_token": access_token, "token_type": "bearer"}
