#!/usr/bin/env python3
"""
Test suite for the user authentication service.
"""

import requests

BASE_URL = "http://127.0.0.1:5000"

def register_user(email: str, password: str) -> None:
    response = requests.post(f"{BASE_URL}/users", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    assert response.json() == {"email": email, "message": "user created"}, response.text

def log_in_wrong_password(email: str, password: str) -> None:
    response = requests.post(f"{BASE_URL}/sessions", json={"email": email, "password": password})
    assert response.status_code == 401, response.text

def log_in(email: str, password: str) -> str:
    response = requests.post(f"{BASE_URL}/sessions", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.cookies.get("session_id")

def profile_unlogged() -> None:
    response = requests.get(f"{BASE_URL}/profile")
    assert response.status_code == 403, response.text

def profile_logged(session_id: str) -> None:
    response = requests.get(f"{BASE_URL}/profile", cookies={"session_id": session_id})
    assert response.status_code == 200, response.text

def log_out(session_id: str) -> None:
    response = requests.delete(f"{BASE_URL}/sessions", cookies={"session_id": session_id})
    assert response.status_code == 200, response.text

def reset_password_token(email: str) -> str:
    response = requests.post(f"{BASE_URL}/reset_password", json={"email": email})
    assert response.status_code == 200, response.text
    return response.json().get("reset_token")

def update_password(email: str, reset_token: str, new_password: str) -> None:
    response = requests.put(f"{BASE_URL}/reset_password", json={
        "email": email,
        "reset_token": reset_token,
        "new_password": new_password
    })
    assert response.status_code == 200, response.text
    assert response.json() == {"email": email, "message": "Password updated"}, response.text

EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"

if __name__ == "__main__":
    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
