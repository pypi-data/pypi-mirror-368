import logging
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
import base64


class EncryptData:
    """
    Utility class for encrypting sensitive data using RSA-OAEP with SHA-1.
    This class is designed to securely encrypt identifiers such as Aadhaar numbers, OTPs, or mobile numbers
    before transmitting them to the ABHA (Ayushman Bharat Health Account) APIs.
    Key Features:
        - Encrypts data using RSA public keys.
        - Supports both PEM-formatted public keys and base64-encoded key strings.
        - Returns the encrypted data as a base64-encoded string.
    Example usage:
        encrypted = await encrypt_data_for_abha("123456789012", public_key_pem)
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def encrypt_data_for_abha(
        self, data_to_encrypt: str, certificate_pem: str
    ) -> str:
        """
        Encrypt sensitive data using RSA-OAEP with SHA-1 and a provided public key.

        This utility is designed for securely encrypting identifiers such as Aadhaar numbers, OTPs, or mobile numbers
        before transmitting them to the ABHA (Ayushman Bharat Health Account) APIs. The function accepts either a full PEM-formatted
        public key or a base64-encoded key string, ensuring compatibility with various key formats.

        Args:
            data_to_encrypt (str): The plaintext data to be encrypted (e.g., Aadhaar number, OTP).
            certificate_pem (str): The public key in PEM format or as a base64-encoded string.

        Returns:
            str: The base64-encoded ciphertext, ready for secure transmission to the ABHA API.

        Raises:
            ValueError: If the provided public key is invalid or encryption fails.

        Example usage:
            encrypted = await encrypt_data_for_abha("123456789012", public_key_pem)
        """

        key_content = certificate_pem.strip()
        if not key_content.startswith("-----BEGIN"):
            key_content = (
                "-----BEGIN PUBLIC KEY-----\n"
                f"{key_content}\n"
                "-----END PUBLIC KEY-----"
            )

        public_key = serialization.load_pem_public_key(
            key_content.encode("utf-8"), backend=default_backend()
        )

        encrypted_bytes = public_key.encrypt(
            data_to_encrypt.encode("utf-8"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None,
            ),
        )

        return base64.b64encode(encrypted_bytes).decode("utf-8")
