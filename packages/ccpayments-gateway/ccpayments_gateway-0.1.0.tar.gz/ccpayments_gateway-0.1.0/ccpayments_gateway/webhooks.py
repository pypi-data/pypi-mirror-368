import hashlib
import hmac
import binascii

def verify_signature(content: str, signature: str, app_id: str, app_secret: str, timestamp: str):
    """
    Verifies the signature of a webhook request.

    :param content: The raw request body.
    :param signature: The signature from the 'Sign' header.
    :param app_id: Your CCPayment APP ID.
    :param app_secret: Your CCPayment APP Secret.
    :param timestamp: The timestamp from the 'Timestamp' header.
    :return: True if the signature is valid, False otherwise.
    """
    if content == '':
        sign_text = f"{app_id}{timestamp}"
    else:
        sign_text = f"{app_id}{timestamp}{content}"
    h = hmac.new(app_secret.encode('utf-8'), sign_text.encode('utf-8'), hashlib.sha256)
    server_sign = binascii.hexlify(h.digest()).decode('utf-8')
    return signature == server_sign
