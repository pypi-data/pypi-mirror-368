import logging
import os
from typing import Any
import json
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
from jose import jwe, jwk
from jose.constants import ALGORITHMS

load_dotenv()


class AiUtilities:
    """
    Utility class for cryptographic operations required by AI services, such as encryption of payloads
    and loading public keys from X.509 certificates.

    This class is intended to be used internally by AI-related service classes to ensure secure
    transmission of sensitive healthcare data to backend APIs.

    !!! note "Key Features"
        - Loads RSA public keys from PEM-encoded X.509 certificates and converts them to JWK format.
        - Encrypts arbitrary payloads using JWE (JSON Web Encryption) with RSA-OAEP-256 and AES-GCM.
        - Handles environment variable management for encryption keys.
        - Provides robust error handling and logging for all cryptographic operations.

    Methods:
        load_public_key_from_x509_certificate : Loads an RSA public key from a PEM-encoded X.509 certificate and returns it as a JWK dictionary.
        encryption : Encrypts a payload dictionary using JWE with an RSA public key loaded from the `ENCRYPTION_PUBLIC_KEY` environment variable.

    Example usage:
        ```
        utils = AiUtilities()
        encrypted = await utils.encryption({"foo": "bar"})
        ```
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def load_public_key_from_x509_certificate(self, certificate_pem: str) -> dict:
        """
        Load an RSA public key from a PEM-encoded X.509 certificate and return it as a JWK (JSON Web Key) dictionary.

        This utility is essential for converting X.509 certificates (typically used in healthcare integrations) into
        JWK format, which is required for JWE encryption.

        ### Args:
            certificate_pem (str): The full PEM-encoded X.509 certificate as a string. Should begin with:
                -----BEGIN CERTIFICATE-----
                ...
                -----END CERTIFICATE-----

        ### Returns:
            dict: A JWK-formatted dictionary that can be used for cryptographic operations such as JWE encryption.

        ### Raises:
            RuntimeError: If the certificate is invalid, unreadable, or does not contain an RSA public key.

        Example:
            ```
            certificate = \"\"\"
            -----BEGIN CERTIFICATE-----
            MIIDdzCCAl+gAwIBAgIEb...
            -----END CERTIFICATE-----
            \"\"\"
            utils = AiUtilities()
            jwk_key = await utils.load_public_key_from_x509_certificate(certificate)
            print(jwk_key)
            ```
        ### Response:

            Output (example JWK):
            {
                "kty": "RSA",
                "e": "AQAB",
                "n": "...",
                "alg": "RSA-OAEP-256",
                "use": "enc"
            }

        ### Notes:
            - This function internally uses the `cryptography` and `python-jose` libraries.
            - It is asynchronous to allow for compatibility with other async workflows.
        """

        try:
            cert = x509.load_pem_x509_certificate(
                certificate_pem.encode("utf-8"), default_backend()
            )
            public_key = cert.public_key()

            if not isinstance(public_key, rsa.RSAPublicKey):
                raise ValueError("The certificate does not contain an RSA public key.")

            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            jwk_object = jwk.construct(
                public_pem.decode("utf-8"),  # public_pem is bytes, decode to string
                algorithm=ALGORITHMS.RSA_OAEP_256,  # Specify the algorithm context
            )
            jwk_dict = jwk_object.to_dict()
            return jwk_dict
        except Exception as e:
            self.logger.error(
                f"Error loading public key from certificate: {e}", exc_info=True
            )
            raise RuntimeError(
                f"Failed to load public key from certificate: {e}"
            ) from e

    async def encryption(self, payload: dict[str, Any]) -> str:
        """
        Encrypt a payload dictionary using JSON Web Encryption (JWE) with RSA-OAEP-256 for key management
        and AES-256-GCM for content encryption.

        The method fetches the public key from the `ENCRYPTION_PUBLIC_KEY` environment variable (as a PEM X.509 certificate),
        converts it into JWK format, and then encrypts the payload using the JWE standard. This ensures safe transmission
        of sensitive healthcare data, such as patient information, clinical summaries, or prescriptions.

        ### Args:
            payload (dict[str, Any]): The data to encrypt. This must be JSON-serializable and typically includes sensitive
            content such as:
                - Personal patient information
                - Clinical observations
                - Encounter records

        ### Returns:
            str: A Base64-encoded UTF-8 JWE compact-serialized string representing the encrypted payload.

        ### Raises:
            RuntimeError: If the encryption fails due to:
                - Missing `ENCRYPTION_PUBLIC_KEY` environment variable
                - Invalid or non-RSA certificate
                - Errors during JWE encryption

        ### Environment Variables:
            ENCRYPTION_PUBLIC_KEY: Must contain a valid PEM-encoded X.509 certificate string.

        Example:
            ```
            import os
            os.environ["ENCRYPTION_PUBLIC_KEY"] = \"\"\"
            -----BEGIN CERTIFICATE-----
            MIIDdzCCAl+gAwIBAgIEb...
            -----END CERTIFICATE-----
            \"\"\"

            utils = AiUtilities()
            encrypted_data = await utils.encryption({
                "patientName": "John Doe",
                "dob": "1985-05-01",
                "diagnosis": "Hypertension"
            })

            print(encrypted_data)
            ```

        ### Response:
            The output will be a JWE string that can be safely transmitted to backend AI APIs for processing.
            # Output (truncated JWE string):
            eyJhbGciOiJSU0EtT0FFUC0yNTYiLCJlbmMiOiJBMTI4R0NN...

        ### Notes:
            - Encryption uses RSA-OAEP-256 for secure key wrapping and AES-256-GCM for fast and secure content encryption.
            - Designed to work seamlessly with backend AI APIs expecting encrypted payloads.

        """
        try:

            # Load the public key as a JWK from the certificate
            certificate_pem_raw = os.getenv("ENCRYPTION_PUBLIC_KEY")
            if not certificate_pem_raw:
                self.logger.error(
                    "ENCRYPTION_PUBLIC_KEY environment variable not set or empty."
                )
                raise ValueError(
                    "ENCRYPTION_PUBLIC_KEY environment variable not set or empty."
                )

            public_jwk = await self.load_public_key_from_x509_certificate(
                certificate_pem_raw
            )

            payload_bytes = json.dumps(payload).encode("utf-8")

            encrypted_payload = jwe.encrypt(
                plaintext=payload_bytes,
                key=public_jwk,  # Use the JWK dictionary
                algorithm=ALGORITHMS.RSA_OAEP_256,
                encryption=ALGORITHMS.A256GCM,
                # 'zip', 'cty', 'kid' could be passed here if needed and supported
            )
            self.logger.debug("Encryption successful.")
            return encrypted_payload.decode("utf-8")

        except Exception as error:
            self.logger.error(f"Failed to encrypt data: {error}", exc_info=True)
            raise RuntimeError(f"Failed to encrypt data: {error}") from error
