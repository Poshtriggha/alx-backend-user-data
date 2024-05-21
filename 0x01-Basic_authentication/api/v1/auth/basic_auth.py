#!/usr/bin/env python3
""" inherits from Auth """

from api.v1.auth.auth import Auth
import base64
from flask import request
from typing import List, TypeVar
from models.user import User


class BasicAuth(Auth):
    """_summary_

    Args:
        Auth (_type_): The class to inherit from
    """
    def extract_base64_authorization_header(self,
                                            authorization_header: str
                                            ) -> str:
        """ returns the Base64 part of the Authorization header
        for a Basic Authentication """
        if authorization_header is None or\
           type(authorization_header) is not str:
            return None
        head = authorization_header.split(' ')

        return head[1] if head[0] == 'Basic' else None

    def decode_base64_authorization_header(self,
                                           base64_authorization_header: str
                                           ) -> str:
        """ returns the decoded value of a Base64 string
        base64_authorization_header """
        if base64_authorization_header is None or\
           type(base64_authorization_header) is not str:
            return None
        try:
            base64_bytes = base64_authorization_header.encode('utf-8')
            message_bytes = base64.b64decode(base64_bytes)
            message = message_bytes.decode('utf-8')
            return message
        except Exception:
            return None

    def extract_user_credentials(self,
                                 decoded_base64_authorization_header: str
                                 ) -> (str, str):
        """ returns the user email & password from the Base64 decoded value"""
        if not decoded_base64_authorization_header or\
           not isinstance(decoded_base64_authorization_header, str)\
           or ":" not in decoded_base64_authorization_header:
            return (None, None)
        to_extract = decoded_base64_authorization_header.split(':', 1)
        return (to_extract[0], to_extract[1]) if to_extract else (None, None)

    def user_object_from_credentials(self, user_email: str,
                                     user_pwd: str) -> TypeVar('User'):
        """ returns the User instance based on his email and password """
        if not user_email or not isinstance(user_email, str)\
           or not user_pwd or not isinstance(user_pwd, str):
            return None
        users = User.search({'email': user_email})
        if not users:
            return None
        for user in users:
            if user.is_valid_password(user_pwd):
                return user
        return None

    def current_user(self, request=None) -> TypeVar('User'):
        """ overloads Auth and retrieves the User instance for a request """
        try:
            head = self.authorization_header(request)
            base64_h = self.extract_base64_authorization_header(head)
            decode_h = self.decode_base64_authorization_header(base64_h)
            credentials = self.extract_user_credentials(decode_h)
            return self.user_object_from_credentials(credentials[0],
                                                     credentials[1])
        except Exception:
            return None