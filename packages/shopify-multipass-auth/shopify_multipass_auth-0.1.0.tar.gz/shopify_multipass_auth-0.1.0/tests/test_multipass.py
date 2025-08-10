"""
Comprehensive tests for the Shopify MultiPass service.
"""

import json
import re
from base64 import urlsafe_b64decode
from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256

from shopify_multipass.multipass import MultiPass


class TestMultiPass(TestCase):
    """Test cases for MultiPass class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_secret = "test_secret_key_for_shopify_multipass"
        self.multipass = MultiPass(self.test_secret)
        self.test_email = "test@example.com"
        self.test_domain = "test-shop.myshopify.com"
        self.test_return_to = "https://test-shop.myshopify.com/pages/welcome"

    def test_init_with_valid_secret(self):
        """Test initialization with valid secret."""
        mp = MultiPass("valid_secret")
        self.assertIsNotNone(mp.encryptionKey)
        self.assertIsNotNone(mp.signatureKey)
        self.assertEqual(len(mp.encryptionKey), 16)
        self.assertEqual(len(mp.signatureKey), 16)

    def test_init_with_empty_secret(self):
        """Test initialization with empty secret raises ValueError."""
        with self.assertRaises(ValueError) as context:
            MultiPass("")
        self.assertEqual(str(context.exception), "SHOPIFY_MULTIPASS_SECRET is required")

    def test_init_with_none_secret(self):
        """Test initialization with None secret raises ValueError."""
        with self.assertRaises(ValueError) as context:
            MultiPass(None)
        self.assertEqual(str(context.exception), "SHOPIFY_MULTIPASS_SECRET is required")

    def test_validate_email_valid_addresses(self):
        """Test email validation with valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "first+last@subdomain.domain.org",
            "test123@test-domain.com",
            "a@b.co"
        ]
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(self.multipass._validate_email(email))

    def test_validate_email_invalid_addresses(self):
        """Test email validation with invalid email addresses."""
        invalid_emails = [
            "",
            "invalid",
            "@domain.com",
            "test@",
            "test@domain",
            "test.domain.com",
            "test@.com",
            "test @domain.com"
        ]
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(self.multipass._validate_email(email))

    def test_validate_domain_valid_shopify_domains(self):
        """Test domain validation with valid Shopify domains."""
        valid_domains = [
            "test-shop.myshopify.com",
            "mystore.myshopify.com",
            "test123.myshopify.com",
            "https://test-shop.myshopify.com",
            "http://test-shop.myshopify.com"
        ]
        for domain in valid_domains:
            with self.subTest(domain=domain):
                self.assertTrue(self.multipass._validate_domain(domain))

    def test_validate_domain_valid_custom_domains(self):
        """Test domain validation with valid custom domains."""
        valid_domains = [
            "example.com",
            "my-store.co",
            "https://example.com",
            "http://example.com"
        ]
        for domain in valid_domains:
            with self.subTest(domain=domain):
                self.assertTrue(self.multipass._validate_domain(domain))

    def test_validate_domain_invalid_domains(self):
        """Test domain validation with invalid domains."""
        invalid_domains = [
            "",
            "invalid",
            ".com",
            "test.",
            "test..com",
            "test space.com",
            "http://",
            "https://"
        ]
        for domain in invalid_domains:
            with self.subTest(domain=domain):
                self.assertFalse(self.multipass._validate_domain(domain))

    def test_get_token_only_success(self):
        """Test successful token generation."""
        result = self.multipass.get_token_only(self.test_email, self.test_return_to)
        
        self.assertEqual(result["error"], 0)
        self.assertIn("token", result)
        self.assertIsInstance(result["token"], str)
        self.assertGreater(len(result["token"]), 0)

    def test_get_token_only_invalid_email(self):
        """Test token generation with invalid email."""
        result = self.multipass.get_token_only("invalid_email", self.test_return_to)
        
        self.assertEqual(result["error"], 1)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Invalid email format")

    def test_get_token_only_missing_email(self):
        """Test token generation with missing email."""
        result = self.multipass.get_token_only("", self.test_return_to)
        
        self.assertEqual(result["error"], 1)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Email and return_to are required")

    def test_get_token_only_missing_return_to(self):
        """Test token generation with missing return_to."""
        result = self.multipass.get_token_only(self.test_email, "")
        
        self.assertEqual(result["error"], 1)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Email and return_to are required")

    def test_get_login_url_with_token_success(self):
        """Test successful login URL generation with token."""
        # First get a token
        token_result = self.multipass.get_token_only(self.test_email, self.test_return_to)
        token = token_result["token"]
        
        # Then generate login URL
        result = self.multipass.get_login_url_with_token(token, self.test_domain)
        
        self.assertEqual(result["error"], 0)
        self.assertIn("redirect", result)
        expected_url = f"https://{self.test_domain}/account/login/multipass/{token}"
        self.assertEqual(result["redirect"], expected_url)

    def test_get_login_url_with_token_domain_with_protocol(self):
        """Test login URL generation with domain that already has protocol."""
        token_result = self.multipass.get_token_only(self.test_email, self.test_return_to)
        token = token_result["token"]
        
        domain_with_protocol = f"https://{self.test_domain}"
        result = self.multipass.get_login_url_with_token(token, domain_with_protocol)
        
        self.assertEqual(result["error"], 0)
        expected_url = f"https://{self.test_domain}/account/login/multipass/{token}"
        self.assertEqual(result["redirect"], expected_url)

    def test_get_login_url_with_token_missing_token(self):
        """Test login URL generation with missing token."""
        result = self.multipass.get_login_url_with_token("", self.test_domain)
        
        self.assertEqual(result["error"], 1)
        self.assertEqual(result["message"], "Token and domain are required")

    def test_get_login_url_with_token_missing_domain(self):
        """Test login URL generation with missing domain."""
        result = self.multipass.get_login_url_with_token("test_token", "")
        
        self.assertEqual(result["error"], 1)
        self.assertEqual(result["message"], "Token and domain are required")

    def test_get_login_url_with_token_invalid_domain(self):
        """Test login URL generation with invalid domain."""
        result = self.multipass.get_login_url_with_token("test_token", "invalid_domain")
        
        self.assertEqual(result["error"], 1)
        self.assertEqual(result["message"], "Invalid domain format")

    def test_generate_complete_login_url_success(self):
        """Test successful complete login URL generation."""
        result = self.multipass._generate_complete_login_url(
            self.test_email, self.test_return_to, self.test_domain
        )
        
        self.assertEqual(result["error"], 0)
        self.assertIn("redirect", result)
        self.assertTrue(result["redirect"].startswith(f"https://{self.test_domain}/account/login/multipass/"))

    def test_generate_complete_login_url_missing_params(self):
        """Test complete login URL generation with missing parameters."""
        # Missing email
        result = self.multipass._generate_complete_login_url("", self.test_return_to, self.test_domain)
        self.assertEqual(result["error"], 1)
        self.assertEqual(result["message"], "Email, domain, and return_to are required")
        
        # Missing return_to
        result = self.multipass._generate_complete_login_url(self.test_email, "", self.test_domain)
        self.assertEqual(result["error"], 1)
        self.assertEqual(result["message"], "Email, domain, and return_to are required")
        
        # Missing domain
        result = self.multipass._generate_complete_login_url(self.test_email, self.test_return_to, "")
        self.assertEqual(result["error"], 1)
        self.assertEqual(result["message"], "Email, domain, and return_to are required")

    def test_generate_login_url_backward_compatibility(self):
        """Test backward compatibility method."""
        result = self.multipass.generate_login_url(self.test_email, self.test_domain, self.test_return_to)
        
        self.assertEqual(result["error"], 0)
        self.assertIn("redirect", result)
        self.assertTrue(result["redirect"].startswith(f"https://{self.test_domain}/account/login/multipass/"))

    def test_token_contains_valid_data(self):
        """Test that generated token contains valid customer data."""
        result = self.multipass.get_token_only(self.test_email, self.test_return_to)
        token = result["token"]
        
        # Decode and verify token structure
        decoded_data = urlsafe_b64decode(token.encode())
        
        # Token should have encrypted data + signature
        # The signature is 32 bytes (SHA256), so split accordingly
        encrypted_data = decoded_data[:-32]
        signature = decoded_data[-32:]
        
        # Verify signature
        expected_signature = HMAC.new(self.multipass.signatureKey, encrypted_data, SHA256).digest()
        self.assertEqual(signature, expected_signature)
        
        # Decrypt and verify data
        iv = encrypted_data[:AES.block_size]
        ciphertext = encrypted_data[AES.block_size:]
        cipher = AES.new(self.multipass.encryptionKey, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(ciphertext).decode('utf-8')
        
        # Remove PKCS7 padding
        pad_length = ord(decrypted_padded[-1])
        decrypted_data = decrypted_padded[:-pad_length]
        
        # Parse JSON and verify content
        customer_data = json.loads(decrypted_data)
        self.assertEqual(customer_data["email"], self.test_email)
        self.assertEqual(customer_data["return_to"], self.test_return_to)
        self.assertIn("created_at", customer_data)
        
        # Verify timestamp format
        datetime.fromisoformat(customer_data["created_at"].replace('Z', '+00:00'))

    def test_pad_functionality(self):
        """Test PKCS7 padding functionality."""
        test_cases = [
            ("hello", 11),  # 5 chars, needs 11 chars padding to reach 16
            ("1234567890123456", 16),  # 16 chars, needs 16 chars padding (full block)
            ("test", 12),  # 4 chars, needs 12 chars padding to reach 16
        ]
        
        for text, expected_pad_length in test_cases:
            with self.subTest(text=text):
                padded = self.multipass._pad(text)
                actual_pad_length = len(padded) - len(text)
                self.assertEqual(actual_pad_length, expected_pad_length)
                
                # Verify total length is multiple of 16
                self.assertEqual(len(padded) % 16, 0)
                
                # Verify padding content
                padding_char = chr(expected_pad_length)
                self.assertTrue(padded.endswith(padding_char * expected_pad_length))

    def test_encrypt_decrypt_cycle(self):
        """Test that encryption and manual decryption work correctly."""
        test_data = "test data for encryption"
        encrypted = self.multipass._encrypt(test_data)
        
        # Manual decryption
        iv = encrypted[:AES.block_size]
        ciphertext = encrypted[AES.block_size:]
        cipher = AES.new(self.multipass.encryptionKey, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(ciphertext).decode('utf-8')
        
        # Remove padding
        pad_length = ord(decrypted_padded[-1])
        decrypted = decrypted_padded[:-pad_length]
        
        self.assertEqual(decrypted, test_data)

    def test_sign_verification(self):
        """Test HMAC signing functionality."""
        test_data = b"test data to sign"
        signature = self.multipass._sign(test_data)
        
        # Verify signature
        expected_signature = HMAC.new(self.multipass.signatureKey, test_data, SHA256).digest()
        self.assertEqual(signature, expected_signature)
        self.assertEqual(len(signature), 32)  # SHA256 produces 32-byte hash

    @patch('shopify_multipass.multipass.datetime')
    def test_consistent_timestamps(self, mock_datetime):
        """Test that timestamps are consistent and in correct format."""
        # Mock datetime to return a fixed time
        fixed_time = datetime(2023, 12, 25, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.datetime.now.return_value = fixed_time
        mock_datetime.timezone = timezone
        
        result = self.multipass.get_token_only(self.test_email, self.test_return_to)
        token = result["token"]
        
        # Decode and verify timestamp
        decoded_data = urlsafe_b64decode(token.encode())
        encrypted_data = decoded_data[:-32]
        
        iv = encrypted_data[:AES.block_size]
        ciphertext = encrypted_data[AES.block_size:]
        cipher = AES.new(self.multipass.encryptionKey, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(ciphertext).decode('utf-8')
        
        pad_length = ord(decrypted_padded[-1])
        decrypted_data = decrypted_padded[:-pad_length]
        
        customer_data = json.loads(decrypted_data)
        self.assertEqual(customer_data["created_at"], fixed_time.isoformat())

    def test_different_secrets_produce_different_tokens(self):
        """Test that different secrets produce different tokens for same data."""
        mp1 = MultiPass("secret1")
        mp2 = MultiPass("secret2")
        
        token1 = mp1.get_token_only(self.test_email, self.test_return_to)["token"]
        token2 = mp2.get_token_only(self.test_email, self.test_return_to)["token"]
        
        self.assertNotEqual(token1, token2)

    def test_same_data_different_tokens_due_to_randomness(self):
        """Test that same data produces different tokens due to random IV."""
        token1 = self.multipass.get_token_only(self.test_email, self.test_return_to)["token"]
        token2 = self.multipass.get_token_only(self.test_email, self.test_return_to)["token"]
        
        # Tokens should be different due to random IV
        self.assertNotEqual(token1, token2)

    def test_url_trailing_slash_handling(self):
        """Test that URLs with trailing slashes are handled correctly."""
        domain_with_slash = f"{self.test_domain}/"
        result = self.multipass._generate_complete_login_url(
            self.test_email, self.test_return_to, domain_with_slash
        )
        
        self.assertEqual(result["error"], 0)
        # Should not have double slashes
        self.assertNotIn("//account", result["redirect"])
        self.assertTrue(result["redirect"].startswith(f"https://{self.test_domain}/account/login/multipass/"))

    def test_error_handling_in_methods(self):
        """Test error handling in various methods."""
        # Test with invalid inputs that might cause exceptions
        with patch.object(self.multipass, '_validate_email', side_effect=Exception("Test error")):
            result = self.multipass.get_token_only(self.test_email, self.test_return_to)
            self.assertEqual(result["error"], 1)
            self.assertIn("Error:", result["message"])

    def test_edge_case_very_long_email(self):
        """Test with very long email address."""
        long_email = "a" * 50 + "@" + "b" * 50 + ".com"
        result = self.multipass.get_token_only(long_email, self.test_return_to)
        
        self.assertEqual(result["error"], 0)
        self.assertIn("token", result)

    def test_edge_case_very_long_return_to(self):
        """Test with very long return_to URL."""
        long_return_to = "https://" + "a" * 200 + ".com/path"
        result = self.multipass.get_token_only(self.test_email, long_return_to)
        
        self.assertEqual(result["error"], 0)
        self.assertIn("token", result)

    def test_unicode_handling(self):
        """Test handling of unicode characters in email and URLs."""
        unicode_data = {
            "email": "tëst@éxample.com",
            "return_to": "https://example.com/págë"
        }
        
        # Note: While the email might not pass validation due to unicode,
        # the encryption should handle unicode properly
        result = self.multipass.get_token_only(unicode_data["email"], unicode_data["return_to"])
        
        # The email validation will likely fail, but let's test encryption directly
        customer_data = {
            "email": unicode_data["email"],
            "return_to": unicode_data["return_to"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # This should not raise an exception
        token = self.multipass._generate_token(customer_data)
        self.assertIsInstance(token, bytes)


if __name__ == "__main__":
    import unittest
    unittest.main()
