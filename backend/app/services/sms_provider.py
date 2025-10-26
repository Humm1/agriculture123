import os
import logging
from typing import Optional

log = logging.getLogger('sms_provider')

TWILIO_ACCOUNT = os.environ.get('TWILIO_ACCOUNT')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
TWILIO_FROM = os.environ.get('TWILIO_FROM')

def send_sms_via_gateway(to: str, message: str) -> bool:
    """Attempt to send SMS via configured gateway (Twilio). Returns True on success."""
    if not (TWILIO_ACCOUNT and TWILIO_TOKEN and TWILIO_FROM):
        log.warning('Twilio not configured; falling back to log')
        return False
    try:
        # lazy import to avoid dependency requirement unless configured
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT, TWILIO_TOKEN)
        client.messages.create(body=message, from_=TWILIO_FROM, to=to)
        log.info('SMS sent via Twilio to %s', to)
        return True
    except Exception as e:
        log.exception('Failed to send SMS via gateway: %s', e)
        return False

def send_sms(to: str, message: str, attempt_gateway: bool = True) -> bool:
    """High-level SMS sender. If gateway not configured, logs the message.
    Returns True if message was sent (gateway) otherwise logs and returns False.
    """
    if attempt_gateway:
        ok = send_sms_via_gateway(to, message)
        if ok:
            return True
    # fallback: log message so operator / dev can inspect; mobile app can also send SMS locally
    log.info('SMS (logged) -> %s: %s', to, message)
    return False
