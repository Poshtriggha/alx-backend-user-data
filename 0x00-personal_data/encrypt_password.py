#!/usr/bin/env python3
"""AAAAA"""


import bcrypt
import typing


def hash_password(password: str) -> bytes:
    """AAAA"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    """AAAA"""
    return bcrypt.checkpw(password.encode(), hashed_password)