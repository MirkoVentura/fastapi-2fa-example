import pytest
import os
import pyotp
from fastapi.testclient import TestClient
from fastapi import Depends
from unittest.mock import patch
from main import app, get_main_db
from authcooking.core.database import DBInitTest
from authcooking.core.crud import get_seed
from unittest.mock import patch

def get_test_db():
    session = None
    try:
        session = DBInitTest("sqlite:///./test.db").get_session()
        session = session()
        yield session
    finally:
        session.close()

def get_test_seed():
    return "NTSFBMZJ2EIDG576Y33JSL6K3ND7MZ5C"

@pytest.fixture
def delete_database():
    os.unlink("./test.db")

client = TestClient(app)

app.dependency_overrides[get_main_db] = get_test_db
app.dependency_overrides[get_seed] = get_test_seed


class TestUserRegistration:
    """TestUserRegistration tests /users/register"""

    def test_get_request_returns_405(self):
        """registration endpoint does only expect a post request"""
        response = client.get("/users/register")
        assert response.status_code == 405

    def test_post_request_without_body_returns_422(self):
        """body should have username, password and fullname""" 
        response = client.post("/users/register")
        assert response.status_code == 422

    def test_post_request_with_improper_body_returns_422(self):
        """all of username, password and fullname is required"""
        response = client.post(
            "/users/register",
            json={"username": "miro"}
        )
        assert response.status_code == 422

    def test_post_request_with_proper_body_returns_201(self, delete_database):
        response = client.post(
            "/users/register",
            json={"username": "miro", "password": "mi3333", "fullname": "MIROKO ", "email":"mirko@aaa.com", "need_otp": True}
        )
        assert response.status_code == 201


class TestUserAuth:
    """TestUserAuth tests /users/auth"""

    def test_get_request_returns_405(self):
        """login endpoint does only expect a post request"""
        response = client.get("/users/auth")
        assert response.status_code == 405
    
    def test_post_request_with_improper_body_returns_422(self):
        """both username and password should be added"""
        response = client.post(
            "/users/auth",
            json = {"username": "mirrr"})
        assert response.status_code == 422
        
    def test_post_request_with_proper_body_returns_200_with_jwt_token(self, delete_database):
        """act a registration"""
        response = client.post(
            "/users/register",
            json={"username": "miro", "password": "mi3333", "fullname": "MIROKO ", "email":"mirko@aaa.com", "need_otp": False}
        )

        """Login Correct for given credential"""
        response = client.post(
            "/users/auth",
            json = {"username": "miro", "password": "mi3333"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 3
    
    def test_post_request_with_proper_body_returns_200_with_otp_challange(self, delete_database):
        """act a registration"""
        response = client.post(
            "/users/register",
            json={"username": "miro", "password": "mi3333", "fullname": "MIROKO ", "email":"mirko@aaa.com", "need_otp": True}
        )

        """Login Correct for given credential"""
        response = client.post(
            "/users/auth",
            json = {"username": "miro", "password": "mi3333"}
        )
        assert response.status_code == 200
        assert response.json()["token_type"] == "OTP_CHALLANGE"
        assert len(response.json()) == 3

class TestVerifyOTP:
    """Test for api /users/auth/verify-otp"""
    def test_get_request_returns_405(self):
        """registration endpoint does only expect a post request"""
        response = client.get("/users/auth/verify-otp")
        assert response.status_code == 405
    
    def test_post_request_with_improper_body_returns_422(self):
        """both username and password should be added"""
        response = client.post(
            "/users/auth/verify-otp",
            json = {"username": "mirrr"})
        assert response.status_code == 422

        response = client.post(
            "/users/register",
            json={"username": "miro", "password": "mi3333", "fullname": "MIROKO ", "email":"mirko@aaa.com", "need_otp": True}
        )
        
        """Login Correct for given credential"""
        response = client.post(
            "/users/auth",
            json = {"username": "miro", "password": "mi3333"}
        )

        totp = pyotp.TOTP(get_test_seed(), interval = 60)
        print(get_test_seed())
        """Login Correct for given totp"""
        response = client.post(
            "/users/auth/verify-otp",
            json = {"username": "miro", "password": totp.now()}
        )
        assert response.status_code == 200
        assert response.json()["token_type"] == "OTP_CHALLANGE"
        assert len(response.json()) == 3
