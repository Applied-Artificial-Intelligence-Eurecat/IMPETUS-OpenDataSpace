"""
auth.py

Dependencies:
- FastAPI: For building web APIs and managing authentication with OAuth2.
- JOSE (JWT): For handling JSON Web Tokens (JWT) used for authentication.
- Passlib: For securely hashing and verifying passwords.
- datetime: For managing token expiration.
- Typing: For type hinting.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Annotated
from passlib.context import CryptContext
import utils
from schemas import TokenData, User, UserRequest, UserDB
import repository.fiware  as fiware_repository
# Configuration constants
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if the provided plain password matches the hashed password stored in the database.

    Args:
        plain_password (str): The plain text password input by the user.
        hashed_password (str): The hashed password stored in the database.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    if not plain_password or not hashed_password:
        raise ValueError("Both password and hashed_password must be provided.")
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hashes the provided password using bcrypt hashing algorithm.

    Args:
        password (str): The plain text password to be hashed.

    Returns:
        str: The hashed password.
    """
    if not password:
        raise ValueError("Password must not be empty.")
    return pwd_context.hash(password)

def update_password(username: str, new_password:str):
    user_in_db = get_user(username)
    user_in_db.hashed_password = get_password_hash(new_password)
    fiware_repository.send_entity([user_in_db.user_to_fiware()])
    return user_in_db

def register_user(user: UserRequest) -> Optional[UserDB]:
    # Check if username already exists
    user_in_db = get_user(user.username)
    if user_in_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Hash the password before storing it
    hashed_password = get_password_hash(user.password)
    
    # Create a new user record
    new_user_entry = UserDB(username=user.username, hashed_password=hashed_password, company=user.company)
    fiware_repository.send_entity([new_user_entry.user_to_fiware()])
    return new_user_entry

def authenticate_user(username: str, password: str) -> Optional[UserDB]:
    """
    Authenticates a user by verifying their password and retrieving their details from the database.

    Args:
        database (Session): The database session to query the user.
        username (str): The username of the user.
        password (str): The plain text password provided by the user.

    Returns:
        Optional[DBUser]: The authenticated user object if credentials are valid, None otherwise.
    """
    if not username or not password:
        raise ValueError("Username and password must not be empty.")
    
    user: Optional[UserDB] = get_user(username)
    
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password."
        )

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token with an optional expiration time.

    Args:
        data (dict): The data to encode in the token (usually the username).
        expires_delta (Optional[timedelta]): Optional expiration time for the token. Defaults to 15 minutes if not provided.

    Returns:
        str: The encoded JWT token.
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary.")
    
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Token encoding failed: {str(e)}"
        )
    return encoded_jwt



async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> UserDB:
    """
    Retrieves the current user based on the JWT token passed in the request.

    Args:
        database (Session): The database session to query the user.
        token (str): The JWT token passed for authentication.

    Returns:
        DBUser: The user object associated with the token.

    Raises:
        HTTPException: If the token is invalid or user cannot be found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user


def get_user(username: str) -> Optional[UserDB]:
    """
    Retrieves a user from the database by username.

    Args:
        username (str): The username of the user.

    Returns:
        Optional[UserDB]: The user object if found, None otherwise.
    """
    if not username:
        raise ValueError("Username must not be empty.")
    user_fiware = fiware_repository.get_specific_entity(utils.get_full_user_id(username))
    if not user_fiware:
        return None
    return UserDB.from_fiware(user_fiware.json())

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Retrieves the current active user.

    Args:
        current_user (User): The currently authenticated user.

    Returns:
        User: The current active user object.
    """
    return current_user
