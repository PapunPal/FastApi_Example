from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
import os
from dotenv import load_dotenv


# --------------------------------------------------
# 1. FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="JWT Authentication Lab",
    description="Learn JWT authentication using FastAPI",
    version="1.0.0"
)


# --------------------------------------------------
# 2. JWT CONFIGURATION
# --------------------------------------------------

# DEMO ONLY: Use a strong secret from an environment
# variable or secrets manager in production.
# Load environment variables from .env file
load_dotenv()

# Read SECRET_KEY from .env
SECRET_KEY = os.getenv("SECRET_KEY")

# Validate SECRET_KEY
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is missing. Please configure it in .env file."
    )

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# --------------------------------------------------
# 3. PASSWORD HASHING
# --------------------------------------------------

password_hash = PasswordHash.recommended()


# --------------------------------------------------
# 4. SAMPLE USER DATABASE
# --------------------------------------------------

# In-memory data for learning.
# The password is hashed, not stored as plain text.

fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrator",
        "email": "admin@example.com",
        "hashed_password": password_hash.hash("Admin@123"),
        "role": "admin",
        "disabled": False
    }
}


# --------------------------------------------------
# 5. OAUTH2 CONFIGURATION
# --------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# --------------------------------------------------
# 6. VERIFY USER PASSWORD
# --------------------------------------------------

def verify_password(plain_password, hashed_password):
    return password_hash.verify(
        plain_password,
        hashed_password
    )


# --------------------------------------------------
# 7. AUTHENTICATE USER
# --------------------------------------------------

def authenticate_user(username, password):

    user = fake_users_db.get(username)

    if not user:
        return False

    if not verify_password(
        password,
        user["hashed_password"]
    ):
        return False

    return user


# --------------------------------------------------
# 8. GENERATE JWT TOKEN
# --------------------------------------------------

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# --------------------------------------------------
# 9. UNPROTECTED HOME ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Welcome to FastAPI JWT Authentication Lab",
        "authentication_required": False
    }


# --------------------------------------------------
# 10. LOGIN ENDPOINT
# --------------------------------------------------

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    user = authenticate_user(
        form_data.username,
        form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={
            "sub": user["username"],
            "role": user["role"]
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


# --------------------------------------------------
# 11. GET CURRENT USER FROM JWT
# --------------------------------------------------

def get_current_user(token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = fake_users_db.get(username)

    if user is None or user["disabled"]:
        raise credentials_exception

    return user


# --------------------------------------------------
# 12. PROTECTED PROFILE ENDPOINT
# --------------------------------------------------

@app.get("/profile")
def get_profile(
    current_user: dict = Depends(get_current_user)
):

    return {
        "message": "You accessed a protected endpoint",
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "email": current_user["email"],
        "role": current_user["role"]
    }


# --------------------------------------------------
# 13. PROTECTED ADMIN ENDPOINT
# --------------------------------------------------

@app.get("/admin")
def admin_dashboard(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return {
        "message": "Welcome to the Admin Dashboard",
        "username": current_user["username"]
    }

