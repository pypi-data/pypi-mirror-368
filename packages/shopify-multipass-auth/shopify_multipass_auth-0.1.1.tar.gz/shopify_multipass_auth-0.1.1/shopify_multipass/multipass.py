"""
Shopify multipass service for customer authentication.

This service generates Shopify multipass tokens for customer login.
"""

from __future__ import annotations

import datetime
import json
import re
from base64 import urlsafe_b64encode
from typing import Any
from urllib.parse import urlparse

from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
from Crypto.Random import get_random_bytes


class MultiPass:
    """
    Service for generating Shopify multipass login tokens.

    :class:`MultipassService`
    """

    def __init__(self, secret: str):
        """Initialize the multipass service."""
        if not secret:
            raise ValueError("SHOPIFY_MULTIPASS_SECRET is required")

        # Initialize crypto keys using the provided style
        key = SHA256.new(secret.encode("utf-8")).digest()
        self.encryptionKey = key[0:16]
        self.signatureKey = key[16:32]

    def _validate_domain(self, domain: str) -> bool:
        """
        Validate if the domain is a valid Shopify domain.

        :param domain: Domain to validate
        :type domain: str
        :return: True if domain is valid, False otherwise
        :rtype: bool
        """
        if not domain:
            return False

        try:
            # Parse the URL
            parsed = urlparse(
                domain
                if domain.startswith(("http://", "https://"))
                else f"https://{domain}"
            )
            hostname = parsed.hostname

            if not hostname:
                return False

            # Check if it's a valid Shopify domain
            shopify_pattern = r"^[a-zA-Z0-9\-]+\.myshopify\.com$"
            if re.match(shopify_pattern, hostname):
                return True

            # Also allow custom domains (basic validation)
            domain_pattern = r"^[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}$"
            return bool(re.match(domain_pattern, hostname))

        except Exception:
            return False

    def get_token_only(self, email: str, return_to: str) -> dict[str, Any]:
        """
        Job 1: Generate only a multipass token for given email and return_to URL.

        :param email: Customer email address
        :type email: str
        :param return_to: URL to redirect to after authentication
        :type return_to: str
        :return: Response dict with error code and token or error message
        :rtype: dict[str, Any]
        """
        try:
            # Validate inputs
            if not email or not return_to:
                return {"error": 1, "message": "Email and return_to are required"}

            # Validate email format
            if not self._validate_email(email):
                return {"error": 1, "message": "Invalid email format"}

            # Prepare customer data
            customer_data = {
                "email": email,
                "return_to": return_to,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }

            # Generate token only
            token = self._generate_token(customer_data).decode("utf-8")
            return {"error": 0, "token": token}

        except Exception as e:
            return {"error": 1, "message": f"Error: {str(e)}"}

    def get_login_url_with_token(self, token: str, domain: str) -> dict[str, Any]:
        """
        Job 2: Generate login URL using an existing token and domain.

        :param token: Previously generated multipass token
        :type token: str
        :param domain: Shopify domain for multipass authentication
        :type domain: str
        :return: Response dict with error code and redirect URL or error message
        :rtype: dict[str, Any]
        """
        try:
            # Validate inputs
            if not token or not domain:
                return {"error": 1, "message": "Token and domain are required"}

            # Validate domain
            if not self._validate_domain(domain):
                return {"error": 1, "message": "Invalid domain format"}

            # Ensure URL has proper protocol
            if not domain.startswith(("http://", "https://")):
                domain = f"https://{domain}"

            # Generate login URL
            login_url = f"{domain.rstrip('/')}/account/login/multipass/{token}"
            return {"error": 0, "redirect": login_url}

        except Exception as e:
            return {"error": 1, "message": f"Error: {str(e)}"}

    def _generate_complete_login_url(
        self, email: str, return_to: str, domain: str
    ) -> dict[str, Any]:
        """
        Job 3: Generate a complete multipass login URL with token for a customer.
        This is a combination of jobs 1 and 2.

        :param email: Customer email address
        :type email: str
        :param return_to: URL to redirect to after authentication
        :type return_to: str
        :param domain: Shopify domain for multipass authentication
        :type domain: str
        :return: Response dict with error code and redirect URL or error message
        :rtype: dict[str, Any]
        """
        try:
            # Validate inputs
            if not email or not domain or not return_to:
                return {
                    "error": 1,
                    "message": "Email, domain, and return_to are required",
                }

            # Validate domain
            if not self._validate_domain(domain):
                return {"error": 1, "message": "Invalid domain format"}

            # Validate email format
            if not self._validate_email(email):
                return {"error": 1, "message": "Invalid email format"}

            # Prepare customer data
            customer_data = {
                "email": email,
                "return_to": return_to,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }

            # Generate URL using the provided domain
            url = self._generate_url(customer_data, domain)
            return {"error": 0, "redirect": url}

        except Exception as e:
            return {"error": 1, "message": f"Error: {str(e)}"}

    # Backward compatibility - keep the original method name
    def generate_login_url(
        self, email: str, domain: str, return_to: str
    ) -> dict[str, Any]:
        """
        Generate a multipass login URL for a customer.
        This method is kept for backward compatibility and calls generate_complete_login_url.

        :param email: Customer email address
        :type email: str
        :param domain: Shopify domain for multipass authentication
        :type domain: str
        :param return_to: URL to redirect to after authentication
        :type return_to: str
        :return: Response dict with error code and redirect URL or error message
        :rtype: dict[str, Any]
        """
        return self._generate_complete_login_url(email, return_to, domain)

    def _validate_email(self, email: str) -> bool:
        """
        Validate email format.

        :param email: Email to validate
        :type email: str
        :return: True if email is valid, False otherwise
        :rtype: bool
        """
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_pattern, email))

    def _generate_url(self, customerDataHash: dict[str, Any], url: str) -> str:
        """
        Generate a multipass login URL.

        :param customerDataHash: Customer information
        :type customerDataHash: dict[str, Any]
        :param url: Shop URL
        :type url: str
        :return: Complete multipass login URL
        :rtype: str
        """
        token = self._generate_token(customerDataHash).decode("utf-8")

        # Ensure URL has proper protocol
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        return f"{url.rstrip('/')}/account/login/multipass/{token}"

    def _generate_token(self, customerDataHash: dict[str, Any]) -> bytes:
        """
        Generate a multipass token.

        :param customerDataHash: Customer information
        :type customerDataHash: dict[str, Any]
        :return: Base64-encoded multipass token
        :rtype: bytes
        """
        cipherText = self._encrypt(json.dumps(customerDataHash))
        return urlsafe_b64encode(cipherText + self._sign(cipherText))

    def _encrypt(self, plainText: str) -> bytes:
        """
        Encrypt plaintext data.

        :param plainText: Data to encrypt
        :type plainText: str
        :return: Encrypted data with IV
        :rtype: bytes
        """
        plainText = self._pad(plainText)
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.encryptionKey, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(plainText.encode("utf-8"))

    def _sign(self, secret: bytes) -> bytes:
        """
        Sign data with HMAC.

        :param secret: Data to sign
        :type secret: bytes
        :return: HMAC signature
        :rtype: bytes
        """
        return HMAC.new(self.signatureKey, secret, SHA256).digest()

    def _pad(self, s: str) -> str:
        """
        Apply PKCS7 padding for AES encryption.

        :param s: String to pad
        :type s: str
        :return: Padded string
        :rtype: str
        """
        pad_length = AES.block_size - len(s) % AES.block_size
        return s + (pad_length * chr(pad_length))
