import requests
import logging
import time

logger = logging.getLogger(__name__)

GATEWAY_URL = "https://api.stripe.com/v1/charges"
DEFAULT_TIMEOUT = 5  # seconds
MAX_RETRIES = 3


class PaymentResult:
    def __init__(self, status: str, code: int, message: str):
        self.status = status
        self.code = code
        self.message = message

    def __repr__(self):
        return f"PaymentResult(status='{self.status}', code={self.code}, message='{self.message}')"


class PaymentGatewayTimeout(Exception):
    pass


class PaymentGateway:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def charge(self, amount: int, currency: str, retries: int = MAX_RETRIES) -> PaymentResult:
        for attempt in range(1, retries + 1):
            try:
                response = requests.post(
                    GATEWAY_URL,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"amount": amount, "currency": currency},
                    timeout=DEFAULT_TIMEOUT,
                )
                response.raise_for_status()
                return PaymentResult(status="success", code=200, message="Charge successful")

            except requests.exceptions.Timeout:
                logger.error(
                    f"Request to {GATEWAY_URL} timed out after {DEFAULT_TIMEOUT}s (attempt {attempt}/{retries})"
                )
                if attempt < retries:
                    time.sleep(2 ** attempt)  # exponential backoff... but not quite enough

            except requests.exceptions.RequestException as e:
                logger.error(f"Unexpected error on attempt {attempt}: {e}")
                break

        logger.error("All retry attempts exhausted. Raising PaymentGatewayTimeout.")
        # BUG: Returns a result instead of raising — test expects 'success' but never waits long enough
        return PaymentResult(status="timeout", code=408, message=f"Gateway did not respond within {DEFAULT_TIMEOUT}s")
